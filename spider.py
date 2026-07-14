import asyncio
import logging
import random

from playwright.async_api import async_playwright
from playwright.async_api import Browser, Page, Playwright

from config import spider_config, yaml_config
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

LEGAL_FORMS = [
    "ООО",
    "АО — Акционерные общества",
]
"""list: Suitable legal forms."""

parser = Parser()


class Spider:
    """Object for collecting data from the site."""

    def __init__(self):
        self.chrome_path = spider_config.chrome_path
        self.base_url = spider_config.base_url

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
        page_number = 1
        links = []
        async with async_playwright() as p:
            browser = await self._create_browser(p)
            try:
                page = await self._create_page(browser)

                await self.login(page=page)

                await self._open_search_page(page)

                while page_number:
                    links.append(await self._collect_company_links(page))
                    page_number = await self._go_next_page(
                        page_number=page_number, page=page
                    )
                    await self.wait()

                flatten_link_list = [x for sub in links for x in sub]
                return await self._collect_rows(page, flatten_link_list)
            finally:
                await browser.close()

    @staticmethod
    async def wait():
        """Performs code execution delay to simulate human actions."""
        await asyncio.sleep(random.uniform(0.8, 2.1))

    async def login(self, page: Page) -> None:
        """Authorizes the user.

        Args:
            page (Page): Playwright Browser Page instance
        """
        await page.goto(f"{self.base_url}")
        await page.locator("#menu-personal-trigger").click()
        await self.wait()

        await page.locator("input[name='email']").fill(spider_config.rusprofile_login)
        await self.wait()

        await page.get_by_text("Продолжить").click()
        await self.wait()

        await page.locator("#current-password").fill(spider_config.rusprofile_password)
        await self.wait()

        await page.locator(".btn__content:has-text(' Войти ')").click()
        await self.wait()

        continue_btn = page.get_by_text(" Продолжить работу ")
        if await continue_btn.count() > 0:
            await continue_btn.click()
            await self.wait()

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

    async def _open_search_page(self, page: Page) -> None:
        """Opens the page with the filtred companies.

        Args:
            page (Page): Playwright Browser Page instance.
        """
        await page.goto(f"{self.base_url}/search-advanced")
        await self.apply_filters(page=page)

    async def apply_okved_filters(self, page: Page) -> None:
        """Applies a filter by type of activity.

        Args:
            page (Page): Playwright Browser Page instance.
        """
        await page.get_by_text("Вид деятельности").click()

        for code in yaml_config.client_radar.filters.okved_codes:
            code_integer_part, code_float_part = code.split(".")

            await page.get_by_role("textbox", name="Название или код").fill(code)
            await self.wait()

            if code_float_part:
                toggle = page.locator(f"[data-code='{code_integer_part}']")
                classes = await toggle.get_attribute("class")
                if classes and "expanded" not in classes.split():
                    await toggle.click(
                        position={
                            "x": 10,
                            "y": 15,
                        }
                    )

                await page.locator(f'[id="tree-okved-{code}"] + label').click()
            else:
                await page.locator(
                    f'[id="tree-okved-{code_integer_part}"] + label'
                ).click()
            await self.wait()

        await self.close_modal(page=page)

    async def apply_region_filter(self, page: Page) -> None:
        """Applies a filter by company region.

        Args:
            page (Page): Playwright Browser Page instance.
        """
        await page.locator("//legend[text()='Регион']").click()
        for region in yaml_config.client_radar.filters.regions:
            await page.get_by_role("textbox", name="Округ или регион").fill(region)
            await self.wait()
            await page.locator(f"//mark[text()='{region}']").click()
            await self.wait()

        await self.close_modal(page=page)

    async def apply_status_filter(self, page: Page) -> None:
        """Applies a filter by company status.

        Args:
            page (Page): Playwright Browser Page instance.
        """
        for status in yaml_config.client_radar.filters.statuses:
            status_span = page.locator(f"//span[text()='{status}']")
            checkbox = status_span.locator("xpath=preceding-sibling::*[1]")
            if not await checkbox.is_checked():
                await status_span.click()

    async def apply_legal_form_filter(self, page: Page) -> None:
        """Applies a filter by company legal form.

        Args:
            page (Page): Playwright Browser Page instance.
        """
        await page.locator("//legend[text()='Правовая форма']").click()
        for legal_form in LEGAL_FORMS:
            await page.get_by_role("textbox", name="Наименование или код").fill(
                legal_form
            )
            await self.wait()

            toggle = page.locator("[data-code='12000']")
            classes = await toggle.get_attribute("class")
            if classes and "expanded" not in classes.split():
                await toggle.click(
                    position={
                        "x": 10,
                        "y": 15,
                    }
                )
            await page.locator(f"//mark[text()='{legal_form}']").click()
            await self.wait()
        await self.close_modal(page=page)

    async def apply_revenue_filter(self, page: Page) -> None:
        """Applies a filter by company revenue.

        Args:
            page (Page): Playwright Browser Page instance.
        """
        await page.locator("//legend[text()='Прибыль']").click()

        container = page.locator("div.merged").filter(
            has=page.locator("#finance_profit_from")
        )

        finance_profit_from = container.locator("input").nth(0)
        finance_profit_to = container.locator("input").nth(1)

        await finance_profit_from.fill(
            str(yaml_config.client_radar.filters.revenue.min)
        )
        await self.wait()

        if yaml_config.client_radar.filters.revenue.max:
            await finance_profit_to.fill(
                str(yaml_config.client_radar.filters.revenue.max)
            )

    async def apply_contacts_filter(self, page: Page) -> None:
        """Applies a filter by company contacts.

        Args:
            page (Page): Playwright Browser Page instance.
        """
        await page.locator("//legend[text()='Контакты']").click()

        for contact_type in yaml_config.client_radar.filters.contacts:
            contact_span = page.locator(f"//span[text()='{contact_type}']")
            if await contact_span.count() > 0:
                await contact_span.click()
            await self.wait()

    async def apply_employees_number_filter(self, page: Page) -> None:
        """Applies a filter by company employees number.

        Args:
            page (Page): Playwright Browser Page instance.
        """
        await page.locator("//legend[text()='Количество сотрудников']").click()
        employees_fieldset = page.locator("fieldset").filter(
            has=page.locator("legend", has_text="Количество сотрудников")
        )
        employees_from = employees_fieldset.locator("input").nth(0)
        employees_to = employees_fieldset.locator("input").nth(1)

        await employees_from.fill(
            str(yaml_config.client_radar.filters.employees_number.min)
        )
        await self.wait()
        if yaml_config.client_radar.filters.employees_number.max:
            await employees_to.fill(
                str(yaml_config.client_radar.filters.employees_number.max)
            )

    async def close_modal(self, page: Page) -> None:
        """Closes the modal window by applying the selected filter.

        Args:
            page (Page): Playwright Browser Page instance.
        """
        modal = page.locator("div.modal-pop-wrp.tree-list-wrp.active")
        done_button = modal.locator("div.btn.btn-blue.modal-pop-close.tree-list-submit")
        await done_button.click()

    async def apply_filters(self, page: Page) -> None:
        """Applies the filters to search for ther equired companies.

        Args:
            page (Page): Playwright Browser Page instance.
        """
        await self.apply_okved_filters(page=page)
        await self.apply_region_filter(page=page)
        await self.apply_status_filter(page=page)
        await self.apply_legal_form_filter(page=page)
        await self.apply_revenue_filter(page=page)
        await self.apply_contacts_filter(page=page)
        await self.apply_employees_number_filter(page=page)

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

    async def _go_next_page(self, page_number: int, page: Page) -> int | bool:
        """Opens the next page.

        Args:
            page_number (int): The number if the page where the parser
                is currently located.
            page (Page): Playwright Browser Page instance.

        Returns:
            int | bool: The number of the page that the parser went to,
                or False if the page is the last one.
        """
        next_page = page.locator(f'.fakelink.to-page[data-target="{page_number + 1}"]')
        if not await next_page.count():
            return False

        await next_page.click()
        return page_number + 1

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

        contacts_container = page.locator("#contacts-row")
        buttons = contacts_container.locator("button.all-text-link")

        count = await buttons.count()

        for i in range(count):
            await buttons.nth(i).click()

        html = await page.content()
        company_data = parser.parse_company(html)

        await self.wait()

        return [company_data.get(h, "") for h in HEADERS]
