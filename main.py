import asyncio
import logging

from spider import Spider
from sheets_api import SheetsApi


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

_logger = logging.getLogger("client.radar.logger")


async def main():
    """Collect data using the spider and write the results to Google Sheets."""
    spider = Spider()
    sheets_api = SheetsApi()

    rows = await spider.run()
    sheets_api.write_to_google_sheets(rows)


async def run_with_retry(retries=5):
    """Run the application with retries.

    Args:
        retries: Maximum number of execution attempts.

    Raises:
        RuntimeError: If all retry attempts fail.
    """
    for attempt in range(retries):
        try:
            await main()
            return
        except Exception as e:
            _logger.exception(f"Ошибка запуска (попытка {attempt+1}): {e}")
            await asyncio.sleep(2)

    raise RuntimeError("Не удалось запустить браузер")


asyncio.run(run_with_retry())
