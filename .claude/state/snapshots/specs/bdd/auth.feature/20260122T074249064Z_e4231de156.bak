@F001 @US-001
Feature: User Authentication
  As a boxer seeking analysis
  I want to sign up and log in using my existing social accounts
  So that I can quickly access the platform without creating new credentials

  Background:
    Given the application is running
    And the database is available

  @F001 @US-001 @happy-path
  Scenario: Successful Kakao OAuth login
    Given I am on the landing page
    When I click "Continue with Kakao"
    And I complete Kakao OAuth authentication successfully
    Then I should be redirected to the dashboard
    And I should see my profile information in the app bar
    And my session should be active

  @F001 @US-001 @happy-path
  Scenario: Successful Google OAuth login
    Given I am on the landing page
    When I click "Continue with Google"
    And I complete Google OAuth authentication successfully
    Then I should be redirected to the dashboard
    And I should see my profile information in the app bar
    And my session should be active

  @F001 @US-001 @happy-path
  Scenario: User logs out successfully
    Given I am logged in as a user
    And I am on the dashboard
    When I click on my profile menu
    And I click "Log out"
    Then my session should be terminated
    And I should be redirected to the landing page
    And I should see the "Get Started" button

  @F001 @US-001 @auth-guard
  Scenario: Unauthenticated user redirected to login
    Given I am not logged in
    When I navigate directly to "/dashboard"
    Then I should be redirected to "/login"
    And the redirect parameter should preserve my original destination
    And I should see the login options

  @F001 @US-001 @session
  Scenario: Session expiration prompts re-authentication
    Given I am logged in as a user
    And my OAuth token has expired
    When I attempt to access a protected resource
    Then I should see a "Session expired" dialog
    And I should be able to re-authenticate
    And my previous context should be preserved after login

  @F001 @US-001 @error
  Scenario: OAuth login cancelled by user
    Given I am on the login page
    When I click "Continue with Kakao"
    And I cancel the OAuth authentication in the provider
    Then I should be returned to the login page
    And I should see "Login cancelled" message
    And I should be able to try again

  @F001 @US-001 @error @network
  Scenario: OAuth provider unavailable
    Given I am on the login page
    And the Kakao OAuth service is unavailable
    When I click "Continue with Kakao"
    Then I should see an error message about the provider
    And I should be offered to try Google login as alternative
