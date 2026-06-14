# BioPharmGuy Directory Scraper — Design

## Goal

Generate a `candidates.json` file (the input format expected by
`scraper/discover_companies.py`) by scraping the Northern California biotech
company directory at
`https://biopharmguy.com/links/company-by-name-northern-california.php`.

This is a one-shot manual tool: run it once to produce `candidates.json`,
then feed that into `scraper/discover_companies.py` to find which candidates
use Greenhouse or Lever.

## Architecture

New standalone script `scraper/scrape_biopharmguy.py`, following the existing
fetcher conventions: plain functions using `requests` and `BeautifulSoup`
(`bs4`), both already project dependencies (`BeautifulSoup` is already used
in `scraper/html_extract.py`).

### `parse_companies(html)`

Pure function. Parses the page HTML with `BeautifulSoup` and finds every
`<tr class="odd">` and `<tr class="even">` row (the directory's real
listings — the 2 promotional `<tr class="sponsor">` rows are skipped, since
their `<td class="company">` cell has no separate company-name link).

For each row:

1. Find `<td class="company">`.
2. Within it, find the `<a>` tag whose `style` attribute contains
   `text-decoration:none` — this is the external website link (as opposed
   to the internal `/company.php/...` profile link, which has
   `class="company"` and wraps only an `<img>`).
3. `name` = that `<a>` tag's text, stripped (the source HTML has a trailing
   space, e.g. `"10X Genomics "`).
4. `website` = that `<a>` tag's `href`.

If a row's `<td class="company">` doesn't contain a matching `<a>` tag, the
row is skipped and a warning is logged (not fatal — one malformed row
shouldn't abort the whole scrape).

Returns a list of `{"name": ..., "website": ...}` dicts, in document order.

### `main(output_path="candidates.json")`

CLI entry point (`python -m scraper.scrape_biopharmguy [output_path]`,
defaulting `output_path` to `candidates.json`):

1. Fetch the hardcoded URL via `requests.get` (10s timeout, matching other
   fetchers).
2. Call `parse_companies` on the response HTML.
3. Write the resulting list as indented JSON to `output_path`.
4. Log a summary: `"Scraped %d companies from biopharmguy.com"`.

## Output Format

```json
[
  {"name": "10X Genomics", "website": "https://www.10xgenomics.com/"},
  {"name": "10x Science", "website": "https://10xscience.com/"}
]
```

This is directly consumable as the `candidates_path` argument to
`scraper/discover_companies.py`'s `main()`.

## Error Handling

- The page fetch itself is allowed to raise on failure — this is a one-shot
  manual script, not part of the resilient daily scrape pipeline
  (`scraper/run.py`).
- Per-row parse failures (missing/malformed company link) are logged as
  warnings and skipped, so one bad row doesn't abort the whole scrape.

## Testing

`tests/test_scrape_biopharmguy.py`:

- `parse_companies` tests using small HTML fixtures:
  - A normal `<tr class="even">`/`<tr class="odd">` row, verifying correct
    `name` (stripped) and `website` extraction.
  - A row whose `<td class="description">` contains its own embedded `<a>`
    tag, verifying that link is not mistaken for the company website.
  - A `<tr class="sponsor">` row, verifying it is skipped.
  - A row with a malformed `<td class="company">` (no matching `<a>` tag),
    verifying it is skipped with a warning rather than raising.
- `main()` test with mocked `requests.get` and `tmp_path`, asserting the
  written JSON file's contents and shape.

## Out of Scope

- Deduplication against `companies.json` — `scraper/discover_companies.py`
  already detects duplicate ATS tokens downstream, so re-listing an existing
  company here is harmless.
- Parameterizing the script for other biopharmguy directory pages (e.g.
  other regions) — this is hardcoded to the Northern California URL.
- Integration into `scraper/run.py` or the scheduled scrape workflow.
