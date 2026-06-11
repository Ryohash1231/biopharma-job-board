import json
from datetime import datetime, timezone
from pathlib import Path

from scraper.lever import fetch_lever_jobs

FIXTURE = json.loads(
    Path(__file__).parent.joinpath("fixtures", "lever_jobs.json").read_text()
)


def test_fetch_lever_jobs(requests_mock):
    requests_mock.get(
        "https://api.lever.co/v0/postings/boltbio?mode=json",
        json=FIXTURE,
    )

    jobs = fetch_lever_jobs("Bolt Biotherapeutics", "boltbio")

    assert jobs == [
        {
            "company": "Bolt Biotherapeutics",
            "title": "Senior Scientist, Protein Engineering",
            "location": "Redwood City, CA",
            "url": "https://jobs.lever.co/boltbio/a1b2c3d4-0000-0000-0000-000000000001",
            "date_posted": datetime.fromtimestamp(
                FIXTURE[0]["createdAt"] / 1000, tz=timezone.utc
            ).isoformat(),
        },
        {
            "company": "Bolt Biotherapeutics",
            "title": "Research Associate, Antibody Discovery",
            "location": "Redwood City, CA",
            "url": "https://jobs.lever.co/boltbio/a1b2c3d4-0000-0000-0000-000000000002",
            "date_posted": datetime.fromtimestamp(
                FIXTURE[1]["createdAt"] / 1000, tz=timezone.utc
            ).isoformat(),
        },
    ]


def test_fetch_lever_jobs_empty(requests_mock):
    requests_mock.get(
        "https://api.lever.co/v0/postings/boltbio?mode=json",
        json=[],
    )

    jobs = fetch_lever_jobs("Bolt Biotherapeutics", "boltbio")

    assert jobs == []
