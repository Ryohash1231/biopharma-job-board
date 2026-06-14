import json
import logging
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DIRECTORY_URL = "https://biopharmguy.com/links/company-by-name-northern-california.php"


def parse_companies(html):
    soup = BeautifulSoup(html, "html.parser")
    companies = []

    for row in soup.find_all("tr", class_=["odd", "even"]):
        company_cell = row.find("td", class_="company")
        if company_cell is None:
            logger.warning("Skipping row with no company cell")
            continue

        link = company_cell.find(
            "a", style=lambda value: value and "text-decoration:none" in value
        )
        if link is None:
            logger.warning("Skipping row with no company website link")
            continue

        companies.append({
            "name": link.get_text().strip(),
            "website": link["href"],
        })

    return companies


def main(output_path="candidates.json"):
    response = requests.get(DIRECTORY_URL, timeout=10)
    response.raise_for_status()

    companies = parse_companies(response.text)

    Path(output_path).write_text(json.dumps(companies, indent=2))
    logger.info("Scraped %d companies from biopharmguy.com", len(companies))


if __name__ == "__main__":
    output_arg = sys.argv[1] if len(sys.argv) > 1 else "candidates.json"
    main(output_arg)
