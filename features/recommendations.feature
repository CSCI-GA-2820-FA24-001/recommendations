Feature: Recommendation Service Web Interface
  As a service administrator
  I want to manage recommendations through a web interface
  So that I can maintain product recommendations

  Background:
    Given the following recommendations exist
      | user_id | product_id | score | timestamp              |
      | 100     | 1001       | 4.5   | 2023-10-14T12:00:00Z   |
      | 101     | 1002       | 3.8   | 2023-10-15T14:30:00Z   |

  Scenario: List all recommendations
    When I visit the homepage
    Then I should see all recommendations
    And I should see "100" in the results
    And I should see "1001" in the results

  Scenario: Create a recommendation
    When I visit the homepage
    And I press the "Create" button
    And I fill in "user_id" with "102"
    And I fill in "product_id" with "1003"
    And I fill in "score" with "4.2"
    And I fill in "timestamp" with "2023-10-16T09:15:00Z"
    And I press the "Submit" button
    Then I should see "102" in the results
    And I should see "1003" in the results

  Scenario: Read a recommendation
    Given the following recommendations exist
      | user_id | product_id | score | timestamp              |
      | 100     | 1001       | 4.5   | 2023-10-14T12:00:00Z   |
      | 101     | 1002       | 3.8   | 2023-10-15T14:30:00Z   |
    When I visit the homepage
    And I press the "View" button for recommendation with "user_id" "100"
    Then I should see the details page
    And I should see "100" in the details
    And I should see "1001" in the details
    And I should see "4.5" in the details

  Scenario: Update a recommendation
    Given the following recommendations exist
      | user_id | product_id | score | timestamp              |
      | 100     | 1001       | 4.5   | 2023-10-14T12:00:00Z   |
      | 101     | 1002       | 3.8   | 2023-10-15T14:30:00Z   |
    When I visit the homepage
    And I press the "Edit" button for recommendation with "user_id" "100"
    When I modify the "score" field to "4.8"
    And I press the "Save" button
    Then I should see "4.8" in the results

  Scenario: Delete a recommendation
    Given the following recommendations exist
      | user_id | product_id | score | timestamp              |
      | 100     | 1001       | 4.5   | 2023-10-14T12:00:00Z   |
      | 101     | 1002       | 3.8   | 2023-10-15T14:30:00Z   |
    When I visit the homepage
    And I press the "Delete" button for recommendation with "user_id" "101"
    Then I should not see "101" in the results

  Scenario: Query recommendations by user
    Given the following recommendations exist
      | user_id | product_id | score | timestamp              |
      | 100     | 1001       | 4.5   | 2023-10-14T12:00:00Z   |
      | 101     | 1002       | 3.8   | 2023-10-15T14:30:00Z   |
    When I visit the homepage
    And I fill in "search_user" with "100"
    And I press the "Search" button
    Then I should see "100" in the results
    And I should not see "101" in the results

  Scenario: Query recommendations by product
    Given the following recommendations exist
      | user_id | product_id | score | timestamp              |
      | 100     | 1001       | 4.5   | 2023-10-14T12:00:00Z   |
      | 101     | 1002       | 3.8   | 2023-10-15T14:30:00Z   |
    When I visit the homepage
    And I fill in "search_product" with "1001"
    And I press the "Search" button
    Then I should see "1001" in the results
    And I should not see "1002" in the results
