# Job Posting Dates — Design

## Goal

Show users when each job posting was posted (or last updated), and let them
filter the job board to recent postings only (last 24 hours / 7 days / 30
days / all time).

## Data Model Change

Each job dict gains one new field, `date_posted`, in addition to the
existing `company`, `title`, `location`, `url`:

```json
{
  "company": "Annexon Biosciences",
  "title": "Research Associate, Protein Sciences",
  "location": "San Francisco Bay Area",
  "url": "https://job-boards.greenhouse.io/annexonbioscience/jobs/0000000001",
  "date_posted": "2026-06-01T08:00:00-05:00"
}
```

`date_posted` is an ISO 8601 timestamp string, or `null` if no date is
available for that job.

## Per-Source Behavior

### Greenhouse (`scraper/greenhouse.py`)

The Greenhouse Job Board API returns an `updated_at` field per job (ISO 8601
string with timezone offset, e.g. `"2026-06-01T08:00:00-05:00"`). This is the
last-updated time, not necessarily the original posting date, but it's the
best signal Greenhouse's public API exposes. Pass it through directly:

```python
"date_posted": job["updated_at"],
```

### Lever (`scraper/lever.py`)

The Lever Postings API returns `createdAt` as epoch milliseconds (the actual
posting-creation time). Convert to an ISO 8601 UTC string for consistency
with the other sources:

```python
from datetime import datetime, timezone

"date_posted": datetime.fromtimestamp(job["createdAt"] / 1000, tz=timezone.utc).isoformat(),
```

### HTML + Claude (`scraper/html_extract.py`)

Career pages handled via Claude-assisted extraction (BigHat Biosciences,
Gordian Biotechnology, 3T Biosciences) generally don't expose a reliable
posting date, and asking Claude to guess one risks hallucination. These jobs
get:

```python
"date_posted": None,
```

### Orchestrator (`scraper/run.py`)

No changes — job dicts are passed through unchanged regardless of which
fetcher produced them.

## Frontend

### Display

- Add a "Posted" column to the jobs table (after Location).
- Render: `job.date_posted ? new Date(job.date_posted).toLocaleDateString() : '—'`
- Jobs with `date_posted: null` show `—` in this column.

### Recency Filter

- Add a `<select id="recency">` dropdown next to the search box with options:
  - "All time" (default)
  - "Last 24 hours"
  - "Last 7 days"
  - "Last 30 days"
- Filtering combines with the existing text search via AND: a job must match
  both the search query and the selected recency bucket to be shown.
- A new `withinRecency(job, bucket)` helper:
  - `bucket === 'all'` → always `true`.
  - Otherwise, `job.date_posted` must be non-null AND within the bucket's
    time window of `Date.now()`. Jobs with `date_posted: null` are excluded
    from any non-"all" recency filter.
- No change to default sort order (jobs remain in scrape order; this design
  does not add date-based sorting).

### Sample data

Update the sample `jobs.json` (used for local frontend testing) so its 3
jobs cover all three cases: two with realistic ISO `date_posted` values
(Greenhouse-style), and one (BigHat, the HTML-sourced sample) with
`date_posted: null`.

## Testing

- `tests/test_greenhouse.py`: fixture includes `updated_at`; assert
  `date_posted` matches it directly.
- `tests/test_lever.py`: fixture includes `createdAt` (epoch ms); assert
  `date_posted` is the correct ISO conversion.
- `tests/test_html_extract.py`: assert `date_posted` is `None` in returned
  job dicts.
- Manual frontend check: load sample `jobs.json` via local server, confirm
  the "Posted" column renders dates and `—` correctly, and that each recency
  filter option narrows results as expected — including the case where a
  job with `date_posted: null` is correctly excluded by a non-"all" filter.

## Out of Scope

- Sorting the job list by posting date.
- Relative time display (e.g. "3 days ago") — absolute dates only.
- Extracting posting dates for HTML/Claude-sourced companies.
