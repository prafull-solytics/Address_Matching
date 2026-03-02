"""
scoring_config.py — Pure Configuration for Location Fuzzy Matching Engine

This file contains ALL tunable parameters, scores, penalties, thresholds,
and word lists used by the LocationMatcher algorithm. No logic lives here.

An operations team can modify any value in this file without touching
algorithm code. All values are imported by location_matcher.py.

Author: novushq
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Union


# ─────────────────────────────────────────────────────────────────────────────
# CORE SCORING PARAMETERS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ScoringConfig:
    """
    Immutable configuration dataclass holding every tunable parameter
    for the LocationMatcher scoring engine.

    Frozen=True ensures thread-safety and prevents accidental mutation.
    """

    # ── Exact / Direct Match Scores ──────────────────────────────────────
    EXACT_MATCH_SCORE: float = 1.0
    ABBREVIATION_MATCH_SCORE: float = 0.88
    ALTERNATE_NAME_MATCH_SCORE: float = 0.82
    PHONETIC_MATCH_SCORE: float = 0.72

    # ── Penalty Factors ──────────────────────────────────────────────────
    REVERSED_ORDER_PENALTY: float = 0.22
    NOISE_WORD_PENALTY_PER_WORD: float = 0.30
    MULTI_TOKEN_NOISE_MAX_PENALTY: float = 0.65
    DIRECTIONAL_MISMATCH_PENALTY: float = 0.30
    COMMON_WORD_COLLISION_PENALTY: float = 0.70

    # ── Substring Match Scores ─────────────────────────��─────────────────
    SUBSTRING_MATCH_BASE_SCORE: float = 0.55
    SUBSTRING_RESULT_IN_QUERY_SCORE: float = 0.65
    SUBSTRING_QUERY_IN_RESULT_SCORE: float = 0.55
    FALSE_POSITIVE_SUBSTRING_MIN_LENGTH: int = 4
    SHORT_RESULT_SUBSTRING_HALVE_THRESHOLD: int = 4

    # ── Token Coverage ───────────────────────────────────────────────────
    PARTIAL_TOKEN_COVERAGE_WEIGHT: float = 1.0
    DIRECTIONAL_WORD_WEIGHT: float = 0.85

    # ── Token Filtering ──────────────────────────────────────────────────
    MIN_TOKEN_LENGTH: int = 2

    # ── Fuzzy / Edit Distance ────────────────────────────────────────────
    FUZZY_MATCH_THRESHOLD: float = 0.82
    TYPO_EDIT_DISTANCE_WEIGHTS: Dict[int, float] = field(default_factory=lambda: {
        0: 1.00,   # 0 edits → perfect
        1: 0.88,   # 1 edit  → high confidence
        2: 0.75,   # 2 edits → moderate confidence
        3: 0.55,   # 3 edits → low confidence
    })
    MAX_TYPO_EDIT_DISTANCE: int = 3

    # ── Jaro-Winkler Tuning ──────────────────────────────────────────────
    JARO_WINKLER_WEIGHT: float = 0.91

    # ── Score Floor & Bounds ─────────────────────────────────────────────
    SCORE_FLOOR: float = 0.0
    SCORE_PRECISION: int = 4

    # ── Stemming Match ───────────────────────────────────────────────────
    STEM_MATCH_SCORE: float = 0.70


# ─────────────────────────────────────────────────────────────────────────────
# ADDRESS STOPWORDS  (removed from the QUERY only)
#
# These are tokens commonly found in raw address strings that carry zero
# location-identification value. Aggressively broad by design.
# ─────────────────────────────────────────────────────────────────────────────

STOPWORDS_ADDRESS: Set[str] = {
    # ── Articles / Prepositions / Conjunctions ───────────────────────────
    "a", "an", "the", "of", "and", "or", "in", "on", "at", "to", "for",
    "by", "with", "from", "into", "is", "it", "its",

    # ── Street / Road Types ──────────────────────────────────────────────
    "street", "st", "road", "rd", "avenue", "ave", "boulevard", "blvd",
    "lane", "ln", "drive", "dr", "court", "ct", "place", "pl",
    "way", "circle", "cir", "terrace", "ter", "trail", "trl",
    "highway", "hwy", "parkway", "pkwy", "alley", "aly",
    "crescent", "cres", "close", "marg", "path", "route",

    # ── Building / Unit Identifiers ──────────────────────────────────────
    "apt", "apartment", "suite", "ste", "unit", "flat", "floor",
    "building", "bldg", "block", "blk", "tower", "wing",
    "room", "rm", "office", "ofc", "shop", "store",
    "house", "cottage", "villa", "residence", "complex",

    # ── Number / Address Prefixes ────────────────────────────────────────
    "no", "number", "num", "plot", "sector", "sec", "phase",
    "zone", "ward", "district", "div", "division",
    "pin", "pincode", "zip", "zipcode", "postal", "code",

    # ── Postal / Mail ────────────────────────────────────────────────────
    "po", "box", "gpo", "pob", "postbox", "mailbox",

    # ── Relational / Directional (address context only) ──────────────────
    "near", "opposite", "opp", "behind", "beside", "next",
    "above", "below", "between", "across", "along", "adj", "adjacent",
    "front", "back", "corner", "junction", "crossing",

    # ── Care-of / Relationship ───────────────────────────────────────────
    "co", "care", "wo", "so", "do",  # c/o, w/o, s/o, d/o after slash split
    "attn", "attention",

    # ── Locality / Area Descriptors ──────────────────────────────────────
    "nagar", "colony", "enclave", "extension", "ext", "layout",
    "garden", "gardens", "park", "estate", "estates", "society",
    "township", "town", "village", "hamlet", "camp", "cantonment",
    "bazaar", "market", "chowk", "square", "main", "cross",
    "inner", "outer", "old", "new", "upper", "lower", "central",
    "greater", "metro", "suburban", "industrial", "commercial",
    "residential", "green", "white", "blue", "red",

    # ── Other Noise ──────────────────────────────────────────────────────
    "area", "region", "locality", "location", "address",
    "city", "state", "country", "province", "territory",
    "county", "borough", "municipality", "prefecture",
    "republic", "kingdom", "federation", "commonwealth",
    "hno", "doorno",
    "i", "ran", "live", "here", "there", "this", "that",
    "restaurant", "shop", "cafe", "hotel", "hospital",
    "school", "college", "university", "institute",
    "church", "temple", "mosque", "station", "airport",
    "bridge", "dam", "fort", "port", "island",
    "cabinet", "sandwich", "shoes", "brand", "rent",
    "furniture", "store", "mall", "center", "centre",
    "market", "outlet", "gallery", "studio", "lab",
}


# ─────────────────────────────────────────────────────────────────────────────
# RESULT STOPWORDS  (removed from the ELASTIC RESULT only)
#
# MUCH smaller than address stopwords. We must NOT strip words like "and"
# or "the" when they are part of official location names.
# e.g., "Bosnia and Herzegovina", "The Gambia"
#
# Only truly meaningless filler words go here.
# ─────────────────────────────────────────────────────────────────────────────

STOPWORDS_RESULT: Set[str] = {
    "republic", "kingdom", "federation", "commonwealth",
    "territory", "province", "state", "prefecture",
    "region", "district", "municipality",
}


# ─────────────────────────────────────────────────────────────────────────────
# COMMERCIAL CONTEXT WORDS
#
# Words that signal a COMMERCIAL or NON-GEOGRAPHIC context.
# Used ONLY in Rule 2 (common-word collision detection) to distinguish:
#   "China Cabinet Store" (commercial → penalise) from
#   "No. 1 Changan Ave, Beijing, China" (address → don't penalise)
#
# These are a SUBSET of STOPWORDS_ADDRESS — only the clearly non-geographic ones.
# Street/road/address-structure words (ave, st, no, blvd) are NOT included.
# ─────────────────────────────────────────────────────────────────────────────

COMMERCIAL_CONTEXT_WORDS: Set[str] = {
    # Business / retail — only clearly commercial words, NOT ambiguous ones like "bar"
    "restaurant", "shop", "cafe", "hotel",
    "cabinet", "sandwich", "shoes", "brand", "rent",
    "furniture", "mall", "outlet", "gallery", "studio",
    "store", "market", "center", "centre", "lab",
    # Non-place descriptors
    "apartment", "for", "sale", "lease", "hire",
    "food", "eat", "wear", "sport", "tech",
    # Building types that are commercial signals
    "office", "ofc",
}


# ─────────────────────────────────────────────────────────────────────────────
# KNOWN ABBREVIATIONS
#
# Maps abbreviation → full name(s). When the value is a list, it means
# the abbreviation is ambiguous and ALL expansions should be tried.
# ─────────────────────────────────────────────────────────────────────────────

KNOWN_ABBREVIATIONS: Dict[str, Union[str, List[str]]] = {
    # ── Country Codes ────────────────────────────────────────────────────
    "usa":    "united states",
    "us":     "united states",
    "uk":     "united kingdom",
    "uae":    "united arab emirates",
    "ussr":   "soviet union",
    "rsa":    "south africa",
    "drc":    "democratic republic of the congo",
    "prc":    "china",
    "rok":    "south korea",
    "dprk":   "north korea",
    "ksa":    "saudi arabia",
    "nz":     "new zealand",
    "png":    "papua new guinea",
    "bih":    "bosnia and herzegovina",
    "cz":     "czech republic",
    "sk":     "slovakia",

    # ─�� US State Codes (common) ──────────────────────────────────────────
    "ny":     "new york",
    "ca":     ["california", "canada"],
    "tx":     "texas",
    "fl":     "florida",
    "il":     "illinois",
    "pa":     "pennsylvania",
    "oh":     "ohio",
    "ga":     ["georgia"],
    "ma":     "massachusetts",
    "wa":     ["washington", "western australia"],
    "dc":     "district of columbia",
    "nj":     "new jersey",
    "nc":     "north carolina",
    "sc":     "south carolina",
    "va":     "virginia",
    "md":     "maryland",
    "ct":     "connecticut",
    "la":     ["louisiana", "los angeles"],
    "mn":     "minnesota",
    "wi":     "wisconsin",
    "co":     "colorado",
    "az":     "arizona",
    "nv":     "nevada",
    "or":     "oregon",
    "tn":     "tennessee",
    "mo":     "missouri",
    "al":     "alabama",
    "ms":     "mississippi",

    # ── Directional Abbreviations ────────────────────────────────────────
    "n":      "north",
    "s":      "south",
    "e":      "east",
    "w":      "west",
    "ne":     "northeast",
    "nw":     "northwest",
    "se":     "southeast",
    "sw":     "southwest",

    # ── City / Region Abbreviations ──────────────────────────────────────
    "sf":     "san francisco",
    "hk":     "hong kong",
    "sg":     "singapore",
    "bkk":    "bangkok",
    "jfk":    "new york",
    "lhr":    "london",
}


# ─────────────────────────────────────────────────────────────────────────────
# KNOWN ALTERNATE NAMES / TRANSLITERATIONS
#
# Maps non-English or historical names to their standard English equivalents.
# Used in Step 7 of the matching pipeline.
# ─────────────────────────────────────────────────────────────────────────────

KNOWN_ALTERNATE_NAMES: Dict[str, str] = {
    # ── Endonyms / Local Names ───────────────────────────────────────────
    "bharat":       "india",
    "hindustan":    "india",
    "nippon":       "japan",
    "nihon":        "japan",
    "zhongguo":     "china",
    "hanguk":       "south korea",
    "joseon":       "north korea",
    "chosen":       "north korea",
    "deutschland":  "germany",
    "allemagne":    "germany",
    "alemania":     "germany",
    "germania":     "germany",
    "francia":      "france",
    "frankreich":   "france",
    "espana":       "spain",
    "espagne":      "spain",
    "italia":       "italy",
    "italie":       "italy",
    "rossiya":      "russia",
    "russie":       "russia",
    "brasil":       "brazil",
    "bresil":       "brazil",
    "mexique":      "mexico",
    "turquie":      "turkey",
    "turkiye":      "turkey",
    "hellas":       "greece",
    "ellada":       "greece",
    "hrvatska":     "croatia",
    "cesko":        "czech republic",
    "czechia":      "czech republic",
    "suomi":        "finland",
    "sverige":      "sweden",
    "norge":        "norway",
    "danmark":      "denmark",
    "osterreich":   "austria",
    "schweiz":      "switzerland",
    "svizzera":     "switzerland",
    "suisse":       "switzerland",
    "nederland":    "netherlands",
    "hollande":     "netherlands",
    "holland":      "netherlands",
    "belgique":     "belgium",
    "belgie":       "belgium",
    "polska":       "poland",
    "pologne":      "poland",
    "magyarorszag": "hungary",
    "hongrie":      "hungary",
    "romania":      "romania",
    "roumanie":     "romania",
    "srbija":       "serbia",
    "shqiperia":    "albania",
    "sakartvelo":   "georgia",
    "hayastan":     "armenia",
    "misr":         "egypt",
    "egypte":       "egypt",
    "masr":         "egypt",
    "al-jazair":    "algeria",
    "tunisie":      "tunisia",
    "maroc":        "morocco",
    "libye":        "libya",
    "lubnan":       "lebanon",
    "suriya":       "syria",
    "al-iraq":      "iraq",
    "filastin":     "palestine",
    "yisrael":      "israel",
    "eire":         "ireland",
    "cymru":        "wales",
    "alba":         "scotland",
    "kernow":       "cornwall",
    "aotearoa":     "new zealand",

    # ── Regional/Historical Names ────────────────────────────────────────
    "east timor":   "timor leste",
    "timor leste":  "timor leste",
    "burma":        "myanmar",
    "siam":         "thailand",
    "persia":       "iran",
    "eyran":        "iran",
    "eiran":        "iran",
    "formosa":      "taiwan",
    "rhodesia":     "zimbabwe",
    "abyssinia":    "ethiopia",
    "peking":       "beijing",
    "bombay":       "mumbai",
    "madras":       "chennai",
    "calcutta":     "kolkata",
    "rangoon":      "yangon",
    "saigon":       "ho chi minh city",
    "constantinople": "istanbul",
    "byzantium":    "istanbul",
    "moskva":       "moscow",
    "moscou":       "moscow",
    "roma":         "rome",
    "wien":         "vienna",
    "vienne":       "vienna",
    "praha":        "prague",
    "prag":         "prague",
    "warszawa":     "warsaw",
    "varsovie":     "warsaw",
    "bucuresti":    "bucharest",
    "kobenhavn":    "copenhagen",
    "copenhague":   "copenhagen",
    "lisboa":       "lisbon",
    "lisbonne":     "lisbon",
    "athina":       "athens",
    "athenes":      "athens",
    "beograd":      "belgrade",
    "munchen":      "munich",
    "koln":         "cologne",
    "bruxelles":    "brussels",
    "brussel":      "brussels",
    "geneve":       "geneva",
    "genf":         "geneva",
    "zurich":       "zurich",
    "den haag":     "the hague",
    "le caire":     "cairo",
    "al-qahira":    "cairo",
    "dimashq":      "damascus",
    "bayrut":       "beirut",
    "al-riyadh":    "riyadh",
    "krung thep":   "bangkok",
}


# ─────────────────────────────────────────────────────────────────────────────
# GARBAGE TOKENS
#
# Tokens / full inputs that indicate null, missing, or placeholder data.
# If the ENTIRE input (after cleaning) consists only of these → return 0.0
# ─────────────────────────────────────────────────────────────────────────────

GARBAGE_TOKENS: Set[str] = {
    "na", "n/a", "n.a.", "n.a",
    "nil", "null", "none", "nill",
    "unknown", "undefined", "unspecified",
    "test", "testing", "dummy", "sample", "example",
    "tbd", "tba", "pending",
    "xxx", "zzz", "abc", "aaa",
    "-", "--", "---", ".", "..", "...",
    "0", "00", "000",
}


# ─────────────────────────────────────────────────────────────────────────────
# DIRECTIONAL WORDS
#
# Words that carry semantic weight when part of a location name.
# Must NOT be treated as stopwords when they appear in the elastic result.
# ─────────────────────────────────────────────────────────────────────────────

DIRECTIONAL_WORDS: Set[str] = {
    "north", "south", "east", "west",
    "northern", "southern", "eastern", "western",
    "northeast", "northwest", "southeast", "southwest",
    "central", "upper", "lower",
}


# ─────────────────────────────────────────────────────────────────────────────
# COMMON WORD COLLISION LIST
#
# Location names that are also common English words. These require extra
# caution to avoid false positives (Edge Case Category 16).
# ─────────────────────────────────────────────────────────────────────────────

COMMON_WORD_COLLISIONS: Set[str] = {
    "nice",         # city in France / adjective
    "turkey",       # country / food
    "jordan",       # country / name / brand
    "china",        # country / material (porcelain)
    "chile",        # country / food (chili)
    "guinea",       # country / animal (guinea pig)
    "cuba",         # country / cocktail ingredient
    "chad",         # country / name
    "lima",         # city / bean
    "peru",         # country / street name
    "bath",         # city in UK / common word
    "reading",      # city in UK / common word
    "orange",       # city in US / color / fruit
    "mobile",       # city in US / adjective
    "norman",       # city in US / name
    "troy",         # city in US / name
    "victoria",     # city / name
    "florence",     # city / name
    "carolina",     # state / name
    "virginia",     # state / name
    "montana",      # state / name
    "georgia",      # state+country / name
    "dakota",       # state / name
    "phoenix",      # city / mythological bird
    "aurora",       # city / natural phenomenon
    "pearl",        # city / gem
    "temple",       # city / building
    "paris",        # city / name
    "berlin",       # city / name
    "dover",        # city / name
    "salem",        # city / name
    "jackson",      # city / name
    "madison",      # city / name
    "lincoln",      # city / name
    "cleveland",    # city / name
    "oakland",      # city
    "portland",     # city
    "durham",       # city / name
    "cambridge",    # city
    "oxford",       # city
    "hull",         # city / nautical term
    "cork",         # city / material
    "split",        # city / verb
    "essen",        # city / German word (eating)
    "nice",         # repeated for emphasis: very common false positive
    "mars",         # city / planet
    "alpine",       # city / adjective
    "riverside",    # city / common noun
    "spring",       # city / season
    "springs",      # city / common noun
}


# ─────────────────────────────────────────────────────────────────────────────
# KNOWN ABBREVIATION TOKENS EXEMPT FROM MIN_TOKEN_LENGTH FILTER
#
# These tokens are shorter than MIN_TOKEN_LENGTH but are legitimate
# abbreviations that should NOT be discarded during tokenization.
# ─────────────────────────────────────────────────────────────────────────────

ABBREVIATION_EXEMPT_TOKENS: Set[str] = set(KNOWN_ABBREVIATIONS.keys())


# ─────────────────────────────────────────────────────────────────────────────
# SINGLETON DEFAULT CONFIG INSTANCE
#
# Import this directly:  from scoring_config import DEFAULT_CONFIG
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_CONFIG = ScoringConfig()