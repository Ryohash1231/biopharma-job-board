# AdSense Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Privacy Policy, About page, and a 3-post blog/insights section
with a shared nav bar, so the site has the content AdSense reviewers expect
before a future AdSense application.

**Architecture:** This is a static-content addition to an existing static
HTML/CSS/JS site (no backend, no build step). All new pages are plain HTML
files following the same structure as `index.html`, sharing `style.css`.
There is no automated test suite for HTML content (the existing `tests/`
directory only covers the Python scraper) — verification is manual, via a
local HTTP server, in the final task.

**Tech Stack:** Plain HTML, CSS. No new dependencies.

---

## Site Map (for reference)

```
/index.html          (existing, gains nav bar)
/about.html           (new)
/privacy.html         (new)
/style.css            (existing, gains nav/article/blog-list styles)
/blog/index.html      (new — post listing)
/blog/hiring-trends-2026.html       (new — post 1)
/blog/reading-job-postings.html     (new — post 2)
/blog/bay-area-biopharma-hubs.html  (new — post 3)
```

All root-level pages link to each other and to `blog/index.html` using
relative paths (`index.html`, `about.html`, `privacy.html`, `blog/index.html`).
All pages inside `blog/` link back out using `../` (e.g., `../index.html`,
`../style.css`) and link to each other / the blog index using bare filenames
(e.g., `index.html`, `hiring-trends-2026.html`).

This matters because the site is hosted as a GitHub Pages **project site**
at `https://ryohash1231.github.io/biopharma-job-board/` — absolute paths
starting with `/` would resolve to the wrong location.

---

### Task 1: Shared nav and content styles

**Files:**
- Modify: `style.css`

- [ ] **Step 1: Append nav, article, and blog-list styles to `style.css`**

Add this to the end of `style.css`:

```css
nav {
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

nav a {
  color: #0645ad;
  text-decoration: none;
}

nav a:hover {
  text-decoration: underline;
}

article h1 {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}

article .post-date {
  color: #666;
  font-size: 0.9rem;
  margin-top: 0;
}

article p {
  line-height: 1.6;
  margin-bottom: 1rem;
}

.post-list {
  list-style: none;
  padding: 0;
}

.post-list li {
  margin-bottom: 1.25rem;
}

.post-list h2 {
  font-size: 1.1rem;
  margin: 0 0 0.25rem 0;
}

.post-excerpt {
  color: #666;
  margin: 0;
}
```

- [ ] **Step 2: Commit**

```bash
git add style.css
git commit -m "style: add nav, article, and blog-list styles"
```

---

### Task 2: Add nav bar to the home page

**Files:**
- Modify: `index.html`

- [ ] **Step 1: Add the nav bar to `index.html`**

In `index.html`, insert a `<nav>` block immediately after the opening
`<body>` tag, before `<h1>Bay Area Biopharma Jobs</h1>`:

```html
<body>
  <nav>
    <a href="index.html">Home</a> |
    <a href="blog/index.html">Blog</a> |
    <a href="about.html">About</a> |
    <a href="privacy.html">Privacy</a>
  </nav>
  <h1>Bay Area Biopharma Jobs</h1>
```

- [ ] **Step 2: Verify the page still loads**

Run: `python -m http.server 8000` from the repo root, then load
`http://localhost:8000/` in a browser. Confirm the nav bar renders above the
heading and the job table still works as before. Stop the server
(Ctrl+C) when done.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add site nav bar to home page"
```

---

### Task 3: About page

**Files:**
- Create: `about.html`

- [ ] **Step 1: Create `about.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>About - Bay Area Biopharma Jobs</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <nav>
    <a href="index.html">Home</a> |
    <a href="blog/index.html">Blog</a> |
    <a href="about.html">About</a> |
    <a href="privacy.html">Privacy</a>
  </nav>
  <article>
    <h1>About This Site</h1>
    <p>
      Bay Area Biopharma Jobs aggregates open positions from Bay Area
      biopharmaceutical companies' career pages into a single, searchable
      page. Instead of checking a dozen different career sites, you can
      search and filter listings from all tracked companies in one place.
    </p>
    <h2>How it works</h2>
    <p>
      Once a day, an automated job pulls the current openings directly from
      each company's job board. Most companies publish their openings
      through a structured job board API (Greenhouse or Lever), which this
      site queries directly. For companies that don't expose a structured
      API, an AI-assisted step reads the company's careers page and extracts
      the current listings.
    </p>
    <p>
      The result is written to a single data file that powers the search
      table on the home page. Because this runs daily, listings here may lag
      a company's own careers page by up to a day, and a listing that's been
      filled or removed may briefly remain until the next refresh.
    </p>
    <h2>Which companies are tracked</h2>
    <p>
      The current list of tracked companies is maintained in this project's
      source repository, in a file called
      <code>companies.json</code>. New companies can be added there over
      time.
    </p>
    <h2>Questions or feedback</h2>
    <p>
      This project is open source. If you notice a problem with a listing,
      or have a suggestion, please open an issue on the
      <a href="https://github.com/Ryohash1231/biopharma-job-board/issues">project's GitHub Issues page</a>.
    </p>
  </article>
</body>
</html>
```

- [ ] **Step 2: Verify the page renders**

Run: `python -m http.server 8000` from the repo root, then load
`http://localhost:8000/about.html`. Confirm the page renders with the nav bar
and all links are clickable. Stop the server (Ctrl+C) when done.

- [ ] **Step 3: Commit**

```bash
git add about.html
git commit -m "feat: add About page"
```

---

### Task 4: Privacy Policy page

**Files:**
- Create: `privacy.html`

- [ ] **Step 1: Create `privacy.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Privacy Policy - Bay Area Biopharma Jobs</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <nav>
    <a href="index.html">Home</a> |
    <a href="blog/index.html">Blog</a> |
    <a href="about.html">About</a> |
    <a href="privacy.html">Privacy</a>
  </nav>
  <article>
    <h1>Privacy Policy</h1>
    <p class="post-date"><em>Last updated: June 10, 2026</em></p>

    <h2>Data this site collects</h2>
    <p>
      Bay Area Biopharma Jobs does not have user accounts, forms, or
      analytics, and does not directly collect or store any personal
      information about visitors.
    </p>
    <p>
      This site is hosted on GitHub Pages. GitHub, as the hosting provider,
      may automatically log standard request information (such as IP
      address and browser type) for security and operational purposes. See
      <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub's Privacy Statement</a>
      for details.
    </p>

    <h2>Links to other sites</h2>
    <p>
      Job listings on this site link out to external company career pages
      and applicant tracking systems (such as Greenhouse and Lever). Once
      you click through to one of these sites, that site's own privacy
      policy applies. This site has no control over, and is not responsible
      for, the privacy practices of those external sites.
    </p>

    <h2>Advertising</h2>
    <p>
      This site may display advertising in the future, including ads served
      through Google AdSense. If enabled, Google and its partners may use
      cookies to serve ads based on a user's visits to this and other
      websites. You can learn more about how Google uses information from
      sites that use its services at
      <a href="https://policies.google.com/technologies/partner-sites">How Google uses information from sites or apps that use our services</a>,
      and you can opt out of personalized advertising by visiting
      <a href="https://adssettings.google.com/">Google Ads Settings</a>.
    </p>

    <h2>Contact</h2>
    <p>
      If you have questions about this privacy policy, please open an issue
      on the
      <a href="https://github.com/Ryohash1231/biopharma-job-board/issues">project's GitHub Issues page</a>.
    </p>
  </article>
</body>
</html>
```

- [ ] **Step 2: Verify the page renders**

Run: `python -m http.server 8000` from the repo root, then load
`http://localhost:8000/privacy.html`. Confirm the page renders with the nav
bar and all links are clickable. Stop the server (Ctrl+C) when done.

- [ ] **Step 3: Commit**

```bash
git add privacy.html
git commit -m "feat: add Privacy Policy page"
```

---

### Task 5: Blog post 1 — Hiring Trends in Bay Area Biopharma for 2026

**Files:**
- Create: `blog/hiring-trends-2026.html`

- [ ] **Step 1: Create `blog/hiring-trends-2026.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hiring Trends in Bay Area Biopharma for 2026 - Bay Area Biopharma Jobs</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
  <nav>
    <a href="../index.html">Home</a> |
    <a href="index.html">Blog</a> |
    <a href="../about.html">About</a> |
    <a href="../privacy.html">Privacy</a>
  </nav>
  <article>
    <h1>Hiring Trends in Bay Area Biopharma for 2026</h1>
    <p class="post-date"><em>Published June 10, 2026</em></p>

    <p>
      Despite the ups and downs of biotech funding cycles, the Bay Area
      remains the largest concentration of biopharmaceutical employers in
      the country, and hiring here continues at a steady pace. A look at the
      listings on this site offers a snapshot of where companies are
      investing right now.
    </p>

    <h2>Cell and gene therapy keeps growing</h2>
    <p>
      As more cell and gene therapies move from clinical trials toward
      approval, companies in this space are building out process
      development and manufacturing teams. Roles in cell line engineering,
      analytical development, and CMC (chemistry, manufacturing, and
      controls) are appearing more often, especially at companies preparing
      for their first commercial launches.
    </p>

    <h2>AI-driven drug discovery is reshaping R&amp;D teams</h2>
    <p>
      Computational biology and machine learning roles are increasingly
      embedded directly within research and discovery teams, rather than
      siloed in separate data science groups. Postings for these roles often
      emphasize collaboration with bench scientists, signaling that
      companies want computational staff working closely with experimental
      teams rather than at arm's length.
    </p>

    <h2>Where the openings are concentrated</h2>
    <p>
      Across the companies tracked by this site, four functional areas
      consistently show up:
    </p>
    <p>
      <strong>Research &amp; Discovery</strong> — bench scientists, research
      associates, and computational biologists working on early-stage
      pipelines.
    </p>
    <p>
      <strong>Clinical Operations</strong> — as more programs reach
      mid-to-late stage trials, companies need clinical trial managers and
      directors to run multi-site studies.
    </p>
    <p>
      <strong>Manufacturing &amp; CMC</strong> — particularly at companies
      with a therapy nearing or at commercial scale.
    </p>
    <p>
      <strong>Regulatory Affairs</strong> — specialists who can navigate FDA
      submissions for novel modalities, where the regulatory playbook is
      still evolving.
    </p>

    <h2>Tips for job seekers</h2>
    <p>
      Because listings on this site refresh daily, it's worth checking back
      regularly rather than relying on a single visit. It's also worth
      casting a wide net across company sizes — large, established
      companies tend to have more structured hiring processes and broader
      teams, while smaller and earlier-stage companies often offer more
      cross-functional exposure and faster decision-making.
    </p>
  </article>
</body>
</html>
```

- [ ] **Step 2: Verify the page renders**

Run: `python -m http.server 8000` from the repo root, then load
`http://localhost:8000/blog/hiring-trends-2026.html`. Confirm the page
renders with the nav bar, the stylesheet is applied, and the "Home", "Blog",
"About", and "Privacy" links resolve correctly (Blog and Home will 404 until
Tasks 6-8 are done — that's expected at this point). Stop the server
(Ctrl+C) when done.

- [ ] **Step 3: Commit**

```bash
git add blog/hiring-trends-2026.html
git commit -m "feat: add blog post - Hiring Trends in Bay Area Biopharma for 2026"
```

---

### Task 6: Blog post 2 — How to Read a Biopharma Job Posting

**Files:**
- Create: `blog/reading-job-postings.html`

- [ ] **Step 1: Create `blog/reading-job-postings.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>How to Read a Biopharma Job Posting - Bay Area Biopharma Jobs</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
  <nav>
    <a href="../index.html">Home</a> |
    <a href="index.html">Blog</a> |
    <a href="../about.html">About</a> |
    <a href="../privacy.html">Privacy</a>
  </nav>
  <article>
    <h1>How to Read a Biopharma Job Posting</h1>
    <p class="post-date"><em>Published June 10, 2026</em></p>

    <p>
      If you're new to biopharma, or coming in from another industry, job
      titles and postings can be confusing. A few conventions show up
      consistently across companies, and understanding them can help you
      quickly figure out whether a role fits your experience level and
      interests.
    </p>

    <h2>The title ladder</h2>
    <p>
      Most biopharma companies use a fairly consistent career ladder, even
      if exact titles vary slightly:
    </p>
    <p>
      <strong>Associate / Research Associate</strong> — typically an
      entry-to-early-career lab or operational role, often requiring a
      bachelor's degree and little to no prior industry experience.
    </p>
    <p>
      <strong>Senior Associate / Scientist / Specialist</strong> — a few
      years of relevant experience, more independent ownership of projects
      or processes.
    </p>
    <p>
      <strong>Senior Scientist / Senior Specialist</strong> — significant
      individual expertise, often a graduate degree (MS or PhD) or
      equivalent industry experience.
    </p>
    <p>
      <strong>Principal</strong> — deep technical expertise, often
      cross-team scope, but typically still an individual-contributor role
      rather than people management.
    </p>
    <p>
      <strong>Director / Senior Director</strong> — manages a team or
      function, with broader strategic responsibility.
    </p>
    <p>
      <strong>VP and above</strong> — executive-level roles overseeing
      multiple teams or an entire function.
    </p>

    <h2>What "Bay Area" location actually means</h2>
    <p>
      Location fields can hide important details. "San Francisco Bay Area"
      might mean a specific office in South San Francisco, Berkeley, or
      Redwood City — or it might mean a hybrid arrangement where you're
      expected on-site only a few days a week. Some postings are fully
      remote with occasional travel to a Bay Area site for team meetings.
      When a posting's location is ambiguous, it's worth confirming the
      expected on-site schedule early in the application process, especially
      if you're considering relocating.
    </p>

    <h2>Reading between the lines</h2>
    <p>
      Postings often mention the specific therapeutic area, modality, or
      team a role sits within — for example, "Cell Therapy CMC team" or
      "Oncology Clinical Development." These details can tell you a lot
      about what background the hiring team is prioritizing, even when the
      job title itself is fairly generic. If a posting lists a long set of
      "nice to have" qualifications alongside a shorter "required"
      list, it's often worth applying even if you don't meet every
      preferred qualification.
    </p>

    <h2>Putting it together</h2>
    <p>
      When scanning listings, try matching the title level to your years of
      experience first, then read the location and team details to gauge
      fit. This two-step approach can help you quickly narrow a long list of
      openings down to the ones worth a closer look.
    </p>
  </article>
</body>
</html>
```

- [ ] **Step 2: Verify the page renders**

Run: `python -m http.server 8000` from the repo root, then load
`http://localhost:8000/blog/reading-job-postings.html`. Confirm the page
renders with the nav bar and stylesheet applied. Stop the server (Ctrl+C)
when done.

- [ ] **Step 3: Commit**

```bash
git add blog/reading-job-postings.html
git commit -m "feat: add blog post - How to Read a Biopharma Job Posting"
```

---

### Task 7: Blog post 3 — Bay Area Biopharma Hubs: Where the Jobs Are

**Files:**
- Create: `blog/bay-area-biopharma-hubs.html`

- [ ] **Step 1: Create `blog/bay-area-biopharma-hubs.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bay Area Biopharma Hubs: Where the Jobs Are - Bay Area Biopharma Jobs</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
  <nav>
    <a href="../index.html">Home</a> |
    <a href="index.html">Blog</a> |
    <a href="../about.html">About</a> |
    <a href="../privacy.html">Privacy</a>
  </nav>
  <article>
    <h1>Bay Area Biopharma Hubs: Where the Jobs Are</h1>
    <p class="post-date"><em>Published June 10, 2026</em></p>

    <p>
      "Bay Area biopharma" isn't really one place — it's a handful of
      distinct clusters, each with its own character. Knowing the
      differences can help you target your search and think about commute
      and lifestyle tradeoffs.
    </p>

    <h2>South San Francisco</h2>
    <p>
      Often called the birthplace of the biotech industry, South San
      Francisco is home to one of the densest concentrations of
      biopharmaceutical companies anywhere in the world, ranging from large,
      established companies with major manufacturing and clinical
      operations to mid-size and growth-stage companies. If you're looking
      for a company with a large local footprint and established
      infrastructure, South San Francisco postings are a good place to
      start.
    </p>

    <h2>Berkeley and Emeryville</h2>
    <p>
      Close to UC Berkeley and the broader East Bay research community, this
      corridor tends to have more academic spinouts and earlier-stage
      biotech companies. Teams here are often smaller, with research and
      discovery roles making up a larger share of openings, and
      cross-functional exposure tends to come earlier in your career than at
      larger companies.
    </p>

    <h2>Peninsula and South Bay</h2>
    <p>
      Cities like Redwood City, Menlo Park, and San Carlos host a mix of
      clinical- and commercial-stage companies, often with a platform
      technology at their core — a core scientific approach the company
      applies across multiple disease areas. Roles here span the full range
      from early research through commercial launch, depending on the
      company's stage.
    </p>

    <h2>Thinking about commute and hybrid work</h2>
    <p>
      Because these hubs are spread across the Bay Area, commute time can
      vary enormously depending on where you live. Many companies now offer
      hybrid schedules, but lab-based and manufacturing roles typically
      require more on-site time than office-based roles in clinical,
      regulatory, or commercial functions. When comparing similar roles at
      different companies, it's worth weighing the hub location alongside
      the role itself — a slightly less senior role close to home may be a
      better overall fit than a more senior role with a long commute.
    </p>
  </article>
</body>
</html>
```

- [ ] **Step 2: Verify the page renders**

Run: `python -m http.server 8000` from the repo root, then load
`http://localhost:8000/blog/bay-area-biopharma-hubs.html`. Confirm the page
renders with the nav bar and stylesheet applied. Stop the server (Ctrl+C)
when done.

- [ ] **Step 3: Commit**

```bash
git add blog/bay-area-biopharma-hubs.html
git commit -m "feat: add blog post - Bay Area Biopharma Hubs: Where the Jobs Are"
```

---

### Task 8: Blog index page

**Files:**
- Create: `blog/index.html`

- [ ] **Step 1: Create `blog/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blog - Bay Area Biopharma Jobs</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
  <nav>
    <a href="../index.html">Home</a> |
    <a href="index.html">Blog</a> |
    <a href="../about.html">About</a> |
    <a href="../privacy.html">Privacy</a>
  </nav>
  <h1>Blog &amp; Insights</h1>
  <ul class="post-list">
    <li>
      <h2><a href="hiring-trends-2026.html">Hiring Trends in Bay Area Biopharma for 2026</a></h2>
      <p class="post-excerpt">
        What's driving hiring across cell and gene therapy, AI-driven drug
        discovery, and which functional areas have the most openings right
        now.
      </p>
    </li>
    <li>
      <h2><a href="reading-job-postings.html">How to Read a Biopharma Job Posting</a></h2>
      <p class="post-excerpt">
        A guide to title ladders, what "Bay Area" location really means, and
        how to read between the lines of a posting.
      </p>
    </li>
    <li>
      <h2><a href="bay-area-biopharma-hubs.html">Bay Area Biopharma Hubs: Where the Jobs Are</a></h2>
      <p class="post-excerpt">
        A tour of South San Francisco, Berkeley/Emeryville, and the
        Peninsula/South Bay — and the kinds of companies and roles
        concentrated in each.
      </p>
    </li>
  </ul>
</body>
</html>
```

- [ ] **Step 2: Verify the page renders**

Run: `python -m http.server 8000` from the repo root, then load
`http://localhost:8000/blog/index.html`. Confirm all three post links work
and lead to the correct posts, and that the nav bar's "Home", "About", and
"Privacy" links work correctly. Stop the server (Ctrl+C) when done.

- [ ] **Step 3: Commit**

```bash
git add blog/index.html
git commit -m "feat: add blog index page"
```

---

### Task 9: Full-site manual verification

**Files:** None (verification only)

- [ ] **Step 1: Start a local server**

Run: `python -m http.server 8000` from the repo root.

- [ ] **Step 2: Walk every page and every nav link**

Using a browser, visit each of the following and confirm: the nav bar
appears, the stylesheet is applied (fonts/spacing match the home page), and
all four nav links (Home, Blog, About, Privacy) resolve to the correct page
without 404s:

- `http://localhost:8000/index.html`
- `http://localhost:8000/about.html`
- `http://localhost:8000/privacy.html`
- `http://localhost:8000/blog/index.html`
- `http://localhost:8000/blog/hiring-trends-2026.html`
- `http://localhost:8000/blog/reading-job-postings.html`
- `http://localhost:8000/blog/bay-area-biopharma-hubs.html`

Pay particular attention to the blog pages' nav links (they use `../`
prefixes for Home/About/Privacy and a bare `index.html` for Blog) — these
are the most likely place for a broken relative path.

- [ ] **Step 3: Confirm the home page job board still works**

On `http://localhost:8000/index.html`, confirm the search box and job table
still function as before (this change should not have touched
`app.js` or the table itself).

- [ ] **Step 4: Stop the server**

Stop the local server (Ctrl+C).

---

## Out of Scope (do not implement)

- AdSense script, ad units, or any ad-related code.
- Analytics (e.g., Google Analytics).
- Any changes to `app.js`, `jobs.json`, `companies.json`, or the Python
  scraper.
- A CMS or dynamic blog system — posts are static HTML files.
