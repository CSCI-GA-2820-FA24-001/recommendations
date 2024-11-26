######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
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
from behave import when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = "rec_"


@when('I visit the "Home Page"')
def step_impl(context):
    """Make a call to the base URL"""
    context.driver.get(context.base_url)


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """Check the document title for a message"""
    assert message in context.driver.title


@when('I set the "{field}" to "{value}"')
def step_impl(context, field, value):
    element_id = f"{ID_PREFIX}{field.lower().replace(' ', '_')}"
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(value)


@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = f"{button.lower().replace(' ', '_')}-btn"
    logging.info("Clicking button with ID: %s", button_id)
    WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.element_to_be_clickable((By.ID, button_id))
    ).click()


@then('I should see the message "{message}"')
def step_impl(context, message):
    flash_message = (
        WebDriverWait(context.driver, context.wait_seconds)
        .until(
            expected_conditions.presence_of_element_located((By.ID, "flash_message"))
        )
        .text
    )
    assert (
        message in flash_message
    ), f'Expected message "{message}" but got "{flash_message}"'


@then('the "id" field should not be empty')
def step_impl(context):
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, f"{ID_PREFIX}id"))
    )
    field_value = element.get_attribute("value")
    assert field_value, 'The "id" field is empty!'


@then('I should see "{expected_value}" in the "{element_name}" field')
def step_impl(context, expected_value, element_name):
    element_id = f"{ID_PREFIX}{element_name.lower().replace(' ', '_')}"
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    actual_value = element.get_attribute("value")
    assert (
        actual_value == expected_value
    ), f'Expected "{expected_value}" in {element_name}, but got "{actual_value}"'


@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = f"{ID_PREFIX}{element_name.lower().replace(' ', '_')}"
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")
    assert context.clipboard, f'The "{element_name}" field is empty!'
    logging.info(
        "Copied value '%s' from the '%s' field to clipboard",
        context.clipboard,
        element_name,
    )


@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = f"{ID_PREFIX}{element_name.lower().replace(' ', '_')}"
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.element_to_be_clickable((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)
    logging.info(
        "Pasted value '%s' into the '%s' field",
        context.clipboard,
        element_name,
    )


@then('I should see "{name}" in the results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_results"), name
        )
    )
    assert found


@then('I should not see "{name}" in the results')
def step_impl(context, name):
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, "search_results"))
    )
    assert name not in element.text


@then('I should not see "404 Not Found"')
def step_impl(context):
    body = context.driver.find_element(By.TAG_NAME, "body")
    assert "404 Not Found" not in body.text, '"404 Not Found" was found on the page!'
