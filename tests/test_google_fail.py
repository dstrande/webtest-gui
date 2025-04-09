import pytest
from selenium import webdriver
from selenium.webdriver.firefox.service import Service


@pytest.fixture
def browser():
    service = Service("/snap/bin/firefox.geckodriver")
    driver = webdriver.Firefox(service=service)
    yield driver
    driver.quit()


def test_google_page_title(browser):
    """Test that the page title of google.com is correct."""
    browser.get("https://www.google.com")

    title = browser.title
    assert title == "AskJeeves", f"Expected 'AskJeeves', but got {title}"

    browser.quit()
