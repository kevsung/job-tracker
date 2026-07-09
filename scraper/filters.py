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
    # Creative Operations (Lead/Manager/Director/Head), without requiring "Manager" suffix
    re.compile(r"\b(senior|sr\.?|staff|lead|head\s+of)?\s*creative\s+operations\b", re.I),
    # Creative Producer / Senior Producer / Production Producer (any seniority)
    re.compile(r"\b(senior|sr\.?|staff|lead|executive)?\s*(creative|production|content)\s+producer\b", re.I),
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
    # Senior / Sr. / Staff / Lead Delivery Manager (prefix + suffix variants)
    re.compile(r"\b(senior|sr\.?|staff|lead)\s+delivery\s+manager", re.I),
    re.compile(r"\bdelivery\s+manager[,\s\-]+(senior|sr\.?|staff|lead)", re.I),
    # Senior PM with ad/advertising/operations/platform/growth/enablement context
    re.compile(r"\bsenior\s+product\s+manager.{0,40}(ad|advertising|operations|platform|growth|enablement)", re.I),
    # Director / Head of advertising/marketing/creative/content operations
    re.compile(r"\b(director|head)\s+of\s+(advertising|marketing|creative|content)\s+operations", re.I),
    # Senior PM with operations/platform/growth/enablement context (broader)
    re.compile(r"\bsenior\s+product\s+manager.{0,40}(operations|platform|growth|enablement)", re.I),
    # Senior/Sr/Staff/Lead Manager in media/advertising/creative/brand ops
    re.compile(r"\b(senior|sr\.?|staff|lead)\s+manager.{0,40}(advertising|media|content|creative|brand)\s+operations", re.I),
    # Program/Project/Operations Manager in advertising/media/monetization/revenue context
    re.compile(r"\b(program|project|operations)\s+manager.{0,40}(advertising|media|monetization|revenue)", re.I),
    # Staff Product Operations or Staff Product Manager
    re.compile(r"\bstaff\s+product\s+(operations|manager)", re.I),
    # Senior/Sr/Lead/Staff Product Operations (without "Manager" suffix)
    re.compile(r"\b(senior|sr\.?|lead|staff)\s+product\s+operations", re.I),
]


def title_matches(title: str) -> bool:
    return any(p.search(title) for p in _TITLE_PATTERNS)


# ---------------------------------------------------------------------------
# Location matching: remote US  OR  within ~25 miles of Bethesda MD 20854
# ---------------------------------------------------------------------------

_US_RE = re.compile(
    r"\b(united\s+states|u\.s\.a?\.?|usa|us)\b",
    re.I,
)

# Reject remote roles located in a non-US country/region.
# "Remote" with no country, or "Remote - US / United States", is accepted.
_NON_US_COUNTRY_RE = re.compile(
    r"\b("
    # North America (non-US)
    r"canada|canadian|mexico|"
    # UK / Ireland
    r"uk|united kingdom|great britain|england|scotland|wales|ireland|"
    # Europe
    r"europe|european union|eu\s+only|emea|"
    r"germany|france|netherlands|belgium|spain|italy|portugal|"
    r"sweden|norway|denmark|finland|switzerland|austria|poland|"
    # Asia-Pacific
    r"apac|australia|new zealand|"
    r"india|pakistan|bangladesh|sri lanka|nepal|"
    r"china|japan|south korea|korea|taiwan|hong kong|singapore|"
    r"philippines|vietnam|thailand|indonesia|malaysia|"
    # Latin America
    r"latam|latin america|brazil|argentina|colombia|chile|peru|"
    # Middle East / Africa
    r"south africa|nigeria|kenya|egypt|"
    r"israel|uae|united arab emirates|saudi arabia|qatar|turkey|"
    # Eastern Europe / Central Asia
    r"russia|ukraine"
    r")\b",
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
        # Reject if any non-US country is named; otherwise accept
        # (covers "Remote", "Fully Remote", "Remote - US", etc.)
        return not bool(_NON_US_COUNTRY_RE.search(loc))

    # Bare "US" / "USA" / "United States" (no city), e.g. Stripe's location
    # field for its remote-eligible-anywhere-in-US postings.
    if _US_RE.search(loc) and not _NON_US_COUNTRY_RE.search(loc):
        return True

    # Non-remote: DC metro only
    return bool(_DC_METRO_RE.search(loc))
