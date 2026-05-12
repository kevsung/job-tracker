import hashlib
import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; job-tracker/1.0)",
    "Content-Type": "application/json",
}
_LIMIT = 20


def scrape_workday(tenant: str, board: str, wd_subdomain: str = "wd5") -> list[dict]:
    base = f"https://{tenant}.{wd_subdomain}.myworkdayjobs.com"
    api_url = f"{base}/wday/cxs/{tenant}/{board}/jobs"

    jobs = []
    offset = 0
    while True:
        resp = requests.post(
            api_url,
            headers=_HEADERS,
            json={"limit": _LIMIT, "offset": offset, "searchText": "", "appliedFacets": {}},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        postings = data.get("jobPostings", [])
        for job in postings:
            path = job.get("externalPath", "")
            uid = hashlib.md5(path.encode()).hexdigest()[:12]
            jobs.append(
                {
                    "id": f"workday_{tenant}_{uid}",
                    "title": job.get("title", ""),
                    "location": job.get("locationsText", ""),
                    "url": f"{base}{path}",
                }
            )
        if len(postings) < _LIMIT:
            break
        offset += _LIMIT
    return jobs
