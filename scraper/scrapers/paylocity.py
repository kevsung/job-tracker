import requests

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; job-tracker/1.0)"}
_BASE = "https://recruiting.paylocity.com/recruiting/v2/api/feed/jobs/{guid}"


def scrape_paylocity(guid: str) -> list[dict]:
    resp = requests.get(_BASE.format(guid=guid), headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    jobs = []
    for job in data.get("jobs", []):
        jobs.append(
            {
                "id": f"paylocity_{guid}_{job['jobId']}",
                "title": job.get("title", ""),
                "location": job.get("jobLocation", ""),
                "url": job.get("applyUrl", ""),
            }
        )
    return jobs
