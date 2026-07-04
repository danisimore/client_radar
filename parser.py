import logging
from bs4 import BeautifulSoup
from bs4.element import Tag

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
            company_data["Название"] = self.clean_text(header.text if header else "")

            company_data["Основной вид деятельности"] = self.get_company_info_item(
                "Основной вид деятельности ", "span", soup
            )

            company_data["Юридический адрес"] = self.get_company_info_item(
                " Юридический адрес ", "span", soup
            )

            director = self.get_company_info_item(" Руководитель ", "span", soup)
            if not director:
                managing_organization = self.get_company_info_item(
                    " Управляющая организация ", "span", soup
                )
            company_data["Директор/Компания"] = director or managing_organization

            finance_columns_div = soup.find(class_=["finance-columns"])

            if finance_columns_div:
                tab_revenue = finance_columns_div.find(
                    attrs={"data-tab_name": "tab_revenue"}
                )
                if tab_revenue:
                    nums_div = tab_revenue.find_next_sibling()
                    if nums_div:
                        revenue_num = nums_div.find(class_="num")
                        revenue_num_text = (
                            revenue_num.find_next_sibling() if revenue_num else None
                        )

                        company_data["Выручка"] = self.clean_text(
                            (revenue_num.text if revenue_num else "")
                            + " "
                            + (revenue_num_text.text if revenue_num_text else "")
                        )

                        company_data["Динамика выручки"] = self.get_dynamics(
                            finance_columns_div, "tab_revenue"
                        )

                company_data["Динамика прибыли"] = self.get_dynamics(
                    finance_columns_div, "tab_profit"
                )
                company_data["Динамика стоимости"] = self.get_dynamics(
                    finance_columns_div, "tab_value"
                )

            return company_data

        except Exception:
            _logger.exception("Ошибка при получении данных о компании!")
            return {}

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

    def get_dynamics(self, finance_columns_div: Tag, tab_name: str) -> str:
        """Parses profit dynamic,  revenue dynamic and value dynamic.

        Args:
            finance_columns_div (Tag): div with financial dynamics data.
            tab_name (str): The name of the tab in the financial dynamics
                section.

        Returns:
            str: _description_
        """
        tab = finance_columns_div.find(attrs={"data-tab_name": tab_name})
        if tab:
            dynamics_span = tab.find_next_sibling().find_next_sibling()
            return self.clean_text(dynamics_span.text if dynamics_span else "")
        return ""
