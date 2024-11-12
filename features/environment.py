"""
Environment for Behave Testing
"""

from os import getenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

WAIT_SECONDS = int(getenv("WAIT_SECONDS", "60"))
PORT = getenv("PORT", "8000")
BASE_URL = getenv("BASE_URL", f"http://localhost:{PORT}")
DRIVER = getenv("DRIVER", "chrome").lower()


def before_all(context):
    """Setup before all tests"""
    options = Options()

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Use the Service class to specify the ChromeDriver executable
    service = Service(ChromeDriverManager().install())
    context.driver = webdriver.Chrome(service=service, options=options)
    context.driver.implicitly_wait(10)
    context.base_url = BASE_URL
    context.wait_seconds = WAIT_SECONDS


def after_all(context):
    """Teardown after all tests"""
    if hasattr(context, "driver"):
        context.driver.quit()


######################################################################
# Utility functions to create web drivers
######################################################################


def get_chrome():
    """Creates a headless Chrome driver"""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def get_firefox():
    """Creates a headless Firefox driver"""
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    return webdriver.Firefox(options=options)
