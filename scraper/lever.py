from datetime import datetime, timezone

import requests

def fetch_lever_jobs(company_name, token):
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    return [
        {
            "company": company_name,
            "title": job["text"],
            "location": job.get("categories", {}).get("location", ""),
            "url": job["hostedUrl"],
            "date_posted": datetime.fromtimestamp(
                job["createdAt"] / 1000, tz=timezone.utc
            ).isoformat(),
        }
        for job in data
    ]
