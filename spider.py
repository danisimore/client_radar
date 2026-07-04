import asyncio
import logging
from playwright.async_api import async_playwright
from playwright.async_api import Browser, Page, Playwright

from config import spider_config
from parser import Parser

_logger = logging.getLogger("client.radar.logger")

HEADERS = [
    "Название",
    "Основной вид деятельности",
    "Юридический адрес",
    "Выручка",
    "Динамика выручки",
    "Динамика прибыли",
    "Динамика стоимости",
    "Директор/Компания",
]
"""list: The names of of the table."""

parser = Parser()


class Spider:
    """Object for collecting data from the site."""

    def __init__(self):
        self.chrome_path = spider_config.chrome_path
        self.base_url = spider_config.base_url

        self.endpoint = (
            input("Введите endpoint компании (напр. /id/1234600000766): ")
            or "/id/1234600000766"
        )

        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        )

    async def run(self):
        """Run the spider and collect company data.

        Launches the browser, navigates to the companies page,
        collects company links, parses each company page, and
        returns the extracted data.

        Returns:
            A list of rows ready to be written to Google Sheets.
        """
        async with async_playwright() as p:
            browser = await self._create_browser(p)
            try:
                page = await self._create_page(browser)

                await self._open_companies_page(page)
                links = await self._collect_company_links(page)

                return await self._collect_rows(page, links)
            finally:
                await browser.close()

    async def _create_browser(self, playwright: Playwright):
        """Create and configure a Chromium browser instance.

        Args:
            playwright: Playwright instance used to launch the browser.

        Returns:
            A configured Chromium browser instance.
        """
        return await playwright.chromium.launch(
            executable_path=self.chrome_path,
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )

    async def _create_page(self, browser: Browser):
        """Create a new browser page with the configured context.

        Args:
            browser: Browser instance.

        Returns:
            A newly created browser page.
        """
        context = await browser.new_context(
            user_agent=self.user_agent,
        )
        return await context.new_page()

    async def _open_companies_page(self, page: Page) -> None:
        """Open the companies page and select legal entities.

        Navigates to the target page, waits for it to load,
        and applies the "Юрлица" filter.

        Args:
            page: Browser page.
        """
        await page.goto(f"{self.base_url}{self.endpoint}")
        await page.wait_for_selector("[data-tab_name='top_okved_region']")

        await (
            page.locator("[data-tab_name='top_okved_region']")
            .get_by_role("button")
            .click()
        )
        await page.get_by_text("Юрлица").click()

    async def _collect_company_links(self, page: Page) -> list[str]:
        """Collect links to company pages.

        Args:
            page: Browser page displaying the companies list.

        Returns:
            A list of absolute URLs to company pages.
        """
        company_links = page.locator("a.list-element__title[href^='/id/']")

        links = []

        for i in range(await company_links.count()):
            href = await company_links.nth(i).get_attribute("href")
            if href:
                links.append(self.base_url + href)

        _logger.info("Found %d companies", len(links))

        return links

    async def _collect_rows(self, page: Page, links: list[str]) -> list[list[str]]:
        """Collect data rows for all companies.

        Args:
            page: Browser page.
            links: Company page URLs.

        Returns:
            A list of parsed company data rows.
        """
        rows = []

        for link in links:
            rows.append(await self._parse_company(page, link))

        return rows

    async def _parse_company(self, page: Page, link: str) -> list[str]:
        """Parse data from a company page.

        Args:
            page: Browser page.
            link: Company page URL.

        Returns:
            A row containing company data ordered according to
            ``HEADERS``.
        """
        await page.goto(link)
        await page.wait_for_load_state("networkidle")

        html = await page.content()
        company_data = parser.parse_company(html)

        await asyncio.sleep(0.5)

        return [company_data.get(h, "") for h in HEADERS]
