import json

import scraper.scrape_biopharmguy as scrape_module
from scraper.scrape_biopharmguy import main, parse_companies


NORMAL_ROW = """
<table>
<tr class="even">
<td class="company"><a href="/company.php/10X Genomics" class="company" target="_blank"><img src="/images/url.png" alt="Add'l Locations" height="9"></a><a href="https://www.10xgenomics.com/" style="text-decoration:none" target="_blank">10X Genomics </a></td>
<td class="location">CA - Pleasanton</td>
<td class="description">Genomics Platform</td>
</tr>
</table>
"""

ROW_WITH_DESCRIPTION_LINK = """
<table>
<tr class="odd">
<td class="company"><a href="/company.php/Selvita" class="company" target="_blank"><img src="/images/url.png" alt="Add'l Locations" height="9"></a><a href="https://selvita.com/" style="text-decoration:none" target="_blank">Selvita </a></td>
<td class="location">CA - South SF</td>
<td class="description">Selvita | Fully-integrated <a href="https://selvita.com/cro" target="_blank" rel="nofollow">CRO</a> providing support.</td>
</tr>
</table>
"""

SPONSOR_ROW = """
<table>
<tr class="sponsor">
<td class="company"><a href="https://www.mispro.com/space-services" style="text-decoration:none" target="_blank"><img class="database" src="/images/companies/mispro.png" alt="Mispro Biotech Services"> </a></td>
<td class="location">CA - South SF</td>
<td class="description">Mispro is a contract vivarium organization.</td>
</tr>
</table>
"""

ROW_WITHOUT_WEBSITE_LINK = """
<table>
<tr class="even">
<td class="company"><a href="/company.php/BadCo" class="company" target="_blank"><img src="/images/url.png" alt="Add'l Locations" height="9"></a></td>
<td class="location">CA - Somewhere</td>
<td class="description">No website link</td>
</tr>
</table>
"""


def test_parse_companies_extracts_name_and_website():
    result = parse_companies(NORMAL_ROW)

    assert result == [
        {"name": "10X Genomics", "website": "https://www.10xgenomics.com/"}
    ]


def test_parse_companies_ignores_links_in_description():
    result = parse_companies(ROW_WITH_DESCRIPTION_LINK)

    assert result == [
        {"name": "Selvita", "website": "https://selvita.com/"}
    ]


def test_parse_companies_skips_sponsor_rows():
    result = parse_companies(SPONSOR_ROW)

    assert result == []


def test_parse_companies_skips_rows_without_website_link():
    result = parse_companies(ROW_WITHOUT_WEBSITE_LINK)

    assert result == []


def test_parse_companies_handles_multiple_rows():
    html = NORMAL_ROW.replace("</table>", "") + ROW_WITH_DESCRIPTION_LINK.replace("<table>", "")

    result = parse_companies(html)

    assert result == [
        {"name": "10X Genomics", "website": "https://www.10xgenomics.com/"},
        {"name": "Selvita", "website": "https://selvita.com/"},
    ]


class FakeResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


def test_main_writes_candidates_json(tmp_path, monkeypatch):
    monkeypatch.setattr(
        scrape_module.requests,
        "get",
        lambda url, timeout: FakeResponse(NORMAL_ROW),
    )

    output_path = tmp_path / "candidates.json"

    main(output_path=str(output_path))

    data = json.loads(output_path.read_text())
    assert data == [
        {"name": "10X Genomics", "website": "https://www.10xgenomics.com/"}
    ]
