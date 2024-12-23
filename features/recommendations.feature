Feature: The recommendation service back-end
    As a Recommendation Service Administrator
    I need a RESTful recommendation service
    So that I can manage product recommendations for users

Background:
    Given the following recommendations
        | user_id | product_id | score | timestamp           | num_likes |
        | 1       | 101        | 0.85  | 2024-03-15 10:00:00 | 5         |
        | 1       | 102        | 0.75  | 2024-03-15 11:00:00 | 3         |
        | 2       | 101        | 0.90  | 2024-03-15 12:00:00 | 8         |
        | 3       | 103        | 0.95  | 2024-03-15 13:00:00 | 2         |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendation Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Recommendation
    When I visit the "Home Page"
    And I set the "user_id" to "1"
    And I set the "product_id" to "101"
    And I set the "score" to "0.82"
    And I set the "num_likes" to "5"
    And I press the "Create" button
    Then I should see the message "Success"
    And the "id" field should not be empty
    When I copy the "id" field
    And I press the "Clear" button
    And I paste the "id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "1" in the "user_id" field
    And I should see "101" in the "product_id" field
    And I should see "0.82" in the "score" field
    And I should see "5" in the "num_likes" field

Scenario: Update a Recommendation
    When I visit the "Home Page"
    And I set the "user_id" to "2"
    And I set the "product_id" to "101"
    And I set the "score" to "0.88"
    And I set the "num_likes" to "10"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Clear" button
    And I paste the "id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    When I set the "score" to "0.95"
    And I set the "num_likes" to "12"
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Clear" button
    And I paste the "id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "0.95" in the "score" field
    And I should see "12" in the "num_likes" field

Scenario: Delete a Recommendation
    When I visit the "Home Page"
    And I set the "user_id" to "3"
    And I set the "product_id" to "103"
    And I set the "score" to "0.90"
    And I set the "num_likes" to "5"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Delete" button
    Then I should see the message "Success"
    When I press the "Clear" button
    And I paste the "id" field
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found"

Scenario: Search Recommendations
    When I visit the "Home Page"
    And I set the "user_id" to "1"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "101" in the results
    And I should see "102" in the results
    And I should not see "103" in the results

Scenario: Query Recommendations by User and Product
    When I visit the "Home Page"
    And I set the "user_id" to "1"
    And I set the "product_id" to "101"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "101" in the results
    And I should not see "102" in the results
    And I should not see "103" in the results