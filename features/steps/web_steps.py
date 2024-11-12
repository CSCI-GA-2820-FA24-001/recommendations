######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import logging
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ID_PREFIX = "recommendation_"


@when('I visit the "Home Page"')
def step_impl(context):
    """Make a call to the base URL"""
    context.driver.get(context.root_url)
    # Uncomment next line to take a screenshot of the web page
    # context.driver.save_screenshot('home_page.png')


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """Check the document title for a message"""
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    assert element.first_selected_option.text == text


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clean button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################


@then('I should see "{name}" in the results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.text_to_be_present_in_element((By.ID, "search_results"), name)
    )
    assert found


@then('I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element(By.ID, "search_results")
    assert name not in element.text


@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.text_to_be_present_in_element((By.ID, "flash_message"), message)
    )
    assert found


@then('the message should contain "{message}"')
def step_impl(context, message):
    element = context.driver.find_element(By.ID, "flash_message")
    assert message in element.text


##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Name field has an id='pet_name'
# We can then lowercase the name and prefix with pet_ to get the id
##################################################################


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.text_to_be_present_in_element_value((By.ID, element_id), text_string)
    )
    assert found


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)


@given("the following recommendations exist")
def step_impl(context):
    """Add given recommendations to the service"""
    for row in context.table:
        context.driver.get(f"{context.base_url}/recommendations/new")
        context.driver.find_element(By.ID, f"{ID_PREFIX}user_id").send_keys(
            row["user_id"]
        )
        context.driver.find_element(By.ID, f"{ID_PREFIX}product_id").send_keys(
            row["product_id"]
        )
        context.driver.find_element(By.ID, f"{ID_PREFIX}score").send_keys(row["score"])
        if "timestamp" in row.headings:
            context.driver.find_element(By.ID, f"{ID_PREFIX}timestamp").send_keys(
                row["timestamp"]
            )
        context.driver.find_element(By.ID, "submit-btn").click()


@when("I visit the homepage")
def step_impl(context):
    context.driver.get(context.base_url)


@when('I press the "{button_text}" button')
def step_impl(context, button_text):
    button = context.driver.find_element(By.ID, f"{button_text.lower()}-btn")
    button.click()


@when('I fill in "{field_name}" with "{value}"')
def step_impl(context, field_name, value):
    field = context.driver.find_element(By.ID, f"{ID_PREFIX}{field_name}")
    field.clear()
    field.send_keys(value)


@when(
    'I press the "{button_text}" button for recommendation with "user_id" "{user_id}"'
)
def step_impl(context, button_text, user_id):
    row = context.driver.find_element(By.XPATH, f"//tr[td[text()='{user_id}']]")
    button = row.find_element(By.ID, f"{button_text.lower()}-btn")
    button.click()


@then("I should see all recommendations")
def step_impl(context):
    elements = context.driver.find_elements(
        By.XPATH, "//table[@id='search_results']/tbody/tr"
    )
    assert len(elements) > 0  # Ensure at least one recommendation is listed


@then("I should see the details page")
def step_impl(context):
    assert "Recommendation Details" in context.driver.title


@then('I should see "{text}" in the details')
def step_impl(context, text):
    element = context.driver.find_element(By.ID, "recommendation_details")
    assert text in element.text
