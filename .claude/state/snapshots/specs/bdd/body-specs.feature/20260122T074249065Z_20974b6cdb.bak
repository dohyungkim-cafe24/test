@F004 @US-004
Feature: Body Specification Input
  As a user preparing my video for analysis
  I want to input my physical attributes
  So that the analysis can be contextualized to my body type and experience level

  Background:
    Given the application is running
    And I am logged in as a user
    And I have selected myself in the subject selection
    And I am on the body specification page

  @F004 @US-004 @happy-path
  Scenario: User enters valid body specifications
    Given all form fields are empty
    When I enter height "175" cm
    And I enter weight "70" kg
    And I select experience level "Intermediate (1-3 years)"
    And I select stance "Orthodox"
    Then the "Start Analysis" button should be enabled
    When I tap "Start Analysis"
    Then my body specs should be saved
    And I should be navigated to the processing status page

  @F004 @US-004 @validation @error
  Scenario: Height below minimum shows validation error
    When I enter height "95" cm
    And I tap outside the field
    Then I should see validation error "Height must be at least 100cm"
    And the height field should have a red border
    And the "Start Analysis" button should be disabled

  @F004 @US-004 @validation @error
  Scenario: Height above maximum shows validation error
    When I enter height "260" cm
    And I tap outside the field
    Then I should see validation error "Height must be under 250cm"
    And the height field should have a red border
    And the "Start Analysis" button should be disabled

  @F004 @US-004 @validation @error
  Scenario: Weight below minimum shows validation error
    When I enter weight "25" kg
    And I tap outside the field
    Then I should see validation error "Weight must be at least 30kg"
    And the weight field should have a red border
    And the "Start Analysis" button should be disabled

  @F004 @US-004 @validation @error
  Scenario: Weight above maximum shows validation error
    When I enter weight "210" kg
    And I tap outside the field
    Then I should see validation error "Weight must be under 200kg"
    And the weight field should have a red border
    And the "Start Analysis" button should be disabled

  @F004 @US-004 @validation @error
  Scenario: All fields required for submission
    When I enter height "175" cm
    And I leave weight empty
    And I have not selected experience level
    And I have not selected stance
    Then the "Start Analysis" button should be disabled
    When I tap "Start Analysis" anyway
    Then I should see required field errors on empty fields
    And the focus should move to the first error field

  @F004 @US-004 @returning-user @happy-path
  Scenario: Body specs pre-filled for returning user
    Given I have previously submitted body specs
      | height | weight | experience | stance |
      | 180    | 75     | Advanced   | Southpaw |
    When I upload a new video
    And I complete subject selection
    And I arrive at the body specification page
    Then the height field should show "180"
    And the weight field should show "75"
    And experience level should be "Advanced (3-5 years)"
    And stance should be "Southpaw"
    And the "Start Analysis" button should be enabled

  @F004 @US-004 @validation @error
  Scenario: Invalid number format shows error
    When I enter height "abc"
    Then I should see validation error "Please enter a valid number"
    When I enter height "175.5"
    Then the height should be accepted as "176" (rounded)
    When I paste "175cm" into height field
    Then non-numeric characters should be stripped
    And height should show "175"
