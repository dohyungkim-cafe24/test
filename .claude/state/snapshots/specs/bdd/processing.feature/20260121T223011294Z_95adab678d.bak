@F005 @F006 @F007 @US-005 @US-006 @US-007
Feature: Video Processing Pipeline
  As a system processing uploaded video
  I want to extract pose data, generate stamps, and produce strategic analysis
  So that users receive comprehensive coaching feedback

  Background:
    Given the application is running
    And the processing service is available
    And a user has submitted a video for analysis
    And body specifications have been provided

  # US-005: Pose Estimation Processing

  @F005 @US-005 @happy-path
  Scenario: Pose estimation extracts joint coordinates
    Given a valid sparring video has been uploaded
    When the pose estimation processing begins
    Then the system should extract 33-joint XYZ coordinates using MediaPipe
    And coordinate data should be extracted from each frame
    And the data should be stored in structured JSON format

  @F005 @US-005 @happy-path
  Scenario: Subject tracking maintains across frames
    Given pose estimation is in progress
    And a subject has been selected with bounding box
    When processing frames sequentially
    Then the selected subject should be tracked via bounding box correlation
    And the same person should be identified across all frames

  @F005 @US-005 @happy-path
  Scenario: Processing status shows step progress
    Given I am on the processing status page
    When processing is in progress
    Then I should see the video thumbnail
    And I should see "Analyzing movements..." during pose estimation
    And I should see "Step 1 of 3"
    And I should see estimated time remaining
    And I should see elapsed time since start
    And status should update every 5 seconds

  @F005 @US-005 @error
  Scenario: Pose estimation fails with poor video quality
    Given a video with poor lighting has been uploaded
    When pose estimation fails for more than 20% of frames
    Then the analysis should be marked as failed
    And I should see "Unable to analyze video"
    And I should see "Unable to track subject clearly"
    And I should see guidance about better lighting or camera angle
    And I should see "Upload New Video" button

  @F005 @US-005 @timeout
  Scenario: Processing takes longer than expected
    Given processing has been running for over 5 minutes
    When the estimated time has been exceeded
    Then I should see "Taking longer than expected" message
    And processing should continue
    And status polling should continue

  # US-006: Stamp Generation

  @F006 @US-006 @happy-path
  Scenario: Strike detection identifies punch types
    Given pose estimation has completed successfully
    When stamp generation processes the coordinate data
    Then strikes should be detected by arm velocity and trajectory
    And detected strikes should be classified as:
      | type      |
      | Jab       |
      | Straight  |
      | Hook      |
      | Uppercut  |
    And each strike should have a timestamp and frame number

  @F006 @US-006 @happy-path
  Scenario: Defensive action detection identifies guards
    Given pose estimation has completed successfully
    When stamp generation processes the coordinate data
    Then defensive actions should be detected by torso and arm positioning
    And detected actions should include:
      | type       |
      | Guard up   |
      | Guard down |
      | Slip       |
      | Duck       |

  @F006 @US-006 @happy-path
  Scenario: Stamps include confidence scores
    Given stamp generation is processing
    When actions are detected
    Then each stamp should include:
      | attribute   |
      | action_type |
      | timestamp   |
      | frame_number |
      | body_side   |
      | confidence  |
    And confidence scores should be between 0 and 1

  @F006 @US-006 @edge-case
  Scenario: No significant actions detected
    Given a video with minimal movement has been uploaded
    When stamp generation completes with no detected actions
    Then the analysis should proceed
    And the report should provide generic movement feedback
    And I should see a note about limited action detection

  # US-007: LLM Strategic Analysis

  @F007 @US-007 @happy-path
  Scenario: LLM generates strategic analysis
    Given pose data and stamps have been generated
    When LLM analysis begins
    Then I should see "Generating insights..." on the status page
    And the system should format data as structured JSON for LLM
    And derived metrics should be calculated:
      | metric                    |
      | Reach-to-distance ratio   |
      | Upper body tilt           |
      | Guard recovery speed      |
      | Punch frequency           |
    And the LLM should generate 3-5 items for each:
      | section         |
      | Strengths       |
      | Weaknesses      |
      | Recommendations |

  @F007 @US-007 @happy-path
  Scenario: Analysis adapts to beginner experience level
    Given the user has set experience level to "Beginner"
    When LLM analysis generates feedback
    Then the analysis should use beginner-friendly terminology
    And recommendations should focus on fundamental techniques
    And the advice should be more instructional in tone

  @F007 @US-007 @happy-path
  Scenario: Analysis adapts to competitive experience level
    Given the user has set experience level to "Competitive"
    When LLM analysis generates feedback
    Then the analysis should use advanced boxing terminology
    And recommendations should focus on refinement and optimization
    And metrics should include more detailed technical analysis

  @F007 @US-007 @error @retry
  Scenario: LLM API failure triggers retry
    Given stamp generation has completed
    When LLM API call fails
    Then the system should retry with exponential backoff
    And retry attempts should be logged
    And the user should see "Generating insights..." continue

  @F007 @US-007 @error
  Scenario: LLM API exhausts retries
    Given the LLM API has failed
    And the system has retried 3 times
    When all retries are exhausted
    Then I should see "Analysis incomplete"
    And I should see "We couldn't generate the analysis"
    And I should see "Retry Analysis" button for manual retry
