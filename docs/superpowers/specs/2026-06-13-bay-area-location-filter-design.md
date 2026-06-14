# Bay Area / Remote Location Filter — Design

## Goal

The scraper currently writes every job it finds to `jobs.json`, including
postings located far outside the Bay Area (e.g. Boston, Paris, "Remote
(Japan)", "APAC - China, Guangzhou"). Add a filter so that only jobs located
in the Bay Area, or remote within the US/unspecified, are written to
`jobs.json`.

## Architecture

Add a new module `scraper/location_filter.py` exposing a single function:

```python
def is_bay_area_or_remote(location: str) -> bool:
    ...
```

In `scraper/run.py`, after the existing loop builds `all_jobs` from all
fetchers, filter the combined list through this function before writing
`jobs.json`:

```python
filtered_jobs = [j for j in all_jobs if is_bay_area_or_remote(j["location"])]
dropped = len(all_jobs) - len(filtered_jobs)
logger.info("Filtered out %d jobs outside the Bay Area/remote-US", dropped)
```

`filtered_jobs` (not `all_jobs`) is written to `jobs.json`.

This is centralized rather than applied per-fetcher
(`greenhouse.py`/`lever.py`/`html_extract.py`) because the matching logic is
identical regardless of source — centralizing it avoids duplicating keyword
lists across three files and is easier to unit test in isolation.

## Bay Area Matching

A location counts as Bay Area if it contains (case-insensitive) any of the
following substrings:

```
bay area, san francisco, redwood city, emeryville, berkeley, brisbane,
foster city, menlo park, palo alto, mountain view, sunnyvale, santa clara,
san jose, fremont, hayward, oakland, alameda, vacaville, novato,
san rafael, san mateo, burlingame, san carlos, union city, pleasanton,
walnut creek, hercules, milpitas, daly city, belmont, half moon bay,
petaluma, vallejo, richmond, ca, concord, ca
```

Notes:
- `"san francisco"` as a substring naturally covers `"South San Francisco"`
  and `"San Francisco (UCSF)"`.
- `"richmond, ca"` and `"concord, ca"` include the state suffix to avoid
  false matches on Richmond, VA or Concord, NH.
- Broad/ambiguous California regions like `"Northern California, United
  States"` and `"Sacramento, California, United States"` are intentionally
  NOT in this list and will not match.

## Remote Matching

A location counts as remote (US/unspecified) if it contains `"remote"`
(case-insensitive) AND does not contain any of these non-US country/region
markers (case-insensitive):

```
japan, uk, italy, spain, switzerland, netherlands, france, germany,
apac, ireland, canada, australia, china, mexico, brazil, india
```

Examples:
- `"Remote"`, `"Remote, United States"`, `"USA - Remote"`,
  `"Remote (United States)"` → remote (kept)
- `"Remote (Japan)"`, `"Remote (UK)"`, `"APAC - Remote"` → not remote
  (dropped, unless they also match the Bay Area list)

## Combined Rule

`is_bay_area_or_remote(location)` returns `True` if EITHER the Bay Area
check OR the remote check passes. Multi-location strings (e.g. `"USA -
Carlsbad, CA; USA - South San Francisco, CA"`, `"Hybrid, Berkeley,
California, United States, Remote"`) are correctly handled by substring
matching — if any part of the string matches, the job is kept.

Jobs with an empty or missing `location` are dropped (fail closed — cannot
be classified as Bay Area or remote).

## Testing

- New `tests/test_location_filter.py`: table-driven tests covering Bay Area
  cities (`"South San Francisco"`, `"Redwood City, CA"`, `"Emeryville,
  California; Remote, United States"`), US/unspecified remote (`"Remote"`,
  `"USA - Remote"`, `"Remote (United States)"`), non-US remote (`"Remote
  (Japan)"`, `"APAC - Remote"`), and clearly-excluded locations (`"Boston,
  Massachusetts, United States"`, `"Northern California, United States"`,
  `"Various Locations"`, `""`).
- `tests/test_run.py`: new test confirming `run()` drops a non-matching job
  from the output `jobs.json`.

## Out of Scope

- Re-running the scraper against live APIs to regenerate `jobs.json` with
  the new filter applied — that happens on the next scheduled scrape after
  this change is merged.
- Changes to the frontend (`app.js`, `index.html`) — filtering happens at
  scrape time, not display time.
