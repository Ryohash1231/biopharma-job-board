# Bay Area Biopharma Job Board

Aggregates open positions from Bay Area biopharma companies' career pages
into one searchable page.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-api-key-here
```

## Running the scraper

```bash
python -m scraper.run
```

This reads `companies.json` and writes `jobs.json`.

## Running the frontend locally

```bash
python -m http.server 8000
```

Then open http://localhost:8000/

## Running tests

```bash
pytest
```
