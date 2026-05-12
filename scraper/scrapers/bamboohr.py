import requests

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; job-tracker/1.0)", "Accept": "application/json"}
_LIST_URL = "https://{slug}.bamboohr.com/careers/list"
_JOB_URL  = "https://{slug}.bamboohr.com/careers/{id}"

# BambooHR locationType: 1 = office, 2 = hybrid, 3 = remote
_REMOTE_TYPE = {"3"}


def scrape_bamboohr(slug: str) -> list[dict]:
    resp = requests.get(_LIST_URL.format(slug=slug), headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    jobs = []
    for job in resp.json().get("result", []):
        loc = job.get("atsLocation") or {}
        parts = [loc.get("city"), loc.get("state") or loc.get("province"), loc.get("country")]
        location = ", ".join(p for p in parts if p)

        is_remote = str(job.get("locationType", "")) in _REMOTE_TYPE
        if is_remote and "remote" not in location.lower():
            location = f"Remote - {location}" if location else "Remote"

        jobs.append(
            {
                "id": f"bamboohr_{slug}_{job['id']}",
                "title": job.get("jobOpeningName", ""),
                "location": location,
                "url": _JOB_URL.format(slug=slug, id=job["id"]),
            }
        )
    return jobs
