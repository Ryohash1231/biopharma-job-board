import json
from pathlib import Path

from scraper.ashby import fetch_ashby_jobs

FIXTURE = json.loads(
    Path(__file__).parent.joinpath("fixtures", "ashby_jobs.json").read_text()
)


def test_fetch_ashby_jobs(requests_mock):
    requests_mock.get(
        "https://api.ashbyhq.com/posting-api/job-board/examplebio",
        json=FIXTURE,
    )

    jobs = fetch_ashby_jobs("Example Biosciences", "examplebio")

    assert jobs == [
        {
            "company": "Example Biosciences",
            "title": "Research Scientist",
            "location": "South San Francisco",
            "url": "https://jobs.ashbyhq.com/examplebio/bd99fef5-c71a-4bab-979c-000000000001",
            "date_posted": "2026-05-15T10:00:00.000+00:00",
        },
        {
            "company": "Example Biosciences",
            "title": "Senior Engineer, Platform",
            "location": "Remote",
            "url": "https://jobs.ashbyhq.com/examplebio/bd99fef5-c71a-4bab-979c-000000000002",
            "date_posted": "2026-05-20T14:30:00.000+00:00",
        },
    ]


def test_fetch_ashby_jobs_empty(requests_mock):
    requests_mock.get(
        "https://api.ashbyhq.com/posting-api/job-board/examplebio",
        json={"jobs": [], "apiVersion": "1"},
    )

    jobs = fetch_ashby_jobs("Example Biosciences", "examplebio")

    assert jobs == []
