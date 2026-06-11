# AdSense Readiness — Design

## Goal

Prepare the site for a future Google AdSense application by adding the
content and pages AdSense reviewers expect: a Privacy Policy, an About page,
and a blog/insights section with original written content. No ad code is
added in this work — that comes later, after AdSense approval.

## Navigation

Add a small nav bar to every page (existing and new):

```html
<nav>
  <a href="/">Home</a> |
  <a href="/blog/">Blog</a> |
  <a href="/about.html">About</a> |
  <a href="/privacy.html">Privacy</a>
</nav>
```

Shared styling for `nav` added to `style.css`. Pages inside `blog/` use
relative paths (`../`, `../style.css`) to reach the site root.

## File Structure

- `about.html` — About the project
- `privacy.html` — Privacy Policy
- `blog/index.html` — Blog/Insights listing page
- `blog/hiring-trends-2026.html` — Post 1
- `blog/reading-job-postings.html` — Post 2
- `blog/bay-area-biopharma-hubs.html` — Post 3
- `style.css` — extended with nav and article/blog styles
- `index.html` — gains the nav bar (no other changes)

## Privacy Policy (`privacy.html`)

Covers, in plain language:

- **Data collected today:** none directly — no accounts, forms, or
  analytics. Note that GitHub Pages (the host) may log standard request
  data (e.g., IP address, browser type) per GitHub's own privacy policy,
  linked from this page.
- **Third-party links:** job listings link to external company career
  sites and applicant tracking systems (e.g., Greenhouse, Lever), which
  have their own privacy practices.
- **Future advertising:** if/when this site enables advertising (e.g.,
  Google AdSense), third-party vendors including Google may use cookies to
  serve ads based on a user's prior visits to this or other sites. Links to
  Google's "How Google uses information from sites that use our services."
- **Contact:** link to the GitHub repository's Issues page for privacy
  questions.
- **Last updated:** date of publication.

## About Page (`about.html`)

Covers:

- What the site does: aggregates open positions from Bay Area biopharma
  companies' career pages into one searchable page.
- How it works: a daily automated scraper pulls listings from each
  company's Greenhouse or Lever job board API; for companies without a
  structured API, an AI-assisted extraction step reads the careers page
  directly.
- Which companies are tracked: brief mention that the company list is
  visible in the project's repository (`companies.json`), with a link.
- Update frequency: listings refresh once daily via an automated job.
- Contact: link to the GitHub repository's Issues page.

## Blog / Insights Section

`blog/index.html` lists all posts with title, one-sentence excerpt, and a
link to the full post. Each post is a standalone static HTML page
(~400-600 words of original written content, no scraped data), sharing the
site nav and stylesheet.

### Post 1: `blog/hiring-trends-2026.html` — "Hiring Trends in Bay Area Biopharma for 2026"

Overview of what's driving hiring in the region: growth in cell and gene
therapy, AI-driven drug discovery roles, and which functional areas
(R&D, clinical operations, manufacturing/CMC, regulatory) are seeing the
most openings.

### Post 2: `blog/reading-job-postings.html` — "How to Read a Biopharma Job Posting"

Explains common title conventions (Associate → Senior → Principal →
Director → VP), what Bay Area location variants mean (on-site, hybrid,
remote), and how to gauge a role's seniority and team context from the
posting itself.

### Post 3: `blog/bay-area-biopharma-hubs.html` — "Bay Area Biopharma Hubs: Where the Jobs Are"

Overview of the region's biopharma clusters — South San Francisco, the
Berkeley/Emeryville corridor, and the Peninsula/South Bay — and the kinds
of companies and roles concentrated in each.

## Out of Scope

- AdSense script, ad units, or any ad-related code — added later, after
  AdSense approval.
- Analytics (e.g., Google Analytics) — not part of this work; if added
  later, the Privacy Policy will need a corresponding update.
- Dynamic/CMS-driven blog — posts are static HTML files, matching the
  site's existing all-static architecture.
- Changes to the job board's data, scraper, or filtering functionality.
