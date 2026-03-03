# Location Matcher — Implementation Documentation

## Overview

`matcher/location_matcher.py` implements a **fuzzy address-to-location matching engine** that scores how well a query address matches a location name (city/state/country). It returns a confidence score in `[0.0, 1.0]`.

**Public API:**
```python
class LocationMatcher:
    def match(self, query: str, elastic_result: str) -> float: ...
    def get_debug_breakdown(self, query: str, elastic_result: str) -> dict: ...
```

---

## Architecture — 6-Stage Pipeline

```
  Query: "10, Green Apt, Iran"    Result: "Iran"
          │                              │
   ┌──────▼──────────────────────────────▼──────┐
   │  Stage 1: Normalize & Tokenize              │
   │  • Garbage detection                         │
   │  • Unicode NFD → strip combining marks       │
   │  • Lowercase + punctuation cleanup           │
   │  • Delimiter split (/ \ | -)                 │
   │  • Filter numerics, alphanumeric noise       │
   │  • Stopword removal + deduplication          │
   │  Output: qt=["iran"], rt=["iran"]            │
   └──────────────────┬─────────────────────────┘
                      │
   ┌──────────────────▼─────────────────────────┐
   │  Stage 2: Build Token Features              │
   │  • Abbreviation expansion (USA→united,states)│
   │  • Alternate name mapping (bharat→india)     │
   │  Output: enriched query tokens               │
   └──────────────────┬─────────────────────────┘
                      │
   ┌──────────────────▼─────────────────────────┐
   │  Stage 3: Pairwise Token Similarity         │
   │  Priority ladder (best applicable wins):     │
   │  1. Exact equality          → 1.0           │
   │  2. Abbreviation mapping    → 0.88          │
   │  3. Alternate name mapping  → 0.82          │
   │  4. Stem match (≥4 chars)   → 0.70          │
   │  5. Fuzzy (JW + Levenshtein)→ bounded       │
   │  6. Phonetic (Soundex+Meta) → 0.72          │
   │  7. Substring result⊂query  → bounded       │
   │  8. Substring query⊂result  → bounded       │
   └──────────────────┬─────────────────────────┘
                      │
   ┌──────────────────▼─────────────────────────┐
   │  Stage 4: Result-Level Aggregation          │
   │                                              │
   │  Single-token result: MAX strategy           │
   │  • Best matching query token wins            │
   │  • Elevated embedded substring path          │
   │                                              │
   │  Multi-token result: Best of 6 sub-strategies│
   │  (a) Contiguous ordered     → up to 1.0     │
   │  (b) Ordered + noise gaps   → penalized     │
   │  (c) All tokens, wrong order→ reversed pen  │
   │  (d) Partial coverage       → coverage×avg  │
   │  (e) Per-result-token avg   → capped by b/c │
   │  (f) Compound match         → concat check  │
   │  + Directional penalty                       │
   └──────────────────┬─────────────────────────┘
                      │
   ┌──────────────────▼─────────────────────────┐
   │  Stage 5: Contextual Penalties (bounded)    │
   │                                              │
   │  P1: Deep substring          max: ×0.30     │
   │  P1b: Near-miss token        max: ×0.65     │
   │  P2: Commercial/collision    max: ×0.30     │
   │  P3: Abbreviation/alt cap    cap: 0.88      │
   │  P4: Directional excess      max: ×0.70     │
   │  P5: Address-noise dampening max: ×0.55     │
   │  P6: Admin-prefix reduction  max: ×0.90     │
   └──────────────────┬─────────────────────────┘
                      │
   ┌──────────────────▼─────────────────────────┐
   │  Stage 6: Clamp & Return                    │
   │  • Bound to [0.0, 1.0]                      │
   │  • Round to 4 decimal places                 │
   └──────────────────┬─────────────────────────┘
                      │
                      ▼
              Score: 1.0
```

---

## Stage Details

### Stage 1: Normalize & Tokenize

**Garbage Detection:**
- Empty/whitespace-only strings → 0.0
- Known garbage tokens (`n/a`, `unknown`, `na`, `nil`, `none`, `tbd`, `test`) → 0.0
- Pure numeric input (`123456`) → 0.0
- Pure symbols (`@#$%`) → 0.0

**Unicode Normalization:**
- NFD decomposition + strip combining marks (removes accents/diacritics)
- Lowercase conversion
- `Réunion` → `reunion`, `São Paulo` → `sao paulo`, `München` → `munchen`

**Punctuation Cleanup:**
- Split on delimiters: `/`, `\`, `|`, `-`
- Strip: `.`, `,`, `"`, `'`, `(`, `)`, `[`, `]`, `#`, `;`, `:`, `!`, `?`, `{`, `}`
- Collapse whitespace

**Token Filtering:**
- Remove pure numeric tokens from query (`10`, `400001`, `75008`)
- Remove alphanumeric noise from query (`B204`, `SW1A`)
- Remove tokens shorter than 2 characters (except abbreviation-exempt: `s.`, `n.`, `us`, etc.)

**Stopword Removal:**
- Query stopwords: common address words (`street`, `road`, `avenue`, `apartment`, `suite`, `floor`, etc.)
- Protected tokens: any token that appears in the result + all directional words
- Result stopwords: very conservative (only `the` in some contexts)
- `"and"` is NOT blindly stripped — preserved when part of result name

**Deduplication:** Preserve order, remove repeated tokens.

### Stage 2: Build Token Features

**Abbreviation Expansion:**
- `USA` → adds `united`, `states`
- `UK` → adds `united`, `kingdom`
- `UAE` → adds `united`, `arab`, `emirates`
- `CA` → adds `california`
- `NY` → adds `new`, `york`
- `s.` → adds `south`; `n.` → adds `north`

**Alternate Name Mapping:**
- `bharat` → `india`
- `peking` → `beijing`
- `bombay` → `mumbai`
- `calcutta` → `kolkata`
- `deutschland` → `germany`
- `nippon` → `japan`
- `holland` → `netherlands`
- `constantinople` → `istanbul`
- And many more (see `scoring_config.py`)

### Stage 3: Pairwise Token Similarity

For each (query_token, result_token) pair, the priority ladder returns the **first matching** score:

| Priority | Method | Score | Example |
|----------|--------|-------|---------|
| 1 | Exact equality | 1.0 | `"iran"` = `"iran"` |
| 2 | Abbreviation map | 0.88 | `"usa"` → `"united states"` |
| 3 | Alternate name map | 0.82 | `"bharat"` → `"india"` |
| 4 | Stem match (≥4 chars) | 0.70 | `"koreans"` → `"korea"` |
| 5 | Fuzzy (JW ≥ 0.82) | bounded | `"iarn"` → `"iran"` ~0.82 |
| 6 | Phonetic (Soundex/Metaphone) | 0.72 | `"eyran"` → `"iran"` |
| 7 | Substring: result ⊂ query | bounded | `"hirani"` contains `"iran"` |
| 8 | Substring: query ⊂ result | bounded | `"franc"` in `"france"` |

**Fuzzy scoring details:**
- Jaro-Winkler similarity × 0.91 weight
- Edit-distance caps: 0 edits → 0.95, 1 → 0.90, 2 → 0.82, 3 → 0.75
- Length-ratio dampening: `factor = 0.7 + 0.3 × (min_len/max_len)`
- JW skipped when result is a substring of query with ratio < 0.75

**Substring scoring:**
- Minimum result token length: 4 characters
- Prefix/suffix match: `min(0.65 × ratio × 1.6, 0.58)`
- Embedded (mid-word): `min(0.65 × ratio × depth, 0.45)` where depth depends on ratio
- **Elevated embedded path:** When ratio ≥ 0.55, quality = (1.0 + ratio)/2, capped at 0.85
  - E.g., `"hirani"` ↔ `"iran"`: ratio=0.667, quality=0.833 → score ~0.83

### Stage 4: Result-Level Aggregation

**Single-token result:** MAX strategy — the best-matching query token determines the score.

**Multi-token result:** Six sub-strategies compete:

| Sub | Strategy | Example |
|-----|----------|---------|
| (a) | Contiguous ordered | `["north", "korea"]` found in query → 1.0 |
| (b) | Ordered + noise | `["north", "hirani", "korea"]` → penalized per noise word |
| (c) | All matched, wrong order | `"Korea North"` → `"North Korea"` with reversal penalty |
| (d) | Partial coverage | K of M result tokens matched |
| (e) | Per-result-token avg | Average best scores, capped by (b)/(c) |
| (f) | Compound match | `"guineabissau"` = `"guinea"` + `"bissau"` |

**Caps:** When noise exists (b > 0), scores d and e are capped at b. When reversed order (c > 0), d and e are capped at c. This prevents noise/order-ignored paths from scoring higher.

**Directional penalty** (multi-token):
- Result directional contradicted by different query directional → ×(1 - 0.30)
- Result directional absent from query entirely → ×0.85

### Stage 5: Contextual Penalties

All penalties are bounded and applied after evidence scoring:

| # | Penalty | Trigger | Effect | Cap |
|---|---------|---------|--------|-----|
| P1 | Deep substring | Result embedded in query token (not prefix/suffix) | ×0.30 (deep) or ×0.55 (shallow) | Skipped if elevated quality |
| P1b | Near-miss | 1-edit distance, structurally different | ×0.65 | Single application |
| P2 | Commercial context | ≥2 commercial words → strong; ≥1 → moderate | ×0.30 (strong) / ×0.51 (moderate) | — |
| P2 | Collision word | Result in collision list, no exact match | ×0.30 | — |
| P3 | Abbreviation cap | Score from abbreviation/alt-name expansion only | Capped at 0.88/0.82 | Direct match bypasses |
| P4 | Directional excess | Adjacent directional word modifies single-token result | ×(1 - 0.15 per dir) | Max ×0.70 |
| P5 | Address noise | Collision word with ≥2 non-geo extra tokens | ×(1 - 0.40×count) | Max ×0.55 |
| P6 | Admin prefix | Formal admin words stripped (kingdom, republic, state) | ×(1 - 0.05×count) | Max ×0.90 |

### Stage 6: Clamp & Return

- Bound score to `[0.0, 1.0]`
- Round to 4 decimal places
- Return single float

---

## Key Scoring Behaviors

### Exact token in address → ~1.0
When a result token appears **exactly** (after normalization) as a token in the query address, the score is 1.0 before penalties. In most cases, no penalties apply:
```
"204, MG Road, Bangalore, Karnataka, India" → "India"     = 1.0
"221B Baker Street, Los Angeles, CA, USA"   → "USA"       = 1.0
"221B Baker Street, Los Angeles, CA, USA"   → "Los Angeles"= 1.0
```

### Abbreviation expansion → capped at 0.88
```
"USA"  → "United States"     = 0.88
"UK"   → "United Kingdom"    = 0.88
"CA"   → "California"        = 0.88
```

### Alternate names → capped at 0.82
```
"Bharat"  → "India"    = 0.82
"Bombay"  → "Mumbai"   = 0.82 (or 0.88 with context)
```

### Substring containment
```
"Hirani"      → "Iran"    = ~0.83 (elevated embedded)
"Franceville" → "France"  = ~0.47 (prefix, bounded)
"Koreans"     → "Korea"   = 0.70 (stem match)
"Indira"      → "India"   = ~0.54 (near-miss penalized)
```

### False positive suppression
```
"Marine Drive, India"  → "Iran"    = 0.0  (no token match)
"Turkey sandwich shop" → "Turkey"  = 0.30 (commercial penalty)
"Nice apartment"       → "Nice"    = 0.30 (commercial penalty)
```

### Directional handling
```
"North Korea" → "North Korea"   = 1.0  (exact)
"North Korea" → "South Korea"   = ~0.55 (directional mismatch)
"Korea North" → "North Korea"   = ~0.78 (reversed order)
"Western Australia" → "Australia"= ~0.85 (adjacent directional)
```

---

## Dependencies

- **jellyfish** (required): Jaro-Winkler, Levenshtein, Soundex, Metaphone
- **nltk** (required): PorterStemmer
- **Safe fallbacks**: difflib SequenceMatcher for JW, basic DP for Levenshtein

---

## Configuration

All scoring parameters are defined as module-level constants in `location_matcher.py` and can be tuned. Additional configuration (stopwords, abbreviation maps, collision words) is imported from `scoring_config.py`.
