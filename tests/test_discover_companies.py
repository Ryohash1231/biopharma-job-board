import json
import pytest
import requests

import scraper.discover_companies as discover_module
from scraper.discover_companies import classify_company, extract_ats_token, main


@pytest.mark.parametrize(
    "html, expected",
    [
        (
            '<a href="https://job-boards.greenhouse.io/examplebio">Careers</a>',
            ("greenhouse", "examplebio"),
        ),
        (
            '<a href="https://boards.greenhouse.io/examplebio">Careers</a>',
            ("greenhouse", "examplebio"),
        ),
        (
            '<iframe src="https://www.greenhouse.io/embed/job_board?for=examplebio"></iframe>',
            ("greenhouse", "examplebio"),
        ),
        (
            '<a href="https://jobs.lever.co/examplebio">Careers</a>',
            ("lever", "examplebio"),
        ),
        (
            "<html><body>No jobs here</body></html>",
            None,
        ),
        (
            '<a href="https://jobs.lever.co/examplebio">Careers</a>'
            '<a href="https://job-boards.greenhouse.io/examplebio2">Careers</a>',
            ("greenhouse", "examplebio2"),
        ),
    ],
)
def test_extract_ats_token(html, expected):
    assert extract_ats_token(html) == expected


class FakeResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


def test_classify_company_greenhouse_match(monkeypatch):
    monkeypatch.setattr(
        discover_module.requests,
        "get",
        lambda url, timeout: FakeResponse(
            '<a href="https://job-boards.greenhouse.io/examplebio">Careers</a>'
        ),
    )
    monkeypatch.setattr(discover_module, "fetch_greenhouse_jobs", lambda name, token: [])

    result = classify_company("Example Biosciences", "https://examplebio.com/careers", set())

    assert result == {
        "name": "Example Biosciences",
        "type": "greenhouse",
        "token": "examplebio",
        "careers_url": "https://job-boards.greenhouse.io/examplebio",
    }


def test_classify_company_lever_match(monkeypatch):
    monkeypatch.setattr(
        discover_module.requests,
        "get",
        lambda url, timeout: FakeResponse(
            '<a href="https://jobs.lever.co/examplebio">Careers</a>'
        ),
    )
    monkeypatch.setattr(discover_module, "fetch_lever_jobs", lambda name, token: [])

    result = classify_company("Example Biosciences", "https://examplebio.com/careers", set())

    assert result == {
        "name": "Example Biosciences",
        "type": "lever",
        "token": "examplebio",
        "careers_url": "https://jobs.lever.co/examplebio",
    }


def test_classify_company_no_ats_link(monkeypatch):
    monkeypatch.setattr(
        discover_module.requests,
        "get",
        lambda url, timeout: FakeResponse("<html><body>No jobs here</body></html>"),
    )

    result = classify_company("OtherCo", "https://otherco.com/careers", set())

    assert result == {"name": "OtherCo", "reason": "no greenhouse/lever link found"}


def test_classify_company_duplicate_token(monkeypatch):
    monkeypatch.setattr(
        discover_module.requests,
        "get",
        lambda url, timeout: FakeResponse(
            '<a href="https://job-boards.greenhouse.io/examplebio">Careers</a>'
        ),
    )

    result = classify_company("DupeCo", "https://dupeco.com/careers", {"examplebio"})

    assert result == {"name": "DupeCo", "reason": "duplicate token already in companies.json"}


def test_classify_company_website_fetch_failure(monkeypatch):
    def fake_get(url, timeout):
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(discover_module.requests, "get", fake_get)

    result = classify_company("BrokenCo", "https://brokenco.com/careers", set())

    assert result["name"] == "BrokenCo"
    assert result["reason"].startswith("failed to fetch website:")


def test_classify_company_verification_failure(monkeypatch):
    monkeypatch.setattr(
        discover_module.requests,
        "get",
        lambda url, timeout: FakeResponse(
            '<a href="https://job-boards.greenhouse.io/examplebio">Careers</a>'
        ),
    )

    def fake_fetch(name, token):
        raise requests.HTTPError("404 Client Error")

    monkeypatch.setattr(discover_module, "fetch_greenhouse_jobs", fake_fetch)

    result = classify_company("Example Biosciences", "https://examplebio.com/careers", set())

    assert result["name"] == "Example Biosciences"
    assert result["reason"].startswith("verification failed:")


def test_main_writes_discovered_companies(tmp_path, monkeypatch):
    companies_path = tmp_path / "companies.json"
    companies_path.write_text(json.dumps([
        {
            "name": "Existing Co",
            "type": "greenhouse",
            "token": "existingco",
            "careers_url": "https://job-boards.greenhouse.io/existingco",
        },
    ]))

    candidates_path = tmp_path / "candidates.json"
    candidates_path.write_text(json.dumps([
        {"name": "Example Biosciences", "website": "https://examplebio.com/careers"},
        {"name": "OtherCo", "website": "https://otherco.com/careers"},
    ]))

    output_path = tmp_path / "discovered_companies.json"

    responses = {
        "https://examplebio.com/careers": '<a href="https://job-boards.greenhouse.io/examplebio">Careers</a>',
        "https://otherco.com/careers": "<html><body>No jobs here</body></html>",
    }

    monkeypatch.setattr(
        discover_module.requests,
        "get",
        lambda url, timeout: FakeResponse(responses[url]),
    )
    monkeypatch.setattr(discover_module, "fetch_greenhouse_jobs", lambda name, token: [])

    main(
        candidates_path=str(candidates_path),
        output_path=str(output_path),
        companies_path=str(companies_path),
    )

    data = json.loads(output_path.read_text())

    assert data["matches"] == [
        {
            "name": "Example Biosciences",
            "type": "greenhouse",
            "token": "examplebio",
            "careers_url": "https://job-boards.greenhouse.io/examplebio",
        }
    ]
    assert data["skipped"] == [
        {"name": "OtherCo", "reason": "no greenhouse/lever link found"}
    ]
