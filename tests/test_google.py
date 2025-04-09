from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import pytest
import time


@pytest.fixture
def browser():
    service = Service("/snap/bin/firefox.geckodriver")
    driver = webdriver.Firefox(service=service)
    yield driver
    driver.quit()


def test_google_search(browser):
    browser.get("https://www.google.com")
    assert "Google" in browser.title
    search_box = browser.find_element(By.NAME, "q")
    search_box.send_keys("Selenium")
    time.sleep(0.1)
    search_box.submit()
    time.sleep(1)

    assert "Selenium" in browser.page_source
