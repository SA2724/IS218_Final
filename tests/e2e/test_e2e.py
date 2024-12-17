import pytest
from playwright.sync_api import Page
from subprocess import Popen
import time


@pytest.mark.e2e
def test_hello_world(page: Page, fastapi_server):
    """
    Test that the homepage displays "Hello World".
    """
    # Navigate to the homepage and ensure the page is fully loaded
    page.goto('http://localhost:8000', wait_until="networkidle")

    # Wait for the <h1> element to appear
    page.wait_for_selector('h1')

    # Assert the main header displays the expected text
    assert page.inner_text('h1') == 'Hello World', "Homepage did not display 'Hello World'."

@pytest.mark.e2e
def test_calculator_add(page: Page, fastapi_server):
    """
    Test the addition functionality of the calculator.
    """
    page.goto('http://localhost:8000', wait_until="networkidle")
    page.wait_for_selector('#a')
    page.wait_for_selector('#b')
    page.wait_for_selector('button:text("Add")')
    page.fill('#a', '10')
    page.fill('#b', '5')
    page.click('button:text("Add")')
    page.wait_for_selector('#result')
    assert page.inner_text('#result') == 'Result: 15', "Addition result was not correct."

@pytest.mark.e2e
def test_calculator_divide_by_zero(page: Page, fastapi_server):
    """
    Test the divide by zero functionality of the calculator.
    """
    page.goto('http://localhost:8000', wait_until="networkidle")
    page.wait_for_selector('#a')
    page.wait_for_selector('#b')
    page.wait_for_selector('button:text("Divide")')
    page.fill('#a', '10')
    page.fill('#b', '0')
    page.click('button:text("Divide")')
    page.wait_for_selector('#result')
    assert page.inner_text('#result') == 'Error: Cannot divide by zero!', "Division by zero did not return the correct error message."
@pytest.fixture(scope="session")
def fastapi_server():
    # Start the FastAPI server
    process = Popen(["uvicorn", "your_fastapi_app:app", "--host", "127.0.0.1", "--port", "8000"])
    time.sleep(5)  # Wait for the server to start
    yield
    process.terminate()