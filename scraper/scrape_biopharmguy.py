import logging

from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


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
