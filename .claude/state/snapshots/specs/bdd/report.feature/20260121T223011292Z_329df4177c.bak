@F008 @US-008
Feature: Report Display
  As a user whose video has been analyzed
  I want to view my analysis in a readable report format
  So that I can understand and act on the feedback

  Background:
    Given the application is running
    And I am logged in as a user
    And I have a completed analysis report

  @F008 @US-008 @happy-path
  Scenario: Report displays summary section
    When I navigate to my report
    Then I should see the report header with title and date
    And I should see the video thumbnail
    And I should see the Summary section
    And the summary should contain an overall performance assessment

  @F008 @US-008 @happy-path
  Scenario: Report displays strengths section
    When I view my analysis report
    Then I should see the Strengths section
    And I should see 3-5 specific positive observations
    And each strength should be a concrete, specific statement
    And the section should be expandable/collapsible

  @F008 @US-008 @happy-path
  Scenario: Report displays weaknesses section
    When I view my analysis report
    Then I should see the "Areas for Improvement" section
    And I should see 3-5 specific areas for improvement
    And each weakness should be actionable
    And the section should be expandable/collapsible

  @F008 @US-008 @happy-path
  Scenario: Report displays recommendations section
    When I view my analysis report
    Then I should see the Recommendations section
    And I should see 3-5 actionable drills or focus areas
    And each recommendation should be specific and practical
    And the section should be expandable/collapsible

  @F008 @US-008 @happy-path
  Scenario: Report displays key moments with timestamps
    When I view my analysis report
    Then I should see the Key Moments section
    And I should see a horizontal scroll of timestamp cards
    And each card should show:
      | element    |
      | thumbnail  |
      | action type |
      | timestamp  |
    And timestamps should be in format "0:34"

  @F008 @US-008 @happy-path
  Scenario: Report displays metrics with visualizations
    When I view my analysis report
    Then I should see the Key Metrics section
    And I should see 4 metric cards in a grid:
      | metric                  |
      | Reach-to-Distance Ratio |
      | Guard Recovery Speed    |
      | Upper Body Tilt         |
      | Punch Frequency         |
    And each card should show the metric value prominently
    And each card should have a colored indicator for positive/negative

  @F008 @US-008 @compliance
  Scenario: Report includes AI disclaimer
    When I view my analysis report
    Then I should see the AI disclaimer at the bottom
    And the disclaimer should state "This AI analysis is for training purposes only and is not a substitute for professional coaching."

  @F008 @US-008 @performance
  Scenario: Report loads within performance target
    When I navigate to my report
    Then the report page should load within 1.5 seconds
    And all sections should be visible
    And no loading spinners should remain after load

  @F008 @US-008 @responsive @mobile
  Scenario: Report displays correctly on mobile viewport
    Given I am viewing on a 375px mobile viewport
    When I view my analysis report
    Then the report should render correctly
    And sections should stack vertically
    And the metrics grid should show 2 columns
    And key moments should be horizontally scrollable
    And all touch targets should be at least 48x48px

  @F008 @US-008 @responsive @desktop
  Scenario: Report displays correctly on desktop viewport
    Given I am viewing on a 1280px desktop viewport
    When I view my analysis report
    Then the report should render correctly
    And the layout should use the full width appropriately
    And the metrics grid should show 4 columns
    And sections should have proper spacing
