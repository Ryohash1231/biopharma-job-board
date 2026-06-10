import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from scraper.greenhouse import fetch_greenhouse_jobs
from scraper.lever import fetch_lever_jobs
from scraper.html_extract import fetch_html_jobs

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def run(companies_path="companies.json", output_path="jobs.json"):
    companies = json.loads(Path(companies_path).read_text())

    fetchers = {
        "greenhouse": lambda c: fetch_greenhouse_jobs(c["name"], c["token"]),
        "lever": lambda c: fetch_lever_jobs(c["name"], c["token"]),
        "html": lambda c: fetch_html_jobs(c["name"], c["careers_url"]),
    }

    all_jobs = []
    for company in companies:
        try:
            jobs = fetchers[company["type"]](company)
            logger.info("%s: found %d jobs", company["name"], len(jobs))
            all_jobs.extend(jobs)
        except Exception:
            logger.exception("Failed to fetch jobs for %s", company["name"])

    output = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "jobs": all_jobs,
    }
    Path(output_path).write_text(json.dumps(output, indent=2))
    logger.info("Wrote %d total jobs to %s", len(all_jobs), output_path)


if __name__ == "__main__":
    run()
