import requests


def fetch_ashby_jobs(company_name, token):
    url = f"https://api.ashbyhq.com/posting-api/job-board/{token}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    return [
        {
            "company": company_name,
            "title": job["title"],
            "location": job["location"],
            "url": job["jobUrl"],
            "date_posted": job["publishedAt"],
        }
        for job in data.get("jobs", [])
    ]
