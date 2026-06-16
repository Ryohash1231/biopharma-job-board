import json

from scraper import run as run_module


def test_run_writes_jobs_and_skips_failures(tmp_path, monkeypatch):
    companies = [
        {
            "name": "GoodCo",
            "type": "greenhouse",
            "token": "goodco",
            "careers_url": "https://goodco.example/careers",
        },
        {
            "name": "BadCo",
            "type": "lever",
            "token": "badco",
            "careers_url": "https://badco.example/careers",
        },
    ]
    companies_path = tmp_path / "companies.json"
    companies_path.write_text(json.dumps(companies))
    output_path = tmp_path / "jobs.json"

    monkeypatch.setattr(
        run_module,
        "fetch_greenhouse_jobs",
        lambda name, token: [
            {
                "company": name,
                "title": "Research Associate",
                "location": "Bay Area",
                "url": "https://goodco.example/jobs/1",
            }
        ],
    )

    def boom(name, token):
        raise RuntimeError("site is down")

    monkeypatch.setattr(run_module, "fetch_lever_jobs", boom)

    run_module.run(companies_path=str(companies_path), output_path=str(output_path))

    data = json.loads(output_path.read_text())
    assert "scraped_at" in data
    assert data["jobs"] == [
        {
            "company": "GoodCo",
            "title": "Research Associate",
            "location": "Bay Area",
            "url": "https://goodco.example/jobs/1",
        }
    ]


def test_run_filters_out_jobs_outside_bay_area(tmp_path, monkeypatch):
    companies = [
        {
            "name": "GoodCo",
            "type": "greenhouse",
            "token": "goodco",
            "careers_url": "https://goodco.example/careers",
        },
    ]
    companies_path = tmp_path / "companies.json"
    companies_path.write_text(json.dumps(companies))
    output_path = tmp_path / "jobs.json"

    monkeypatch.setattr(
        run_module,
        "fetch_greenhouse_jobs",
        lambda name, token: [
            {
                "company": name,
                "title": "Research Associate",
                "location": "South San Francisco, California, United States",
                "url": "https://goodco.example/jobs/1",
            },
            {
                "company": name,
                "title": "Sales Director",
                "location": "Boston, Massachusetts, United States",
                "url": "https://goodco.example/jobs/2",
            },
        ],
    )

    run_module.run(companies_path=str(companies_path), output_path=str(output_path))

    data = json.loads(output_path.read_text())
    assert [job["title"] for job in data["jobs"]] == ["Research Associate"]


def test_run_handles_ashby_company(tmp_path, monkeypatch):
    companies = [
        {
            "name": "ExampleBio",
            "type": "ashby",
            "token": "examplebio",
            "careers_url": "https://jobs.ashbyhq.com/examplebio",
        },
    ]
    companies_path = tmp_path / "companies.json"
    companies_path.write_text(json.dumps(companies))
    output_path = tmp_path / "jobs.json"

    monkeypatch.setattr(
        run_module,
        "fetch_ashby_jobs",
        lambda name, token: [
            {
                "company": name,
                "title": "Research Scientist",
                "location": "South San Francisco, CA",
                "url": "https://jobs.ashbyhq.com/examplebio/abc123",
                "date_posted": "2026-05-15T10:00:00.000+00:00",
            }
        ],
    )

    run_module.run(companies_path=str(companies_path), output_path=str(output_path))

    data = json.loads(output_path.read_text())
    assert data["jobs"] == [
        {
            "company": "ExampleBio",
            "title": "Research Scientist",
            "location": "South San Francisco, CA",
            "url": "https://jobs.ashbyhq.com/examplebio/abc123",
            "date_posted": "2026-05-15T10:00:00.000+00:00",
        }
    ]
