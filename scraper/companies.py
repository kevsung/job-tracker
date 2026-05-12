# ATS slugs and tenant IDs are best-effort guesses and may need updating.
# Greenhouse: verify at https://boards.greenhouse.io/<slug>
# Lever:      verify at https://jobs.lever.co/<slug>
# Workday:    verify tenant/board/subdomain from the company's careers URL
# Ashby:      verify at https://jobs.ashbyhq.com/<slug>

COMPANIES: dict[str, list[dict]] = {
    "Strong": [
        {"name": "Databricks",  "ats": "greenhouse", "slug": "databricks"},
        {"name": "Wiz",         "ats": "greenhouse", "slug": "Wizinc"},
        {"name": "Samsara",     "ats": "greenhouse", "slug": "samsara"},
        {"name": "Stripe",      "ats": "greenhouse", "slug": "stripe"},
        {"name": "Ramp",        "ats": "ashby",      "slug": "ramp"},
        {"name": "Mercury",     "ats": "greenhouse", "slug": "mercury"},
        {"name": "Hightouch",   "ats": "greenhouse", "slug": "hightouch"},
        {"name": "1Password",   "ats": "ashby",      "slug": "1password"},
        {
            "name": "Genesys",
            "ats": "workday",
            "tenant": "genesys",
            "board": "Genesys",
            "wd_subdomain": "wd1",
        },
        {
            "name": "Adobe",
            "ats": "workday",
            "tenant": "adobe",
            "board": "external_experienced",
            "wd_subdomain": "wd5",
        },
    ],
    "Moderate": [
        {"name": "Dandy",       "ats": "ashby",      "slug": "dandy"},
        {"name": "Openly",      "ats": "greenhouse", "slug": "openly"},
        {"name": "Ashby",       "ats": "ashby",      "slug": "ashby"},
        {"name": "Benepass",    "ats": "ashby",      "slug": "benepass"},
        {"name": "PolyAI",      "ats": "greenhouse", "slug": "polyai"},
        {"name": "Hungryroot",  "ats": "greenhouse", "slug": "hungryroot"},
        {"name": "Attentive",   "ats": "greenhouse", "slug": "attentive"},
        {"name": "Pinterest",   "ats": "greenhouse", "slug": "pinterest"},
        {"name": "Instacart",   "ats": "greenhouse", "slug": "instacart"},
        {"name": "Discord",     "ats": "greenhouse", "slug": "discord"},
        {"name": "Acorns",      "ats": "ashby",      "slug": "acorns"},
        {"name": "Beehiiv",     "ats": "bamboohr",   "slug": "beehiiv"},
        {"name": "Whatnot",     "ats": "ashby",      "slug": "whatnot"},
        {"name": "Webflow",     "ats": "greenhouse", "slug": "webflow"},
        {"name": "Aha!",        "ats": "greenhouse", "slug": "aha"},
        {"name": "Pacvue",      "ats": "greenhouse", "slug": "pacvue"},
        {"name": "Halcyon",     "ats": "greenhouse", "slug": "halcyon"},
        {"name": "Kitman Labs", "ats": "lever",      "slug": "kitmanlabs"},
        {"name": "Viral Nation","ats": "greenhouse", "slug": "viralnation"},
        {"name": "Payscale",    "ats": "ashby",      "slug": "payscale"},
        {"name": "Duetto",      "ats": "greenhouse", "slug": "duettoresearch"},
        {"name": "DEPT",        "ats": "greenhouse", "slug": "dept"},
        {"name": "Motive",      "ats": "greenhouse", "slug": "gomotive"},
        {
            "name": "LiveRamp",
            "ats": "workday",
            "tenant": "liveramp",
            "board": "LiveRampCareers",
            "wd_subdomain": "wd5",
        },
        {
            "name": "Fractal",
            "ats": "workday",
            "tenant": "fractal",
            "board": "Careers",
            "wd_subdomain": "wd1",
        },
        {
            "name": "Cotiviti",
            "ats": "generic",
            "url": "https://careers-cotiviti.icims.com/jobs/intro",
        },
        {
            "name": "ICF Next",
            "ats": "generic",
            "url": "https://careers.icf.com/us/en/search-results",
        },
        {
            "name": "Infosys",
            "ats": "generic",
            "url": "https://digitalcareers.infosys.com/infosys/global-careers?location=USA",
        },
        {
            "name": "Revance",
            "ats": "generic",
            "url": "https://www.revance.com/careers/jobs#current-openings",
        },
        {
            "name": "Salted",
            "ats": "generic",
            "url": "https://www.salted.com/careers",
        },
    ],
    "Weak": [
        {"name": "Typeface",    "ats": "greenhouse", "slug": "typeface"},
        {"name": "Stitch Fix",  "ats": "greenhouse", "slug": "stitchfix"},
        {"name": "Replicant",   "ats": "ashby",      "slug": "replicant"},
        {"name": "Dropbox",     "ats": "greenhouse", "slug": "dropbox"},
        {"name": "SmartBug Media", "ats": "lever",   "slug": "SmartBugOperatingLLC"},
    ],
    "Weak with Caveats": [
        {"name": "Known",           "ats": "greenhouse", "slug": "known"},
        {
            "name": "Adly",
            "ats": "generic",
            "url": "https://adly.com/careers",
        },
    ],
}
