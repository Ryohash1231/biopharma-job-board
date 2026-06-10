import json
from pathlib import Path

from scraper.greenhouse import fetch_greenhouse_jobs

FIXTURE = json.loads(
    Path(__file__).parent.joinpath("fixtures", "greenhouse_jobs.json").read_text()
)


def test_fetch_greenhouse_jobs(requests_mock):
    requests_mock.get(
        "https://boards-api.greenhouse.io/v1/boards/annexonbioscience/jobs",
        json=FIXTURE,
    )

    jobs = fetch_greenhouse_jobs("Annexon Biosciences", "annexonbioscience")

    assert jobs == [
        {
            "company": "Annexon Biosciences",
            "title": "Associate Director, Clinical Trial Management",
            "location": "San Francisco Bay Area",
            "url": "https://job-boards.greenhouse.io/annexonbioscience/jobs/4699427005",
        },
        {
            "company": "Annexon Biosciences",
            "title": "Director, Procurement Strategic Contract Negotiator",
            "location": "San Francisco Bay Area",
            "url": "https://job-boards.greenhouse.io/annexonbioscience/jobs/4684932005",
        },
    ]
