import hashlib
import re
import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; job-tracker/1.0)",
    "Content-Type": "application/json",
}
_LIMIT = 20

# Some Workday tenants (e.g. Capital One) collapse multi-location postings'
# locationsText to a generic "N Locations" placeholder instead of naming
# cities. Workday's externalPath encodes the requisition's primary posting
# location as its first segment (e.g. "/job/McLean-VA/..."), so fall back
# to that when locationsText doesn't name a place.
_GENERIC_LOCATIONS_RE = re.compile(r"^\d+\s+locations?$", re.I)
_PATH_LOCATION_RE = re.compile(r"^/job/([^/]+)/")


def _location_from_path(path: str) -> str:
    match = _PATH_LOCATION_RE.match(path)
    if not match:
        return ""
    slug = match.group(1).replace("-", " ").strip()
    # "McLean VA" -> "McLean, VA" (last token is a 2-letter state code)
    parts = slug.rsplit(" ", 1)
    if len(parts) == 2 and len(parts[1]) == 2 and parts[1].isalpha():
        return f"{parts[0]}, {parts[1]}"
    return slug


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
            location = job.get("locationsText", "")
            if not location or _GENERIC_LOCATIONS_RE.match(location.strip()):
                location = _location_from_path(path) or location
            jobs.append(
                {
                    "id": f"workday_{tenant}_{uid}",
                    "title": job.get("title", ""),
                    "location": location,
                    "url": f"{base}/en-US/{board}{path}",
                    "posted_date": "",
                }
            )
        if len(postings) < _LIMIT:
            break
        offset += _LIMIT
    return jobs
