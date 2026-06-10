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
