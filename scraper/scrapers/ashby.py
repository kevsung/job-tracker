import requests

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; job-tracker/1.0)"}
_BASE = "https://api.ashbyhq.com/posting-api/job-board/{slug}"


def scrape_ashby(slug: str) -> list[dict]:
    resp = requests.get(_BASE.format(slug=slug), headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # API v1 uses "jobs"; older boards used "jobPostings"
    raw = data.get("jobs") or data.get("jobPostings") or []
    jobs = []
    for job in raw:
        location = job.get("location", "") or job.get("locationName", "") or ""
        if job.get("workplaceType") == "Remote" and "remote" not in location.lower():
            location = f"Remote - {location}" if location else "Remote"
        jobs.append(
            {
                "id": f"ashby_{slug}_{job['id']}",
                "title": job.get("title", ""),
                "location": location,
                "url": job.get("jobUrl", ""),
                "posted_date": (job.get("publishedAt") or "")[:10],
            }
        )
    return jobs
