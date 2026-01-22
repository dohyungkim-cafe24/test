@F009 @US-009
Feature: Report Sharing
  As a user with a completed analysis report
  I want to share my report with my coach or training community
  So that I can get feedback and discuss improvements

  Background:
    Given the application is running
    And I am logged in as a user
    And I have a completed analysis report

  @F009 @US-009 @happy-path
  Scenario: Report shows share button in private state
    When I view my report
    Then I should see the "Share" button
    And the report should be in private state by default
    And no share URL should exist yet

  @F009 @US-009 @happy-path
  Scenario: User enables sharing and gets unique URL
    Given I am viewing my report
    When I click the "Share" button
    Then I should see the Share dialog
    And I should see "Enable sharing" toggle
    When I toggle sharing on
    Then a unique URL should be generated
    And the URL should be displayed in the dialog
    And the URL should use a short 8-character hash

  @F009 @US-009 @happy-path
  Scenario: User copies share link to clipboard
    Given I have enabled sharing for my report
    And the share dialog is open
    When I click "Copy Link"
    Then the URL should be copied to my clipboard
    And I should see a toast "Link copied to clipboard"
    And the toast should disappear after 4 seconds

  @F009 @US-009 @happy-path @public-access
  Scenario: Shared report accessible without login
    Given I have enabled sharing for my report
    And I have the share URL
    When an unauthenticated user accesses the share URL
    Then they should see the report content
    And the view should be read-only
    And there should be no edit or delete options
    And the AI disclaimer should be visible
    And there should be a "Try PunchAnalytics" CTA

  @F009 @US-009 @toggle
  Scenario: User disables sharing
    Given I have enabled sharing for my report
    When I open the Share dialog
    And I toggle sharing off
    Then the share URL should be invalidated
    And I should see "Sharing disabled" confirmation
    And the Copy Link button should be disabled

  @F009 @US-009 @error @public-access
  Scenario: Disabled share link returns error
    Given I had enabled sharing for my report
    And I have disabled sharing
    When someone accesses the old share URL
    Then they should see a 403 error page
    And they should see "Sharing disabled"
    And they should see "The owner has disabled sharing for this report"

  @F009 @US-009 @toggle
  Scenario: User re-enables sharing gets new URL
    Given I had enabled then disabled sharing
    When I toggle sharing back on
    Then a new unique URL should be generated
    And the new URL should be different from the previous one
    And the old URL should remain invalid

  @F009 @US-009 @social @meta
  Scenario: Shared report displays social preview
    Given I have enabled sharing for my report
    When the share URL is pasted in Kakao or Twitter
    Then the page should have Open Graph meta tags
    And the preview should show:
      | element     |
      | title       |
      | description |
      | thumbnail   |
    And the preview should be visually appealing for sharing
