@F010 @US-010
Feature: Report History Dashboard
  As a returning user
  I want to view my past analysis reports
  So that I can track my improvement over time and revisit feedback

  Background:
    Given the application is running
    And I am logged in as a user

  @F010 @US-010 @happy-path
  Scenario: Dashboard displays report list sorted by date
    Given I have multiple analysis reports
    When I navigate to the dashboard
    Then I should see a list of my reports
    And the reports should be sorted by date with newest first
    And I should see "My Reports" as the page title

  @F010 @US-010 @happy-path
  Scenario: Report list item shows thumbnail and summary
    Given I have analysis reports
    When I view the dashboard
    Then each report card should display:
      | element           |
      | video thumbnail   |
      | analysis date     |
      | summary indicator |
    And the date should be formatted as "Analyzed on {date}"
    And the summary should show "{count} key moments detected"

  @F010 @US-010 @happy-path @navigation
  Scenario: User navigates to report from list
    Given I am on the dashboard with reports
    When I click on a report card
    Then I should be navigated to the full report view
    And the URL should be "/dashboard/report/{id}"

  @F010 @US-010 @delete
  Scenario: User deletes report with confirmation
    Given I am on the dashboard with reports
    When I click the delete button on a report
    Then I should see a confirmation dialog
    And the dialog should say "Delete this report?"
    And the dialog should warn "This action cannot be undone."
    When I click "Delete" to confirm
    Then the report should be deleted
    And I should see a toast "Report deleted"
    And the toast should show an "Undo" option for 10 seconds
    And the report should be removed from the list

  @F010 @US-010 @empty-state
  Scenario: Dashboard shows empty state for new user
    Given I have no analysis reports
    When I navigate to the dashboard
    Then I should see the empty state illustration
    And I should see "No analysis reports yet"
    And I should see "Upload your first sparring video to get AI-powered coaching feedback"
    And I should see an "Upload Video" button
    When I click "Upload Video"
    Then I should be navigated to the upload page

  @F010 @US-010 @loading
  Scenario: Dashboard loading state shows skeletons
    Given I am loading the dashboard
    When the page is fetching report data
    Then I should see 3 skeleton list items
    And the skeletons should have pulse animation
    And skeletons should be replaced with actual data when loaded
