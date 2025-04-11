import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service


@pytest.fixture
def browser():
    """Set up and tear down the browser."""
    service = Service("/snap/bin/firefox.geckodriver")
    driver = webdriver.Firefox(service=service)
    yield driver
    driver.quit()


def test_title_contains_python(browser):
    """Verify that the title contains 'Python'."""
    browser.get("https://www.python.org")
    assert "Python" in browser.title


def test_search_for_download(browser):
    """Search for 'download' and check if results appear."""
    browser.get("https://www.python.org")
    search_input = browser.find_element(By.ID, "id-search-field")
    search_input.clear()
    search_input.send_keys("download")
    search_input.send_keys(Keys.RETURN)
    time.sleep(0.5)
    results = browser.find_elements(By.CSS_SELECTOR, ".list-recent-events li")
    assert len(results) > 0


def test_navigation_docs_link(browser):
    """Check that the Docs link is present and works."""
    browser.get("https://www.python.org")
    docs_link = browser.find_element(By.LINK_TEXT, "Documentation")
    docs_link.click()
    assert (
        "docs.python.org" in browser.current_url
        or "documentation" in browser.page_source
    )
