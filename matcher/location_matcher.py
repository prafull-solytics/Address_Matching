"""
location_matcher.py — Fuzzy Location Name Matching Engine (v2)

Matches a raw address query string against a location name (city/state/country)
and returns a confidence score in [0.0, 1.0].

Architecture (6 clean stages):
  Stage 1: Normalize & tokenize
  Stage 2: Build token features (abbreviation expansion, alternate names)
  Stage 3: Pairwise token similarity (exact > abbrev > fuzzy > substring > phonetic)
  Stage 4: Result-level aggregation (single-token MAX, multi-token coverage)
  Stage 5: Contextual penalties (bounded, documented)
  Stage 6: Clamp & return

Design principles:
  - No entity-type bias (city/state/country agnostic)
  - Deterministic and auditable scoring
  - Token-level max evidence logic
  - Bounded penalties applied after evidence scoring
  - All constants self-contained with clear grouping
"""

import logging
import re
import unicodedata
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set, Tuple

# ── Optional dependency imports with safe fallbacks ──────────────────────────

try:
    from nltk.stem import PorterStemmer
    _STEMMER = PorterStemmer()
except ImportError:
    _STEMMER = None

try:
    from jellyfish import (
        jaro_winkler_similarity as _jf_jw,
        levenshtein_distance as _jf_lev,
        metaphone as _jf_metaphone,
        soundex as _jf_soundex,
    )
    _HAS_JELLYFISH = True
except ImportError:
    _HAS_JELLYFISH = False

# ── Config imports ───────────────────────────────────────────────────────────

from .scoring_config import (
    ABBREVIATION_EXEMPT_TOKENS,
    COMMERCIAL_CONTEXT_WORDS,
    COMMON_WORD_COLLISIONS,
    DEFAULT_CONFIG,
    DIRECTIONAL_WORDS,
    GARBAGE_TOKENS,
    KNOWN_ABBREVIATIONS,
    KNOWN_ALTERNATE_NAMES,
    STOPWORDS_ADDRESS,
    STOPWORDS_RESULT,
    ScoringConfig,
)

logger = logging.getLogger(__name__)

# ═════════════════════════════════════════════════════════════════════════════
# INTERNAL CONSTANTS
# ═════════════════════════════════════════════════════════════════════════════

# ── Score anchors ────────────────────────────────────────────────────────────
EXACT_SCORE: float = 1.0
ABBREVIATION_CAP: float = 0.88
ALTERNATE_NAME_CAP: float = 0.82
PHONETIC_FULL_SCORE: float = 0.72
PHONETIC_PARTIAL_MULT: float = 0.65
STEM_SCORE: float = 0.70
COMPOUND_SCORE: float = 0.85

# ── Substring parameters ────────────────────────────────────────────────────
SUBSTR_MIN_LEN: int = 4
SUBSTR_RIQ_BASE: float = 0.65
SUBSTR_PREFIX_SUFFIX_CAP: float = 0.58
SUBSTR_EMBEDDED_CAP: float = 0.45
SUBSTR_QIR_CAP: float = 0.40
ELEVATED_SUBSTR_MAX: float = 0.85

# ── Fuzzy / edit-distance parameters ────────────────────────────────────────
JW_THRESHOLD: float = 0.82
JW_WEIGHT: float = 0.91
EDIT_CAPS: Dict[int, float] = {0: 0.95, 1: 0.90, 2: 0.82, 3: 0.75}
EDIT_WEIGHTS: Dict[int, float] = {0: 1.00, 1: 0.88, 2: 0.75, 3: 0.55}
MAX_EDIT_DIST: int = 3

# ── Penalty caps/rates ──────────────────────────────────────────────────────
REVERSED_ORDER_PENALTY: float = 0.22
NOISE_PER_WORD: float = 0.30
NOISE_MAX_PENALTY: float = 0.65
DIR_MISMATCH_PENALTY: float = 0.30
DIR_ABSENT_WEIGHT: float = 0.85
COLLISION_PENALTY: float = 0.70

# ── Token filtering ─────────────────────────────────────────────────────────
MIN_TOKEN_LEN: int = 2

# ── Regex patterns ───────────────────────────────────────────────────────────
_SPLIT_RE = re.compile(r"[/|\\-]+")
_STRIP_CHARS = frozenset('.,"\'\u2018\u2019\u201c\u201d()[]#;:!?{}')
_PURE_NUMERIC_RE = re.compile(r"^\d+$")
_ALPHANUM_NOISE_RE = re.compile(r"^[a-z]\d+|^\d+[a-z]+$", re.IGNORECASE)

# ── Administrative prefix words ──────────────────────────────────────────────
_ADMIN_WORDS = frozenset({
    "kingdom", "republic", "federation", "commonwealth",
    "state", "province", "territory", "prefecture",
})

# ── Optional connectors in result names ──────────────────────────────────────
_OPTIONAL_CONNECTORS = frozenset({"and", "the", "of", "al", "el"})


# ═════════════════════════════════════════════════════════════════════════════
# CACHED HELPERS
# ═════════════════════════════════════════════════════════════════════════════

@lru_cache(maxsize=4096)
def _normalize_unicode(text: str) -> str:
    """NFD decomposition + strip combining marks + lowercase."""
    nfd = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn").lower()


@lru_cache(maxsize=4096)
def _soundex(token: str) -> str:
    if _HAS_JELLYFISH:
        try:
            return _jf_soundex(token)
        except Exception:
            return ""
    return ""


@lru_cache(maxsize=4096)
def _metaphone(token: str) -> str:
    if _HAS_JELLYFISH:
        try:
            return _jf_metaphone(token)
        except Exception:
            return ""
    return ""


@lru_cache(maxsize=4096)
def _stem(token: str) -> str:
    return _STEMMER.stem(token) if _STEMMER else token


try:
    from difflib import SequenceMatcher as _SequenceMatcher
except ImportError:
    _SequenceMatcher = None  # type: ignore[misc,assignment]


@lru_cache(maxsize=4096)
def _jw(a: str, b: str) -> float:
    """Jaro-Winkler similarity with fallback."""
    if _HAS_JELLYFISH:
        return _jf_jw(a, b)
    if _SequenceMatcher is not None:
        return _SequenceMatcher(None, a, b).ratio()
    return 1.0 if a == b else 0.0


@lru_cache(maxsize=4096)
def _lev(a: str, b: str) -> int:
    """Levenshtein edit distance with fallback."""
    if _HAS_JELLYFISH:
        return _jf_lev(a, b)
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i in range(la):
        curr = [i + 1] + [0] * lb
        for j in range(lb):
            cost = 0 if a[i] == b[j] else 1
            curr[j + 1] = min(curr[j] + 1, prev[j + 1] + 1, prev[j] + cost)
        prev = curr
    return prev[lb]


# ═════════════════════════════════════════════════════════════════════════════
# LocationMatcher
# ═════════════════════════════════════════════════════════════════════════════

class LocationMatcher:
    """
    Fuzzy location name matching engine.
    Returns a confidence score in [0.0, 1.0].

    Usage:
        matcher = LocationMatcher()
        score = matcher.match("10, Green Apt, Iran", "Iran")    # -> 1.0
        debug = matcher.get_debug_breakdown("Hirani", "Iran")   # -> dict
    """

    def __init__(self, config: Optional[ScoringConfig] = None) -> None:
        self._cfg: ScoringConfig = config or DEFAULT_CONFIG

    # ── Public API ───────────────────────────────────────────────────────

    def match(self, query: str, elastic_result: str) -> float:
        """Score match(query, result) -> float in [0.0, 1.0].
        Raises TypeError if inputs are not strings."""
        self._validate(query, elastic_result)
        score, _ = self._pipeline(query, elastic_result)
        return score

    def get_debug_breakdown(self, query: str, elastic_result: str) -> Dict[str, Any]:
        """Full scoring breakdown for auditing."""
        self._validate(query, elastic_result)
        score, dbg = self._pipeline(query, elastic_result, debug=True)
        dbg["final_score"] = score
        return dbg

    # ── Validation ───────────────────────────────────────────────────────

    @staticmethod
    def _validate(query: Any, result: Any) -> None:
        if not isinstance(query, str):
            raise TypeError(f"query must be str, got {type(query).__name__}")
        if not isinstance(result, str):
            raise TypeError(f"elastic_result must be str, got {type(result).__name__}")

    # ═════════════════════════════════════════════════════════════════════
    # PIPELINE
    # ═════════════════════════════════════════════════════════════════════

    def _pipeline(
        self, query: str, result: str, debug: bool = False
    ) -> Tuple[float, Dict[str, Any]]:
        dbg: Dict[str, Any] = {"raw_query": query, "raw_result": result} if debug else {}

        # ── Stage 1: Normalize & tokenize ────────────────────────────────

        if self._is_garbage(query) or self._is_garbage(result):
            if debug:
                dbg["stage1_garbage"] = True
            return 0.0, dbg

        nq = _normalize_unicode(query)
        nr = _normalize_unicode(result)
        if debug:
            dbg["stage1_normalized"] = {"query": nq, "result": nr}

        # Quick exact after normalization
        if nq.strip() == nr.strip():
            if debug:
                dbg["quick_exact"] = True
                dbg["token_scores"] = [{"query_token": nq.strip(),
                                        "result_token": nr.strip(),
                                        "score": 1.0, "method": "exact"}]
            return 1.0, dbg

        cq = self._clean_punct(nq)
        cr = self._clean_punct(nr)

        qt_raw = self._tokenize(cq, is_query=True)
        rt_raw = self._tokenize(cr, is_query=False)
        q_prefilter = len(cq.split())
        q_filtered = q_prefilter - len(qt_raw)

        qt = self._dedup(self._strip_stopwords_query(qt_raw, rt_raw))
        rt = self._dedup(self._strip_stopwords_result(rt_raw))
        if debug:
            dbg["stage1_tokens"] = {"query": qt, "result": rt}

        if not rt or not qt:
            return 0.0, dbg

        # ── Stage 2: Build token features ────────────────────────────────

        expanded = self._expand_abbreviations(qt)
        enriched = self._apply_alternate_names(expanded)

        has_abbrev = any(t in KNOWN_ABBREVIATIONS for t in qt)
        has_alt = any(t in KNOWN_ALTERNATE_NAMES for t in qt)
        admin_stripped = sum(
            1 for t in cq.split()
            if t in _ADMIN_WORDS and t not in set(qt)
        )

        if debug:
            dbg["stage2_enriched"] = enriched

        # ── Stage 4: Result-level aggregation ────────────────────────────

        if len(rt) == 1:
            raw, detail = self._aggregate_single(enriched, rt[0], qt_raw, qt)
        else:
            raw, detail = self._aggregate_multi(enriched, rt, qt)

        if debug:
            dbg["stage4_raw"] = raw
            dbg["stage4_detail"] = detail

        # ── Stage 5: Contextual penalties ────────────────────────────────

        adjusted, pen_detail = self._apply_penalties(
            raw, enriched, qt, rt, qt_raw,
            has_abbrev, has_alt,
            q_prefilter, q_filtered,
            admin_stripped, detail,
        )

        if debug:
            dbg["stage5_adjusted"] = adjusted
            dbg["stage5_penalties"] = pen_detail

        # ── Stage 6: Clamp & return ──────────────────────────────────────

        final = self._clamp(adjusted)

        if debug:
            dbg["stage6_final"] = final
            token_scores = []
            for q in enriched:
                for r in rt:
                    s, d = self._token_similarity(q, r)
                    if s > 0:
                        token_scores.append({
                            "query_token": q, "result_token": r,
                            "score": round(s, 4),
                            "method": d.get("method", "none"),
                        })
            dbg["token_scores"] = token_scores
            dbg["steps"] = {
                "normalized": dbg.get("stage1_normalized"),
                "tokens": dbg.get("stage1_tokens"),
                "raw_score": raw,
                "adjusted_score": adjusted,
            }

        return final, dbg

    # ═════════════════════════════════════════════════════════════════════
    # STAGE 1: NORMALIZE & TOKENIZE
    # ═════════════════════════════════════════════════════════════════════

    @staticmethod
    def _is_garbage(text: str) -> bool:
        """Detect empty, null-like, or pure-noise input."""
        if not text or not text.strip():
            return True
        norm = _normalize_unicode(text.strip())
        if norm in GARBAGE_TOKENS:
            return True
        tokens = norm.split()
        meaningful = [t for t in tokens
                      if t not in GARBAGE_TOKENS and not _PURE_NUMERIC_RE.match(t)]
        return len(meaningful) == 0

    @staticmethod
    def _clean_punct(text: str) -> str:
        """Split on delimiter chars and strip punctuation."""
        out = _SPLIT_RE.sub(" ", text)
        out = "".join(ch if ch not in _STRIP_CHARS else " " for ch in out)
        return re.sub(r"\s+", " ", out).strip()

    @staticmethod
    def _tokenize(text: str, is_query: bool) -> List[str]:
        """Tokenize with filtering: remove numerics, alphanumeric noise, short tokens."""
        out: List[str] = []
        for tok in text.split():
            if is_query and _PURE_NUMERIC_RE.match(tok):
                continue
            if is_query and _ALPHANUM_NOISE_RE.match(tok) and tok not in ABBREVIATION_EXEMPT_TOKENS:
                continue
            if len(tok) < MIN_TOKEN_LEN and tok not in ABBREVIATION_EXEMPT_TOKENS:
                continue
            out.append(tok)
        return out

    @staticmethod
    def _strip_stopwords_query(qtokens: List[str], rtokens: List[str]) -> List[str]:
        """Remove address stopwords from query, protecting result tokens & directionals."""
        protected = set(rtokens) | DIRECTIONAL_WORDS
        return [t for t in qtokens if t not in STOPWORDS_ADDRESS or t in protected]

    @staticmethod
    def _strip_stopwords_result(rtokens: List[str]) -> List[str]:
        """Remove only result-specific stopwords (very conservative)."""
        return [t for t in rtokens if t not in STOPWORDS_RESULT]

    @staticmethod
    def _dedup(tokens: List[str]) -> List[str]:
        """Deduplicate preserving order."""
        seen: Set[str] = set()
        out: List[str] = []
        for t in tokens:
            if t not in seen:
                seen.add(t)
                out.append(t)
        return out

    # ═════════════════════════════════════════════════════════════════════
    # STAGE 2: TOKEN FEATURE EXPANSION
    # ═════════════════════════════════════════════════════════════════════

    @staticmethod
    def _expand_abbreviations(tokens: List[str]) -> List[str]:
        """Expand known abbreviations, adding expansion tokens."""
        expanded = list(tokens)
        for tok in tokens:
            if tok in KNOWN_ABBREVIATIONS:
                exp = KNOWN_ABBREVIATIONS[tok]
                for e in (exp if isinstance(exp, list) else [exp]):
                    for sub in e.split():
                        if sub not in expanded:
                            expanded.append(sub)
        return expanded

    @staticmethod
    def _apply_alternate_names(tokens: List[str]) -> List[str]:
        """Add alternate name expansions (e.g., bharat->india)."""
        enriched = list(tokens)
        for tok in tokens:
            if tok in KNOWN_ALTERNATE_NAMES:
                for sub in KNOWN_ALTERNATE_NAMES[tok].split():
                    if sub not in enriched:
                        enriched.append(sub)
        return enriched

    # ═════════════════════════════════════════════════════════════════════
    # STAGE 3: PAIRWISE TOKEN SIMILARITY
    # ═════════════════════════════════════════════════════════════════════

    def _token_similarity(
        self, qt: str, rt: str
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Compute similarity between a single query token and result token.

        Priority ladder (ordered evidence, best applicable wins):
          1. Exact equality            -> 1.0
          2. Abbreviation mapping      -> ABBREVIATION_CAP (0.88)
          3. Alternate name mapping    -> ALTERNATE_NAME_CAP (0.82)
          4. Stem match (>=4 chars)    -> STEM_SCORE (0.70)
          5. Fuzzy (JW + edit dist)    -> bounded by edit caps
          6. Phonetic (soundex+metaphone) -> PHONETIC_FULL_SCORE (0.72)
          7. Substring: result in query -> bounded
          8. Substring: query in result -> bounded
        """
        # 1. Exact
        if qt == rt:
            return 1.0, {"method": "exact"}

        # 2. Abbreviation
        if qt in KNOWN_ABBREVIATIONS:
            exp = KNOWN_ABBREVIATIONS[qt]
            for e in (exp if isinstance(exp, list) else [exp]):
                if rt in e.split():
                    return ABBREVIATION_CAP, {"method": "abbreviation", "expansion": e}

        # 3. Alternate name
        if qt in KNOWN_ALTERNATE_NAMES:
            if rt in KNOWN_ALTERNATE_NAMES[qt].split():
                return ALTERNATE_NAME_CAP, {"method": "alternate_name"}

        # 4. Stem match
        if len(qt) >= 4 and len(rt) >= 4:
            if _stem(qt) == _stem(rt):
                return STEM_SCORE, {"method": "stem_match"}

        # 5. Fuzzy (Jaro-Winkler + Levenshtein)
        # Skip JW when result is a substring of query with low coverage
        skip_jw = (
            (len(rt) >= SUBSTR_MIN_LEN and rt in qt
             and len(rt) / len(qt) < 0.75)
            or (len(qt) <= 2 and len(rt) >= 4)
        )

        jw = _jw(qt, rt)
        if not skip_jw and jw >= JW_THRESHOLD:
            ed = _lev(qt, rt)
            ed_capped = min(ed, MAX_EDIT_DIST)
            ed_score = EDIT_WEIGHTS.get(ed_capped, 0.0)
            edit_cap = EDIT_CAPS.get(ed_capped, 0.75)
            len_ratio = min(len(qt), len(rt)) / max(len(qt), len(rt))
            len_factor = 0.7 + 0.3 * len_ratio
            fuzzy = min(
                max(jw * JW_WEIGHT, ed_score * 0.9) * len_factor,
                edit_cap,
            )
            return fuzzy, {"method": "jaro_winkler", "jw": round(jw, 4),
                           "edit_distance": ed}

        # 6. Phonetic
        ph = self._phonetic_score(qt, rt)
        if ph > 0.0:
            return ph, {"method": "phonetic"}

        # 7. Substring: result in query_token
        if len(rt) >= SUBSTR_MIN_LEN and rt in qt and qt != rt:
            ratio = len(rt) / len(qt)
            if qt.startswith(rt) or qt.endswith(rt):
                sub = min(SUBSTR_RIQ_BASE * ratio * 1.6, SUBSTR_PREFIX_SUFFIX_CAP)
            else:
                depth = 1.0 if ratio > 0.75 else (0.75 if ratio > 0.5 else 0.45)
                sub = min(SUBSTR_RIQ_BASE * ratio * depth, SUBSTR_EMBEDDED_CAP)
            return sub, {"method": "substring_result_in_query", "ratio": round(ratio, 4)}

        # 8. Substring: query_token in result
        if len(qt) >= SUBSTR_MIN_LEN and qt in rt and qt != rt:
            ratio = len(qt) / len(rt)
            sub = min(SUBSTR_RIQ_BASE * ratio, SUBSTR_QIR_CAP)
            return sub, {"method": "substring_query_in_result", "ratio": round(ratio, 4)}

        return 0.0, {"method": "none"}

    @staticmethod
    def _phonetic_score(a: str, b: str) -> float:
        """Phonetic similarity using Soundex + Metaphone."""
        if len(a) < 3 or len(b) < 3:
            return 0.0
        sa, sb = _soundex(a), _soundex(b)
        ma, mb = _metaphone(a), _metaphone(b)
        sdx = bool(sa and sb and sa == sb)
        mtn = bool(ma and mb and ma == mb)
        if sdx and mtn:
            return PHONETIC_FULL_SCORE
        if sdx or mtn:
            return PHONETIC_FULL_SCORE * PHONETIC_PARTIAL_MULT
        return 0.0

    def _tokens_fuzzy_match(self, a: str, b: str) -> bool:
        """Quick check: do two tokens match (exact, abbreviation, alt-name, or fuzzy)?"""
        if a == b:
            return True
        if a in KNOWN_ABBREVIATIONS:
            exp = KNOWN_ABBREVIATIONS[a]
            for e in (exp if isinstance(exp, list) else [exp]):
                if b in e.split():
                    return True
        if a in KNOWN_ALTERNATE_NAMES and b in KNOWN_ALTERNATE_NAMES[a].split():
            return True
        return _jw(a, b) >= JW_THRESHOLD

    # ═════════════════════════════════════════════════════════════════════
    # STAGE 4: RESULT-LEVEL AGGREGATION
    # ═════════════════════════════════════════════════════════════════════

    def _aggregate_single(
        self,
        query_tokens: List[str],
        result_token: str,
        qt_raw: List[str],
        qt_clean: List[str],
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Single-token result: MAX strategy.
        Best matching query token determines the score.

        Elevated path: when the best match is an embedded substring with high
        overlap ratio (>=0.55), compute bidirectional quality = (1.0 + ratio)/2.
        This lifts cases like "hirani"->"iran" (ratio~0.667) to ~0.83.
        """
        best_score = 0.0
        best_detail: Dict[str, Any] = {}

        for qt in query_tokens:
            s, d = self._token_similarity(qt, result_token)
            if s > best_score:
                best_score = s
                best_detail = {"matched_query_token": qt,
                               "result_token": result_token, **d}
            if best_score >= 1.0:
                break

        # Elevated embedded substring path
        if (best_detail.get("method") == "substring_result_in_query"
                and best_detail.get("ratio", 0.0) >= 0.55
                and len(result_token) >= SUBSTR_MIN_LEN):
            bqt = best_detail.get("matched_query_token", "")
            is_embedded = (not bqt.startswith(result_token)
                           and not bqt.endswith(result_token))
            if is_embedded:
                ratio = best_detail["ratio"]
                quality = (1.0 + ratio) / 2.0
                elevated = min(quality, ELEVATED_SUBSTR_MAX)
                if elevated > best_score:
                    best_score = elevated
                    best_detail["elevated_quality"] = True
                    best_detail["quality"] = round(quality, 4)

        return best_score, best_detail

    def _aggregate_multi(
        self,
        query_tokens: List[str],
        result_tokens: List[str],
        qt_clean: List[str],
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Multi-token result: best of six sub-strategies.
          (a) Contiguous ordered match    -> up to 1.0
          (b) Ordered with noise gaps     -> penalized per noise word
          (c) All tokens, wrong order     -> reversed-order penalty
          (d) Partial coverage            -> coverage x avg
          (e) Per-result-token average    -> capped by (b)/(c)
          (f) Compound match              -> single query token = concat of result
        Then apply directional penalty.
        """
        detail: Dict[str, Any] = {"sub_scores": {}}

        sa = self._sub_contiguous(query_tokens, result_tokens)
        detail["sub_scores"]["a_contiguous"] = round(sa, 4)

        sb, noise = self._sub_ordered_noise(query_tokens, result_tokens)
        detail["sub_scores"]["b_ordered_noise"] = round(sb, 4)
        detail["sub_scores"]["b_noise_count"] = noise

        sc = self._sub_unordered(query_tokens, result_tokens)
        detail["sub_scores"]["c_unordered"] = round(sc, 4)

        sd, k, m = self._sub_partial(query_tokens, result_tokens)
        detail["sub_scores"]["d_partial"] = round(sd, 4)
        detail["sub_scores"]["d_k_of_m"] = f"{k}/{m}"

        se = self._sub_per_result_avg(query_tokens, result_tokens)
        # Cap when noise or wrong order
        if sb > 0.0 and noise > 0:
            se = min(se, sb)
            sd = min(sd, sb)
        if sc > 0.0:
            se = min(se, sc)
            sd = min(sd, sc)
        detail["sub_scores"]["e_fuzzy"] = round(se, 4)

        sf = self._sub_compound(query_tokens, result_tokens)
        detail["sub_scores"]["f_compound"] = round(sf, 4)

        best = max(sa, sb, sc, sd, se, sf)
        best_method = max(
            [("a", sa), ("b", sb), ("c", sc), ("d", sd), ("e", se), ("f", sf)],
            key=lambda x: x[1],
        )[0]
        detail["best_sub_method"] = best_method

        best = self._directional_penalty(best, query_tokens, result_tokens)
        detail["after_directional_penalty"] = round(best, 4)

        return best, detail

    # ── Multi-token sub-strategies ───────────────────────────────────────

    def _sub_contiguous(self, qtoks: List[str], rtoks: List[str]) -> float:
        """(a) All result tokens appear contiguously and in order in query."""
        rlen = len(rtoks)
        for i in range(len(qtoks) - rlen + 1):
            window = qtoks[i: i + rlen]
            if window == rtoks:
                return 1.0
            if all(self._tokens_fuzzy_match(w, r) for w, r in zip(window, rtoks)):
                scores = [
                    self._token_similarity(w, r)[0] if w != r else 1.0
                    for w, r in zip(window, rtoks)
                ]
                return min(scores)
        return 0.0

    def _sub_ordered_noise(
        self, qtoks: List[str], rtoks: List[str]
    ) -> Tuple[float, int]:
        """(b) All result tokens appear in order but with noise words between."""
        positions: List[int] = []
        qualities: List[float] = []
        start = 0

        for rt in rtoks:
            found = False
            for i in range(start, len(qtoks)):
                if self._tokens_fuzzy_match(qtoks[i], rt):
                    positions.append(i)
                    q = _jw(qtoks[i], rt) if qtoks[i] != rt else 1.0
                    qualities.append(q)
                    start = i + 1
                    found = True
                    break
            if not found:
                return 0.0, 0

        noise_count = 0
        if len(positions) >= 2:
            for idx in range(len(positions) - 1):
                noise_count += positions[idx + 1] - positions[idx] - 1

        avg_q = sum(qualities) / len(qualities)
        if noise_count == 0:
            return avg_q, 0

        penalty = min(noise_count * NOISE_PER_WORD, NOISE_MAX_PENALTY)
        return (1.0 - penalty) * avg_q, noise_count

    def _sub_unordered(self, qtoks: List[str], rtoks: List[str]) -> float:
        """(c) All result tokens matched but in wrong order -> reversed penalty."""
        positions: List[int] = []
        used: Set[int] = set()
        qualities: List[float] = []

        for rt in rtoks:
            best_idx, best_sim = -1, 0.0
            for i, qt in enumerate(qtoks):
                if i in used:
                    continue
                if qt == rt:
                    best_idx, best_sim = i, 1.0
                    break
                sim = _jw(qt, rt)
                if sim >= JW_THRESHOLD and sim > best_sim:
                    best_idx, best_sim = i, sim
            if best_idx == -1:
                return 0.0
            positions.append(best_idx)
            used.add(best_idx)
            qualities.append(best_sim)

        if all(positions[i] < positions[i + 1] for i in range(len(positions) - 1)):
            return 0.0

        avg_q = sum(qualities) / len(qualities)
        return (1.0 - REVERSED_ORDER_PENALTY) * avg_q

    def _sub_partial(
        self, qtoks: List[str], rtoks: List[str]
    ) -> Tuple[float, int, int]:
        """(d) K of M result tokens matched -> coverage x avg."""
        m = len(rtoks)
        matched: List[float] = []
        for rt in rtoks:
            best = 0.0
            for qt in qtoks:
                s, _ = self._token_similarity(qt, rt)
                if s > best:
                    best = s
            if best > 0.0:
                matched.append(best)
        k = len(matched)
        if k == 0:
            return 0.0, 0, m
        coverage = k / m
        avg = sum(matched) / k
        return coverage * avg, k, m

    def _sub_per_result_avg(self, qtoks: List[str], rtoks: List[str]) -> float:
        """(e) Average of best-score per result token.
        Optional connectors in result don't penalize coverage."""
        per_token: List[float] = []
        for rt in rtoks:
            best = 0.0
            for qt in qtoks:
                s, _ = self._token_similarity(qt, rt)
                if s > best:
                    best = s
            per_token.append(best)

        zero_non_opt = sum(
            1 for i, s in enumerate(per_token)
            if s == 0.0 and rtoks[i] not in _OPTIONAL_CONNECTORS
        )

        if zero_non_opt == 0:
            mandatory = [
                s for i, s in enumerate(per_token)
                if rtoks[i] not in _OPTIONAL_CONNECTORS or s > 0
            ]
            base = sum(mandatory) / len(mandatory) if mandatory else 0.0
            missing_opt = sum(
                1 for i, s in enumerate(per_token)
                if s == 0.0 and rtoks[i] in _OPTIONAL_CONNECTORS
            )
            return base * (1.0 - 0.05 * missing_opt)

        nonzero = [s for s in per_token if s > 0]
        if not nonzero:
            return 0.0

        mand_total = sum(1 for rt in rtoks if rt not in _OPTIONAL_CONNECTORS)
        mand_matched = sum(
            1 for i, s in enumerate(per_token)
            if s > 0 and rtoks[i] not in _OPTIONAL_CONNECTORS
        )
        coverage = mand_matched / mand_total if mand_total > 0 else 0.0
        avg = sum(nonzero) / len(nonzero)
        return coverage * avg

    def _sub_compound(self, qtoks: List[str], rtoks: List[str]) -> float:
        """(f) Single query token equals all result tokens concatenated."""
        if len(qtoks) != 1:
            return 0.0
        qt = qtoks[0]
        concat = "".join(rtoks)
        if qt == concat:
            return COMPOUND_SCORE
        if len(concat) >= 4:
            jw = _jw(qt, concat)
            if jw >= 0.90:
                return COMPOUND_SCORE * jw
        return 0.0

    # ── Directional penalty ──────────────────────────────────────────────

    @staticmethod
    def _directional_penalty(
        score: float, qtoks: List[str], rtoks: List[str]
    ) -> float:
        """Penalize when a result directional is contradicted or absent."""
        result_dirs = [t for t in rtoks if t in DIRECTIONAL_WORDS]
        if not result_dirs:
            return score

        query_dirs = {t for t in qtoks if t in DIRECTIONAL_WORDS}
        query_set = set(qtoks)

        for rd in result_dirs:
            if rd in query_set:
                continue
            if query_dirs:
                score *= (1.0 - DIR_MISMATCH_PENALTY)
                break
            else:
                score *= DIR_ABSENT_WEIGHT
                break

        return score

    # ═════════════════════════════════════════════════════════════════════
    # STAGE 5: CONTEXTUAL PENALTIES (bounded, documented)
    # ═════════════════════════════════════════════════════════════════════

    def _apply_penalties(
        self,
        score: float,
        enriched: List[str],
        qt: List[str],
        rt: List[str],
        qt_raw: List[str],
        has_abbrev: bool,
        has_alt: bool,
        q_prefilter: int,
        q_filtered: int,
        admin_stripped: int,
        score_detail: Optional[Dict[str, Any]],
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Apply bounded contextual penalties after evidence scoring.

        Penalty 1: Deep substring — result embedded in longer query token
                   (max multiplier: 0.30 for deep, 0.55 for shallow)
        Penalty 1b: Near-miss token (1 edit, structurally different)
                    (multiplier: 0.65, capped)
        Penalty 2: Commercial/collision word context
                    (max: COLLISION_PENALTY = 0.70)
        Penalty 3: Abbreviation/alternate-name score cap
        Penalty 4: Directional excess for single-token result
                    (max: 0.30)
        Penalty 5: Address-noise context dampening
                    (max: 0.45 for collision, 0.40 for filtered, 0.20 for multi)
        Penalty 6: Admin-prefix reduction
                    (max: 0.10)
        """
        detail: Dict[str, Any] = {"penalties_applied": []}
        adj = score
        qset = set(enriched)

        # ── Penalty 1: Deep substring (single-token result) ─────────────
        if len(rt) == 1 and adj >= 0.35:
            r = rt[0]
            if r not in qset:
                for q in enriched:
                    if r in q and q != r and len(q) > len(r):
                        is_prefix = q.startswith(r)
                        is_suffix = q.endswith(r)
                        if not is_prefix and not is_suffix:
                            if score_detail is not None and score_detail.get("elevated_quality"):
                                detail["penalties_applied"].append(
                                    f"p1_skipped_elevated: '{r}' in '{q}'"
                                )
                            else:
                                ratio = len(r) / len(q)
                                if ratio < 0.65:
                                    adj *= 0.30
                                    detail["penalties_applied"].append(
                                        f"p1_deep_substr: '{r}' in '{q}' ratio={ratio:.2f}"
                                    )
                                else:
                                    adj *= 0.55
                                    detail["penalties_applied"].append(
                                        f"p1_shallow_substr: '{r}' in '{q}' ratio={ratio:.2f}"
                                    )
                        break

        # ── Penalty 1b: Near-miss token ─────────────────────────────────
        if len(rt) == 1 and adj >= 0.45:
            r = rt[0]
            if r not in qset and len(r) >= 4:
                for q in enriched:
                    if q != r and len(q) > len(r):
                        ed = _lev(q, r)
                        if ed == 1:
                            diff = len(q) - len(r)
                            if diff >= 1 and not q.startswith(r) and not q.endswith(r):
                                adj *= 0.65
                                detail["penalties_applied"].append(
                                    f"p1b_near_miss: '{r}' vs '{q}' ed=1"
                                )
                                break

        # ── Penalty 2: Commercial/collision word detection ──────────────
        result_joined = " ".join(rt)
        rt_set = set(rt)
        raw_set = set(qt_raw)

        commercial_count = sum(
            1 for t in qt_raw
            if t not in rt_set and t in COMMERCIAL_CONTEXT_WORDS
        )

        if commercial_count >= 2:
            adj *= (1.0 - COLLISION_PENALTY)
            detail["penalties_applied"].append(
                f"p2_commercial_strong: count={commercial_count}"
            )
        elif commercial_count >= 1:
            adj *= (1.0 - COLLISION_PENALTY * 0.70)
            detail["penalties_applied"].append(
                f"p2_commercial_moderate: count={commercial_count}"
            )
        elif result_joined in COMMON_WORD_COLLISIONS:
            has_exact = any(r in raw_set for r in rt)
            if not has_exact:
                adj *= (1.0 - COLLISION_PENALTY)
                detail["penalties_applied"].append(
                    f"p2_collision_no_exact: '{result_joined}'"
                )

        # ── Penalty 3: Abbreviation / alternate-name score cap ──────────
        if has_abbrev or has_alt:
            all_alt = all(
                t in KNOWN_ALTERNATE_NAMES
                for t in qt if t not in KNOWN_ABBREVIATIONS
            )
            cap = (ALTERNATE_NAME_CAP if (has_alt and all_alt and not has_abbrev)
                   else ABBREVIATION_CAP)
            has_direct = any(t in set(rt) for t in qt)
            if not has_direct and adj > cap:
                adj = cap
                detail["penalties_applied"].append(
                    f"p3_abbrev_alt_cap: capped at {cap}"
                )

        # ── Penalty 4: Directional excess for single-token result ───────
        if len(rt) == 1:
            r = rt[0]
            if r in qset:
                try:
                    ridx = qt.index(r)
                except ValueError:
                    ridx = -1
                if ridx >= 0:
                    adj_dirs = [
                        t for t in qt
                        if t != r and t in DIRECTIONAL_WORDS
                        and abs(qt.index(t) - ridx) <= 1
                    ]
                    if adj_dirs:
                        pen = min(len(adj_dirs) * 0.15, 0.30)
                        adj *= (1.0 - pen)
                        detail["penalties_applied"].append(
                            f"p4_dir_excess: {adj_dirs}, penalty={pen:.2f}"
                        )

        # ── Penalty 5: Address-noise context dampening ──────────────────
        if adj >= 0.90:
            if len(rt) == 1 and len(qt) == 1:
                r = rt[0]
                if r in qset and q_filtered >= 2:
                    pen = min(q_filtered * 0.12, 0.40)
                    adj *= (1.0 - pen)
                    detail["penalties_applied"].append(
                        f"p5_addr_noise: filtered={q_filtered}, penalty={pen:.2f}"
                    )
            elif len(rt) == 1:
                r = rt[0]
                if r in qset and result_joined in COMMON_WORD_COLLISIONS:
                    geo_vals: Set[str] = set()
                    for exp in KNOWN_ABBREVIATIONS.values():
                        for tok in (exp if isinstance(exp, list) else [exp]):
                            for w in tok.split():
                                geo_vals.add(w)
                    for av in KNOWN_ALTERNATE_NAMES.values():
                        for w in av.split():
                            geo_vals.add(w)

                    extra = [
                        t for t in qt
                        if t != r
                        and t not in STOPWORDS_ADDRESS
                        and t not in DIRECTIONAL_WORDS
                        and t not in geo_vals
                        and t not in KNOWN_ABBREVIATIONS
                        and t not in KNOWN_ALTERNATE_NAMES
                        and len(t) < 7
                    ]
                    if len(extra) >= 2:
                        pen = min(len(extra) * 0.40, 0.45)
                        adj *= (1.0 - pen)
                        detail["penalties_applied"].append(
                            f"p5_collision_extra: '{r}' extra={extra}"
                        )
            elif len(rt) >= 2:
                contiguous = (
                    score_detail.get("sub_scores", {}).get("a_contiguous", 0.0)
                    if score_detail else 0.0
                )
                if contiguous < 1.0:
                    excess = q_prefilter - len(rt)
                    if excess >= 4:
                        pen = min((excess - 3) * 0.04, 0.20)
                        adj *= (1.0 - pen)
                        detail["penalties_applied"].append(
                            f"p5_multi_noise: prefilter={q_prefilter}, penalty={pen:.2f}"
                        )

        # ── Penalty 6: Admin-prefix reduction ───────────────────────────
        if admin_stripped > 0 and adj >= 0.90:
            pen = min(admin_stripped * 0.05, 0.10)
            adj *= (1.0 - pen)
            detail["penalties_applied"].append(
                f"p6_admin: stripped={admin_stripped}, penalty={pen:.2f}"
            )

        return adj, detail

    # ═════════════════════════════════════════════════════════════════════
    # STAGE 6: CLAMP & RETURN
    # ═════════════════════════════════════════════════════════════════════

    @staticmethod
    def _clamp(score: float) -> float:
        """Ensure final score in [0.0, 1.0], rounded to 4 decimal places."""
        clamped = max(0.0, min(1.0, score))
        return round(clamped, 4)
