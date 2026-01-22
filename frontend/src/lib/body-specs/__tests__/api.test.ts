/**
 * Body Specification API client tests
 * @file api.test.ts
 * @feature F004 - Body Specification Input
 *
 * Tests:
 * - AC-018: Form with height, weight, experience level, stance
 * - AC-019: Validation: height (100-250cm), weight (30-200kg)
 * - AC-024: Body specs pre-filled for returning users
 */

import {
  submitBodySpecs,
  getPrefillSpecs,
  BodySpecsError,
  BodySpecsResponse,
  PrefillResponse,
} from '../api';

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('Body Specification API', () => {
  const accessToken = 'test-token';
  const videoId = 'test-video-id';

  beforeEach(() => {
    mockFetch.mockReset();
  });

  describe('submitBodySpecs', () => {
    const validData = {
      height_cm: 175,
      weight_kg: 70,
      experience_level: 'intermediate' as const,
      stance: 'orthodox' as const,
    };

    it('should submit body specs successfully', async () => {
      const mockResponse: BodySpecsResponse = {
        video_id: videoId,
        body_specs_id: 'specs-123',
        saved: true,
        persist_to_profile: true,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await submitBodySpecs(accessToken, videoId, validData);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining(`/analysis/body-specs/${videoId}`),
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify(validData),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should throw BodySpecsError on 404 (video not found)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Video not found' }),
      });

      await expect(
        submitBodySpecs(accessToken, videoId, validData)
      ).rejects.toMatchObject({
        name: 'BodySpecsError',
        code: 'VIDEO_NOT_FOUND',
        statusCode: 404,
      });
    });

    it('should throw BodySpecsError on 401 (unauthorized)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Not authenticated' }),
      });

      await expect(
        submitBodySpecs(accessToken, videoId, validData)
      ).rejects.toMatchObject({
        name: 'BodySpecsError',
        code: 'UNAUTHORIZED',
        statusCode: 401,
      });
    });

    it('should throw BodySpecsError on 422 (validation error)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => ({ detail: 'Height must be between 100 and 250' }),
      });

      await expect(
        submitBodySpecs(accessToken, videoId, validData)
      ).rejects.toMatchObject({
        name: 'BodySpecsError',
        code: 'VALIDATION_ERROR',
        statusCode: 422,
      });
    });

    it('should throw BodySpecsError on server error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Internal server error' }),
      });

      await expect(
        submitBodySpecs(accessToken, videoId, validData)
      ).rejects.toMatchObject({
        name: 'BodySpecsError',
        code: 'SAVE_FAILED',
        statusCode: 500,
      });
    });
  });

  describe('getPrefillSpecs', () => {
    it('should return prefill data for returning user (AC-024)', async () => {
      const mockResponse: PrefillResponse = {
        has_saved_specs: true,
        height_cm: 180,
        weight_kg: 75,
        experience_level: 'advanced',
        stance: 'southpaw',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await getPrefillSpecs(accessToken);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/analysis/body-specs/prefill'),
        expect.objectContaining({
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        })
      );
      expect(result).toEqual(mockResponse);
      expect(result.has_saved_specs).toBe(true);
    });

    it('should return empty prefill for new user', async () => {
      const mockResponse: PrefillResponse = {
        has_saved_specs: false,
        height_cm: null,
        weight_kg: null,
        experience_level: null,
        stance: null,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await getPrefillSpecs(accessToken);

      expect(result.has_saved_specs).toBe(false);
      expect(result.height_cm).toBeNull();
    });

    it('should throw BodySpecsError on 401 (unauthorized)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Not authenticated' }),
      });

      await expect(getPrefillSpecs(accessToken)).rejects.toMatchObject({
        name: 'BodySpecsError',
        code: 'UNAUTHORIZED',
        statusCode: 401,
      });
    });

    it('should throw BodySpecsError on server error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Internal server error' }),
      });

      await expect(getPrefillSpecs(accessToken)).rejects.toMatchObject({
        name: 'BodySpecsError',
        code: 'PREFILL_FAILED',
        statusCode: 500,
      });
    });
  });
});
