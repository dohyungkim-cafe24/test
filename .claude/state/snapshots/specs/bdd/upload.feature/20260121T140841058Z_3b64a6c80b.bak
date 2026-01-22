@F002 @US-002
Feature: Video Upload
  As a boxer with sparring footage
  I want to upload my video to the platform
  So that I can receive AI analysis of my performance

  Background:
    Given the application is running
    And I am logged in as a user
    And I am on the upload page

  @F002 @US-002 @happy-path
  Scenario: Successful video upload with valid file
    Given I have a valid sparring video file
      | attribute | value |
      | format    | MP4   |
      | size      | 200MB |
      | duration  | 2 minutes |
    When I select the video file for upload
    Then I should see the upload progress card
    And the upload should complete successfully
    And I should be navigated to the subject selection screen

  @F002 @US-002 @happy-path
  Scenario: Upload shows progress indicator
    Given I have a valid video file of 300MB
    When I select the video file for upload
    Then I should see the upload progress bar
    And I should see the percentage uploaded
    And I should see the bytes transferred and total
    And I should see the estimated time remaining
    And the progress should update every 500ms

  @F002 @US-002 @validation @error
  Scenario: File exceeds maximum size limit
    Given I have a video file of 650MB
    When I select the video file for upload
    Then I should see the error message "Video file too large. Please upload a file under 500MB."
    And I should see "Current file: 650MB"
    And the upload should not begin
    And I should remain on the upload page

  @F002 @US-002 @validation @error
  Scenario: Video duration too short
    Given I have a video file with duration of 30 seconds
    When I select the video file for upload
    Then I should see the error message "Video must be between 1 and 3 minutes."
    And I should see "Current duration: 30 seconds"
    And the upload should not begin

  @F002 @US-002 @validation @error
  Scenario: Video duration too long
    Given I have a video file with duration of 5 minutes
    When I select the video file for upload
    Then I should see the error message "Video must be between 1 and 3 minutes."
    And I should see "Current duration: 5 minutes"
    And the upload should not begin

  @F002 @US-002 @validation @error
  Scenario: Unsupported file format rejected
    Given I have a video file in AVI format
    When I select the video file for upload
    Then I should see the error message "Unsupported format. Please upload MP4, MOV, or WebM."
    And I should see "Detected format: AVI"
    And the upload should not begin

  @F002 @US-002 @network @resilience
  Scenario: Upload resumes after network interruption
    Given I have a valid video file of 400MB
    And I have started uploading the file
    And the upload has reached 50%
    When the network connection is lost
    Then I should see "Connection lost" message
    And the upload progress should be paused
    When the network connection is restored
    Then the upload should resume automatically from 50%
    And the upload should complete successfully

  @F002 @US-002 @cancel
  Scenario: User cancels upload in progress
    Given I have started uploading a valid video file
    And the upload is at 60% progress
    When I click the "Cancel" button
    Then I should see a cancellation confirmation dialog
    When I confirm cancellation
    Then the partial upload should be discarded
    And I should remain on the upload page
    And the upload area should be reset

  @F002 @US-002 @empty-state
  Scenario: Upload area shows empty state initially
    Given I am on the upload page
    And I have not selected a file
    Then I should see the drop zone with dashed border
    And I should see the cloud upload icon
    And I should see "Drop your video here"
    And I should see "or tap to browse"
    And I should see the video requirements:
      | requirement |
      | Formats: MP4, MOV, WebM |
      | Maximum size: 500MB |
      | Duration: 1-3 minutes |
