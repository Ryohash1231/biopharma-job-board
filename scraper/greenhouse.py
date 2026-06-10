import requests


def fetch_greenhouse_jobs(company_name, token):
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    return [
        {
            "company": company_name,
            "title": job["title"],
            "location": job["location"]["name"],
            "url": job["absolute_url"],
        }
        for job in data.get("jobs", [])
    ]
