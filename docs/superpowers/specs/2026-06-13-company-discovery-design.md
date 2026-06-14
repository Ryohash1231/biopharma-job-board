# Company Discovery Script — Design

## Goal

Help scale `companies.json` beyond its current 17 entries by automating the
tedious part of adding new companies: figuring out whether a candidate
company uses Greenhouse or Lever (and what its token is), without requiring
the Anthropic API (`"html"` type is out of scope for this tool).

Given a list of candidate companies (name + website/careers URL), produce a
review file listing which ones are Greenhouse/Lever (ready to paste into
`companies.json`) and which ones aren't (skipped, candidates for future
Tier 2/html support).

## Architecture

New standalone script `scraper/discover_companies.py`, following the
existing fetcher conventions (`scraper/greenhouse.py`, `scraper/lever.py`):
plain functions using `requests`, no new dependencies.

### `extract_ats_token(html)`

Pure function. Regex-searches an HTML string for Greenhouse or Lever
embed/link patterns:

- Greenhouse: `(?:boards|job-boards)\.greenhouse\.io/([a-zA-Z0-9_-]+)` or
  `greenhouse\.io/embed/job_board\?for=([a-zA-Z0-9_-]+)`
- Lever: `jobs\.lever\.co/([a-zA-Z0-9_-]+)`

Returns `("greenhouse", token)`, `("lever", token)`, or `None` if neither
pattern matches. If both patterns match, Greenhouse wins (checked first).

### `classify_company(name, website_url, existing_tokens)`

1. Fetch `website_url` via `requests.get` (10s timeout, same as existing
   fetchers). If the request fails (non-200, timeout, connection error),
   return a skip result with reason `"failed to fetch website: <error>"`.
2. Run `extract_ats_token` on the response HTML. If no match, return a skip
   result with reason `"no greenhouse/lever link found"`.
3. If a token is found but it's already in `existing_tokens` (tokens already
   present in `companies.json`), return a skip result with reason
   `"duplicate token already in companies.json"`.
4. Otherwise, verify the token is real by calling the existing
   `fetch_greenhouse_jobs(name, token)` or `fetch_lever_jobs(name, token)`
   (imported, not duplicated). If this raises, return a skip result with
   reason `"verification failed: <error>"`.
5. On success, return a match result:
   - Greenhouse: `{"name": name, "type": "greenhouse", "token": token, "careers_url": f"https://job-boards.greenhouse.io/{token}"}`
   - Lever: `{"name": name, "type": "lever", "token": token, "careers_url": f"https://jobs.lever.co/{token}"}`

### `main()`

CLI entry point (`python -m scraper.discover_companies <candidates_path> [<output_path>]`,
defaulting `output_path` to `discovered_companies.json`):

1. Load `companies.json` and build `existing_tokens` = set of all `token`
   values present (for greenhouse/lever entries).
2. Load the candidates file (array of `{"name", "website"}`).
3. For each candidate, call `classify_company` inside a `try/except`
   (mirroring `scraper/run.py`'s per-company resilience) — an unexpected
   exception becomes a skip result with reason `"error: <exception>"`, never
   aborts the batch.
4. Collect results into `{"matches": [...], "skipped": [...]}` and write to
   `output_path` as indented JSON.
5. Log a summary: `"Checked %d candidates: %d matches, %d skipped"`.

## Input Format

A JSON file (path given as the first CLI argument) — an array of candidate
companies:

```json
[
  {"name": "Example Biosciences", "website": "https://examplebio.com/careers"}
]
```

This file is user-provided (e.g. compiled manually from a directory site).
The script does not fetch or parse any directory site itself.

## Output Format

```json
{
  "matches": [
    {
      "name": "Example Biosciences",
      "type": "greenhouse",
      "token": "examplebio",
      "careers_url": "https://job-boards.greenhouse.io/examplebio"
    }
  ],
  "skipped": [
    {"name": "OtherCo", "reason": "no greenhouse/lever link found"},
    {"name": "DupeCo", "reason": "duplicate token already in companies.json"}
  ]
}
```

`matches` entries are in the exact shape of `companies.json` entries — ready
to copy/paste. `skipped` entries are logged with a reason so the user can
decide whether to investigate manually or defer to Tier 2 (html/Claude API).

## Error Handling

- Per-candidate errors (fetch failure, no match, verification failure,
  unexpected exception) never abort the run — each becomes a `skipped` entry
  with a reason, matching the resilience pattern already used in
  `scraper/run.py`.
- The script does not modify `companies.json`. It only reads it (to compute
  `existing_tokens`) and writes a separate `discovered_companies.json`.

## Testing

- `tests/test_discover_companies.py`:
  - Table-driven tests for `extract_ats_token` covering: Greenhouse iframe
    embed, Greenhouse job-boards link, Lever link, no match, both
    Greenhouse and Lever present (Greenhouse wins).
  - `classify_company` tests with mocked `requests.get` (via
    `monkeypatch`) and mocked `fetch_greenhouse_jobs`/`fetch_lever_jobs`,
    covering: successful Greenhouse match, successful Lever match, no ATS
    link found, duplicate token, website fetch failure, verification
    failure.
  - `main()` test using `tmp_path`: writes a small temp `candidates.json`
    and temp `companies.json`, runs `main()`, and asserts the shape and
    contents of the resulting `discovered_companies.json`.

## Out of Scope

- Fetching or parsing any third-party directory site (e.g. biopharmguy) —
  the candidate list is user-provided.
- `"html"`/Claude-API-based company types — this tool only detects
  Greenhouse and Lever.
- Automatically merging discovered companies into `companies.json` — the
  user reviews `discovered_companies.json` and merges manually.
- Changes to `scraper/run.py` or the daily scrape workflow.
