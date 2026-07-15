import logging
from bs4 import BeautifulSoup

_logger = logging.getLogger("client.radar.logger")


class Parser:
    """Object for parsing an HTML page."""

    def parse_company(self, html: str) -> dict[str, str]:
        """Parses the HTML page collecting the necessary data about company.

        Args:
            html (str): HTML markup that needs to be parsed

        Returns:
            dict: Dictionary with the collected company data from the HTML.
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            company_data = {}

            header = soup.find("h1", attrs={"itemprop": "name"})
            company_data["name"] = self.clean_text(header.text if header else "")

            company_data["okved"] = self.get_company_info_item(
                "Основной вид деятельности ", "span", soup
            )

            company_data["address"] = self.get_company_info_item(
                " Юридический адрес ", "span", soup
            )

            # ------------- Employees -------------
            employees_data = self.get_company_info_item(
                " Среднесписочная численность ", "dt", soup
            )

            employees_number = employees_data.split(" ")[0]

            if employees_number and employees_number.isdigit():
                company_data["employees_number"] = int(employees_number)
            else:
                company_data["employees_number"] = None

            # ------------- Director -------------
            director = self.get_company_info_item(" Руководитель ", "span", soup)
            if not director:
                managing_organization = self.get_company_info_item(
                    " Управляющая организация ", "span", soup
                )
            company_data["director"] = director or managing_organization

            # ------------- Finance -------------
            company_data["revenue"] = self._parse_finance_value(soup, "tab_revenue")
            company_data["profit"] = self._parse_finance_value(soup, "tab_profit")

            # ------------- Contacts -------------
            company_data["phones"] = self._parse_contact_list(
                soup,
                "company-info__contact phone iconer",
                "telephone",
            )

            company_data["emails"] = self._parse_contact_list(
                soup,
                "company-info__contact mail iconer",
                "email",
            )

            company_data["sites"] = self._parse_contact_list(
                soup,
                "company-info__contact site iconer",
                "url",
            )

        except Exception:
            _logger.exception("Ошибка при получении данных о компании!")
            return {}

    def _parse_contact_list(
        self,
        soup: BeautifulSoup,
        container_class: str,
        itemprop: str,
    ) -> list[str]:
        """Parses a list of company contact values.

        Args:
            soup (BeautifulSoup): Parsed HTML of the company page.

            container_class (str): CSS class of the ``div`` element that
                contains the target contact links (e.g.
                ``"company-info__contact phone iconer"``).

            itemprop (str): Value of the ``itemprop`` attribute used to
                identify the target ``<a>`` elements (e.g. ``"url"`` or
                ``"email"``).

        Returns:
            list[str]: A list of extracted contact values. Returns an empty
                list if the container cannot be found.
        """
        container = soup.find(name="div", class_=container_class)
        if container is None:
            return []

        return [
            link.get_text(strip=True)
            for link in container.find_all(name="a", attrs={"itemprop": itemprop})
        ]

    def _parse_finance_value(self, soup: BeautifulSoup, tab_name: str) -> str:
        """ "Parses a financial metric from the company page.

        Args:
            soup (BeautifulSoup): Parsed HTML of the company page.
            tab_name (str): Value of the ``data-tab_name`` attribute that
                identifies the required financial metric (e.g.
                ``"tab_revenue"`` or ``"tab_profit"``).

        Returns:
            str: Financial metric formatted as a single string, including
                both the numeric value and its unit (e.g. ``"1.2 млрд ₽"``).
                Returns an empty string if the metric cannot be found.
        """
        container = soup.select_one(
            f"div.finance-col:has(div[data-tab_name='{tab_name}'])"
        )

        if container is None:
            return ""

        num = container.find("span", class_="num")
        num_text = container.find("span", class_="num-text")

        if num is None or num_text is None:
            return ""

        return f"{num.text.strip()} {num_text.text.strip()}"

    def parse_ogrn(self, html: str) -> str:
        """Parses company OGRN.

        Args:
            html (str): HTML markup that needs to be parsed

        Returns:
            str: company OGRN
        """
        soup = BeautifulSoup(html, "html.parser")
        return soup.find(name="span", id="clip_ogrn").text

    def clean_text(self, text: str) -> str:
        """Normalize text by removing extra whitespace.

        Replaces non-breaking spaces, newlines, carriage returns,
        and tab characters with regular spaces, then collapses
        consecutive whitespace into a single space.

        Args:
            text (str): Text to normalize.

        Returns:
            str: The normalized text. Returns an empty string if the input
            is empty.
        """
        if not text:
            return ""

        text = text.replace("\xa0", " ")
        text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        text = " ".join(text.split())

        return text

    def get_company_info_item(
        self, company_info_element_text: str, tag_name: str, soup: BeautifulSoup
    ) -> str:
        """Extract a company information value from the parsed HTML.

        Searches for an element with the specified tag and text,
        then returns the normalized text of its next sibling element.

        Args:
            company_info_element_text: Text of the label identifying
                the desired company information.
            tag_name: HTML tag to search for.
            soup: Parsed HTML document.

        Returns:
            str: The normalized value associated with the specified label,
            or an empty string if the label is not found.
        """
        label_element = soup.find(tag_name, string=company_info_element_text)
        if label_element:
            info_item = label_element.find_next_sibling()
            return self.clean_text(info_item.text)
        return ""
