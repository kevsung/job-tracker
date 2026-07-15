import requests

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; job-tracker/1.0)"}
_BASE = "https://api.smartrecruiters.com/v1/companies/{company_id}/postings"


def scrape_smartrecruiters(company_id: str) -> list[dict]:
    jobs = []
    offset = 0
    limit = 100
    while True:
        resp = requests.get(
            _BASE.format(company_id=company_id),
            params={"limit": limit, "offset": offset},
            headers=_HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data.get("content", [])
        for job in content:
            loc = job.get("location", {})
            parts = [loc.get("city"), loc.get("region"), loc.get("country")]
            location = ", ".join(p for p in parts if p)
            jobs.append(
                {
                    "id": f"smartrecruiters_{company_id}_{job['id']}",
                    "title": job.get("name", ""),
                    "location": location,
                    "url": f"https://jobs.smartrecruiters.com/{company_id}/{job['id']}",
                    "posted_date": (job.get("releasedDate") or "")[:10],
                }
            )
        if offset + len(content) >= data.get("totalFound", 0):
            break
        offset += limit
    return jobs
