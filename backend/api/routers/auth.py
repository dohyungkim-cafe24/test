"""Authentication router for OAuth flows and session management.

Implements F001: User Authentication
- AC-001: Kakao OAuth login
- AC-002: Google OAuth login
- AC-003: Session expiration and refresh
- AC-004: Logout
- AC-005: Protected route access

Security fixes from code review:
- B1: CSRF state validated against server-side storage
- B2/M2: Refresh tokens stored and validated in database
- M1: Access token delivered via fragment identifier (not query param)
- M3: User persisted to database on OAuth callback
- m1: redirect_uri validated against allowlist
"""
from typing import Annotated, Optional
from urllib.parse import urlencode, urlparse

from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse

from api.config import Settings, get_settings
from api.schemas.auth import LogoutResponse, TokenError, TokenResponse, UserProfile
from api.services.oauth_service import OAuthService
from api.services.database import get_db_session
from api.services import user_service, token_service

router = APIRouter(prefix="/auth", tags=["auth"])

# Allowed redirect paths (relative paths only for security)
ALLOWED_REDIRECT_PATHS = {"/dashboard", "/upload", "/history", "/settings", "/profile"}


def get_oauth_service(settings: Annotated[Settings, Depends(get_settings)]) -> OAuthService:
    """Dependency to get OAuth service instance."""
    return OAuthService(settings)


def validate_redirect_path(redirect_uri: Optional[str]) -> Optional[str]:
    """Validate redirect URI against allowlist.

    Only allows relative paths from the allowed set.
    Addresses m1: Open redirect prevention.

    Args:
        redirect_uri: The redirect URI/path to validate.

    Returns:
        Validated redirect path or None if invalid.
    """
    if not redirect_uri:
        return None

    # Parse the URI
    parsed = urlparse(redirect_uri)

    # Reject absolute URLs (must be relative path)
    if parsed.scheme or parsed.netloc:
        return None

    # Get the path portion
    path = parsed.path

    # Check against allowlist
    if path in ALLOWED_REDIRECT_PATHS:
        return path

    # Default: reject unknown paths
    return None


async def get_current_user(
    authorization: Annotated[Optional[str], Header()] = None,
    settings: Settings = Depends(get_settings),
) -> dict:
    """Dependency to get current authenticated user.

    Args:
        authorization: Bearer token from Authorization header.
        settings: Application settings.

    Returns:
        User data dictionary.

    Raises:
        HTTPException: If token is missing or invalid.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[7:]  # Remove "Bearer " prefix
    oauth_service = OAuthService(settings)

    try:
        payload = oauth_service.verify_access_token(token)
        return {
            "id": payload["sub"],
            "email": payload["email"],
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_or_guest(
    authorization: Annotated[Optional[str], Header()] = None,
    settings: Settings = Depends(get_settings),
) -> dict:
    """Dependency to get current user (including guest users).

    All users (including guests) now use JWT tokens.
    Guest users are created via /auth/guest endpoint.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[7:]  # Remove "Bearer " prefix

    # Verify JWT token (works for both regular and guest users)
    oauth_service = OAuthService(settings)
    try:
        payload = oauth_service.verify_access_token(token)
        return {
            "id": payload["sub"],
            "email": payload["email"],
            "is_guest": payload["email"].endswith("@guest.punchanalytics.app"),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# === Kakao OAuth ===


@router.get("/kakao", response_class=RedirectResponse, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def kakao_auth(
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    redirect_uri: Optional[str] = Query(None, description="Post-auth redirect path"),
):
    """Initiate Kakao OAuth flow.

    Redirects to Kakao authorization page.
    """
    # Validate redirect path
    validated_path = validate_redirect_path(redirect_uri)
    auth_url = await oauth_service.get_kakao_auth_url(validated_path)
    return RedirectResponse(url=auth_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/kakao/callback", response_class=RedirectResponse, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def kakao_callback(
    request: Request,
    response: Response,
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
):
    """Handle Kakao OAuth callback.

    Exchanges auth code for tokens and creates user session.
    """
    # Handle OAuth errors (user cancelled, etc.)
    if error:
        error_params = urlencode({"error": error, "error_description": error_description or ""})
        return RedirectResponse(
            url=f"{settings.frontend_url}/login?{error_params}",
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    # Validate CSRF state against server-side storage (B1 fix)
    if not state:
        error_params = urlencode({"error": "invalid_state", "error_description": "Missing state parameter"})
        return RedirectResponse(
            url=f"{settings.frontend_url}/login?{error_params}",
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    is_valid, redirect_path = await oauth_service.validate_state(state)
    if not is_valid:
        error_params = urlencode({"error": "invalid_state", "error_description": "Invalid or expired state token"})
        return RedirectResponse(
            url=f"{settings.frontend_url}/login?{error_params}",
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    try:
        # Exchange code for tokens
        token_data = await oauth_service.exchange_kakao_code(code)
        access_token = token_data["access_token"]

        # Get user profile
        user_data = await oauth_service.get_kakao_user(access_token)

        # Extract user info from Kakao response
        provider_id = str(user_data["id"])
        kakao_account = user_data.get("kakao_account", {})
        email = kakao_account.get("email", f"{provider_id}@kakao.user")
        profile = kakao_account.get("profile", {})
        name = profile.get("nickname")
        avatar_url = profile.get("thumbnail_image_url")

        # Persist user to database (M3 fix)
        async with get_db_session() as session:
            user = await user_service.upsert_user(
                session,
                provider="kakao",
                provider_id=provider_id,
                email=email,
                name=name,
                avatar_url=avatar_url,
            )
            user_id = str(user.id)

            # Create JWT access token
            jwt_access_token = oauth_service.create_access_token(user_id, email)

            # Create and store refresh token (B2/M2 fix)
            raw_refresh_token, token_hash, expires_at = oauth_service.create_refresh_token()
            await token_service.create_refresh_token(
                session,
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires_at,
                user_agent=request.headers.get("User-Agent"),
                ip_address=request.client.host if request.client else None,
            )

        # M1 fix: Use fragment identifier instead of query parameter
        # Token is in URL fragment, not sent to server, not logged
        redirect_url = f"{settings.frontend_url}{redirect_path or '/dashboard'}#access_token={jwt_access_token}"
        redirect_response = RedirectResponse(
            url=redirect_url,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

        # Set refresh token as HttpOnly cookie
        redirect_response.set_cookie(
            key="refresh_token",
            value=raw_refresh_token,
            httponly=True,
            secure=settings.is_production,
            samesite="lax",
            max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
            path="/api/v1/auth",
        )

        return redirect_response

    except ValueError as e:
        error_params = urlencode({"error": "oauth_error", "error_description": str(e)})
        return RedirectResponse(
            url=f"{settings.frontend_url}/login?{error_params}",
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )


# === Google OAuth ===


@router.get("/google", response_class=RedirectResponse, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def google_auth(
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    redirect_uri: Optional[str] = Query(None, description="Post-auth redirect path"),
):
    """Initiate Google OAuth flow.

    Redirects to Google authorization page.
    """
    # Validate redirect path
    validated_path = validate_redirect_path(redirect_uri)
    auth_url = await oauth_service.get_google_auth_url(validated_path)
    return RedirectResponse(url=auth_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/google/callback", response_class=RedirectResponse, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def google_callback(
    request: Request,
    response: Response,
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
):
    """Handle Google OAuth callback.

    Exchanges auth code for tokens and creates user session.
    """
    # Handle OAuth errors
    if error:
        error_params = urlencode({"error": error, "error_description": error_description or ""})
        return RedirectResponse(
            url=f"{settings.frontend_url}/login?{error_params}",
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    # Validate CSRF state against server-side storage (B1 fix)
    if not state:
        error_params = urlencode({"error": "invalid_state", "error_description": "Missing state parameter"})
        return RedirectResponse(
            url=f"{settings.frontend_url}/login?{error_params}",
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    is_valid, redirect_path = await oauth_service.validate_state(state)
    if not is_valid:
        error_params = urlencode({"error": "invalid_state", "error_description": "Invalid or expired state token"})
        return RedirectResponse(
            url=f"{settings.frontend_url}/login?{error_params}",
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    try:
        # Exchange code for tokens
        token_data = await oauth_service.exchange_google_code(code)
        access_token = token_data["access_token"]

        # Get user profile
        user_data = await oauth_service.get_google_user(access_token)

        # Extract user info from Google response
        provider_id = user_data["sub"]
        email = user_data.get("email", f"{provider_id}@google.user")
        name = user_data.get("name")
        avatar_url = user_data.get("picture")

        # Persist user to database (M3 fix)
        async with get_db_session() as session:
            user = await user_service.upsert_user(
                session,
                provider="google",
                provider_id=provider_id,
                email=email,
                name=name,
                avatar_url=avatar_url,
            )
            user_id = str(user.id)

            # Create JWT access token
            jwt_access_token = oauth_service.create_access_token(user_id, email)

            # Create and store refresh token (B2/M2 fix)
            raw_refresh_token, token_hash, expires_at = oauth_service.create_refresh_token()
            await token_service.create_refresh_token(
                session,
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires_at,
                user_agent=request.headers.get("User-Agent"),
                ip_address=request.client.host if request.client else None,
            )

        # M1 fix: Use fragment identifier instead of query parameter
        redirect_url = f"{settings.frontend_url}{redirect_path or '/dashboard'}#access_token={jwt_access_token}"
        redirect_response = RedirectResponse(
            url=redirect_url,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

        # Set refresh token as HttpOnly cookie
        redirect_response.set_cookie(
            key="refresh_token",
            value=raw_refresh_token,
            httponly=True,
            secure=settings.is_production,
            samesite="lax",
            max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
            path="/api/v1/auth",
        )

        return redirect_response

    except ValueError as e:
        error_params = urlencode({"error": "oauth_error", "error_description": str(e)})
        return RedirectResponse(
            url=f"{settings.frontend_url}/login?{error_params}",
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )


# === Session Management ===


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
    refresh_token: Annotated[Optional[str], Cookie()] = None,
):
    """Refresh access token using refresh token cookie.

    Returns new access token if refresh token is valid.
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TokenError(
                error="invalid_refresh_token",
                error_description="Missing refresh token",
            ).model_dump(),
        )

    try:
        # Hash the token and validate against database (B2 fix)
        token_hash = oauth_service.hash_refresh_token(refresh_token)

        async with get_db_session() as session:
            result = await token_service.validate_refresh_token(session, token_hash)

            if not result:
                raise ValueError("Token expired or revoked")

            stored_token, user = result

            # Create new access token
            new_access_token = oauth_service.create_access_token(
                str(user.id),
                user.email,
            )

            return TokenResponse(
                access_token=new_access_token,
                token_type="Bearer",
                expires_in=settings.access_token_expire_minutes * 60,
            )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TokenError(
                error="invalid_refresh_token",
                error_description=str(e) if str(e) else "Token expired or revoked",
            ).model_dump(),
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    response: Response,
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
    refresh_token: Annotated[Optional[str], Cookie()] = None,
):
    """Logout user and clear session.

    Revokes refresh token and clears cookies.
    """
    # Revoke token in database if present
    if refresh_token:
        token_hash = oauth_service.hash_refresh_token(refresh_token)
        async with get_db_session() as session:
            await token_service.revoke_refresh_token(session, token_hash)

    # Clear the refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
        secure=settings.is_production,
        httponly=True,
        samesite="lax",
    )

    return LogoutResponse(message="Logged out successfully")


# === Guest Login ===


@router.post("/guest", response_model=TokenResponse)
async def guest_login(
    request: Request,
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    """Create a guest user and return access token.

    Guest users are stored in the database with provider='guest'.
    This allows them to upload videos and use the analysis features.
    """
    import secrets
    from uuid import uuid4

    # Generate unique guest identifier
    guest_id = f"guest_{secrets.token_hex(8)}"
    guest_email = f"{guest_id}@guest.punchanalytics.app"

    async with get_db_session() as session:
        # Create guest user in database
        user = await user_service.upsert_user(
            session,
            provider="guest",
            provider_id=guest_id,
            email=guest_email,
            name="Guest User",
            avatar_url=None,
        )
        user_id = str(user.id)

        # Create JWT access token
        jwt_access_token = oauth_service.create_access_token(user_id, guest_email)

    return TokenResponse(
        access_token=jwt_access_token,
        token_type="Bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


# === Protected Routes ===


@router.get("/me")
async def get_me(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Get current user profile.

    Requires valid access token.
    """
    # Fetch full user from database
    from uuid import UUID

    try:
        user_id = UUID(current_user["id"])
        async with get_db_session() as session:
            user = await user_service.get_user_by_id(session, user_id)
            if user:
                return user.to_dict()
    except (ValueError, TypeError):
        # ID is not a valid UUID (e.g., synthetic ID from test)
        pass

    return current_user
