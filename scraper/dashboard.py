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
    },
    {
        "name": "Cape",
        "tier": "Strong",
        "url": "https://www.cape.co/careers",
    },
    {
        "name": "Nebius (location filter caveat)",
        "tier": "Strong",
        "url": "https://careers.nebius.com",
    },
    {
        "name": "Lonely Planet",
        "tier": "Moderate",
        "url": "https://www.redventures.com/careers/brands/lonely-planet",
    },
    {
        "name": "Indeed",
        "tier": "Moderate",
        "url": "https://indeed.com/cmp/indeed/jobs",
    },
    {
        "name": "Apex Systems",
        "tier": "Moderate",
        "url": "https://www.apexsystems.com/careers",
    },
    {
        "name": "SweetRush",
        "tier": "Moderate",
        "url": "https://www.sweetrush.com/careers",
    },
    {
        "name": "American Journalism Project",
        "tier": "Moderate",
        "url": "https://theajp.org/about/careers/",
    },
    {
        "name": "Fetch",
        "tier": "Moderate",
        "url": "https://jobs.gem.com/fetch",
    },
    {
        "name": "Akamai",
        "tier": "Moderate",
        "url": "https://jobs.akamai.com/en/sites/CX_1",
    },
    {
        "name": "Pearson",
        "tier": "Moderate",
        "url": "https://pearson.jobs/jobs/",
    },
    {
        "name": "Shutterfly",
        "tier": "Weak",
        "url": "https://shutterflycareers.ttcportals.com/search/jobs?q=&location=",
    },
    {
        "name": "Paylocity",
        "tier": "Fair",
        "url": "https://www.paylocity.com/company/careers/all-listings/",
    },
    {
        "name": "Function Health",
        "tier": "Moderate",
        "url": "https://jobs.gem.com/function-health",
    },
    {
        "name": "GC AI",
        "tier": "Strong",
        "url": "https://gc.ai/company/careers#openings",
    },
    {
        "name": "Deel (careers page changed)",
        "tier": "Strong",
        "url": "https://www.deel.com/careers/?location=united+states",
    },
    {
        "name": "Whatnot (Ashby board is JS-rendered)",
        "tier": "Moderate",
        "url": "https://jobs.ashbyhq.com/whatnot?workplaceType=Remote",
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
  <script>
    // Apply saved theme before first paint to avoid a flash of the wrong theme.
    if (localStorage.getItem("theme") === "dark" ||
        (!localStorage.getItem("theme") && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
      document.documentElement.classList.add("dark");
    }
    tailwind = { config: { darkMode: "class" } };
  </script>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 dark:bg-gray-900 font-sans min-h-screen transition-colors">


<div class="max-w-7xl mx-auto px-4 py-8">

  <!-- Header -->
  <div class="mb-6 flex items-start justify-between gap-4">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Job Tracker</h1>
      <p class="text-sm text-gray-400 dark:text-gray-500 mt-1">Scripts last run: __LAST_UPDATED__</p>
    </div>
    <div class="shrink-0 flex items-center gap-2">
      <button id="sync-toggle" type="button" title="Set up cross-device sync"
        class="w-9 h-9 flex items-center justify-center rounded-full bg-white dark:bg-gray-800
               text-gray-500 dark:text-gray-300 shadow-sm hover:shadow-md transition-shadow">
        <svg id="sync-icon-off" class="w-5 h-5 hidden" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        <svg id="sync-icon-on" class="w-5 h-5 hidden text-emerald-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"/>
        </svg>
      </button>
      <button id="theme-toggle" type="button" title="Toggle dark mode"
        class="w-9 h-9 flex items-center justify-center rounded-full bg-white dark:bg-gray-800
               text-gray-500 dark:text-gray-300 shadow-sm hover:shadow-md transition-shadow">
        <svg id="theme-icon-sun" class="w-5 h-5 hidden" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.36 6.36l-.7-.7M6.34 6.34l-.7-.7m12.02 0l-.7.7M6.34 17.66l-.7.7M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
        </svg>
        <svg id="theme-icon-moon" class="w-5 h-5 hidden" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
        </svg>
      </button>
    </div>
  </div>

  <!-- Filter bar -->
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-5 mb-6 flex flex-wrap gap-6 items-end transition-colors">

    <div>
      <p class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide mb-2">Tier</p>
      <div id="tier-filters" class="flex flex-wrap gap-2">
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none">
          <input type="checkbox" data-tier="Strong" checked
            class="w-4 h-4 accent-emerald-600"> <span class="text-sm dark:text-gray-200">Strong</span>
        </label>
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none">
          <input type="checkbox" data-tier="Moderate" checked
            class="w-4 h-4 accent-sky-600"> <span class="text-sm dark:text-gray-200">Moderate</span>
        </label>
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none">
          <input type="checkbox" data-tier="Fair" checked
            class="w-4 h-4 accent-orange-500"> <span class="text-sm dark:text-gray-200">Fair</span>
        </label>
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none">
          <input type="checkbox" data-tier="Weak" checked
            class="w-4 h-4 accent-amber-500"> <span class="text-sm dark:text-gray-200">Weak</span>
        </label>
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none">
          <input type="checkbox" data-tier="Weak with Caveats" checked
            class="w-4 h-4 accent-rose-500"> <span class="text-sm dark:text-gray-200">Weak w/ Caveats</span>
        </label>
      </div>
    </div>

    <div>
      <p class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide mb-2">Work type</p>
      <div class="flex gap-3">
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none text-sm dark:text-gray-200">
          <input type="radio" name="worktype" value="all" checked class="accent-indigo-600"> All
        </label>
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none text-sm dark:text-gray-200">
          <input type="radio" name="worktype" value="remote" class="accent-indigo-600"> Remote
        </label>
        <label class="inline-flex items-center gap-1.5 cursor-pointer select-none text-sm dark:text-gray-200">
          <input type="radio" name="worktype" value="onsite" class="accent-indigo-600"> On-site
        </label>
      </div>
    </div>

    <div class="flex-1 min-w-48">
      <p class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide mb-2">Company</p>
      <input id="co-search" type="text" placeholder="Filter by company…"
        class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100 rounded-lg px-3 py-1.5 text-sm
               focus:outline-none focus:ring-2 focus:ring-indigo-400">
    </div>

    <div class="self-end pb-0.5">
      <span id="job-count" class="text-sm text-gray-400 dark:text-gray-500"></span>
    </div>

  </div>

  <!-- Jobs table -->
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm overflow-x-auto transition-colors">
    <table class="w-full text-sm">
      <thead class="border-b dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-500 dark:text-gray-400">
        <tr>
          <th class="px-5 py-3 text-left font-semibold">Applied</th>
          <th class="px-5 py-3 text-left font-semibold cursor-pointer select-none"
              onclick="sort('company')">Company <span class="text-gray-300 dark:text-gray-600">&#8597;</span></th>
          <th class="px-5 py-3 text-left font-semibold">Tier</th>
          <th class="px-5 py-3 text-left font-semibold cursor-pointer select-none"
              onclick="sort('title')">Title <span class="text-gray-300 dark:text-gray-600">&#8597;</span></th>
          <th class="px-5 py-3 text-left font-semibold cursor-pointer select-none"
              onclick="sort('posted_date')">Posted Date <span class="text-gray-300 dark:text-gray-600">&#8597;</span></th>
          <th class="px-5 py-3 text-left font-semibold">Link</th>
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
    </table>
    <p id="empty-msg" class="hidden text-center text-gray-400 dark:text-gray-500 py-12">No matching jobs.</p>
  </div>

  <!-- Applied To Section -->
  <div class="mt-8">
    <details class="group" id="applied-details">
      <summary class="flex items-center gap-3 cursor-pointer select-none [list-style:none] [&::-webkit-details-marker]:hidden">
        <svg class="w-4 h-4 text-gray-400 dark:text-gray-500 transition-transform duration-150 group-open:rotate-90"
             fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd"
                d="M7.293 4.293a1 1 0 011.414 0l5 5a1 1 0 010 1.414l-5 5a1 1 0 01-1.414-1.414L11.586 10 7.293 5.707a1 1 0 010-1.414z"
                clip-rule="evenodd"/>
        </svg>
        <h2 class="text-lg font-semibold text-gray-700 dark:text-gray-200">Applied To</h2>
        <span id="applied-count" class="text-sm text-gray-400 dark:text-gray-500 font-normal"></span>
      </summary>
      <p class="mt-3 mb-1 text-sm text-gray-400 dark:text-gray-500 ml-7">
        Roles you've checked off as applied. Once a listing disappears from a scrape it becomes a
        permanent record here and can no longer be unchecked.
      </p>
      <p id="sync-status" class="mb-5 text-xs ml-7"></p>
      <div class="ml-7 bg-white dark:bg-gray-800 rounded-2xl shadow-sm overflow-x-auto transition-colors">
        <table class="w-full text-sm">
          <thead class="border-b dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-500 dark:text-gray-400">
            <tr>
              <th class="px-5 py-3 text-left font-semibold">Applied</th>
              <th class="px-5 py-3 text-left font-semibold">Company</th>
              <th class="px-5 py-3 text-left font-semibold">Title</th>
              <th class="px-5 py-3 text-left font-semibold">Applied Date</th>
              <th class="px-5 py-3 text-left font-semibold">Status</th>
              <th class="px-5 py-3 text-left font-semibold">Link</th>
            </tr>
          </thead>
          <tbody id="applied-tbody"></tbody>
        </table>
        <p id="applied-empty-msg" class="hidden text-center text-gray-400 dark:text-gray-500 py-12">No roles marked as applied yet.</p>
      </div>
    </details>
  </div>

  <!-- Manual Check Section -->
  <div class="mt-8">
    <hr class="border-gray-200 dark:border-gray-700 mb-8">
    <details class="group">
      <summary class="flex items-center gap-3 cursor-pointer select-none [list-style:none] [&::-webkit-details-marker]:hidden">
        <svg class="w-4 h-4 text-gray-400 dark:text-gray-500 transition-transform duration-150 group-open:rotate-90"
             fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd"
                d="M7.293 4.293a1 1 0 011.414 0l5 5a1 1 0 010 1.414l-5 5a1 1 0 01-1.414-1.414L11.586 10 7.293 5.707a1 1 0 010-1.414z"
                clip-rule="evenodd"/>
        </svg>
        <h2 class="text-lg font-semibold text-gray-700 dark:text-gray-200">Check Manually</h2>
        <span id="manual-count" class="text-sm text-gray-400 dark:text-gray-500 font-normal"></span>
      </summary>
      <p class="mt-3 mb-5 text-sm text-gray-400 dark:text-gray-500 ml-7">
        These companies couldn't be scraped automatically — check their careers pages directly.
      </p>
      <div id="manual-grid"
           class="ml-7 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"></div>
    </details>
  </div>

  <!-- Scrape Issues Section -->
  <div class="mt-8">
    <details class="group" id="issues-details">
      <summary class="flex items-center gap-3 cursor-pointer select-none [list-style:none] [&::-webkit-details-marker]:hidden">
        <svg class="w-4 h-4 text-gray-400 dark:text-gray-500 transition-transform duration-150 group-open:rotate-90"
             fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd"
                d="M7.293 4.293a1 1 0 011.414 0l5 5a1 1 0 010 1.414l-5 5a1 1 0 01-1.414-1.414L11.586 10 7.293 5.707a1 1 0 010-1.414z"
                clip-rule="evenodd"/>
        </svg>
        <h2 class="text-lg font-semibold text-gray-700 dark:text-gray-200">Needs Attention</h2>
        <span id="issues-count" class="text-sm text-gray-400 dark:text-gray-500 font-normal"></span>
      </summary>
      <p class="mt-3 mb-5 text-sm text-gray-400 dark:text-gray-500 ml-7">
        Companies that errored out or returned 0 results on the last scrape — the ATS URL, tenant, or
        title/location filters may need updating.
      </p>
      <div id="issues-grid"
           class="ml-7 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"></div>
    </details>
  </div>

</div>

<script>

const JOBS   = __JOBS_JSON__;
const MANUAL = __MANUAL_JSON__;
const ISSUES = __ISSUES_JSON__;
const LAST_UPDATED_DATE = "__LAST_UPDATED_DATE__";

// Applied-to state is persisted server-side in this repo (docs/applied.json) via the
// GitHub Contents API, so it stays in sync across every browser/device — only the
// write credential (a fine-grained personal access token) is kept per-browser.
const GH_REPO = "kevsung/job-tracker";
const GH_BRANCH = "main";
const GH_FILE_PATH = "docs/applied.json";
const GH_TOKEN_KEY = "jobTracker.ghToken";

const TIER_BADGE = {
  "Strong":            "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300",
  "Moderate":          "bg-sky-100 text-sky-800 dark:bg-sky-900/50 dark:text-sky-300",
  "Fair":              "bg-orange-100 text-orange-800 dark:bg-orange-900/50 dark:text-orange-300",
  "Weak":              "bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300",
  "Weak with Caveats": "bg-rose-100 text-rose-800 dark:bg-rose-900/50 dark:text-rose-300",
};

let sortKey = "posted_date", sortDir = 1;
let activeTiers = new Set(["Strong","Moderate","Fair","Weak","Weak with Caveats"]);
let worktype = "all";
let coSearch = "";

function esc(s){ return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function postedDate(j){ return j.posted_date || j.first_seen || ''; }
function isNew(j){ return j.first_seen === LAST_UPDATED_DATE; }

// ---------------------------------------------------------------------
// Theme toggle
// ---------------------------------------------------------------------
function updateThemeIcon(){
  const dark = document.documentElement.classList.contains("dark");
  document.getElementById("theme-icon-sun").classList.toggle("hidden", !dark);
  document.getElementById("theme-icon-moon").classList.toggle("hidden", dark);
}
document.getElementById("theme-toggle").addEventListener("click", ()=>{
  const dark = document.documentElement.classList.toggle("dark");
  localStorage.setItem("theme", dark ? "dark" : "light");
  updateThemeIcon();
});
updateThemeIcon();

// ---------------------------------------------------------------------
// Applied-to tracking — persisted server-side in docs/applied.json via
// the GitHub Contents API so desktop and mobile browsers stay in sync.
// ---------------------------------------------------------------------
function getToken(){ return localStorage.getItem(GH_TOKEN_KEY) || ""; }
function setToken(t){ t ? localStorage.setItem(GH_TOKEN_KEY, t) : localStorage.removeItem(GH_TOKEN_KEY); }

function setSyncStatus(msg, cls){
  const el = document.getElementById("sync-status");
  el.textContent = msg;
  el.className = "mb-5 text-xs ml-7 " + cls;
}
function updateSyncIcon(){
  const has = !!getToken();
  document.getElementById("sync-icon-on").classList.toggle("hidden", !has);
  document.getElementById("sync-icon-off").classList.toggle("hidden", has);
  document.getElementById("sync-toggle").title = has ? "Sync enabled — click to change/remove token" : "Set up cross-device sync";
}
document.getElementById("sync-toggle").addEventListener("click", ()=>{
  const current = getToken();
  const next = prompt([
    "Paste a GitHub fine-grained personal access token with 'Contents: Read and write' access to "+GH_REPO+".",
    "This is stored only in this browser's localStorage and used to save your applied-jobs list to the repo.",
    "",
    "Leave blank and submit to remove the saved token."
  ].join("\\n"), current);
  if(next === null) return; // cancelled
  setToken(next.trim());
  updateSyncIcon();
  setSyncStatus(getToken() ? "Sync token saved." : "Sync token removed — applied changes won't save.",
    getToken() ? "text-emerald-600 dark:text-emerald-400" : "text-gray-400 dark:text-gray-500");
});
updateSyncIcon();
setSyncStatus(getToken() ? "" : "Not syncing — click the sync icon (top right) to add a GitHub token for cross-device sync.",
  "text-amber-600 dark:text-amber-400");

let applied = {};
const jobsById = Object.fromEntries(JOBS.map(j=>[j.id, j]));

async function loadApplied(){
  try {
    const res = await fetch("applied.json?_=" + Date.now(), { cache: "no-store" });
    applied = res.ok ? await res.json() : {};
  } catch(e){
    applied = {};
    setSyncStatus("Couldn't load applied.json — showing an empty list.", "text-rose-500 dark:text-rose-400");
  }
  render();
  renderApplied();
}

// Writes the full `applied` object to docs/applied.json via the GitHub Contents API.
// Re-fetches the current sha immediately before writing to minimize (not eliminate)
// races between two devices editing at once; retries once on a sha conflict.
async function persistApplied(attempt){
  const token = getToken();
  if(!token){
    setSyncStatus("Not syncing — click the sync icon (top right) to add a GitHub token.",
      "text-amber-600 dark:text-amber-400");
    return false;
  }
  const api = `https://api.github.com/repos/${GH_REPO}/contents/${GH_FILE_PATH}`;
  const headers = { "Authorization": "Bearer " + token, "Accept": "application/vnd.github+json" };
  try {
    setSyncStatus("Saving…", "text-gray-400 dark:text-gray-500");
    const getRes = await fetch(`${api}?ref=${GH_BRANCH}&_=${Date.now()}`, { headers });
    if(!getRes.ok && getRes.status !== 404) throw new Error("GET failed: " + getRes.status);
    const sha = getRes.ok ? (await getRes.json()).sha : undefined;

    const content = btoa(unescape(encodeURIComponent(JSON.stringify(applied, null, 2))));
    const putRes = await fetch(api, {
      method: "PUT",
      headers: { ...headers, "Content-Type": "application/json" },
      body: JSON.stringify({
        message: "chore: update applied jobs",
        content, sha, branch: GH_BRANCH,
      }),
    });
    if(putRes.status === 409 && !attempt){
      return persistApplied(1); // sha conflict — retry once with a fresh sha
    }
    if(!putRes.ok) throw new Error("PUT failed: " + putRes.status);
    setSyncStatus("Synced ✓", "text-emerald-600 dark:text-emerald-400");
    return true;
  } catch(e){
    setSyncStatus("Sync failed (" + e.message + ") — check your token's permissions.",
      "text-rose-500 dark:text-rose-400");
    return false;
  }
}

async function markApplied(jobId, checkboxEl){
  const job = jobsById[jobId];
  if(!job) return;
  const prev = { ...applied };
  applied[jobId] = { job, appliedDate: new Date().toISOString().slice(0,10) };
  render();
  renderApplied();
  if(checkboxEl) checkboxEl.disabled = true;
  const ok = await persistApplied();
  if(!ok){ applied = prev; render(); renderApplied(); }
}
async function unmarkApplied(jobId, checkboxEl){
  // Only allow undo while the job is still live in the current scrape.
  if(!jobsById[jobId]) return;
  const prev = { ...applied };
  delete applied[jobId];
  render();
  renderApplied();
  if(checkboxEl) checkboxEl.disabled = true;
  const ok = await persistApplied();
  if(!ok){ applied = prev; render(); renderApplied(); }
}

// ---------------------------------------------------------------------
// Main jobs table
// ---------------------------------------------------------------------
function filtered(){
  return JOBS.filter(j=>{
    if(applied[j.id]) return false; // moved to Applied To section
    if(!activeTiers.has(j.tier)) return false;
    if(worktype==="remote" && !j.remote) return false;
    if(worktype==="onsite" && j.remote) return false;
    if(coSearch && !j.company.toLowerCase().includes(coSearch)) return false;
    return true;
  }).sort((a,b)=>{
    const av=sortKey==="posted_date"?postedDate(a):(a[sortKey]??"");
    const bv=sortKey==="posted_date"?postedDate(b):(b[sortKey]??"");
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
      ? "bg-amber-50 dark:bg-amber-950/40 hover:bg-amber-100 dark:hover:bg-amber-900/40"
      : (i%2===0?"bg-white dark:bg-gray-800":"bg-gray-50 dark:bg-gray-800/60")+" hover:bg-indigo-50 dark:hover:bg-indigo-950/40";
    const newBadge = isNew(j)
      ? '<span class="ml-2 inline-flex items-center px-1.5 py-0.5 rounded text-xs font-bold bg-amber-200 text-amber-800 dark:bg-amber-800 dark:text-amber-200">New</span>'
      : '';
    return `
    <tr class="${rowCls} transition-colors">
      <td class="px-5 py-3">
        <input type="checkbox" class="w-4 h-4 accent-emerald-600 cursor-pointer"
          title="Mark as applied" onchange="markApplied('${esc(j.id)}', this)">
      </td>
      <td class="px-5 py-3 font-medium text-gray-900 dark:text-gray-100">${esc(j.company)}${newBadge}</td>
      <td class="px-5 py-3">
        <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold ${TIER_BADGE[j.tier]||'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'}">${esc(j.tier)}</span>
      </td>
      <td class="px-5 py-3 text-gray-800 dark:text-gray-200">${esc(j.title)}</td>
      <td class="px-5 py-3 text-gray-400 dark:text-gray-500">${esc(postedDate(j))}</td>
      <td class="px-5 py-3">
        <a href="${esc(j.url)}" target="_blank" rel="noopener noreferrer"
           class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 hover:underline font-medium">Apply &#8599;</a>
      </td>
    </tr>`;
  }).join("");
}

// ---------------------------------------------------------------------
// Applied To table
// ---------------------------------------------------------------------
function renderApplied(){
  const entries = Object.entries(applied).sort((a,b)=> b[1].appliedDate.localeCompare(a[1].appliedDate));
  document.getElementById("applied-count").textContent = "("+entries.length+")";
  const empty = document.getElementById("applied-empty-msg");
  const tbody = document.getElementById("applied-tbody");
  if(!entries.length){ empty.classList.remove("hidden"); tbody.innerHTML=""; return; }
  empty.classList.add("hidden");
  tbody.innerHTML = entries.map(([jobId, entry], i)=>{
    const j = entry.job;
    const stillListed = !!jobsById[jobId];
    const rowCls = (i%2===0?"bg-white dark:bg-gray-800":"bg-gray-50 dark:bg-gray-800/60");
    const checkbox = stillListed
      ? `<input type="checkbox" checked class="w-4 h-4 accent-emerald-600 cursor-pointer"
           title="Undo applied" onchange="unmarkApplied('${esc(jobId)}', this)">`
      : `<input type="checkbox" checked disabled title="No longer listed — permanent record"
           class="w-4 h-4 accent-emerald-600 opacity-60 cursor-not-allowed">`;
    const status = stillListed
      ? '<span class="text-xs text-emerald-600 dark:text-emerald-400">Still listed</span>'
      : '<span class="text-xs text-gray-400 dark:text-gray-500">No longer listed</span>';
    return `
    <tr class="${rowCls} transition-colors">
      <td class="px-5 py-3">${checkbox}</td>
      <td class="px-5 py-3 font-medium text-gray-900 dark:text-gray-100">${esc(j.company)}</td>
      <td class="px-5 py-3 text-gray-800 dark:text-gray-200">${esc(j.title)}</td>
      <td class="px-5 py-3 text-gray-400 dark:text-gray-500">${esc(entry.appliedDate)}</td>
      <td class="px-5 py-3">${status}</td>
      <td class="px-5 py-3">
        <a href="${esc(j.url)}" target="_blank" rel="noopener noreferrer"
           class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 hover:underline font-medium">View &#8599;</a>
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

loadApplied();

// Manual check section
document.getElementById("manual-count").textContent = "("+MANUAL.length+")";
document.getElementById("manual-grid").innerHTML = MANUAL.map(m=>`
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-4 flex flex-col gap-2 hover:shadow-md transition-shadow">
    <div class="flex items-start justify-between gap-2">
      <a href="${esc(m.url)}" target="_blank" rel="noopener noreferrer"
         class="font-semibold text-gray-900 dark:text-gray-100 hover:text-indigo-600 dark:hover:text-indigo-400 hover:underline leading-snug">${esc(m.name)}</a>
      <span class="shrink-0 px-2.5 py-0.5 rounded-full text-xs font-semibold ${TIER_BADGE[m.tier]||'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'}">${esc(m.tier)}</span>
    </div>
  </div>`).join("");

// Scrape issues section
document.getElementById("issues-count").textContent = "("+ISSUES.length+")";
document.getElementById("issues-grid").innerHTML = ISSUES.length ? ISSUES.map(m=>`
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-4 flex flex-col gap-2 hover:shadow-md transition-shadow">
    <div class="flex items-start justify-between gap-2">
      <a href="${esc(m.url)}" target="_blank" rel="noopener noreferrer"
         class="font-semibold text-gray-900 dark:text-gray-100 hover:text-indigo-600 dark:hover:text-indigo-400 hover:underline leading-snug">${esc(m.company)}</a>
      <span class="shrink-0 px-2.5 py-0.5 rounded-full text-xs font-semibold ${TIER_BADGE[m.tier]||'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'}">${esc(m.tier)}</span>
    </div>
    <p class="text-xs text-rose-500 dark:text-rose-400">${esc(m.reason)}</p>
  </div>`).join("") : `<p class="text-sm text-gray-400 dark:text-gray-500">No issues on the last scrape.</p>`;
</script>
</body>
</html>"""


_TIER_ORDER = {"Strong": 0, "Moderate": 1, "Fair": 2, "Weak": 3}


def render_dashboard(jobs: list[dict], output_path: Path, issues: list[dict] | None = None) -> None:
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo("America/New_York"))
    tz_label = "EDT" if now.dst() else "EST"
    last_updated = now.strftime(f"%Y-%m-%d %H:%M {tz_label}")
    last_updated_date = now.strftime("%Y-%m-%d")
    sorted_manual = sorted(MANUAL_COMPANIES, key=lambda m: _TIER_ORDER.get(m["tier"], 99))
    sorted_issues = sorted(issues or [], key=lambda m: _TIER_ORDER.get(m["tier"], 99))
    html = _TEMPLATE.replace("__JOBS_JSON__", json.dumps(jobs, ensure_ascii=False))
    html = html.replace("__MANUAL_JSON__", json.dumps(sorted_manual, ensure_ascii=False))
    html = html.replace("__ISSUES_JSON__", json.dumps(sorted_issues, ensure_ascii=False))
    html = html.replace("__LAST_UPDATED__", last_updated)
    html = html.replace("__LAST_UPDATED_DATE__", last_updated_date)
    output_path.write_text(html, encoding="utf-8")
