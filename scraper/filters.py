import re

# ---------------------------------------------------------------------------
# Title matching
# ---------------------------------------------------------------------------

_TITLE_PATTERNS = [
    # Senior / Sr. Program Manager (including Technical / Strategic)
    re.compile(r"\b(sr\.?|senior)\s+(technical\s+|strategic\s+)?program\s+manager", re.I),
    re.compile(r"\bprogram\s+manager[,\s\-]+(sr\.?|senior)", re.I),
    # Staff Program Manager
    re.compile(r"\bstaff\s+program\s+manager", re.I),
    # Senior / Sr. Project Manager
    re.compile(r"\b(sr\.?|senior)\s+project\s+manager", re.I),
    re.compile(r"\bproject\s+manager[,\s\-]+(sr\.?|senior)", re.I),
    # Technical Program Manager (any seniority)
    re.compile(r"\btechnical\s+program\s+manager", re.I),
    # Product Operations Manager
    re.compile(r"\bproduct\s+operations\s+manager", re.I),
    # Creative / Marketing Operations Manager
    re.compile(r"\b(creative|marketing)\s+operations\s+manager", re.I),
    # Director of [Creative/Marketing/Product/Program] Operations
    re.compile(r"\bdirector\s+of\s+(creative|marketing|product|program)\s+operations", re.I),
    # Creative Production Lead / Manager / Director (any seniority)
    re.compile(r"\b(senior|sr\.?|staff|lead)?\s*creative\s+production\s+(lead|manager|director)", re.I),
    # Senior / Sr. / Staff / Lead Production Manager / Lead / Director
    re.compile(r"\b(senior|sr\.?|staff|lead)\s+production\s+(manager|lead|director)", re.I),
    # Lead Program Manager
    re.compile(r"\blead\s+program\s+manager", re.I),
    # Senior Manager, [something] Program/Project/PMO/Operations
    re.compile(r"\bsenior\s+manager[,\s]+.{0,30}(program|project|pmo|operations)", re.I),
    # Senior / Sr. / Staff / Lead Release Manager
    re.compile(r"\b(senior|sr\.?|staff|lead)\s+release\s+manager", re.I),
    # Portfolio [Governance/Program/Project] ... Manager (words may intervene)
    re.compile(r"\bportfolio\s+(governance|program|project).{0,40}manager", re.I),
    # Program/Project Management Office  OR  PMO Lead/Manager/Director
    re.compile(r"\b(program|project)\s+management\s+office\b", re.I),
    re.compile(r"\bpmo\s+(lead|manager|director)\b", re.I),
    # Head of [Product Operations / Program Management / Creative Operations]
    re.compile(r"\bhead\s+of\s+(product\s+operations|program\s+management|creative\s+operations)", re.I),
    # Senior / Sr. / Staff / Lead Manager, Program (suffix variant)
    re.compile(r"\b(senior|sr\.?|staff|lead)\s+manager[,\s]+program", re.I),
]


def title_matches(title: str) -> bool:
    return any(p.search(title) for p in _TITLE_PATTERNS)


# ---------------------------------------------------------------------------
# Location matching: remote US  OR  within ~25 miles of Bethesda MD 20854
# ---------------------------------------------------------------------------

_NON_US_RE = re.compile(
    r"\b(canada|canadian|uk|united kingdom|england|scotland|wales|"
    r"europe|eu\s+only|emea|australia|new zealand|india|"
    r"latam|latin america|apac|singapore|germany|france|"
    r"netherlands|brazil|mexico)\b",
    re.I,
)

# Cities / areas within ~25 miles of Bethesda, MD 20854
_DC_METRO_RE = re.compile(
    r"\b("
    # Montgomery County, MD
    r"bethesda|rockville|silver spring|chevy chase|kensington|"
    r"gaithersburg|germantown|potomac|olney|burtonsville|"
    # DC
    r"washington[,\s]+d\.?c\.?|district of columbia|"
    # Northern Virginia
    r"arlington|alexandria|falls church|mclean|tysons|"
    r"vienna|fairfax|reston|annandale|springfield|"
    # Prince George's County, MD
    r"college park|greenbelt|hyattsville|beltsville|"
    # Generic metro labels
    r"northern virginia|dmv|dc metro|dc area"
    r")\b",
    re.I,
)


def location_matches(location: str) -> bool:
    if not location:
        return False
    loc = location.strip()

    if re.search(r"\bremote\b", loc, re.I):
        # Accept unless location is explicitly non-US
        return not bool(_NON_US_RE.search(loc))

    return bool(_DC_METRO_RE.search(loc))
