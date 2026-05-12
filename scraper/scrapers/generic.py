import hashlib
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; job-tracker/1.0)"}
_LOC_RE = re.compile(r"\b(remote|[A-Z][a-z]+(?:,\s*[A-Z]{2})?)\b")


def scrape_generic(url: str) -> list[dict]:
    resp = requests.get(url, headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    jobs = []
    seen = set()
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        if not text or len(text) < 5 or len(text) > 150:
            continue
        full_url = urljoin(url, a["href"])
        if full_url in seen or full_url == url:
            continue
        seen.add(full_url)

        parent_text = a.parent.get_text(separator=" ", strip=True) if a.parent else ""
        loc_match = _LOC_RE.search(parent_text)
        location = loc_match.group(1) if loc_match else ""

        uid = hashlib.md5(full_url.encode()).hexdigest()[:12]
        jobs.append(
            {
                "id": f"generic_{uid}",
                "title": text,
                "location": location,
                "url": full_url,
            }
        )
    return jobs
