import json
from datetime import datetime, timezone
from pathlib import Path

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
  <div class="flex items-center justify-between mb-6">
    <h1 class="text-2xl font-bold text-gray-900">Job Tracker</h1>
    <span class="text-sm text-gray-400">Last updated: __LAST_UPDATED__</span>
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

  <!-- Table -->
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

</div>

<script>
const JOBS = __JOBS_JSON__;

const TIER_BADGE = {
  "Strong":            "bg-emerald-100 text-emerald-800",
  "Moderate":          "bg-sky-100 text-sky-800",
  "Weak":              "bg-amber-100 text-amber-800",
  "Weak with Caveats": "bg-rose-100 text-rose-800",
};

let sortKey = "first_seen", sortDir = -1;
let activeTiers = new Set(["Strong","Moderate","Weak","Weak with Caveats"]);
let worktype = "all";
let coSearch = "";

function esc(s){ return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

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
  tbody.innerHTML = jobs.map((j,i)=>`
    <tr class="${i%2===0?"bg-white":"bg-gray-50"} hover:bg-indigo-50 transition-colors">
      <td class="px-5 py-3 font-medium text-gray-900">${esc(j.company)}</td>
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
    </tr>`).join("");
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
</script>
</body>
</html>"""


def render_dashboard(jobs: list[dict], output_path: Path) -> None:
    last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = _TEMPLATE.replace("__JOBS_JSON__", json.dumps(jobs, ensure_ascii=False))
    html = html.replace("__LAST_UPDATED__", last_updated)
    output_path.write_text(html, encoding="utf-8")
