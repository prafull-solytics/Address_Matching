"""
location_matcher.py — Fuzzy Location Name Matching Engine

Matches a raw address query string against a location name (city/state/country)
and returns a confidence score in [0.0, 1.0].
"""

import logging
import re
import unicodedata
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set, Tuple

import nltk
try:
    from nltk.stem import PorterStemmer
except ImportError as e:
    raise ImportError("NLTK is required. pip install nltk") from e

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    try:
        nltk.download("stopwords", quiet=True)
    except OSError:
        pass

try:
    from jellyfish import jaro_winkler_similarity, levenshtein_distance, metaphone, soundex
except ImportError as e:
    raise ImportError("jellyfish is required. pip install jellyfish") from e

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

_STEMMER = PorterStemmer()
_STRIP_CHARS = set('.,"\'\u2018\u2019\u201c\u201d()[]#;:!?{}')
_SPLIT_PATTERN = re.compile(r"[/|\\-]+")
_PURE_NUMERIC = re.compile(r"^\d+$")
# Alphanumeric noise: single letter + digits (b204) or digits + single letter (204b)
_ALPHANUMERIC_NOISE = re.compile(r"^[a-z]\d+|^\d+[a-z]+$", re.IGNORECASE)


# ─────────────────────────────────────────────────────────────────────────────
# CACHED HELPERS
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=2048)
def _normalize_unicode(text: str) -> str:
    nfd = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn").lower()


@lru_cache(maxsize=2048)
def _get_soundex(token: str) -> str:
    try:
        return soundex(token)
    except Exception:
        return ""


@lru_cache(maxsize=2048)
def _get_metaphone(token: str) -> str:
    try:
        return metaphone(token)
    except Exception:
        return ""


@lru_cache(maxsize=2048)
def _get_stem(token: str) -> str:
    return _STEMMER.stem(token)


@lru_cache(maxsize=2048)
def _jaro_winkler(a: str, b: str) -> float:
    return jaro_winkler_similarity(a, b)


@lru_cache(maxsize=2048)
def _levenshtein(a: str, b: str) -> int:
    return levenshtein_distance(a, b)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CLASS
# ─────────────────────────────────────────────────────────────────────────────

class LocationMatcher:
    """
    Fuzzy location name matching engine. Returns score in [0.0, 1.0].

    Usage:
        matcher = LocationMatcher()
        score = matcher.match("10, Green Apt, Iran", "Iran")    # → 1.0
        score = matcher.match("20, Hirani Apt, Blore", "Iran")  # → ~0.4
    """

    def __init__(self, config: Optional[ScoringConfig] = None) -> None:
        self._cfg: ScoringConfig = config or DEFAULT_CONFIG

    # ── Public API ────────────────────────────────────────────────────────

    def match(self, query: str, elastic_result: str) -> float:
        """Returns float in [0.0, 1.0]. Raises TypeError if inputs are not strings."""
        self._validate(query, elastic_result)
        score, _ = self._run_pipeline(query, elastic_result)
        return score

    def get_debug_breakdown(self, query: str, elastic_result: str) -> Dict[str, Any]:
        """Returns full scoring breakdown dict. Raises TypeError if inputs are not strings."""
        self._validate(query, elastic_result)
        score, debug = self._run_pipeline(query, elastic_result, debug_mode=True)
        debug["final_score"] = score
        return debug

    def _validate(self, query: Any, elastic_result: Any) -> None:
        if not isinstance(query, str):
            raise TypeError(f"query must be str, got {type(query).__name__}")
        if not isinstance(elastic_result, str):
            raise TypeError(f"elastic_result must be str, got {type(elastic_result).__name__}")

    # ── Pipeline ──────────────────────────────────────────────────────────

    def _run_pipeline(
        self, query: str, elastic_result: str, debug_mode: bool = False
    ) -> Tuple[float, Dict[str, Any]]:
        debug: Dict[str, Any] = {"raw_query": query, "raw_result": elastic_result} if debug_mode else {}

        # Step 1 — Garbage detection
        if self._is_garbage(query) or self._is_garbage(elastic_result):
            if debug_mode:
                debug["step1_garbage"] = True
            return 0.0, debug

        # Step 2 — Unicode normalisation
        norm_query = _normalize_unicode(query)
        norm_result = _normalize_unicode(elastic_result)
        if debug_mode:
            debug["step2_normalized"] = {"query": norm_query, "result": norm_result}

        # Quick exact match after normalisation
        if norm_query.strip() == norm_result.strip():
            logger.info("Quick exact match after normalization → 1.0")
            if debug_mode:
                debug["quick_exact_match"] = True
                debug["token_scores"] = [{"query_token": norm_query.strip(), "result_token": norm_result.strip(), "score": 1.0, "method": "exact"}]
            return 1.0, debug

        # Step 3 — Clean punctuation (split on -/|\ , strip .,"'()[]etc)
        clean_query = self._clean_punctuation(norm_query)
        clean_result = self._clean_punctuation(norm_result)
        if debug_mode:
            debug["step3_cleaned"] = {"query": clean_query, "result": clean_result}

        # Step 4 — Tokenise
        query_tokens_raw = self._tokenize(clean_query, is_query=True)
        result_tokens_raw = self._tokenize(clean_result, is_query=False)
        # Count pre-filter tokens for context noise detection
        query_prefilter_count = len(clean_query.split())
        # Count tokens that were explicitly filtered out (numerics, alphanumeric noise, too-short)
        query_filtered_count = query_prefilter_count - len(query_tokens_raw)
        if debug_mode:
            debug["step4_tokens_raw"] = {"query": query_tokens_raw, "result": result_tokens_raw}

        # Step 5 — Stopword removal + dedup
        query_tokens = self._dedup(self._remove_stopwords_query(query_tokens_raw, result_tokens_raw))
        result_tokens = self._dedup(self._remove_stopwords_result(result_tokens_raw))
        if debug_mode:
            debug["step5_after_stopwords"] = {"query": query_tokens, "result": result_tokens}

        if not result_tokens or not query_tokens:
            return 0.0, debug

        # Step 6 — Abbreviation expansion (query only)
        expanded_query = self._expand_abbreviations(query_tokens)
        if debug_mode:
            debug["step6_abbreviation_expanded"] = expanded_query

        # Step 7 — Alternate name mapping (query only)
        enriched_query = self._apply_alternate_names(expanded_query)
        if debug_mode:
            debug["step7_alternate_names"] = enriched_query

        # Track whether any abbreviation or alternate-name expansion was used
        has_abbrev_token = any(t in KNOWN_ABBREVIATIONS for t in query_tokens)
        has_alt_token = any(t in KNOWN_ALTERNATE_NAMES for t in query_tokens)

        # Count administrative prefix words stripped from query
        # (kingdom, republic, state, etc.) — these signal the query is a formal name,
        # not a false positive. We apply a small reduction for the "noise".
        _ADMIN_WORDS = frozenset({"kingdom", "republic", "federation", "commonwealth",
                                   "state", "province", "territory", "prefecture"})
        admin_stripped_count = sum(
            1 for t in clean_query.split()
            if t in _ADMIN_WORDS and t not in set(query_tokens)
        )

        # Step 8 — Core scoring
        if len(result_tokens) == 1:
            raw_score, score_detail = self._score_single_token(
                enriched_query, result_tokens[0], query_tokens_raw, query_tokens
            )
        else:
            raw_score, score_detail = self._score_multi_token(
                enriched_query, result_tokens, query_tokens
            )
        if debug_mode:
            debug["step8_raw_score"] = raw_score
            debug["step8_score_detail"] = score_detail

        # Step 9 — False positive suppression + score caps
        adjusted, fp_detail = self._suppress_false_positives(
            raw_score, enriched_query, query_tokens, result_tokens,
            query_tokens_raw, has_abbrev_token, has_alt_token,
            query_prefilter_count, query_filtered_count, admin_stripped_count
        )
        if debug_mode:
            debug["step9_adjusted_score"] = adjusted
            debug["step9_fp_detail"] = fp_detail

        # Step 10 — Clamp, floor, round
        final = self._finalize(adjusted)
        logger.info("Step 10: Final score for '%s' ↔ '%s' = %.4f", query, elastic_result, final)
        if debug_mode:
            debug["step10_final_score"] = final
            # Build token_scores for test 24.4
            token_scores = []
            for qt in enriched_query:
                for rt in result_tokens:
                    s, d = self._score_token_pair(qt, rt)
                    if s > 0:
                        token_scores.append({
                            "query_token": qt,
                            "result_token": rt,
                            "score": round(s, 4),
                            "method": d.get("method", "none"),
                        })
            debug["token_scores"] = token_scores
            debug["steps"] = {
                "normalized": debug.get("step2_normalized"),
                "tokens": debug.get("step5_after_stopwords"),
                "raw_score": raw_score,
                "adjusted_score": adjusted,
            }

        return final, debug

    # ── Step 1: Garbage ───────────────────────────────────────────────────

    def _is_garbage(self, text: str) -> bool:
        if not text or not text.strip():
            return True
        normalized = _normalize_unicode(text.strip())
        if normalized in GARBAGE_TOKENS:
            return True
        tokens = normalized.split()
        meaningful = [t for t in tokens if t not in GARBAGE_TOKENS and not _PURE_NUMERIC.match(t)]
        return len(meaningful) == 0

    # ── Step 3: Clean punctuation ─────────────────────────────────────────

    def _clean_punctuation(self, text: str) -> str:
        result = _SPLIT_PATTERN.sub(" ", text)
        result = "".join(ch if ch not in _STRIP_CHARS else " " for ch in result)
        return re.sub(r"\s+", " ", result).strip()

    # ── Step 4: Tokenise ──────────────────────────────────────────────────

    def _tokenize(self, text: str, is_query: bool) -> List[str]:
        min_len = self._cfg.MIN_TOKEN_LENGTH
        out = []
        for token in text.split():
            if is_query and _PURE_NUMERIC.match(token):
                continue
            # Skip alphanumeric noise tokens from query (B204, SW1A etc.)
            if is_query and _ALPHANUMERIC_NOISE.match(token) and token not in ABBREVIATION_EXEMPT_TOKENS:
                continue
            if len(token) < min_len and token not in ABBREVIATION_EXEMPT_TOKENS:
                continue
            out.append(token)
        return out

    # ── Step 5: Stopwords + dedup ─────────────────────────────────────────

    def _remove_stopwords_query(
        self, query_tokens: List[str], result_tokens: List[str]
    ) -> List[str]:
        protected = set(result_tokens) | DIRECTIONAL_WORDS
        return [t for t in query_tokens if t not in STOPWORDS_ADDRESS or t in protected]

    def _remove_stopwords_result(self, result_tokens: List[str]) -> List[str]:
        return [t for t in result_tokens if t not in STOPWORDS_RESULT]

    def _dedup(self, tokens: List[str]) -> List[str]:
        seen: Set[str] = set()
        out = []
        for t in tokens:
            if t not in seen:
                seen.add(t)
                out.append(t)
        return out

    # ── Step 6: Abbreviation expansion ───────────────────────────────────

    def _expand_abbreviations(self, tokens: List[str]) -> List[str]:
        expanded = list(tokens)
        for token in tokens:
            if token in KNOWN_ABBREVIATIONS:
                expansion = KNOWN_ABBREVIATIONS[token]
                for exp in (expansion if isinstance(expansion, list) else [expansion]):
                    for sub in exp.split():
                        if sub not in expanded:
                            expanded.append(sub)
        return expanded

    # ── Step 7: Alternate names ───────────────────────────────────────────

    def _apply_alternate_names(self, tokens: List[str]) -> List[str]:
        enriched = list(tokens)
        # Single-token alternate names only (e.g. bharat→india, peking→beijing)
        for token in tokens:
            if token in KNOWN_ALTERNATE_NAMES:
                for sub in KNOWN_ALTERNATE_NAMES[token].split():
                    if sub not in enriched:
                        enriched.append(sub)
        return enriched

    # ── Step 8a: Single-token result ─────────────────────────────────────

    def _score_single_token(
        self,
        query_tokens: List[str],
        result_token: str,
        query_tokens_raw: List[str],
        query_tokens_clean: List[str],
    ) -> Tuple[float, Dict[str, Any]]:
        """
        MAX strategy: best-matching query token determines the score.
        Tracks which method produced the best score for downstream capping.
        """
        best_score = 0.0
        best_detail: Dict[str, Any] = {}

        for qt in query_tokens:
            score, detail = self._score_token_pair(qt, result_token)
            if score > best_score:
                best_score = score
                best_detail = {
                    "matched_query_token": qt,
                    "result_token": result_token,
                    **detail,
                }
            if best_score >= 1.0:
                break

        return best_score, best_detail

    # ── Step 8b: Multi-token result ───────────────────────────────────────

    def _score_multi_token(
        self,
        query_tokens: List[str],
        result_tokens: List[str],
        query_tokens_clean: List[str],
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Five sub-methods, best wins:
          (a) Contiguous ordered        → up to 1.0
          (b) Ordered with noise gaps   → penalised per noise word
          (c) All tokens, wrong order   → reversed-order penalty
          (d) K of M tokens matched     → coverage × avg × weight
          (e) Per-result-token average  → capped by (b) when noise exists

        Cap rule: when (b) finds all tokens with noise words, (e) cannot exceed (b).
        This stops "North Hirani Korea" scoring 1.0 for "North Korea".
        """
        detail: Dict[str, Any] = {"sub_scores": {}}

        score_a = self._score_contiguous_ordered(query_tokens, result_tokens)
        detail["sub_scores"]["a_contiguous"] = round(score_a, 4)

        score_b, noise_count = self._score_ordered_with_noise(query_tokens, result_tokens)
        detail["sub_scores"]["b_ordered_noise"] = round(score_b, 4)
        detail["sub_scores"]["b_noise_count"] = noise_count

        score_c = self._score_unordered(query_tokens, result_tokens)
        detail["sub_scores"]["c_unordered"] = round(score_c, 4)

        score_d, k, m = self._score_partial_coverage(query_tokens, result_tokens)
        detail["sub_scores"]["d_partial"] = round(score_d, 4)
        detail["sub_scores"]["d_k_of_m"] = f"{k}/{m}"

        score_e = self._score_per_result_token_avg(query_tokens, result_tokens)
        if score_b > 0.0 and noise_count > 0:
            # Cap score_d and score_e when noise tokens are present between result tokens.
            # Without this, "North Hirani Korea → North Korea" scores 1.0 via score_d.
            score_e = min(score_e, score_b)
            score_d = min(score_d, score_b)
        if score_c > 0.0:
            # Cap score_d and score_e when tokens are in wrong order.
            # Without this, "Korea North → North Korea" scores 1.0 via score_d.
            score_e = min(score_e, score_c)
            score_d = min(score_d, score_c)
        detail["sub_scores"]["e_fuzzy"] = round(score_e, 4)

        # (f) Compound match: single query token = all result tokens concatenated
        #     "GuineaBissau" → ["guinea", "bissau"]: concat = "guineabissau" = query_token
        score_f = self._score_compound_match(query_tokens, result_tokens)
        detail["sub_scores"]["f_compound"] = round(score_f, 4)

        best = max(score_a, score_b, score_c, score_d, score_e, score_f)
        best_method = max(
            [("a", score_a), ("b", score_b), ("c", score_c), ("d", score_d), ("e", score_e), ("f", score_f)],
            key=lambda x: x[1],
        )[0]
        detail["best_sub_method"] = best_method

        best = self._apply_directional_penalty(best, query_tokens, result_tokens)
        detail["after_directional_penalty"] = round(best, 4)

        return best, detail

    # ── Sub-scoring methods ───────────────────────────────────────────────

    def _score_contiguous_ordered(
        self, query_tokens: List[str], result_tokens: List[str]
    ) -> float:
        r_len = len(result_tokens)
        for i in range(len(query_tokens) - r_len + 1):
            window = query_tokens[i: i + r_len]
            if window == result_tokens:
                return 1.0
            if all(self._tokens_fuzzy_match(w, r) for w, r in zip(window, result_tokens)):
                # Use _score_token_pair for proper edit-cap + length-factor scoring
                pair_scores = [
                    self._score_token_pair(w, r)[0] if w != r else 1.0
                    for w, r in zip(window, result_tokens)
                ]
                return min(pair_scores)
        return 0.0

    def _score_ordered_with_noise(
        self, query_tokens: List[str], result_tokens: List[str]
    ) -> Tuple[float, int]:
        cfg = self._cfg
        positions: List[int] = []
        match_qualities: List[float] = []
        search_start = 0

        for rt in result_tokens:
            found = False
            for i in range(search_start, len(query_tokens)):
                if self._tokens_fuzzy_match(query_tokens[i], rt):
                    positions.append(i)
                    q = _jaro_winkler(query_tokens[i], rt) if query_tokens[i] != rt else 1.0
                    match_qualities.append(q)
                    search_start = i + 1
                    found = True
                    break
            if not found:
                return 0.0, 0

        noise_count = 0
        if len(positions) >= 2:
            for idx in range(len(positions) - 1):
                noise_count += positions[idx + 1] - positions[idx] - 1

        if noise_count == 0:
            avg_q = sum(match_qualities) / len(match_qualities)
            return 1.0 * avg_q, 0

        penalty = min(
            noise_count * cfg.NOISE_WORD_PENALTY_PER_WORD,
            cfg.MULTI_TOKEN_NOISE_MAX_PENALTY,
        )
        avg_quality = sum(match_qualities) / len(match_qualities)
        return 1.0 * (1.0 - penalty) * avg_quality, noise_count

    def _score_unordered(
        self, query_tokens: List[str], result_tokens: List[str]
    ) -> float:
        cfg = self._cfg
        matched_positions: List[int] = []
        used: Set[int] = set()
        match_qualities: List[float] = []

        for rt in result_tokens:
            best_idx, best_sim = -1, 0.0
            for i, qt in enumerate(query_tokens):
                if i in used:
                    continue
                if qt == rt:
                    best_idx, best_sim = i, 1.0
                    break
                sim = _jaro_winkler(qt, rt)
                if sim >= cfg.FUZZY_MATCH_THRESHOLD and sim > best_sim:
                    best_idx, best_sim = i, sim
            if best_idx == -1:
                return 0.0
            matched_positions.append(best_idx)
            used.add(best_idx)
            match_qualities.append(best_sim)

        # If already in order, let (a)/(b) own it
        if all(
            matched_positions[i] < matched_positions[i + 1]
            for i in range(len(matched_positions) - 1)
        ):
            return 0.0

        avg_quality = sum(match_qualities) / len(match_qualities)
        return 1.0 * (1.0 - cfg.REVERSED_ORDER_PENALTY) * avg_quality

    def _score_partial_coverage(
        self, query_tokens: List[str], result_tokens: List[str]
    ) -> Tuple[float, int, int]:
        m = len(result_tokens)
        matched_scores: List[float] = []

        for rt in result_tokens:
            best = 0.0
            for qt in query_tokens:
                s, _ = self._score_token_pair(qt, rt)
                if s > best:
                    best = s
            if best > 0.0:
                matched_scores.append(best)

        k = len(matched_scores)
        if k == 0:
            return 0.0, 0, m
        coverage = k / m
        avg = sum(matched_scores) / k
        return coverage * avg * self._cfg.PARTIAL_TOKEN_COVERAGE_WEIGHT, k, m

    # Connector words in result names that are optional for matching
    _OPTIONAL_RESULT_CONNECTORS = frozenset({"and", "the", "of", "al", "el"})

    def _score_per_result_token_avg(
        self, query_tokens: List[str], result_tokens: List[str]
    ) -> float:
        """Average of best-score per result token.
        Connector tokens (and/the/of) in the result are treated as optional —
        they don't penalise coverage when absent from the query.
        """
        per_token: List[float] = []
        optional_zeros = 0
        for rt in result_tokens:
            best = 0.0
            for qt in query_tokens:
                s, _ = self._score_token_pair(qt, rt)
                if s > best:
                    best = s
            per_token.append(best)
            if best == 0.0 and rt in self._OPTIONAL_RESULT_CONNECTORS:
                optional_zeros += 1

        # Count truly missing tokens (exclude optional connectors with 0 score)
        nonzero = [s for s in per_token if s > 0]
        zero_non_optional = sum(
            1 for i, s in enumerate(per_token)
            if s == 0.0 and result_tokens[i] not in self._OPTIONAL_RESULT_CONNECTORS
        )

        if zero_non_optional == 0:
            # All mandatory tokens matched — average only over them
            mandatory_scores = [
                s for i, s in enumerate(per_token)
                if result_tokens[i] not in self._OPTIONAL_RESULT_CONNECTORS or s > 0
            ]
            base = sum(mandatory_scores) / len(mandatory_scores) if mandatory_scores else 0.0
            # If any optional connectors were missing, slightly reduce
            missing_optional = sum(
                1 for i, s in enumerate(per_token)
                if s == 0.0 and result_tokens[i] in self._OPTIONAL_RESULT_CONNECTORS
            )
            return base * (1.0 - 0.05 * missing_optional)

        if not nonzero:
            return 0.0
        # Some mandatory tokens missing — penalise coverage
        mandatory_total = sum(
            1 for rt in result_tokens if rt not in self._OPTIONAL_RESULT_CONNECTORS
        )
        mandatory_matched = sum(
            1 for i, s in enumerate(per_token)
            if s > 0 and result_tokens[i] not in self._OPTIONAL_RESULT_CONNECTORS
        )
        coverage = mandatory_matched / mandatory_total if mandatory_total > 0 else 0.0
        avg = sum(nonzero) / len(nonzero)
        return coverage * avg * self._cfg.PARTIAL_TOKEN_COVERAGE_WEIGHT

    def _score_compound_match(
        self, query_tokens: List[str], result_tokens: List[str]
    ) -> float:
        """
        Detect compound token: a single query token equals all result tokens joined.
        e.g. query=["guineabissau"], result=["guinea","bissau"] → "guineabissau"=="guinea"+"bissau"
        Returns COMPOUND_TOKEN_MATCH_SCORE (slightly below exact) to indicate a likely valid compound match.
        """
        if len(query_tokens) != 1:
            return 0.0
        qt = query_tokens[0]
        concatenated = "".join(result_tokens)
        if qt == concatenated:
            return self._cfg.COMPOUND_TOKEN_MATCH_SCORE
        # Also try fuzzy: allow minor spelling variation in the compound
        if len(concatenated) >= 4:
            jw = _jaro_winkler(qt, concatenated)
            if jw >= 0.90:
                return self._cfg.COMPOUND_TOKEN_MATCH_SCORE * jw
        return 0.0

    # ── Token pair scoring ────────────────────────────────────────────────

    def _score_token_pair(
        self, query_token: str, result_token: str
    ) -> Tuple[float, Dict]:
        """
        Priority ladder:
          1. Exact                     → 1.0
          2. Abbreviation match        → ABBREVIATION_MATCH_SCORE (0.88)
          3. Alternate name match      → ALTERNATE_NAME_MATCH_SCORE (0.82)
          4. Stem match (≥4 chars)     → STEM_MATCH_SCORE (0.70)
          5. Jaro-Winkler ≥ threshold  → scaled, hard cap 0.95
          6. Phonetic (Soundex+MPhn)   → PHONETIC_MATCH_SCORE (0.72)
          7. result ⊂ query_token      → penalised, max 0.45
          8. query_token ⊂ result      → penalised, max 0.40
        """
        cfg = self._cfg

        if query_token == result_token:
            return 1.0, {"method": "exact"}

        if query_token in KNOWN_ABBREVIATIONS:
            expansion = KNOWN_ABBREVIATIONS[query_token]
            for exp in (expansion if isinstance(expansion, list) else [expansion]):
                if result_token in exp.split():
                    return cfg.ABBREVIATION_MATCH_SCORE, {"method": "abbreviation", "expansion": exp}

        if query_token in KNOWN_ALTERNATE_NAMES:
            if result_token in KNOWN_ALTERNATE_NAMES[query_token].split():
                return cfg.ALTERNATE_NAME_MATCH_SCORE, {"method": "alternate_name"}

        if len(query_token) >= 4 and len(result_token) >= 4:
            if _get_stem(query_token) == _get_stem(result_token):
                return cfg.STEM_MATCH_SCORE, {"method": "stem_match"}

        # Skip JW scoring when result is a prefix/substring of query AND tokens
        # differ substantially in length — let substring scoring give a lower score.
        # Also skip JW for very short query tokens against much longer result tokens.
        _skip_jw = (
            (
                len(result_token) >= cfg.FALSE_POSITIVE_SUBSTRING_MIN_LENGTH
                and result_token in query_token
                and len(result_token) / len(query_token) < 0.75
            ) or (
                len(query_token) <= 2 and len(result_token) >= 4
            )
        )

        jw = _jaro_winkler(query_token, result_token)
        if not _skip_jw and jw >= cfg.FUZZY_MATCH_THRESHOLD:
            edit_dist = _levenshtein(query_token, result_token)
            ed_score = cfg.TYPO_EDIT_DISTANCE_WEIGHTS.get(
                min(edit_dist, cfg.MAX_TYPO_EDIT_DISTANCE), 0.0
            )
            # Cap decreases with edit distance: 0 edits→0.95, 1→0.90, 2→0.82, 3→0.75
            edit_cap = cfg.FUZZY_EDIT_DISTANCE_CAPS.get(min(edit_dist, 3), 0.75)
            # Length-ratio dampening: when one token is much longer, reduce confidence
            len_ratio = min(len(query_token), len(result_token)) / max(len(query_token), len(result_token))
            length_factor = 0.7 + 0.3 * len_ratio  # 0.7 when very different, 1.0 when equal
            fuzzy_score = min(
                max(jw * cfg.JARO_WINKLER_WEIGHT, ed_score * 0.9) * length_factor,
                edit_cap,
            )
            return fuzzy_score, {"method": "jaro_winkler", "jw": round(jw, 4), "edit_distance": edit_dist}

        phonetic = self._phonetic_score(query_token, result_token)
        if phonetic > 0.0:
            return phonetic, {"method": "phonetic"}

        # Substring: result ⊂ query_token  (e.g. "iran" inside "hirani")
        if (
            len(result_token) >= cfg.FALSE_POSITIVE_SUBSTRING_MIN_LENGTH
            and result_token in query_token
            and query_token != result_token
        ):
            ratio = len(result_token) / len(query_token)
            if query_token.startswith(result_token) or query_token.endswith(result_token):
                # Prefix/suffix match (franceville→france, koreans→korea): moderate score
                sub_score = min(
                    cfg.SUBSTRING_RESULT_IN_QUERY_SCORE * ratio * 1.6,
                    cfg.SUBSTRING_RESULT_PREFIX_SUFFIX_MAX_SCORE,
                )
            else:
                # Embedded in middle (hirani→iran, indira→india): low-moderate score
                depth = 1.0 if ratio > 0.75 else (0.75 if ratio > 0.5 else 0.45)
                sub_score = min(
                    cfg.SUBSTRING_RESULT_IN_QUERY_SCORE * ratio * depth,
                    cfg.SUBSTRING_RESULT_EMBEDDED_MAX_SCORE,
                )
            return sub_score, {"method": "substring_result_in_query", "ratio": round(ratio, 4)}

        # Substring: query_token ⊂ result  (e.g. "franc" inside "france")
        if (
            len(query_token) >= cfg.FALSE_POSITIVE_SUBSTRING_MIN_LENGTH
            and query_token in result_token
            and query_token != result_token
        ):
            ratio = len(query_token) / len(result_token)
            sub_score = min(
                cfg.SUBSTRING_QUERY_IN_RESULT_SCORE * ratio,
                cfg.SUBSTRING_QUERY_IN_RESULT_MAX_SCORE,
            )
            return sub_score, {"method": "substring_query_in_result", "ratio": round(ratio, 4)}

        return 0.0, {"method": "none"}

    def _phonetic_score(self, a: str, b: str) -> float:
        if len(a) < 3 or len(b) < 3:
            return 0.0
        sa, sb = _get_soundex(a), _get_soundex(b)
        ma, mb = _get_metaphone(a), _get_metaphone(b)
        sdx = bool(sa and sb and sa == sb)
        mtn = bool(ma and mb and ma == mb)
        if sdx and mtn:
            return self._cfg.PHONETIC_MATCH_SCORE
        if sdx or mtn:
            return self._cfg.PHONETIC_MATCH_SCORE * self._cfg.PARTIAL_PHONETIC_MATCH_MULTIPLIER
        return 0.0

    def _tokens_fuzzy_match(self, a: str, b: str) -> bool:
        if a == b:
            return True
        if a in KNOWN_ABBREVIATIONS:
            exp = KNOWN_ABBREVIATIONS[a]
            for e in (exp if isinstance(exp, list) else [exp]):
                if b in e.split():
                    return True
        if a in KNOWN_ALTERNATE_NAMES and b in KNOWN_ALTERNATE_NAMES[a].split():
            return True
        return _jaro_winkler(a, b) >= self._cfg.FUZZY_MATCH_THRESHOLD

    # ── Directional penalty ───────────────────────────────────────────────

    def _apply_directional_penalty(
        self, score: float, query_tokens: List[str], result_tokens: List[str]
    ) -> float:
        """
        Only penalise when a result directional word is CONTRADICTED by a different
        directional in the query. If the result directional is simply absent from the
        query (no directional at all), apply only a mild reduction.
        """
        cfg = self._cfg
        result_dirs = [t for t in result_tokens if t in DIRECTIONAL_WORDS]
        if not result_dirs:
            return score

        query_dirs = {t for t in query_tokens if t in DIRECTIONAL_WORDS}
        query_set = set(query_tokens)

        for rd in result_dirs:
            if rd in query_set:
                continue  # matched — no penalty
            if query_dirs:
                # A different directional is present → strong mismatch
                score *= (1.0 - cfg.DIRECTIONAL_MISMATCH_PENALTY)
                break
            else:
                # No directional in query → mild reduction
                score *= cfg.DIRECTIONAL_WORD_WEIGHT
                break

        return score

    # ── Step 9: False positive suppression ───────────────────────────────

    def _suppress_false_positives(
        self,
        score: float,
        enriched_query: List[str],
        query_tokens: List[str],
        result_tokens: List[str],
        query_tokens_raw: List[str],
        has_abbrev_token: bool,
        has_alt_token: bool,
        query_prefilter_count: int = 1,
        query_filtered_count: int = 0,
        admin_stripped_count: int = 0,
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Rule 1 — Deep substring: result embedded in a longer query token → strong penalty.
        Rule 2 — Common word collision: result is a known ambiguous word with context.
        Rule 3 — Abbreviation/alternate-name cap: prevent inflated scores from expansions.
        Rule 4 — Compound word split: "GuineaBissau" should match "Guinea-Bissau" at moderate score.
        """
        cfg = self._cfg
        detail: Dict[str, Any] = {"penalties_applied": []}
        adjusted = score
        query_set = set(enriched_query)

        # Rule 1: Deep substring (single-token result only)
        # Only applies when result is NOT a prefix of the query token AND score is high.
        # This rule is designed to bring down inflated fuzzy/JW scores for tokens like
        # "marine"→"iran" (JW≈0.85 but it's a false match). It does NOT further penalise
        # already-low substring scores.
        if len(result_tokens) == 1 and adjusted >= 0.35:
            rt = result_tokens[0]
            if rt not in query_set:
                for qt in enriched_query:
                    if rt in qt and qt != rt and len(qt) > len(rt):
                        is_prefix_match = qt.startswith(rt)
                        is_suffix_match = qt.endswith(rt)
                        if not is_prefix_match and not is_suffix_match:
                            ratio = len(rt) / len(qt)
                            if ratio < 0.65:
                                adjusted *= 0.30
                                detail["penalties_applied"].append(f"deep_substring: '{rt}' in '{qt}' ratio={ratio:.2f}")
                            else:
                                adjusted *= 0.55
                                detail["penalties_applied"].append(f"shallow_substring: '{rt}' in '{qt}' ratio={ratio:.2f}")
                        break

        # Rule 1b: Near-miss token penalty
        # When single-token result is NOT found in query tokens BUT a query token is
        # very similar (1 edit distance) AND longer, apply a penalty.
        # "Indira"→"India": indira/india edit_dist=1, len(indira)>len(india) → penalty
        # "Australiaa"→"Australia": australia IS prefix of australiaa → skip (it's a typo)
        # "Iarn"→"Iran": iarn/iran edit_dist=2 → no penalty here
        if len(result_tokens) == 1 and adjusted >= 0.45:
            rt = result_tokens[0]
            if rt not in query_set and len(rt) >= 4:
                for qt in enriched_query:
                    if qt != rt and len(qt) > len(rt):
                        ed = _levenshtein(qt, rt)
                        if ed == 1:
                            length_diff = len(qt) - len(rt)
                            # Skip if result is a prefix/suffix of query token (typo case)
                            is_prefix = qt.startswith(rt)
                            is_suffix = qt.endswith(rt)
                            if length_diff >= 1 and not is_prefix and not is_suffix:
                                adjusted *= 0.50
                                detail["penalties_applied"].append(
                                    f"near_miss: '{rt}' vs '{qt}' ed=1"
                                )
                                break
        # Rule 2: Commercial/Collision word detection
        # Case B fires first: commercial context words in query → penalise ANY result
        # Case A fires only: result in COMMON_WORD_COLLISIONS AND no commercial context
        _ADDRESS_STRUCTURE_WORDS = frozenset({
            "street", "st", "road", "rd", "avenue", "ave", "boulevard", "blvd",
            "lane", "ln", "drive", "dr", "way", "highway", "hwy", "parkway", "pkwy",
            "marg", "nagar",
        })
        has_address_structure = any(t in _ADDRESS_STRUCTURE_WORDS for t in query_tokens_raw)
        result_joined = " ".join(result_tokens)
        result_token_set = set(result_tokens)
        raw_set = set(query_tokens_raw)

        commercial_count = sum(
            1 for t in query_tokens_raw
            if t not in result_token_set and t in COMMERCIAL_CONTEXT_WORDS
        )

        if commercial_count >= 2:
            # Strong commercial: "China Cabinet Store", "Turkey sandwich shop", "Jordan shoes store"
            adjusted *= (1.0 - cfg.COMMON_WORD_COLLISION_PENALTY)
            detail["penalties_applied"].append(f"commercial_strong: count={commercial_count}")
        elif commercial_count >= 1:
            # Moderate commercial: one commercial word
            adjusted *= (1.0 - cfg.COMMON_WORD_COLLISION_PENALTY * 0.70)
            detail["penalties_applied"].append(f"commercial_moderate: count={commercial_count}")
        elif result_joined in COMMON_WORD_COLLISIONS:
            # Case A: known ambiguous word with no commercial context
            has_exact_token = any(rt in raw_set for rt in result_tokens)
            if not has_exact_token:
                adjusted *= (1.0 - cfg.COMMON_WORD_COLLISION_PENALTY)
                detail["penalties_applied"].append(f"collision_no_exact: '{result_joined}'")
            elif not has_address_structure:
                # No address structure → check for non-geo context
                non_geo_raw = [
                    t for t in query_tokens_raw
                    if t not in result_token_set
                    and not _PURE_NUMERIC.match(t)
                    and t not in KNOWN_ABBREVIATIONS
                    and t not in DIRECTIONAL_WORDS
                    and t not in STOPWORDS_ADDRESS
                ]
                if len(non_geo_raw) >= 2:
                    adjusted *= (1.0 - cfg.COMMON_WORD_COLLISION_PENALTY * 0.50)
                    detail["penalties_applied"].append(f"collision_non_geo: '{result_joined}'")
                elif len(non_geo_raw) >= 1:
                    extra_context = [t for t in query_tokens_raw if t not in result_token_set]
                    if len(extra_context) >= 2:
                        adjusted *= (1.0 - cfg.COMMON_WORD_COLLISION_PENALTY * 0.25)
                        detail["penalties_applied"].append(f"collision_mild: '{result_joined}'")

        # Rule 3: Abbreviation / alternate-name score cap
        if has_abbrev_token or has_alt_token:
            # Use appropriate cap: alt-names get ALTERNATE_NAME_MATCH_SCORE, abbrevs get ABBREVIATION_MATCH_SCORE
            all_alt = all(t in KNOWN_ALTERNATE_NAMES for t in query_tokens if t not in KNOWN_ABBREVIATIONS)
            cap = cfg.ALTERNATE_NAME_MATCH_SCORE if (has_alt_token and all_alt and not has_abbrev_token) else cfg.ABBREVIATION_MATCH_SCORE
            result_set = set(result_tokens)
            has_direct_match = any(
                t in result_set
                for t in query_tokens
                if t not in KNOWN_ABBREVIATIONS and t not in KNOWN_ALTERNATE_NAMES
            )
            if not has_direct_match and adjusted > cap:
                adjusted = cap
                detail["penalties_applied"].append(
                    f"abbrev_alt_cap: no direct token match, capped at {cap}"
                )

        # Rule 4: Excess regional context penalty (single-token result)
        # Only applies when directional words are present as extra tokens.
        # Non-directional extra tokens (Bangalore, India) don't reduce confidence.
        # "Western Australia → Australia": western is directional → penalty
        # "MG Road, Bangalore, Karnataka → Karnataka": no directionals → no penalty
        if len(result_tokens) == 1:
            rt = result_tokens[0]
            if rt in query_set:
                directional_extras = [
                    t for t in query_tokens
                    if t != rt and t in DIRECTIONAL_WORDS
                ]
                if directional_extras:
                    penalty = min(len(directional_extras) * 0.30, 0.45)
                    adjusted *= (1.0 - penalty)
                    detail["penalties_applied"].append(
                        f"directional_excess: {directional_extras}, penalty={penalty:.2f}"
                    )

        # Rule 5: Address-noise context dampening
        # For single-token results: fires when numeric/alphanumeric tokens were filtered.
        # For multi-token results: fires when match is in a much longer noisy query.
        if adjusted >= 0.90:
            if len(result_tokens) == 1 and len(query_tokens) == 1:
                rt = result_tokens[0]
                if rt in query_set and query_filtered_count >= 2:
                    noise_penalty = min(query_filtered_count * 0.12, 0.40)
                    adjusted *= (1.0 - noise_penalty)
                    detail["penalties_applied"].append(
                        f"address_noise: filtered={query_filtered_count}, penalty={noise_penalty:.2f}"
                    )
            elif len(result_tokens) == 1:
                # Single-token result in a multi-token query — penalise if the result is
                # a known collision word AND there are extra non-stopword tokens around it
                # that are NOT known geographic place names.
                rt = result_tokens[0]
                if rt in query_set and result_joined in COMMON_WORD_COLLISIONS:
                    # Build a set of known place name values (from abbreviations + alt names)
                    known_geo_values: Set[str] = set()
                    for exp in KNOWN_ABBREVIATIONS.values():
                        for tok in (exp if isinstance(exp, list) else [exp]):
                            for w in tok.split():
                                known_geo_values.add(w)
                    for alt_val in KNOWN_ALTERNATE_NAMES.values():
                        for w in alt_val.split():
                            known_geo_values.add(w)

                    extra_clean = [
                        t for t in query_tokens
                        if t != rt
                        and t not in STOPWORDS_ADDRESS
                        and t not in DIRECTIONAL_WORDS
                        and t not in known_geo_values  # skip known geo tokens like "beijing"
                        and len(t) < 7               # skip long tokens likely to be place names
                    ]
                    if len(extra_clean) >= 1:
                        collision_penalty = min(len(extra_clean) * 0.40, 0.45)
                        adjusted *= (1.0 - collision_penalty)
                        detail["penalties_applied"].append(
                            f"collision_extra_context: '{rt}' extra={extra_clean}"
                        )
            elif len(result_tokens) >= 2:
                # Multi-token result: penalise when query is much longer than result
                result_len = len(result_tokens)
                excess_tokens = query_prefilter_count - result_len
                if excess_tokens >= 4:
                    noise_penalty = min((excess_tokens - 3) * 0.04, 0.20)
                    adjusted *= (1.0 - noise_penalty)
                    detail["penalties_applied"].append(
                        f"multi_token_noise: prefilter={query_prefilter_count}, result_len={result_len}, penalty={noise_penalty:.2f}"
                    )

        # Rule 6: Admin-prefix penalty
        # When formal admin words (kingdom, republic, state) were stripped from the query,
        # apply a small reduction to indicate this is a formal name, not a perfect match.
        # "Kingdom of Saudi Arabia → Saudi Arabia": kingdom stripped → slight reduction
        # "Saudi Arabia → Saudi Arabia": nothing stripped → no reduction
        if admin_stripped_count > 0 and adjusted >= 0.90:
            admin_penalty = min(admin_stripped_count * 0.05, 0.10)
            adjusted *= (1.0 - admin_penalty)
            detail["penalties_applied"].append(
                f"admin_prefix: stripped={admin_stripped_count}, penalty={admin_penalty:.2f}"
            )

        return adjusted, detail

    # ── Step 10: Finalise ─────────────────────────────────────────────────

    def _finalize(self, score: float) -> float:
        cfg = self._cfg
        clamped = max(0.0, min(1.0, score))
        if clamped < cfg.SCORE_FLOOR:
            return 0.0
        return round(clamped, cfg.SCORE_PRECISION)


# ─────────────────────────────────────────────────────────────────────────────
# DEMO / MAIN
# ─────────────────────────────────────────────────────────────────────────────
