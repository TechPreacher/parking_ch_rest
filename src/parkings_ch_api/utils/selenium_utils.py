"""Selenium utilities for web scraping."""

import asyncio
import atexit

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from ..utils.logging import setup_logging

logger = setup_logging(__name__)


class WebDriverFactory:
    """Factory for creating WebDriver instances."""

    _instance: webdriver.Chrome | webdriver.Firefox | None = None

    @classmethod
    def get_driver(
        cls,
        browser: str = "chrome",
        headless: bool = True,
    ) -> webdriver.Chrome | webdriver.Firefox:
        """Get a WebDriver instance.

        Args:
            browser: Browser type ('chrome' or 'firefox')
            headless: Whether to run in headless mode

        Returns:
            WebDriver instance
        """
        # Return existing instance if already created
        if cls._instance is not None:
            return cls._instance

        if browser.lower() == "chrome":
            options = ChromeOptions()
            if headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--remote-debugging-port=9222")

            # User agent to avoid detection
            options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            )

            service = ChromeService(ChromeDriverManager().install())
            cls._instance = webdriver.Chrome(service=service, options=options)

        elif browser.lower() == "firefox":
            firefox_options = FirefoxOptions()
            if headless:
                firefox_options.add_argument("--headless")
            firefox_options.add_argument("--width=1920")
            firefox_options.add_argument("--height=1080")

            firefox_service = FirefoxService(GeckoDriverManager().install())
            cls._instance = webdriver.Firefox(service=firefox_service, options=firefox_options)

        else:
            raise ValueError(f"Unsupported browser: {browser}")

        # Register cleanup function to quit the driver on exit
        atexit.register(cls.quit_driver)

        return cls._instance

    @classmethod
    def quit_driver(cls) -> None:
        """Quit the WebDriver instance."""
        if cls._instance is not None:
            cls._instance.quit()
            cls._instance = None


async def get_page_content(
    url: str,
    wait_for_selector: str | None = None,
    timeout: int = 30,
) -> str:
    """Get page content using Selenium in a non-blocking way.

    Args:
        url: URL to fetch
        wait_for_selector: CSS selector to wait for
        timeout: Timeout in seconds

    Returns:
        Page content
    """
    logger.info(f"Fetching page content from {url} using Selenium")

    # Run in a separate thread to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    page_content = await loop.run_in_executor(
        None,
        lambda: _fetch_page_content(url, wait_for_selector, timeout),
    )

    return page_content


def _fetch_page_content(
    url: str,
    wait_for_selector: str | None = None,
    timeout: int = 30,
) -> str:
    """Fetch page content using Selenium.

    Args:
        url: URL to fetch
        wait_for_selector: CSS selector to wait for
        timeout: Timeout in seconds

    Returns:
        Page content
    """
    driver = WebDriverFactory.get_driver(headless=True)

    try:
        driver.get(url)

        # Wait for specific element if requested
        if wait_for_selector:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector)),
            )

        # Return the page source
        return driver.page_source

    except Exception as e:
        logger.error(f"Error fetching page content: {e!s}")
        return ""
