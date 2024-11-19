Feature: The recommendation service back-end
    As a Recommendation Service Administrator
    I need a RESTful recommendation service
    So that I can manage product recommendations for users

Background:
    Given the following recommendations
        | user_id | product_id | score | timestamp           | num_likes |
        | 1      | 101        | 0.85  | 2024-03-15 10:00:00 | 5         |
        | 1      | 102        | 0.75  | 2024-03-15 11:00:00 | 3         |
        | 2      | 101        | 0.90  | 2024-03-15 12:00:00 | 8         |
        | 3      | 103        | 0.95  | 2024-03-15 13:00:00 | 2         |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendation Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Recommendation
    When I visit the "Home Page"
    And I set the "User ID" to "4"
    And I set the "Product ID" to "104"
    And I set the "Score" to "0.88"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "User ID" field should be empty
    And the "Product ID" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "4" in the "User ID" field
    And I should see "104" in the "Product ID" field
    And I should see "0.88" in the "Score" field

Scenario: List all recommendations
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "101" in the results
    And I should see "102" in the results
    And I should see "103" in the results

Scenario: Search recommendations by user
    When I visit the "Home Page"
    And I set the "User ID" to "1"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "101" in the results
    And I should see "102" in the results
    And I should not see "103" in the results

Scenario: Update a Recommendation
    When I visit the "Home Page"
    And I set the "User ID" to "1"
    And I set the "Product ID" to "101"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "0.85" in the "Score" field
    When I change "Score" to "0.95"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "0.95" in the "Score" field

Scenario: Delete a Recommendation
    When I visit the "Home Page"
    And I set the "User ID" to "2"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Delete" button
    Then I should see the message "Success"
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "not found"

Scenario: Like a Recommendation
    When I visit the "Home Page"
    And I set the "User ID" to "1"
    And I set the "Product ID" to "101"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "5" in the "Num Likes" field
    When I press the "Like" button
    Then I should see the message "Success"
    And I should see "6" in the "Num Likes" field