import requests

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; job-tracker/1.0)"}
_BASE = "https://ats.rippling.com/api/v2/board/{board_id}/jobs"


def scrape_rippling(board_id: str) -> list[dict]:
    jobs = []
    page = 0
    page_size = 50
    while True:
        resp = requests.get(
            _BASE.format(board_id=board_id),
            params={"page": page, "pageSize": page_size},
            headers=_HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        if not items:
            break
        for job in items:
            locs = job.get("locations") or []
            location = locs[0].get("name", "") if locs else ""
            jobs.append(
                {
                    "id": f"rippling_{board_id}_{job['id']}",
                    "title": job.get("name", ""),
                    "location": location,
                    "url": job.get("url", ""),
                }
            )
        total_pages = data.get("totalPages", 1)
        if page + 1 >= total_pages:
            break
        page += 1
    return jobs
