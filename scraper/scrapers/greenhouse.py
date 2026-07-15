import requests

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; job-tracker/1.0)"}
_BASE = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"


def scrape_greenhouse(slug: str) -> list[dict]:
    resp = requests.get(_BASE.format(slug=slug), headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    return [
        {
            "id": f"greenhouse_{slug}_{job['id']}",
            "title": job.get("title", ""),
            "location": job.get("location", {}).get("name", ""),
            "url": job.get("absolute_url", ""),
            "posted_date": (job.get("first_published") or "")[:10],
        }
        for job in resp.json().get("jobs", [])
    ]
