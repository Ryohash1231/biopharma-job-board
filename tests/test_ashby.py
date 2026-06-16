import json
from pathlib import Path

import pytest
import requests

from scraper.ashby import fetch_ashby_jobs

FIXTURE = json.loads(
    Path(__file__).parent.joinpath("fixtures", "ashby_jobs.json").read_text()
)

GQL_URL = "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams"


def test_fetch_ashby_jobs(requests_mock):
    requests_mock.post(GQL_URL, json=FIXTURE)

    jobs = fetch_ashby_jobs("Example Biosciences", "examplebio")

    assert jobs == [
        {
            "company": "Example Biosciences",
            "title": "Research Scientist",
            "location": "South San Francisco",
            "url": "https://jobs.ashbyhq.com/examplebio/bd99fef5-c71a-4bab-979c-000000000001",
            "date_posted": "",
        },
        {
            "company": "Example Biosciences",
            "title": "Senior Engineer, Platform",
            "location": "Remote",
            "url": "https://jobs.ashbyhq.com/examplebio/bd99fef5-c71a-4bab-979c-000000000002",
            "date_posted": "",
        },
    ]


def test_fetch_ashby_jobs_empty(requests_mock):
    requests_mock.post(GQL_URL, json={"data": {"jobBoard": {"jobPostings": []}}})

    jobs = fetch_ashby_jobs("Example Biosciences", "examplebio")

    assert jobs == []


def test_fetch_ashby_jobs_invalid_token(requests_mock):
    requests_mock.post(GQL_URL, json={"data": {"jobBoard": None}})

    with pytest.raises(ValueError, match="not found"):
        fetch_ashby_jobs("Example Biosciences", "invalidtoken")
