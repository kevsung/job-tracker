import json
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Companies that can't be scraped automatically.
# Add new entries here — the dashboard renders this list directly.
# ---------------------------------------------------------------------------
MANUAL_COMPANIES = [
    {
        "name": "GitHub (Microsoft)",
        "tier": "Strong",
        "url": "https://www.github.careers/careers-home/jobs",
        "reason": "iCIMS — JS-rendered, no public API",
    },
    {
        "name": "Cape",
        "tier": "Strong",
        "url": "https://www.cape.co/careers",
        "reason": "Greenhouse board inactive",
    },
    {
        "name": "Nebius (location filter caveat)",
        "tier": "Strong",
        "url": "https://careers.nebius.com",
        "reason": "Some roles tagged 'United States' instead of 'Remote - United States' -- check board directly for roles that may not surface in scraper results",
    },
    {
        "name": "Lonely Planet",
        "tier": "Moderate",
        "url": "https://www.redventures.com/careers/brands/lonely-planet",
        "reason": "Greenhouse board inactive — now on Red Ventures site",
    },
    {
        "name": "Indeed",
        "tier": "Moderate",
        "url": "https://indeed.com/cmp/indeed/jobs",
        "reason": "Custom ATS — removed per user preference",
    },
    {
        "name": "Apex Systems",
        "tier": "Moderate",
        "url": "https://www.apexsystems.com/careers",
        "reason": "Custom ATS — no structured job links in HTML",
    },
    {
        "name": "SweetRush",
        "tier": "Moderate",
        "url": "https://www.sweetrush.com/careers",
        "reason": "Custom ATS — no structured job links in HTML",
    },
    {
        "name": "American Journalism Project",
        "tier": "Moderate",
        "url": "https://theajp.org/about/careers/",
        "reason": "Greenhouse board inactive",
    },
    {
        "name": "Fetch",
        "tier": "Moderate",
        "url": "https://jobs.gem.com/fetch",
        "reason": "Gem CRM — no public API",
    },
    {
        "name": "Akamai",
        "tier": "Moderate",
        "url": "https://jobs.akamai.com/en/sites/CX_1",
        "reason": "iCIMS — JS-rendered, no public API",
    },
    {
        "name": "Pearson",
        "tier": "Moderate",
        "url": "https://pearson.jobs/jobs/",
        "reason": "No structured job links in rendered HTML",
    },
    {
        "name": "Shutterfly",
        "tier": "Weak",
        "url": "https://shutterflycareers.ttcportals.com/search/jobs?q=&location=",
        "reason": "TTC portal blocks automated scraping",
    },
    {
        "name": "Black & Black Creative",
        "tier": "Weak — Caveat Driven",
        "url": "https://blackandblackcreative.com/careers",
        "reason": "Careers URL dead",
    },
    {
        "name": "Hovercraft Studio",
        "tier": "Weak — Caveat Driven",
        "url": "https://hovercraftstudio.com/careers",
        "reason": "Careers URL dead",
    },
    {
        "name": "Tellos Creative",
        "tier": "Weak — Caveat Driven",
        "url": "https://telloscreative.com/careers",
        "reason": "Careers URL dead",
    },
    {
        "name": "Space Dinosaurs",
        "tier": "Weak — Caveat Driven",
        "url": "https://spacedinosaursstudio.com",
        "reason": "Domain does not resolve",
    },
    {
        "name": "Pixalate",
        "tier": "Weak — Caveat Driven",
        "url": "https://pixalate.applytojob.com/apply",
        "reason": "ApplyToJob ATS — no API",
    },
    {
        "name": "That's No Moon",
        "tier": "Weak — Caveat Driven",
        "url": "https://job-boards.greenhouse.io/thatsnomoonentertainment",
        "reason": "Greenhouse board exists but niche studio — check manually",
    },
    {
        "name": "Baylor Genetics",
        "tier": "Weak — Caveat Driven",
        "url": "https://recruiting2.ultipro.com/BAY1006BML/JobBoard/0669eed3-5441-4f8e-a7b1-c5df596a4dfe/?q=&o=postedDateDesc",
        "reason": "UltiPro ATS — no standard API",
    },
    {
        "name": "Paylocity",
        "tier": "Fair",
        "url": "https://www.paylocity.com/company/careers/all-listings/",
        "reason": "Paylocity ATS — GUID-based API but board returns no listings",
    },
]

# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------
_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Job Tracker</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 font-sans min-h-screen">


<div class="max-w-7xl mx-auto px-4 py-8">

  <!-- Header -->
  <div class="mb-6">
    <h1 class="text-2xl font-bold text-gray-900">Job Tracker</h1>
    <p class="text-sm text-gray-400 mt-1">Scripts last run: __LAST_UPDATED__</p>
  </div>

  <!-- Filter bar -->
  <div class="bg-white rounded-2xl shadow-sm p-5 mb-6 flex flex-wrap gap-6 items-end">

    <div>
      <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Tier</p>
      <div id="tier-filters" class="flex flex-wrap gap-2">
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none">
          <input type="checkbox" data-tier="Strong" checked
            class="w-4 h-4 accent-emerald-600"> <span class="text-sm">Strong</span>
        </label>
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none">
          <input type="checkbox" data-tier="Moderate" checked
            class="w-4 h-4 accent-sky-600"> <span class="text-sm">Moderate</span>
        </label>
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none">
          <input type="checkbox" data-tier="Fair" checked
            class="w-4 h-4 accent-orange-500"> <span class="text-sm">Fair</span>
        </label>
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none">
          <input type="checkbox" data-tier="Weak" checked
            class="w-4 h-4 accent-amber-500"> <span class="text-sm">Weak</span>
        </label>
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none">
          <input type="checkbox" data-tier="Weak with Caveats" checked
            class="w-4 h-4 accent-rose-500"> <span class="text-sm">Weak w/ Caveats</span>
        </label>
      </div>
    </div>

    <div>
      <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Work type</p>
      <div class="flex gap-3">
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none text-sm">
          <input type="radio" name="worktype" value="all" checked class="accent-indigo-600"> All
        </label>
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none text-sm">
          <input type="radio" name="worktype" value="remote" class="accent-indigo-600"> Remote
        </label>
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none text-sm">
          <input type="radio" name="worktype" value="onsite" class="accent-indigo-600"> On-site
        </label>
      </div>
    </div>

    <div class="flex-1 min-w-48">
      <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Company</p>
      <input id="co-search" type="text" placeholder="Filter by company…"
        class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm
               focus:outline-none focus:ring-2 focus:ring-indigo-400">
    </div>

    <div class="self-end pb-0.5">
      <span id="job-count" class="text-sm text-gray-400"></span>
    </div>

  </div>

  <!-- Jobs table -->
  <div class="bg-white rounded-2xl shadow-sm overflow-x-auto">
    <table class="w-full text-sm">
      <thead class="border-b bg-gray-50 text-gray-500">
        <tr>
          <th class="px-5 py-3 text-left font-semibold cursor-pointer select-none"
              onclick="sort('company')">Company <span class="text-gray-300">&#8597;</span></th>
          <th class="px-5 py-3 text-left font-semibold">Tier</th>
          <th class="px-5 py-3 text-left font-semibold cursor-pointer select-none"
              onclick="sort('title')">Title <span class="text-gray-300">&#8597;</span></th>
          <th class="px-5 py-3 text-left font-semibold">Location</th>
          <th class="px-5 py-3 text-left font-semibold">Remote</th>
          <th class="px-5 py-3 text-left font-semibold cursor-pointer select-none"
              onclick="sort('first_seen')">First Seen <span class="text-gray-300">&#8597;</span></th>
          <th class="px-5 py-3 text-left font-semibold">Link</th>
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
    </table>
    <p id="empty-msg" class="hidden text-center text-gray-400 py-12">No matching jobs.</p>
  </div>

  <!-- Manual Check Section -->
  <div class="mt-10">
    <hr class="border-gray-200 mb-8">
    <details class="group">
      <summary class="flex items-center gap-3 cursor-pointer select-none [list-style:none] [&::-webkit-details-marker]:hidden">
        <svg class="w-4 h-4 text-gray-400 transition-transform duration-150 group-open:rotate-90"
             fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd"
                d="M7.293 4.293a1 1 0 011.414 0l5 5a1 1 0 010 1.414l-5 5a1 1 0 01-1.414-1.414L11.586 10 7.293 5.707a1 1 0 010-1.414z"
                clip-rule="evenodd"/>
        </svg>
        <h2 class="text-lg font-semibold text-gray-700">Check Manually</h2>
        <span id="manual-count" class="text-sm text-gray-400 font-normal"></span>
      </summary>
      <p class="mt-3 mb-5 text-sm text-gray-400 ml-7">
        These companies couldn't be scraped automatically — check their careers pages directly.
      </p>
      <div id="manual-grid"
           class="ml-7 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"></div>
    </details>
  </div>

</div>

<script>

const JOBS   = __JOBS_JSON__;
const MANUAL = __MANUAL_JSON__;
const LAST_UPDATED_DATE = "__LAST_UPDATED_DATE__";

const TIER_BADGE = {
  "Strong":            "bg-emerald-100 text-emerald-800",
  "Moderate":          "bg-sky-100 text-sky-800",
  "Fair":              "bg-orange-100 text-orange-800",
  "Weak":              "bg-amber-100 text-amber-800",
  "Weak with Caveats": "bg-rose-100 text-rose-800",
};

let sortKey = "first_seen", sortDir = -1;
let activeTiers = new Set(["Strong","Moderate","Fair","Weak","Weak with Caveats"]);
let worktype = "all";
let coSearch = "";

function esc(s){ return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function isNew(j){ return j.first_seen === LAST_UPDATED_DATE; }

function filtered(){
  return JOBS.filter(j=>{
    if(!activeTiers.has(j.tier)) return false;
    if(worktype==="remote" && !j.remote) return false;
    if(worktype==="onsite" && j.remote) return false;
    if(coSearch && !j.company.toLowerCase().includes(coSearch)) return false;
    return true;
  }).sort((a,b)=>{
    const av=a[sortKey]??"", bv=b[sortKey]??"";
    return av<bv ? sortDir : av>bv ? -sortDir : 0;
  });
}

function render(){
  const jobs = filtered();
  document.getElementById("job-count").textContent = jobs.length+" job"+(jobs.length!==1?"s":"");
  const empty = document.getElementById("empty-msg");
  const tbody = document.getElementById("tbody");
  if(!jobs.length){ empty.classList.remove("hidden"); tbody.innerHTML=""; return; }
  empty.classList.add("hidden");
  tbody.innerHTML = jobs.map((j,i)=>{
    const rowCls = isNew(j)
      ? "bg-amber-50 hover:bg-amber-100"
      : (i%2===0?"bg-white":"bg-gray-50")+" hover:bg-indigo-50";
    const newBadge = isNew(j)
      ? '<span class="ml-2 inline-flex items-center px-1.5 py-0.5 rounded text-xs font-bold bg-amber-200 text-amber-800">New</span>'
      : '';
    return `
    <tr class="${rowCls} transition-colors">
      <td class="px-5 py-3 font-medium text-gray-900">${esc(j.company)}${newBadge}</td>
      <td class="px-5 py-3">
        <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold ${TIER_BADGE[j.tier]||'bg-gray-100 text-gray-700'}">${esc(j.tier)}</span>
      </td>
      <td class="px-5 py-3 text-gray-800">${esc(j.title)}</td>
      <td class="px-5 py-3 text-gray-500">${esc(j.location)}</td>
      <td class="px-5 py-3">${j.remote?'<span class="text-emerald-600 font-medium">Yes</span>':'<span class="text-gray-300">No</span>'}</td>
      <td class="px-5 py-3 text-gray-400">${esc(j.first_seen)}</td>
      <td class="px-5 py-3">
        <a href="${esc(j.url)}" target="_blank" rel="noopener noreferrer"
           class="text-indigo-600 hover:text-indigo-800 hover:underline font-medium">Apply &#8599;</a>
      </td>
    </tr>`;
  }).join("");
}

function sort(key){
  sortDir = sortKey===key ? -sortDir : 1;
  sortKey = key;
  render();
}

document.querySelectorAll("[data-tier]").forEach(cb=>{
  cb.addEventListener("change", e=>{
    e.target.checked ? activeTiers.add(e.target.dataset.tier) : activeTiers.delete(e.target.dataset.tier);
    render();
  });
});
document.querySelectorAll("input[name=worktype]").forEach(r=>{
  r.addEventListener("change", e=>{ worktype=e.target.value; render(); });
});
document.getElementById("co-search").addEventListener("input", e=>{
  coSearch=e.target.value.toLowerCase(); render();
});

render();

// Manual check section
document.getElementById("manual-count").textContent = "("+MANUAL.length+")";
document.getElementById("manual-grid").innerHTML = MANUAL.map(m=>`
  <div class="bg-white rounded-2xl shadow-sm p-4 flex flex-col gap-2 hover:shadow-md transition-shadow">
    <div class="flex items-start justify-between gap-2">
      <a href="${esc(m.url)}" target="_blank" rel="noopener noreferrer"
         class="font-semibold text-gray-900 hover:text-indigo-600 hover:underline leading-snug">${esc(m.name)}</a>
      <span class="shrink-0 px-2.5 py-0.5 rounded-full text-xs font-semibold ${TIER_BADGE[m.tier]||'bg-gray-100 text-gray-700'}">${esc(m.tier)}</span>
    </div>
    <p class="text-xs text-gray-400">${esc(m.reason)}</p>
  </div>`).join("");
</script>
</body>
</html>"""


def render_dashboard(jobs: list[dict], output_path: Path) -> None:
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo("America/New_York"))
    tz_label = "EDT" if now.dst() else "EST"
    last_updated = now.strftime(f"%Y-%m-%d %H:%M {tz_label}")
    last_updated_date = now.strftime("%Y-%m-%d")
    html = _TEMPLATE.replace("__JOBS_JSON__", json.dumps(jobs, ensure_ascii=False))
    html = html.replace("__MANUAL_JSON__", json.dumps(MANUAL_COMPANIES, ensure_ascii=False))
    html = html.replace("__LAST_UPDATED__", last_updated)
    html = html.replace("__LAST_UPDATED_DATE__", last_updated_date)
    output_path.write_text(html, encoding="utf-8")
