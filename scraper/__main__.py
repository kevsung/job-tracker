import argparse
import json
import logging
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.companies import COMPANIES
from scraper.dashboard import render_dashboard
from scraper.filters import location_matches, title_matches
from scraper.scrapers.ashby import scrape_ashby
from scraper.scrapers.bamboohr import scrape_bamboohr
from scraper.scrapers.generic import scrape_generic
from scraper.scrapers.greenhouse import scrape_greenhouse
from scraper.scrapers.lever import scrape_lever
from scraper.scrapers.workday import scrape_workday

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

DOCS_DIR = Path(__file__).parent.parent / "docs"
JOBS_FILE = DOCS_DIR / "jobs.json"


def load_existing() -> dict[str, dict]:
    if JOBS_FILE.exists():
        data = json.loads(JOBS_FILE.read_text(encoding="utf-8"))
        return {j["id"]: j for j in data}
    return {}


def scrape_one(company: dict) -> list[dict]:
    ats = company["ats"]
    try:
        if ats == "greenhouse":
            raw = scrape_greenhouse(company["slug"])
        elif ats == "lever":
            raw = scrape_lever(company["slug"])
        elif ats == "workday":
            raw = scrape_workday(
                company["tenant"],
                company["board"],
                company.get("wd_subdomain", "wd5"),
            )
        elif ats == "ashby":
            raw = scrape_ashby(company["slug"])
        elif ats == "bamboohr":
            raw = scrape_bamboohr(company["slug"])
        elif ats == "generic":
            raw = scrape_generic(company["url"])
        else:
            log.warning("Unknown ATS '%s' for %s", ats, company["name"])
            return []
    except Exception as exc:
        log.error("  %s: %s", company["name"], exc)
        return []

    matched = [j for j in raw if title_matches(j["title"]) and location_matches(j["location"])]
    log.info("  %-30s  %d match(es) / %d total", company["name"], len(matched), len(raw))
    return matched


def run(tiers: list[str] | None = None) -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    today = date.today().isoformat()
    tiers_to_scrape = set(tiers) if tiers else set(COMPANIES.keys())

    existing = load_existing()
    new_data: dict[str, dict] = {}

    for tier, companies in COMPANIES.items():
        if tier not in tiers_to_scrape:
            for job_id, job in existing.items():
                if job.get("tier") == tier:
                    new_data[job_id] = job
            continue

        log.info("=== %s ===", tier)
        for company in companies:
            for job in scrape_one(company):
                job["company"] = company["name"]
                job["tier"] = tier
                job["remote"] = "remote" in job["location"].lower()
                job["first_seen"] = existing[job["id"]]["first_seen"] if job["id"] in existing else today
                new_data[job["id"]] = job
            time.sleep(0.5)

    scraped_existing_ids = {jid for jid, j in existing.items() if j.get("tier") in tiers_to_scrape}
    dropped = scraped_existing_ids - set(new_data.keys())
    if dropped:
        log.info("Dropped %d stale listing(s) no longer found in current scrape:", len(dropped))
        for jid in sorted(dropped):
            old = existing[jid]
            log.info("  - %s: %s", old.get("company", "?"), old.get("title", "?"))

    jobs_list = sorted(new_data.values(), key=lambda j: j["first_seen"], reverse=True)
    JOBS_FILE.write_text(json.dumps(jobs_list, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Saved %d jobs → %s", len(jobs_list), JOBS_FILE)

    render_dashboard(jobs_list, DOCS_DIR / "index.html")
    log.info("Dashboard rendered → %s", DOCS_DIR / "index.html")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape job listings")
    parser.add_argument(
        "--tiers",
        nargs="*",
        metavar="TIER",
        help='Tiers to scrape, e.g. --tiers Strong Moderate  (default: all)',
    )
    args = parser.parse_args()
    run(args.tiers)


if __name__ == "__main__":
    main()
