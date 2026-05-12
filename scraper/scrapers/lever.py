import requests

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; job-tracker/1.0)"}
_BASE = "https://api.lever.co/v0/postings/{slug}?mode=json"


def scrape_lever(slug: str) -> list[dict]:
    resp = requests.get(_BASE.format(slug=slug), headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    jobs = []
    for job in resp.json():
        cats = job.get("categories", {})
        location = cats.get("location", "") or ""
        if not location and "allLocations" in cats:
            location = ", ".join(cats["allLocations"])
        jobs.append(
            {
                "id": f"lever_{slug}_{job['id']}",
                "title": job.get("text", ""),
                "location": location,
                "url": job.get("hostedUrl", ""),
            }
        )
    return jobs
