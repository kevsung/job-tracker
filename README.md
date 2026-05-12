# job-tracker

Automated job scraper that watches ~60 company careers pages daily, filters for PM/TPM roles, and publishes a filterable HTML dashboard via GitHub Pages.

## How it works

| Workflow | Schedule | Tiers |
|---|---|---|
| `scrape-daily.yml` | Every day at 8 AM EDT | Strong, Moderate |
| `scrape-triday.yml` | Every 3 days | Weak, Weak with Caveats |

Each run scrapes its companies, filters for [target titles](#target-titles) and [locations](#location-filter), and commits `docs/jobs.json` + `docs/index.html` back to the repo. GitHub Pages serves the dashboard.

## Setup

### 1. Enable GitHub Pages

In the repo → **Settings → Pages**, set source to **Deploy from a branch**, branch `main`, folder `/docs`.

### 2. Enable workflow write permissions

In the repo → **Settings → Actions → General**, set "Workflow permissions" to **Read and write**.

### 3. Run manually first

Trigger either workflow via **Actions → Run workflow** to populate the initial dashboard.

## Local usage

```bash
pip install -r requirements.txt

# Scrape all tiers
python -m scraper

# Scrape specific tiers only
python -m scraper --tiers Strong Moderate
python -m scraper --tiers Weak "Weak with Caveats"
```

Output is written to `docs/jobs.json` and `docs/index.html`.

## Updating company ATS configs

All companies are defined in `scraper/companies.py`. If a company returns a 404 on first run, the slug/tenant is wrong — check the actual careers URL:

- **Greenhouse:** `https://boards.greenhouse.io/<slug>`
- **Lever:** `https://jobs.lever.co/<slug>`
- **Ashby:** `https://jobs.ashbyhq.com/<slug>`
- **Workday:** the `tenant`, `board`, and `wd_subdomain` come from the careers URL, e.g. `https://<tenant>.<wd_subdomain>.myworkdayjobs.com/en-US/<board>`

## Target titles

- Senior / Sr. Program Manager (incl. Technical, Strategic)
- Staff Program Manager
- Senior / Sr. Project Manager
- Technical Program Manager
- Product Operations Manager
- Creative / Marketing Operations Manager

## Location filter

- Remote roles in the US (non-US remote excluded)
- On-site within ~25 miles of Bethesda, MD 20854 (DC metro)
