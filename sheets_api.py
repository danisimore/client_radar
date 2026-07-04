import logging
import gspread
from config import sheets_api_config
from spider import HEADERS

_logger = logging.getLogger("client.radar.logger")


class SheetsApi:
    """Object for implementing interaction with the Google Sheets API."""

    def write_to_google_sheets(self, all_rows: list[list[str]]):
        """Writes data to a table.

        Args:
            all_rows (list[list[str]]): rows that will be written to the table.
        """

        _logger.info("Запись всех данных в Google Sheets...")

        gc = gspread.service_account(filename=sheets_api_config.credentials)
        sheet = gc.open_by_key(key=sheets_api_config.table_key)
        worksheet = sheet.get_worksheet(0)

        worksheet.clear()
        worksheet.append_row(HEADERS)
        worksheet.append_rows(all_rows)

        _logger.info(f"Записано строк: {len(all_rows)}")
