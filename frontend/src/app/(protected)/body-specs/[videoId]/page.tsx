'use client';

/**
 * Body Specification page
 * @file page.tsx
 * @feature F004 - Body Specification Input
 *
 * Implements:
 * - AC-018: Form with height, weight, experience level, stance
 * - AC-019: Validation: height (100-250cm), weight (30-200kg)
 * - AC-020: Submit initiates pose estimation job
 * - AC-024: Body specs pre-filled for returning users
 *
 * BDD Scenarios:
 * - User enters valid body specifications
 * - Height validation (100-250cm) with red border on error
 * - Weight validation (30-200kg) with red border on error
 * - All fields required for submission
 * - Body specs pre-filled for returning user
 * - Invalid number format shows error, decimals rounded
 */

import { useCallback, useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  FormControl,
  FormHelperText,
  InputAdornment,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
  Snackbar,
  TextField,
  Typography,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { useAuth } from '@/lib/auth/hooks';
import {
  BodySpecsError,
  ExperienceLevel,
  getPrefillSpecs,
  Stance,
  submitBodySpecs,
} from '@/lib/body-specs';

/** Validation constants matching backend */
const HEIGHT_MIN = 100;
const HEIGHT_MAX = 250;
const WEIGHT_MIN = 30;
const WEIGHT_MAX = 200;

/** Experience level display options (Korean + English) */
const EXPERIENCE_OPTIONS: { value: ExperienceLevel; labelEn: string; labelKo: string }[] = [
  { value: 'beginner', labelEn: 'Beginner (0-1 year)', labelKo: '초급 (0-1년)' },
  { value: 'intermediate', labelEn: 'Intermediate (1-3 years)', labelKo: '중급 (1-3년)' },
  { value: 'advanced', labelEn: 'Advanced (3-5 years)', labelKo: '고급 (3-5년)' },
  { value: 'competitive', labelEn: 'Competitive (5+ years)', labelKo: '선수급 (5년 이상)' },
];

/** Stance display options (Korean + English) */
const STANCE_OPTIONS: { value: Stance; labelEn: string; labelKo: string }[] = [
  { value: 'orthodox', labelEn: 'Orthodox', labelKo: '오소독스' },
  { value: 'southpaw', labelEn: 'Southpaw', labelKo: '사우스포' },
];

/** Form field errors */
interface FieldErrors {
  height?: string;
  weight?: string;
  experience?: string;
  stance?: string;
}

export default function BodySpecsPage() {
  const params = useParams();
  const router = useRouter();
  const { accessToken, isLoading: isAuthLoading, isAuthenticated } = useAuth();

  const videoId = params.videoId as string;

  // Form state
  const [heightValue, setHeightValue] = useState('');
  const [weightValue, setWeightValue] = useState('');
  const [experience, setExperience] = useState<ExperienceLevel | ''>('');
  const [stance, setStance] = useState<Stance | ''>('');

  // Validation state
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  // Loading/submission state
  const [isPrefillLoading, setIsPrefillLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Error state
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showError, setShowError] = useState(false);

  // Fetch pre-fill data on mount (AC-024)
  useEffect(() => {
    if (!accessToken) return;

    const fetchPrefill = async () => {
      try {
        const data = await getPrefillSpecs(accessToken);

        if (data.has_saved_specs) {
          if (data.height_cm !== null) {
            setHeightValue(String(data.height_cm));
          }
          if (data.weight_kg !== null) {
            setWeightValue(String(data.weight_kg));
          }
          if (data.experience_level !== null) {
            setExperience(data.experience_level as ExperienceLevel);
          }
          if (data.stance !== null) {
            setStance(data.stance as Stance);
          }
        }
      } catch (error) {
        // Pre-fill failure is non-fatal - user can still enter data manually
        console.error('Failed to load prefill data:', error);
      } finally {
        setIsPrefillLoading(false);
      }
    };

    fetchPrefill();
  }, [accessToken]);

  // Validate height field
  const validateHeight = useCallback((value: string): string | undefined => {
    if (!value.trim()) {
      return 'Please enter your height. / 키를 입력해 주세요.';
    }

    // Strip non-numeric characters except decimal point
    const numericValue = value.replace(/[^\d.]/g, '');
    const num = parseFloat(numericValue);

    if (isNaN(num)) {
      return 'Please enter a valid number. / 올바른 숫자를 입력해 주세요.';
    }

    if (num < HEIGHT_MIN) {
      return `Height must be at least ${HEIGHT_MIN}cm. / 키는 ${HEIGHT_MIN}cm 이상이어야 합니다.`;
    }

    if (num > HEIGHT_MAX) {
      return `Height must be under ${HEIGHT_MAX}cm. / 키는 ${HEIGHT_MAX}cm 이하여야 합니다.`;
    }

    return undefined;
  }, []);

  // Validate weight field
  const validateWeight = useCallback((value: string): string | undefined => {
    if (!value.trim()) {
      return 'Please enter your weight. / 체중을 입력해 주세요.';
    }

    // Strip non-numeric characters except decimal point
    const numericValue = value.replace(/[^\d.]/g, '');
    const num = parseFloat(numericValue);

    if (isNaN(num)) {
      return 'Please enter a valid number. / 올바른 숫자를 입력해 주세요.';
    }

    if (num < WEIGHT_MIN) {
      return `Weight must be at least ${WEIGHT_MIN}kg. / 체중은 ${WEIGHT_MIN}kg 이상이어야 합니다.`;
    }

    if (num > WEIGHT_MAX) {
      return `Weight must be under ${WEIGHT_MAX}kg. / 체중은 ${WEIGHT_MAX}kg 이하여야 합니다.`;
    }

    return undefined;
  }, []);

  // Handle height input change
  const handleHeightChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const rawValue = e.target.value;
    // Strip non-numeric except decimal for display
    const numericOnly = rawValue.replace(/[^\d.]/g, '');
    setHeightValue(numericOnly);

    // Validate on change if already touched
    if (touched.height) {
      const error = validateHeight(numericOnly);
      setFieldErrors((prev) => ({ ...prev, height: error }));
    }
  }, [touched.height, validateHeight]);

  // Handle weight input change
  const handleWeightChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const rawValue = e.target.value;
    // Strip non-numeric except decimal for display
    const numericOnly = rawValue.replace(/[^\d.]/g, '');
    setWeightValue(numericOnly);

    // Validate on change if already touched
    if (touched.weight) {
      const error = validateWeight(numericOnly);
      setFieldErrors((prev) => ({ ...prev, weight: error }));
    }
  }, [touched.weight, validateWeight]);

  // Handle height blur - validate and round decimals
  const handleHeightBlur = useCallback(() => {
    setTouched((prev) => ({ ...prev, height: true }));

    if (heightValue) {
      // Round decimal to integer
      const num = parseFloat(heightValue);
      if (!isNaN(num)) {
        setHeightValue(String(Math.round(num)));
      }
    }

    const error = validateHeight(heightValue);
    setFieldErrors((prev) => ({ ...prev, height: error }));
  }, [heightValue, validateHeight]);

  // Handle weight blur - validate and round decimals
  const handleWeightBlur = useCallback(() => {
    setTouched((prev) => ({ ...prev, weight: true }));

    if (weightValue) {
      // Round decimal to integer
      const num = parseFloat(weightValue);
      if (!isNaN(num)) {
        setWeightValue(String(Math.round(num)));
      }
    }

    const error = validateWeight(weightValue);
    setFieldErrors((prev) => ({ ...prev, weight: error }));
  }, [weightValue, validateWeight]);

  // Handle experience change
  const handleExperienceChange = useCallback((e: SelectChangeEvent) => {
    const value = e.target.value as ExperienceLevel;
    setExperience(value);
    setTouched((prev) => ({ ...prev, experience: true }));
    setFieldErrors((prev) => ({ ...prev, experience: undefined }));
  }, []);

  // Handle stance change
  const handleStanceChange = useCallback((e: SelectChangeEvent) => {
    const value = e.target.value as Stance;
    setStance(value);
    setTouched((prev) => ({ ...prev, stance: true }));
    setFieldErrors((prev) => ({ ...prev, stance: undefined }));
  }, []);

  // Validate all fields
  const validateAll = useCallback((): boolean => {
    const errors: FieldErrors = {};

    errors.height = validateHeight(heightValue);
    errors.weight = validateWeight(weightValue);

    if (!experience) {
      errors.experience = 'Please select your experience level. / 경력을 선택해 주세요.';
    }

    if (!stance) {
      errors.stance = 'Please select your stance. / 스탠스를 선택해 주세요.';
    }

    setFieldErrors(errors);
    setTouched({ height: true, weight: true, experience: true, stance: true });

    return !errors.height && !errors.weight && !errors.experience && !errors.stance;
  }, [heightValue, weightValue, experience, stance, validateHeight, validateWeight]);

  // Check if form is valid for enabling submit button
  const isFormValid = useCallback((): boolean => {
    if (!heightValue || !weightValue || !experience || !stance) {
      return false;
    }

    const heightError = validateHeight(heightValue);
    const weightError = validateWeight(weightValue);

    return !heightError && !weightError;
  }, [heightValue, weightValue, experience, stance, validateHeight, validateWeight]);

  // Handle form submission
  const handleSubmit = useCallback(async () => {
    if (!accessToken) return;

    // Validate all fields
    if (!validateAll()) {
      // Focus on first error field
      const errorFields = ['height', 'weight', 'experience', 'stance'];
      for (const field of errorFields) {
        if (fieldErrors[field as keyof FieldErrors]) {
          const element = document.getElementById(`body-specs-${field}`);
          if (element) {
            element.focus();
          }
          break;
        }
      }
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await submitBodySpecs(accessToken, videoId, {
        height_cm: Math.round(parseFloat(heightValue)),
        weight_kg: Math.round(parseFloat(weightValue)),
        experience_level: experience as ExperienceLevel,
        stance: stance as Stance,
      });

      // Navigate to processing status page
      router.push(`/processing/${videoId}`);
    } catch (error) {
      if (error instanceof BodySpecsError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage('Failed to save body specs. Please try again.');
      }
      setShowError(true);
    } finally {
      setIsSubmitting(false);
    }
  }, [accessToken, videoId, heightValue, weightValue, experience, stance, validateAll, fieldErrors, router]);

  // Handle error close
  const handleErrorClose = useCallback(() => {
    setShowError(false);
  }, []);

  // Auth loading state
  if (isAuthLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '60vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // Not authenticated - redirect will happen via middleware
  if (!isAuthenticated) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '60vh',
        }}
      >
        <Typography>Redirecting to login...</Typography>
      </Box>
    );
  }

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom textAlign="center">
        {/* Page Title - Korean + English */}
        Your Profile / 프로필 입력
      </Typography>
      <Typography
        variant="subtitle1"
        color="text.secondary"
        textAlign="center"
        gutterBottom
        sx={{ mb: 4 }}
      >
        {/* Subtitle - Korean + English */}
        Help us personalize your analysis / 맞춤형 분석을 위해 정보를 입력해주세요
      </Typography>

      {isPrefillLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Box
          component="form"
          sx={{
            display: 'flex',
            flexDirection: 'column',
            gap: 3,
          }}
          noValidate
        >
          {/* Height field */}
          <TextField
            id="body-specs-height"
            label="Height / 키"
            value={heightValue}
            onChange={handleHeightChange}
            onBlur={handleHeightBlur}
            error={touched.height && !!fieldErrors.height}
            helperText={touched.height ? fieldErrors.height : ''}
            InputProps={{
              endAdornment: <InputAdornment position="end">cm</InputAdornment>,
            }}
            inputProps={{
              inputMode: 'numeric',
              pattern: '[0-9]*',
              'aria-describedby': 'body-specs-height-helper',
            }}
            fullWidth
            required
            placeholder="Enter height / 키 입력"
          />

          {/* Weight field */}
          <TextField
            id="body-specs-weight"
            label="Weight / 체중"
            value={weightValue}
            onChange={handleWeightChange}
            onBlur={handleWeightBlur}
            error={touched.weight && !!fieldErrors.weight}
            helperText={touched.weight ? fieldErrors.weight : ''}
            InputProps={{
              endAdornment: <InputAdornment position="end">kg</InputAdornment>,
            }}
            inputProps={{
              inputMode: 'numeric',
              pattern: '[0-9]*',
              'aria-describedby': 'body-specs-weight-helper',
            }}
            fullWidth
            required
            placeholder="Enter weight / 체중 입력"
          />

          {/* Experience level dropdown */}
          <FormControl
            fullWidth
            required
            error={touched.experience && !!fieldErrors.experience}
          >
            <InputLabel id="body-specs-experience-label">
              Experience Level / 경력
            </InputLabel>
            <Select
              id="body-specs-experience"
              labelId="body-specs-experience-label"
              value={experience}
              label="Experience Level / 경력"
              onChange={handleExperienceChange}
            >
              {EXPERIENCE_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.labelEn} / {option.labelKo}
                </MenuItem>
              ))}
            </Select>
            {touched.experience && fieldErrors.experience && (
              <FormHelperText>{fieldErrors.experience}</FormHelperText>
            )}
          </FormControl>

          {/* Stance dropdown */}
          <FormControl
            fullWidth
            required
            error={touched.stance && !!fieldErrors.stance}
          >
            <InputLabel id="body-specs-stance-label">
              Stance / 스탠스
            </InputLabel>
            <Select
              id="body-specs-stance"
              labelId="body-specs-stance-label"
              value={stance}
              label="Stance / 스탠스"
              onChange={handleStanceChange}
            >
              {STANCE_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.labelEn} / {option.labelKo}
                </MenuItem>
              ))}
            </Select>
            {touched.stance && fieldErrors.stance && (
              <FormHelperText>{fieldErrors.stance}</FormHelperText>
            )}
          </FormControl>

          {/* Submit button */}
          <Button
            variant="contained"
            size="large"
            onClick={handleSubmit}
            disabled={!isFormValid() || isSubmitting}
            startIcon={
              isSubmitting ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <PlayArrowIcon />
              )
            }
            sx={{ mt: 2 }}
          >
            {isSubmitting ? 'Saving... / 저장 중...' : 'Start Analysis / 분석 시작'}
          </Button>
        </Box>
      )}

      {/* Error snackbar */}
      <Snackbar
        open={showError}
        autoHideDuration={6000}
        onClose={handleErrorClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleErrorClose}
          severity="error"
          variant="filled"
          sx={{ width: '100%' }}
        >
          {errorMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
}
