import requests

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; job-tracker/1.0)"}
_BASE = "https://api.ashbyhq.com/posting-api/job-board/{slug}"


def scrape_ashby(slug: str) -> list[dict]:
    resp = requests.get(_BASE.format(slug=slug), headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    jobs = []
    for job in resp.json().get("jobPostings", []):
        location = job.get("locationName", "") or job.get("location", "") or ""
        if job.get("isRemote") and "remote" not in location.lower():
            location = f"Remote - {location}" if location else "Remote"
        jobs.append(
            {
                "id": f"ashby_{slug}_{job['id']}",
                "title": job.get("title", ""),
                "location": location,
                "url": job.get("jobUrl", ""),
            }
        )
    return jobs
