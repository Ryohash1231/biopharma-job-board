# Bay Area Biopharma Job Board — Design

## Goal

A free, simple job aggregator that pulls open positions from the career pages
of biopharma companies in the Bay Area (sourced from biopharmguy.com's
Northern California company list) into one searchable page. This is an
introductory project intended to teach the basics of working with the Claude
API (for parsing messy HTML into structured data) while producing something
with potential to generate revenue later (ads, affiliate links, sponsored
listings) once it has traffic.

## Architecture

```
companies.json (curated list: ~15-25 companies, name + careers URL)
        |
        v
scraper.py (Python, run via GitHub Actions cron, e.g. daily)
   - generic extraction first (common ATS/HTML patterns)
   - falls back to Claude API for messy/non-standard pages
   - logs and skips per-company failures
        |
        v
jobs.json (committed back to repo by the Action)
        |
        v
Static frontend (HTML/CSS/JS, hosted on GitHub Pages)
   - loads jobs.json
   - free-text search/filter across title, company, location
   - shows "last updated" timestamp
```

## Components

### 1. Company list (`companies.json`)

A hand-curated list of ~15-25 Bay Area biopharma companies, drawn from
https://biopharmguy.com/links/company-by-name-northern-california.php.
Each entry: `{ "name": "...", "careers_url": "..." }`.

For the MVP, prioritize companies whose careers pages are server-rendered
HTML (e.g., simpler ATS platforms) rather than heavily JS-rendered pages
(e.g., some Greenhouse/Lever/Workday embeds), since those would require a
headless browser (Playwright) — noted as a v2 enhancement.

### 2. Scraper (`scraper.py`)

- Iterates over `companies.json`, fetches each careers page (`requests` +
  `BeautifulSoup`).
- Generic extraction: looks for common job-listing patterns (tables, lists
  of links containing job-title-like text, location text nearby).
- Fallback: if generic extraction yields nothing or looks malformed, sends
  the relevant page HTML to the Claude API with a prompt asking it to
  extract a JSON array of `{title, location, url}` job listings.
- Per-company errors (network failure, no listings found, bad response) are
  caught, logged, and skipped — a single broken site does not fail the whole
  run.
- Writes results to `jobs.json`: array of
  `{company, title, location, url, date_scraped}`.

### 3. Frontend (static site)

- `index.html`, `app.js`, `style.css` — no build tooling.
- On load, fetches `jobs.json` and renders a list/table of postings.
- A search box filters the rendered list in real time via case-insensitive
  substring match across title, company, and location.
- Displays "Last updated: <date>" from the scrape timestamp.
- Hosted free on GitHub Pages, served from this repo.

### 4. Automation

- A GitHub Actions workflow runs `scraper.py` on a daily schedule (e.g.,
  cron `0 13 * * *`), and commits the updated `jobs.json` if it changed.

## Revenue Path (post-MVP)

The MVP itself is free to build and run, focused on proving the concept and
attracting initial traffic. Once there's an audience, monetization options
include Google AdSense, affiliate links to resume/career-coaching services
relevant to biopharma job seekers, or sponsored/featured company placements.

## Testing

- Unit tests for the generic HTML extraction logic, run against saved
  sample HTML fixtures from a few real career pages.
- A smoke test that runs the scraper against the full company list and
  asserts each company returns a non-negative number of listings without
  raising — failures are logged, not fatal.
- Manual check of the frontend rendering against a sample `jobs.json`.

## Deployment

- Create a GitHub repository and push this local repo to it.
- Enable GitHub Pages for the repo (serving the static frontend), giving a
  public URL of the form `https://<username>.github.io/<repo>/`.
- The GitHub Actions scraper workflow runs against this same repo, so
  scheduled updates to `jobs.json` are reflected on the live site
  automatically.

## Out of scope (v2+)

- JS-rendered career pages requiring a headless browser (Playwright).
- User accounts, saved searches, email alerts.
- AI-powered resume matching / cover letter generation.
- Expanding beyond the initial ~15-25 company list.
