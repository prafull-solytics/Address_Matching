# Location Matcher — End-to-End Flow & Configuration Guide

## Overview

The **Location Matcher** is a fuzzy address-matching engine that scores how
well a raw query address string matches an Elastic search result.  It returns
a confidence score in **[0.0 → 1.0]**.

The system handles:
- Intentional and accidental typos (`"Irann"`, `"Ruusia"`)
- Abbreviations and codes (`"IRI"`, `"DPRK"`, `"RU"`)
- Alternate/local names (`"Persia"` for Iran, `"Rossiya"` for Russia)
- Non-Latin scripts (Arabic, Cyrillic, CJK — scored 0.0 if no token overlap, harmless)
- Multi-variant Elastic objects (a result with a primary name plus dozens of aliases)

---

## File Structure

```
Address_Matching/
├── main.py                  Entry point — delegates to run_tests.py
├── run_tests.py             Score all 200 cases → test_results.xlsx
├── main_test_cases.py       200 real-world test cases (Iran / DPRK / Syria / Cuba / Russia)
├── test_results.xlsx        Generated output (200 rows + Summary sheet)
├── matcher/
│   ├── __init__.py          Public API exports + trace_stages() utility
│   ├── location_matcher.py  Core 6-stage scoring pipeline
│   └── scoring_config.py    All tunable constants, penalties, word lists
├── test_edge_cases.py       174 edge-case unit tests (do NOT modify)
├── generate_test_tables.py  Extracts edge-case table → test_cases.xlsx / .md
└── IMPLEMENTATION.md        Algorithm design documentation
```

---

## Scoring Pipeline (6 Stages)

```
Query string
     │
     ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 1 — Normalize & Tokenize                                       │
│  • Unicode NFD normalization, lowercase, strip punctuation            │
│  • Split on whitespace + separators (/ | \ -)                         │
│  • Remove pure numerics (postcodes, house numbers)                    │
│  • Remove ADDRESS stopwords from query (street, apt, building…)       │
│  • Remove RESULT stopwords from result (republic, kingdom…)           │
└──────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 2 — Token Feature Enrichment                                   │
│  • Expand abbreviations: "usa" → "united states"                      │
│  • Attach alternate names: "uk" → "united kingdom"                    │
│  • Flag admin words stripped from query (republic, kingdom…)          │
└──────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 3 — Pairwise Token Similarity                                  │
│  For each (query_token, result_token) pair, try in order:             │
│    1. Exact match                    → 1.00                           │
│    2. Abbreviation expansion match   → 0.88                           │
│    3. Alternate name match           → 0.82                           │
│    4. Stem match (Porter stemmer)    → 0.70                           │
│    5. Jaro-Winkler fuzzy match       → 0.82–0.95 (threshold ≥ 0.82)  │
│    6. Substring result-in-query      → 0.45–0.85                      │
│    7. Phonetic (Metaphone/Soundex)   → 0.72                           │
│    8. Substring query-in-result      → 0.40                           │
└──────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 4 — Result-Level Aggregation                                   │
│  Single-token result → MAX over all query tokens                      │
│  Multi-token result  → best of six sub-strategies:                    │
│    a) Contiguous ordered match                                        │
│    b) Ordered with noise gaps (penalised per noise word)              │
│    c) All tokens present but wrong order (reversed-order penalty)     │
│    d) Partial coverage (k/m tokens matched)                           │
│    e) Per-result-token average                                        │
│    f) Compound: single query token = concatenation of result          │
│  Then apply directional penalty (North/South/East/West mismatch)      │
└──────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 5 — Contextual Penalties                                       │
│  P1: Deep substring (result embedded in longer query token)           │
│  P2: Commercial / collision word detection                            │
│  P3: Abbreviation / alternate-name score cap                          │
│  P5: Address-noise context dampening (skipped for exact matches)      │
│  P6: Admin-prefix reduction (republic, kingdom in query)              │
└──────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 6 — Clamp & Return                                             │
│  • Clamp to [0.0, 1.0], round to 4 decimal places                    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Variant Scoring (for Elastic Result Objects)

Real Elastic results carry a primary name **plus** aliases and abbreviation
codes.  Use `score_with_variants()` to score the query against **all** of
them in parallel and return the maximum:

```python
from matcher import score_with_variants

score, debug = score_with_variants(
    query   = "Unit 4B, Tehran, 14567, Kirana",
    name    = "Iran",
    aliases = ["Islamic Republic of Iran", "Persia", "IRI", "ایران"],
    codes   = ["IR", "IRN"],
)
# score = 1.0  (matched via "Tehran" which is exact in the alias list)
# debug["best_variant"] = "Tehran"
# debug["all_scores"]   = {"Iran": 0.83, "Tehran": 1.0, "IRI": 0.64, ...}
```

For processing many results at once:

```python
from matcher import score_batch

results = score_batch("Persia, Tehran", [
    {"name": "Iran",   "aliases": ["Persia", "IRI"], "codes": ["IR", "IRN"]},
    {"name": "Iraq",   "aliases": ["Al-Iraq"],        "codes": ["IQ"]},
])
# results[0] = (1.0, {...})   # matched "Persia" exact
# results[1] = (0.0, {...})   # no match
```

---

## How to Run the Test Suite

```bash
# Generate test_results.xlsx from the 200 test cases
python main.py

# Or directly
python run_tests.py --verbose          # with per-case console output
python run_tests.py --out my_run.xlsx  # custom output file
```

The Excel file has two sheets:
- **Test Results** — 200 rows with all scoring details
- **Summary** — high / medium / low counts and average score

---

## Score Interpretation

| Score     | Tier   | Colour | Meaning                                               |
|-----------|--------|--------|-------------------------------------------------------|
| ≥ 0.75    | HIGH   | Green  | Strong match; high confidence                         |
| 0.40–0.74 | MEDIUM | Amber  | Partial match; possible typo, abbreviation, or alias  |
| < 0.40    | LOW    | Red    | Weak match; likely different location or noise query  |

---

## Edge-Case Configuration Guide

The following table maps common edge-case patterns to the configuration
knob(s) to adjust in **`matcher/scoring_config.py → ScoringConfig`**.

### 1. Directional Words (North/South/East/West)

| Scenario | Observed | Config to Change | Recommended |
|----------|----------|-----------------|-------------|
| Query "Western Australia" vs result "Australia" scores < 1.0 | P4 directional excess fires | **Already fixed** — P4 removed | — |
| Query "Korea" vs result "North Korea" scores too harshly | `DIR_ABSENT_FROM_RESULT_WEIGHT` too low | `DIRECTIONAL_ABSENT_FROM_RESULT_WEIGHT` | Raise towards `1.0` |
| "North Korea" vs "South Korea" scores too generously | `DIRECTIONAL_MISMATCH_PENALTY` too low | `DIRECTIONAL_MISMATCH_PENALTY` | Raise towards `0.30` |

### 2. Commercial / Noise Penalty (P2)

| Scenario | Observed | Config to Change | Recommended |
|----------|----------|-----------------|-------------|
| "Shop 15, Ahvaz Mall, Ahvaz…" vs "Ahvaz" scores ~0.30 | P2 commercial strong fires (shop + mall = 2 tokens) | `COMMON_WORD_COLLISION_PENALTY` | Lower to `0.50` to be less aggressive |
| "Office 7, Tehran" vs "Tehran" scores 0.51 instead of 1.0 | P2 commercial moderate fires (office = 1 token) | Remove `"office"` from `COMMERCIAL_CONTEXT_WORDS` | `"office"` is an address component, not commercial signal |
| Real commercial noise ("China Cabinet Store" vs "China") should still be caught | — | Add `"cabinet"`, `"store"` to `COMMERCIAL_CONTEXT_WORDS` | Keep as-is |

**To disable P2 for legitimate office addresses**, remove `"office"` and `"ofc"` from `COMMERCIAL_CONTEXT_WORDS` in `scoring_config.py`.

### 3. Typos and Fuzzy Matching

| Scenario | Observed | Config to Change | Recommended |
|----------|----------|-----------------|-------------|
| "Iraan" (2 extra chars) scores < 0.8 | Edit distance > threshold | `FUZZY_MATCH_THRESHOLD` | Lower to `0.78` (more permissive) |
| Short abbreviations like "NK" fuzzy-match wrong tokens | JW similarity too permissive for short tokens | Add to `ABBREVIATION_EXEMPT_TOKENS` | Exempt single/double-char tokens from fuzzy |
| "Irrn" (transposition) not matched at all | Levenshtein distance cap | `MAX_TYPO_EDIT_DISTANCE` | Raise to `4` |

### 4. Address Noise Dampening (P5)

| Scenario | Observed | Config to Change | Recommended |
|----------|----------|-----------------|-------------|
| "10, Green Apt, Iran" vs "Iran" scores < 1.0 | P5 addr-noise fires on filtered tokens | **Already fixed** — P5 skipped for exact matches | — |
| Very long noisy address unfairly penalised for multi-token result | P5 multi-token noise | `MULTI_TOKEN_NOISE_MAX_PENALTY` | Lower from `0.65` to `0.40` |

### 5. Admin Prefix Words (P6)

| Scenario | Observed | Config to Change | Recommended |
|----------|----------|-----------------|-------------|
| "Islamic Republic of Iran" query vs "Iran" result scores slightly below 1.0 | P6 admin-word penalty | **Already relaxed** — rate `0.02`, cap `0.04` | — |
| Still seeing minor drop from "Republic of" prefix | `STOPWORDS_ADDRESS` | Add `"islamic"` to STOPWORDS_ADDRESS | It is already stripped from query |

### 6. Substring Scoring

| Scenario | Observed | Config to Change | Recommended |
|----------|----------|-----------------|-------------|
| "Hirani" query → "Iran" result scores ~0.83 (elevated substr) | This is correct elevated path | — | — |
| Short result token (< 4 chars) embedded in query → false positive | `FALSE_POSITIVE_SUBSTRING_MIN_LENGTH` | Raise to `5` | Prevents e.g. "ira" matching in "tirane" |
| Substring score cap feels too generous | `ELEVATED_SUBSTRING_MAX_SCORE` | Lower from `0.85` to `0.78` | |

### 7. Phonetic Matching

| Scenario | Observed | Config to Change | Recommended |
|----------|----------|-----------------|-------------|
| "Corea" doesn't phonetically match "Korea" (no jellyfish) | `jellyfish` not installed | Install: `pip install jellyfish` | Required for phonetic stage |
| Phonetic score too generous | `PHONETIC_MATCH_SCORE` | Lower from `0.72` to `0.65` | |

### 8. Non-Latin Scripts

| Scenario | Observed | Config to Change | Recommended |
|----------|----------|-----------------|-------------|
| Arabic/Cyrillic aliases (e.g. `"ایران"`, `"Россия"`) score 0.0 | Latin-only queries → 0.0 is correct (max-score logic means harmless) | — | Pass transliterated alias too |
| CJK city name in query should match CJK alias | Unicode normalization strips diacritics only, not CJK | Pass CJK alias in `aliases` list; if query is also CJK, exact match fires | — |

---

## Debugging a Single Case

Use `trace_stages()` for a full per-stage breakdown:

```python
from matcher import trace_stages
trace_stages("Shop 15, Ahvaz Mall, Ahvaz Street, Ahvaz, Iran", "Ahvaz")
```

Or call `get_debug_breakdown()` directly:

```python
from matcher import LocationMatcher
m = LocationMatcher()
dbg = m.get_debug_breakdown("Floor 1, Office Complex, Tehran, Ir-an", "Tehran")
print(dbg["stage5_penalties"]["penalties_applied"])
# ['p2_commercial_moderate: count=1']
```

---

## Updating Configuration

All constants live in `matcher/scoring_config.py` inside the frozen
`ScoringConfig` dataclass.  To change a value for a one-off run without
editing the file:

```python
from matcher.scoring_config import ScoringConfig
from matcher import LocationMatcher

cfg = ScoringConfig(COMMON_WORD_COLLISION_PENALTY=0.50)
m = LocationMatcher(cfg)
score = m.match("Office 7, Tehran", "Tehran")
```

Or pass the same config to `score_with_variants`:

```python
from matcher import score_with_variants
from matcher.scoring_config import ScoringConfig

cfg = ScoringConfig(DIRECTIONAL_MISMATCH_PENALTY=0.10)
score, debug = score_with_variants("North Korea", "South Korea", config=cfg)
```

---

## Test Results Summary (200 cases)

| Tier       | Count | Percentage |
|------------|-------|------------|
| HIGH ≥ 0.75  | 142   | 71 %        |
| MEDIUM 0.40–0.74 | 51 | 25.5 %   |
| LOW < 0.40  | 7     | 3.5 %       |

The 7 LOW-score cases are all caused by strong commercial context signals
in the query (words like **shop**, **mall**, **market**, **center**) combined with
the result being a single-token city name.  This is correct algorithm
behaviour — those queries look like commercial entity names, not pure addresses.
If you want to reduce this, lower `COMMON_WORD_COLLISION_PENALTY` or remove
`"mall"` / `"center"` / `"market"` from `COMMERCIAL_CONTEXT_WORDS`.
