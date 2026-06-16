import requests

_GQL_URL = "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams"
_GQL_QUERY = """
query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) {
  jobBoard: jobBoardWithTeams(
    organizationHostedJobsPageName: $organizationHostedJobsPageName
  ) {
    jobPostings {
      id
      title
      locationName
      employmentType
    }
  }
}
"""


def fetch_ashby_jobs(company_name, token):
    response = requests.post(
        _GQL_URL,
        json={
            "query": _GQL_QUERY,
            "variables": {"organizationHostedJobsPageName": token},
            "operationName": "ApiJobBoardWithTeams",
        },
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    job_board = (data.get("data") or {}).get("jobBoard")
    if job_board is None:
        raise ValueError(f"Ashby board '{token}' not found")

    return [
        {
            "company": company_name,
            "title": job["title"],
            "location": job.get("locationName", ""),
            "url": f"https://jobs.ashbyhq.com/{token}/{job['id']}",
            "date_posted": "",
        }
        for job in job_board.get("jobPostings", [])
    ]
