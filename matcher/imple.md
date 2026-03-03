Here's a comprehensive breakdown of all edge cases for your fuzzy name matching algorithm:

---

## 🗺️ Address-to-Location Fuzzy Matching — Complete Edge Case Catalog

---

### **Category 1: Exact & Clean Matches**

| # | Query Address | Elastic Result | Expected Score | Notes |
|---|---|---|---|---|
| 1.1 | `10, Green Apt, Iran` | `Iran` (country) | 1.0 | Perfect token match after stopword removal |
| 1.2 | `Seoul, South Korea` | `South Korea` | 1.0 | Multi-word exact match |
| 1.3 | `Paris, France` | `France` | 1.0 | Clean single token |
| 1.4 | `new york, usa` | `New York` (city) | 1.0 | Case-insensitive match |

---

### **Category 2: Case Variations**

| # | Query | Elastic Result | Expected Score | Notes |
|---|---|---|---|---|
| 2.1 | `IRAN` | `Iran` | 1.0 | All caps |
| 2.2 | `iran` | `Iran` | 1.0 | All lowercase |
| 2.3 | `iRaN` | `Iran` | 1.0 | Mixed case |
| 2.4 | `NORTH KOREA` | `North Korea` | 1.0 | Multi-word caps |

---

### **Category 3: Noise / Irrelevant Words In Between (Your Core Case)**

| # | Query | Elastic Result | Expected Score | Notes |
|---|---|---|---|---|
| 3.1 | `North Hirani Korea` | `North Korea` | ~0.80 | Noise word "Hirani" between tokens — small penalty for gap |
| 3.2 | `South New Korea` | `South Korea` | ~0.75 | Multi-word result broken by noise |
| 3.3 | `New random York` | `New York` (city) | ~0.80 | Classic interleaved noise |
| 3.4 | `Los random random Angeles` | `Los Angeles` | ~0.65 | Multiple noise words |

**Penalty rule:** `score -= noise_word_count * 0.08` (small penalty per noise word, capped so score stays ≥ 0.50)

---

### **Category 4: Substring / Partial Word Match (Your Hirani→Iran Case)**

| # | Query | Elastic Result | Expected Score | Notes |
|---|---|---|---|---|
| 4.1 | `20, Hirani Apt, Blore` | `Iran` | ~0.70–0.75 | "Iran" is substring of "Hirani" — meaningful containment |
| 4.2 | `Franceville` | `France` | ~0.80 | Prefix match — result is clean prefix of query token |
| 4.3 | `Koreans live here` | `Korea` | ~0.80 | Suffix/prefix match — "Korea" is prefix of "Koreans" |
| 4.4 | `Indira Nagar` | `India` | ~0.70 | Partial mid-word match — weaker containment |
| 4.5 | `Koreana restaurant` | `Korea` | ~0.80 | Result is prefix of query token |

**Rule:** Substring match scores moderately high. Prefix match (result is prefix of query token) → ~0.80. Mid-word containment → ~0.70–0.75. Minimum token length of 4 chars required for substring match to qualify.

---

### **Category 5: Word Order Reversal**

| # | Query | Elastic Result | Expected Score | Notes |
|---|---|---|---|---|
| 5.1 | `Korea North` | `North Korea` | ~0.85 | Reversed token order |
| 5.2 | `Korea South` | `South Korea` | ~0.85 | Same |
| 5.3 | `York New` | `New York` | ~0.85 | City name reversed |
| 5.4 | `Arabia Saudi` | `Saudi Arabia` | ~0.85 | |

**Rule:** All tokens matched but out-of-order → small penalty (~0.10–0.15)

---

### **Category 6: Ambiguous Multi-Match (Same Tokens in Multiple Results)**

| # | Query | Elastic Results | Challenge |
|---|---|---|---|
| 6.1 | `Korea North` | `North Korea`, `South Korea` | "Korea" matches both; "North" disambiguates |
| 6.2 | `Georgia` | `Georgia` (US state), `Georgia` (country) | Identical name, different entity types |
| 6.3 | `New York` | `New York` (city), `New York` (state) | Same name, city vs state |
| 6.4 | `North` | `North Korea`, `North Macedonia`, `North Dakota` | Single token matches many |
| 6.5 | `Guinea` | `Guinea`, `Papua New Guinea`, `Equatorial Guinea` | Substring in multiple countries |

**Rule:** Rank by: (1) token coverage %, (2) entity type priority (city > state > country for specificity), (3) token order match

---

### **Category 7: Abbreviations & Acronyms**

| # | Query | Elastic Result | Expected Score | Notes |
|---|---|---|---|---|
| 7.1 | `USA` | `United States` | ~0.90 | Known abbreviation |
| 7.2 | `UK` | `United Kingdom` | ~0.90 | |
| 7.3 | `UAE` | `United Arab Emirates` | ~0.90 | |
| 7.4 | `US` | `United States` | ~0.85 | Shorter abbrev |
| 7.5 | `NY` | `New York` | ~0.85 | State code |
| 7.6 | `CA` | `California`, `Canada` | Ambiguous | Must handle |
| 7.7 | `S. Korea` | `South Korea` | ~0.90 | Abbreviated word |
| 7.8 | `N. Korea` | `North Korea` | ~0.90 | |

**Rule:** Maintain an abbreviation dictionary. Acronym match = high score but slightly below exact.

---

### **Category 8: Typos & Misspellings (Fuzzy Edit Distance)**

| # | Query | Elastic Result | Expected Score | Notes |
|---|---|---|---|---|
| 8.1 | `Iarn` | `Iran` | ~0.85 | Transposition |
| 8.2 | `Frnace` | `France` | ~0.85 | Swap |
| 8.3 | `Koeea` | `Korea` | ~0.80 | 2 char errors |
| 8.4 | `Germny` | `Germany` | ~0.85 | Missing char |
| 8.5 | `Australiaa` | `Australia` | ~0.90 | Extra char |
| 8.6 | `Noth Korea` | `North Korea` | ~0.88 | Typo in first token |

**Rule:** Use Levenshtein or Jaro-Winkler per token. Score = `1 - (edit_distance / max_len)`

---

### **Category 9: Transliterations & Alternate Spellings**

| # | Query | Elastic Result | Expected Score | Notes |
|---|---|---|---|---|
| 9.1 | `Bharat` | `India` | ~0.75 (dict) | Alternate country name |
| 9.2 | `Allemagne` | `Germany` | ~0.75 (dict) | French name for Germany |
| 9.3 | `Munchen` | `Munich` | ~0.80 | German city vs English |
| 9.4 | `Moskva` | `Moscow` | ~0.78 | Transliteration |
| 9.5 | `Peking` | `Beijing` | ~0.78 | Historical/alternate name |
| 9.6 | `Praha` | `Prague` | ~0.78 | Czech vs English |

**Rule:** Maintain alternate names dictionary or use phonetic matching (Soundex/Metaphone)

---

### **Category 10: Special Characters, Diacritics & Unicode**

| # | Query | Elastic Result | Expected Score | Notes |
|---|---|---|---|---|
| 10.1 | `Réunion` | `Reunion` | 1.0 | Accent stripped |
| 10.2 | `São Paulo` | `Sao Paulo` | 1.0 | Tilde stripped |
| 10.3 | `Côte d'Ivoire` | `Cote d Ivoire` | ~0.95 | Apostrophe + accent |
| 10.4 | `Åland` | `Aland` | 1.0 | Scandinavian chars |
| 10.5 | `München` | `Munchen` / `Munich` | ~0.90 | Umlaut |
| 10.6 | `Korea(South)` | `South Korea` | ~0.85 | Parentheses in address |

**Rule:** Normalize unicode → ASCII before matching (NFD decomposition + strip combining chars)

---

### **Category 11: Hyphenated & Compound Names**

| # | Query | Elastic Result | Expected Score | Notes |
|---|---|---|---|---|
| 11.1 | `Guinea-Bissau` | `Guinea-Bissau` | 1.0 | Exact with hyphen |
| 11.2 | `Guinea Bissau` | `Guinea-Bissau` | ~0.95 | Hyphen vs space |
| 11.3 | `GuineaBissau` | `Guinea-Bissau` | ~0.88 | No separator |
| 11.4 | `Timor-Leste` | `Timor Leste` | ~0.95 | Same reverse |
| 11.5 | `Bosnia Herzegovina` | `Bosnia and Herzegovina` | ~0.88 | Missing connector |

**Rule:** Treat `-` same as space when tokenizing. Strip stop-connectors like "and", "the", "of".

---

### **Category 12: Articles, Connectors & Prepositions (Extended Stopwords)**

| # | Query | Elastic Result | Expected Score | Notes |
|---|---|---|---|---|
| 12.1 | `The Gambia` | `Gambia` | ~0.95 | Leading "The" |
| 12.2 | `Republic of Korea` | `South Korea` / `Korea` | ~0.80 | "Republic of" is noise |
| 12.3 | `Kingdom of Saudi Arabia` | `Saudi Arabia` | ~0.90 | Strip "Kingdom of" |
| 12.4 | `State of New York` | `New York` | ~0.90 | "State of" is noise |
| 12.5 | `Province of Quebec` | `Quebec` | ~0.90 | |
| 12.6 | `Bosnia and Herzegovina` | `Bosnia and Herzegovina` | 1.0 | "and" is part of official name! |

**Critical Rule:** "and" is sometimes part of the official name (Bosnia **and** Herzegovina). Don't blindly strip — only strip when not part of elastic result name.

---

### **Category 13: Numbers & Alphanumeric Tokens in Address**

| # | Query | Elastic Result | Expected Score | Notes |
|---|---|---|---|---|
| 13.1 | `10, Green Apt, Iran` | `Iran` | 1.0 | Number "10" ignored |
| 13.2 | `B-204, Korea Tower` | `Korea` | ~0.80 | Alphanumeric token present |
| 13.3 | `400001, Mumbai` | `Mumbai` | 1.0 | Pincode/zipcode noise |
| 13.4 | `P.O. Box 44, France` | `France` | 1.0 | "P.O. Box 44" is noise |

**Rule:** Strip pure numeric tokens and common address format tokens (P.O. Box, #, etc.)

---

### **Category 14: Repeated / Duplicate Tokens**

| # | Query | Elastic Result | Expected Score | Notes |
|---|---|---|---|---|
| 14.1 | `Iran Iran` | `Iran` | 1.0 | Dedup before matching |
| 14.2 | `North North Korea` | `North Korea` | ~0.95 | Repeated word |
| 14.3 | `Korea Korea South` | `South Korea` | ~0.90 | |

---

### **Category 15: Very Short / Single Character Tokens**

| # | Query | Elastic Result | Expected Score | Notes |
|---|---|---|---|---|
| 15.1 | `I ran to Iran` | `Iran` | Needs care | "I" and "ran" separately could false-match |
| 15.2 | `A, B, Iran` | `Iran` | 1.0 | Skip single-char tokens |
| 15.3 | `S. Korea` | `South Korea` | ~0.90 | "S." is abbreviation, not noise |

**Rule:** Skip tokens with length < 2 (after punctuation strip). But `S.` `N.` are special abbreviation cases.

---

### **Category 16: Common Word Collisions (False Positives)**

| # | Query | Elastic Result | Risk | Notes |
|---|---|---|---|---|
| 16.1 | `Marine Drive, India` | `Iran` | FALSE MATCH | "Marine" contains "iran" as substring — needs min length guard |
| 16.2 | `China Cabinet Store` | `China` | FALSE MATCH | "China" is both country and common word |
| 16.3 | `Turkey sandwich` | `Turkey` | FALSE MATCH | Country name = food |
| 16.4 | `Jordan shoes` | `Jordan` | Ambiguous | Brand vs country |
| 16.5 | `Nice apartment` | `Nice` (city, France) | FALSE MATCH | Common adjective |
| 16.6 | `Peru St, Denver` | `Peru` | Risk | Street named after country |

**Rule:** This is the hardest category. Mitigate by: (1) requiring minimum token length (≥4 chars) for substring match to qualify, (2) still penalizing mid-word substring matches vs exact/prefix, (3) using context from surrounding tokens to suppress false positives like "Marine"→"Iran".

---

### **Category 17: Multi-Entity Address (City + State + Country all present)**

| # | Query | Elastic Results | Expected |
|---|---|---|---|
| 17.1 | `Manhattan, New York, USA` | `Manhattan`(city), `New York`(state), `United States`(country) | All 3 match at 1.0 / high score |
| 17.2 | `Austin, Texas, United States` | `Austin`, `Texas`, `United States` | All 3 → 1.0 (exact tokens present) |
| 17.3 | `London, England, UK` | `London`, `England`, `United Kingdom` | `London`→1.0, `England`→1.0, `UK`→0.90 |

**Rule:** Score each elastic result independently against all query tokens. They're not competing — multiple results can score high. If the city/state/country token appears exactly as-is in the query, score = 1.0.

---

### **Category 18: Directional Words as Part of Name**

| # | Query | Elastic Result | Expected Score | Notes |
|---|---|---|---|---|
| 18.1 | `North Korea` | `North Korea` | 1.0 | Direction = part of name |
| 18.2 | `North Korea` | `South Korea` | ~0.55 | "Korea" matches, "North"≠"South" |
| 18.3 | `East Timor` | `Timor-Leste` | ~0.75 | Old name |
| 18.4 | `Western Australia` | `Australia` | ~0.55 | Region vs country |
| 18.5 | `North` | `North Korea`, `North Macedonia` | Multi-match | Partial result |

**Rule:** Directional words (North/South/East/West) carry high weight when part of official name. Don't treat them as stopwords.

---

### **Category 19: Punctuation Variations**

| # | Query | Elastic Result | Score | Notes |
|---|---|---|---|---|
| 19.1 | `Iran.` | `Iran` | 1.0 | Trailing period |
| 19.2 | `"Iran"` | `Iran` | 1.0 | Quoted |
| 19.3 | `Iran,` | `Iran` | 1.0 | Trailing comma |
| 19.4 | `(Iran)` | `Iran` | 1.0 | Parentheses |
| 19.5 | `Iran/Iraq` | `Iran`, `Iraq` | Both 1.0 | Slash-separated — split into tokens, each exact match |

**Rule:** Strip punctuation, split on `/` `\` `|` as potential additional delimiters.

---

### **Category 20: Empty / Garbage Input**

| # | Query | Elastic Result | Expected |
|---|---|---|---|
| 20.1 | `` (empty) | Anything | 0.0 |
| 20.2 | `123456` | Anything | 0.0 | Pure number |
| 20.3 | `@#$%` | Anything | 0.0 | Pure symbols |
| 20.4 | `N/A` | Anything | 0.0 | |
| 20.5 | `Unknown` | Anything | 0.0 | |

---

### **Scoring Formula Summary**
