@F003 @US-003
Feature: Subject Selection
  As a user who uploaded a sparring video with multiple people
  I want to identify which person is me in the video
  So that the analysis focuses on my performance, not my sparring partner

  Background:
    Given the application is running
    And I am logged in as a user
    And I have successfully uploaded a sparring video

  @F003 @US-003 @happy-path
  Scenario: Thumbnail grid displays extracted frames
    Given the video contains multiple people
    When the frame extraction completes
    Then I should see a grid of 6-9 thumbnail frames
    And each thumbnail should show people visible in the video
    And I should see "Tap on yourself in the video" instruction

  @F003 @US-003 @happy-path
  Scenario: User selects subject from thumbnail
    Given I am on the subject selection page
    And I see the thumbnail grid with multiple people
    When I tap on myself in one of the thumbnails
    Then that person should be highlighted with a blue selection ring
    And I should see a checkmark overlay on the selection
    And the "Confirm Selection" button should become enabled

  @F003 @US-003 @happy-path
  Scenario: User changes selection before confirmation
    Given I am on the subject selection page
    And I have selected a person in the thumbnail grid
    When I tap on a different person
    Then the previous selection should be deselected
    And the new person should be highlighted with the selection ring
    And the "Confirm Selection" button should remain enabled

  @F003 @US-003 @happy-path
  Scenario: User confirms subject selection
    Given I am on the subject selection page
    And I have selected myself in the thumbnail grid
    When I tap "Confirm Selection"
    Then the selected subject's bounding box should be stored
    And I should be navigated to the body specification page

  @F003 @US-003 @single-person
  Scenario: Single person auto-selected
    Given the video contains only one person
    When the frame extraction completes
    Then that person should be automatically selected
    And I should see "We detected one person. Is this you?"
    And I should be able to confirm or upload a different video

  @F003 @US-003 @empty-state @error
  Scenario: No subjects detected in video
    Given the video contains no clearly visible people
    When the frame extraction completes
    Then I should see "No subjects detected" message
    And I should see "We couldn't identify any people in your video"
    And I should see guidance to upload a video with clear visibility
    And I should see "Upload Different Video" button

  @F003 @US-003 @loading
  Scenario: Thumbnail extraction loading state
    Given I have just uploaded a video
    When I am navigated to the subject selection page
    And frame extraction is in progress
    Then I should see "Extracting frames..." with a spinner
    And I should see skeleton placeholders in the grid
    And thumbnails should progressively appear as they are ready
