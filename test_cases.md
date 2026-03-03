# LocationMatcher — Test Cases

> Auto-generated from `test_edge_cases.py`  

> Total test cases: **204**

---


## EC-1 — AbbreviationAmbiguity

*8 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_ca_to_california` | `CA` | `California` | [0.8, 0.92] |  |
| 2 | `test_ca_to_canada` | `CA` | `Canada` | [0.8, 0.92] |  |
| 3 | `test_ca_ambiguous_equal` | `CA` | `California` | see test |  |
| 4 | `test_ca_ambiguous_equal` | `CA` | `Canada` | see test |  |
| 5 | `test_il_abbreviation` | `IL` | `Illinois` | [0.8, 0.92] |  |
| 6 | `test_tx_abbreviation` | `TX` | `Texas` | [0.8, 0.92] |  |
| 7 | `test_dc_abbreviation` | `DC` | `District of Columbia` | [0.8, 0.92] |  |
| 8 | `test_abbreviation_in_address` | `123 Main St, Springfield, IL` | `Illinois` | [0.8, 0.92] |  |

## EC-2 — CompoundConcatenated

*6 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_newyork_no_space` | `NewYork` | `New York` | [0.75, 0.9] |  |
| 2 | `test_sanfrancisco_no_space` | `SanFrancisco` | `San Francisco` | [0.75, 0.9] |  |
| 3 | `test_southkorea_no_space` | `SouthKorea` | `South Korea` | [0.6, 0.85] |  |
| 4 | `test_compound_beats_no_match` | `NewYork` | `New York` | compound > nomatch |  |
| 5 | `test_compound_beats_no_match` | `Abcdefg` | `New York` | compound > nomatch |  |
| 6 | `test_guineabissau_compound` | `GuineaBissau` | `Guinea-Bissau` | [0.75, 0.92] |  |

## EC-3 — GarbageVariations

*13 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_dashes_only` | `---` | `Iran` | == 0.0 |  |
| 2 | `test_dots_only` | `...` | `Iran` | == 0.0 |  |
| 3 | `test_nil_token` | `nil` | `Iran` | == 0.0 |  |
| 4 | `test_tbd_token` | `TBD` | `Iran` | == 0.0 |  |
| 5 | `test_test_token` | `test` | `Iran` | == 0.0 |  |
| 6 | `test_none_raises_type_error` | `None` | `Iran` | raises TypeError |  |
| 7 | `test_int_raises_type_error` | `123` | `Iran` | raises TypeError |  |
| 8 | `test_result_none_raises` | `Iran` | `None` | raises TypeError |  |
| 9 | `test_empty_string_both` | `` | `` | == 0.0 |  |
| 10 | `test_single_space` | ` ` | `Iran` | == 0.0 |  |
| 11 | `test_tab_whitespace` | `	 ` | `Iran` | == 0.0 |  |
| 12 | `test_pure_symbols` | `!@#$%^&*()` | `Iran` | == 0.0 |  |
| 13 | `test_mixed_garbage_number` | `999 888 777` | `Iran` | [0.0, 0.05] |  |

## EC-4 — UnicodeExtended

*6 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_all_caps_diacritics` | `CÔTE D'IVOIRE` | `Cote Ivoire` | [0.85, 1.0] |  |
| 2 | `test_all_caps_tilde` | `SÃO PAULO` | `Sao Paulo` | [0.9, 1.0] |  |
| 3 | `test_umlaut_city` | `Zürich` | `Zurich` | [0.9, 1.0] |  |
| 4 | `test_polish_chars` | `Łódź` | `Lodz` | [0.7, 1.0] |  |
| 5 | `test_turkish_char` | `İstanbul` | `Istanbul` | [0.9, 1.0] |  |
| 6 | `test_french_cedilla` | `Français` | `Francais` | [0.9, 1.0] |  |

## EC-5 — ResultLongerThanQuery

*9 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_korea_vs_north_korea` | `Korea` | `North Korea` | [0.35, 0.55] |  |
| 2 | `test_york_vs_new_york` | `York` | `New York` | [0.4, 0.6] |  |
| 3 | `test_arabia_vs_saudi_arabia` | `Arabia` | `Saudi Arabia` | [0.4, 0.6] |  |
| 4 | `test_guinea_vs_papua_new_guinea` | `Guinea` | `Papua New Guinea` | [0.2, 0.5] |  |
| 5 | `test_full_beats_partial` | `North Korea` | `North Korea` | full > partial |  |
| 6 | `test_full_beats_partial` | `Korea` | `North Korea` | full > partial |  |
| 7 | `test_papua_new_guinea_exact` | `Papua New Guinea` | `Papua New Guinea` | [0.95, 1.0] |  |
| 8 | `test_papua_guinea_partial` | `Papua Guinea` | `Papua New Guinea` | [0.55, 0.8] |  |
| 9 | `test_north_partial_vs_north_korea` | `North` | `North Korea` | [0.65, 0.85] |  |

## EC-6 — CollisionContextDetection

*14 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_turkey_geo_context` | `Turkey, Istanbul` | `Turkey` | [0.95, 1.0] |  |
| 2 | `test_china_geo_context` | `China, Beijing` | `China` | [0.95, 1.0] |  |
| 3 | `test_jordan_geo_context` | `Jordan, Amman` | `Jordan` | [0.95, 1.0] |  |
| 4 | `test_georgia_geo_context` | `Georgia, USA` | `Georgia` | [0.95, 1.0] |  |
| 5 | `test_turkey_food_context` | `Turkey sandwich shop` | `Turkey` | [0.0, 0.35] |  |
| 6 | `test_china_furniture_context` | `China Cabinet Store, LA` | `China` | [0.0, 0.35] |  |
| 7 | `test_jordan_brand_context` | `Jordan shoes store` | `Jordan` | [0.0, 0.4] |  |
| 8 | `test_nice_adjective_context` | `Nice apartment for rent` | `Nice` | [0.0, 0.4] |  |
| 9 | `test_geo_beats_commercial_turkey` | `Turkey, Istanbul` | `Turkey` | geo > com |  |
| 10 | `test_geo_beats_commercial_turkey` | `Turkey sandwich shop` | `Turkey` | geo > com |  |
| 11 | `test_geo_beats_commercial_china` | `China, Beijing` | `China` | geo > com |  |
| 12 | `test_geo_beats_commercial_china` | `China Cabinet Store, LA` | `China` | geo > com |  |
| 13 | `test_geo_beats_commercial_jordan` | `Jordan, Amman` | `Jordan` | geo > com |  |
| 14 | `test_geo_beats_commercial_jordan` | `Jordan shoes store` | `Jordan` | geo > com |  |

## EC-7 — AlternateNamesContext

*10 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_bombay_with_india` | `Bombay, Maharashtra, India` | `Mumbai` | [0.78, 0.92] |  |
| 2 | `test_calcutta_with_india` | `Calcutta, West Bengal, India` | `Kolkata` | [0.78, 0.92] |  |
| 3 | `test_constantinople_with_turkey` | `Constantinople, Turkey` | `Istanbul` | [0.78, 0.92] |  |
| 4 | `test_deutschland_simple` | `Deutschland` | `Germany` | [0.75, 0.9] |  |
| 5 | `test_nippon_simple` | `Nippon` | `Japan` | [0.75, 0.9] |  |
| 6 | `test_holland_simple` | `Holland` | `Netherlands` | [0.75, 0.9] |  |
| 7 | `test_exact_beats_alternate` | `India` | `India` | exact > alt |  |
| 8 | `test_exact_beats_alternate` | `Bharat` | `India` | exact > alt |  |
| 9 | `test_exact_beats_alternate_city` | `Mumbai` | `Mumbai` | exact > alt |  |
| 10 | `test_exact_beats_alternate_city` | `Bombay` | `Mumbai` | exact > alt |  |

## EC-8 — SubstringEdgeCases

*8 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_parisian_vs_paris` | `Parisian cafe` | `Paris` | [0.2, 0.5] |  |
| 2 | `test_pakistani_vs_pakistan` | `Pakistani market` | `Pakistan` | [0.3, 0.55] |  |
| 3 | `test_american_vs_america` | `American food` | `America` | [0.3, 0.55] |  |
| 4 | `test_dparis_vs_paris` | `DParis Hotel` | `Paris` | [0.3, 0.55] |  |
| 5 | `test_exact_beats_substring` | `Paris, France` | `Paris` | exact > sub |  |
| 6 | `test_exact_beats_substring` | `Parisian cafe` | `Paris` | exact > sub |  |
| 7 | `test_short_token_guard` | `Bird sanctuary near lake` | `Ir` | [0.0, 0.25] |  |
| 8 | `test_iran_not_in_marine` | `Marine Drive, India` | `Iran` | [0.0, 0.15] |  |

## EC-9 — VeryLongAddresses

*9 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_usa_in_long` | `Suite 500, 100 Broadway, Floor 12, Manhattan, New York, NY, 10005, USA` | `USA` | [0.95, 1.0] |  |
| 2 | `test_manhattan_in_long` | `Suite 500, 100 Broadway, Floor 12, Manhattan, New York, NY, 10005, USA` | `Manhattan` | [0.95, 1.0] |  |
| 3 | `test_new_york_in_long` | `Suite 500, 100 Broadway, Floor 12, Manhattan, New York, NY, 10005, USA` | `New York` | [0.95, 1.0] |  |
| 4 | `test_india_in_long` | `Flat 1, 2nd Floor, Building A, Green Complex, MG Road, Koramangala, Bangalore, Karnataka, India, 560001` | `India` | [0.95, 1.0] |  |
| 5 | `test_bangalore_in_long` | `Flat 1, 2nd Floor, Building A, Green Complex, MG Road, Koramangala, Bangalore, Karnataka, India, 560001` | `Bangalore` | [0.95, 1.0] |  |
| 6 | `test_karnataka_in_long` | `Flat 1, 2nd Floor, Building A, Green Complex, MG Road, Koramangala, Bangalore, Karnataka, India, 560001` | `Karnataka` | [0.95, 1.0] |  |
| 7 | `test_london_in_long` | `Flat 3, 27 Baker St, London W1U 8EW, United Kingdom` | `London` | [0.95, 1.0] |  |
| 8 | `test_absent_city_in_long` | `Suite 500, 100 Broadway, Floor 12, Manhattan, New York, NY, 10005, USA` | `Tokyo` | [0.0, 0.05] |  |
| 9 | `test_absent_country_in_long` | `Flat 1, 2nd Floor, Building A, Green Complex, MG Road, Koramangala, Bangalore, Karnataka, India, 560001` | `China` | [0.0, 0.05] |  |

## EC-10 — ScatteredTokens

*7 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_scattered_north_korea` | `Korea, officially North, country` | `North Korea` | [0.55, 0.97] |  |
| 2 | `test_reversed_order_simple` | `Korea North` | `North Korea` | [0.72, 0.97] |  |
| 3 | `test_reversed_with_extra_tokens` | `Korea is a great place, North` | `North Korea` | [0.3, 0.97] |  |
| 4 | `test_ordered_beats_reversed` | `North Korea` | `North Korea` | ordered > reversed_ |  |
| 5 | `test_ordered_beats_reversed` | `Korea North` | `North Korea` | ordered > reversed_ |  |
| 6 | `test_reversed_beats_absent` | `Korea North` | `North Korea` | reversed_ > absent |  |
| 7 | `test_reversed_beats_absent` | `Tokyo Japan` | `North Korea` | reversed_ > absent |  |

## EC-11 — ExactTokenPresence

*15 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_exact_token_high` | `Paris, France` | `France` | >= 0.95 | France in Paris addr |
| 2 | `test_exact_token_high` | `Berlin, Germany` | `Germany` | >= 0.95 | Germany in Berlin addr |
| 3 | `test_exact_token_high` | `Tokyo, Japan` | `Japan` | >= 0.95 | Japan in Tokyo addr |
| 4 | `test_exact_token_high` | `Mumbai, India` | `India` | >= 0.95 | India in Mumbai addr |
| 5 | `test_exact_token_high` | `Cairo, Egypt` | `Egypt` | >= 0.95 | Egypt in Cairo addr |
| 6 | `test_exact_token_high` | `Lima, Peru` | `Peru` | >= 0.95 | Peru in Lima addr |
| 7 | `test_exact_token_high` | `Beijing, China` | `Beijing` | >= 0.95 | Beijing exact |
| 8 | `test_exact_token_high` | `Moscow, Russia` | `Russia` | >= 0.95 | Russia exact |
| 9 | `test_exact_token_high` | `Sydney, Australia` | `Australia` | >= 0.95 | Australia exact |
| 10 | `test_seoul_with_directional_adjacent` | `Seoul, South Korea` | `Seoul` | [0.78, 0.9] |  |
| 11 | `test_absent_token_zero` | `Paris, France` | `Germany` | <= 0.05 | Germany NOT in Paris addr |
| 12 | `test_absent_token_zero` | `Berlin, Germany` | `France` | <= 0.05 | France NOT in Berlin addr |
| 13 | `test_absent_token_zero` | `Tokyo, Japan` | `China` | <= 0.05 | China NOT in Tokyo addr |
| 14 | `test_absent_token_zero` | `Mumbai, India` | `Pakistan` | <= 0.05 | Pakistan NOT in Mumbai addr |
| 15 | `test_absent_token_zero` | `Seoul, South Korea` | `Japan` | <= 0.05 | Japan NOT in Seoul addr |

## EC-12 — DirectionalEdgeCases

*6 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_north_vs_south_korea_low` | `North Korea` | `South Korea` | [0.35, 0.6] |  |
| 2 | `test_east_vs_west` | `East Africa` | `West Africa` | [0.5, 0.95] |  |
| 3 | `test_directional_present_exact` | `North Korea` | `North Korea` | [0.95, 1.0] |  |
| 4 | `test_no_directional_vs_directional_result` | `Korea` | `North Korea` | [0.35, 0.55] |  |
| 5 | `test_adjacent_directional_penalty` | `Western Australia` | `Australia` | [0.75, 0.9] |  |
| 6 | `test_non_adjacent_directional_no_penalty` | `South Mumbai, Maharashtra, India` | `India` | [0.95, 1.0] |  |

## EC-13 — HyphenConnector

*6 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_hyphen_split_exact` | `Guinea-Bissau` | `Guinea-Bissau` | [0.92, 1.0] |  |
| 2 | `test_space_vs_hyphen` | `Guinea Bissau` | `Guinea-Bissau` | [0.88, 1.0] |  |
| 3 | `test_missing_and_connector` | `Bosnia Herzegovina` | `Bosnia and Herzegovina` | [0.8, 0.95] |  |
| 4 | `test_and_preserved_in_exact` | `Bosnia and Herzegovina` | `Bosnia and Herzegovina` | [0.92, 1.0] |  |
| 5 | `test_trinidad_and_tobago` | `Trinidad and Tobago` | `Trinidad and Tobago` | [0.92, 1.0] |  |
| 6 | `test_trinidad_tobago_no_and` | `Trinidad Tobago` | `Trinidad and Tobago` | [0.8, 0.95] |  |

## EC-14 — ArticlePrefixStripping

*5 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_the_gambia` | `The Gambia` | `Gambia` | [0.88, 1.0] |  |
| 2 | `test_kingdom_of_stripped` | `Kingdom of Saudi Arabia` | `Saudi Arabia` | [0.8, 0.95] |  |
| 3 | `test_state_of_stripped` | `State of New York` | `New York` | [0.8, 0.95] |  |
| 4 | `test_province_of_stripped` | `Province of Quebec` | `Quebec` | [0.82, 1.0] |  |
| 5 | `test_republic_of_partially` | `Republic of Korea` | `South Korea` | [0.4, 0.65] |  |

## EC-15 — TypoExtended

*9 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_transposition` | `Iarn` | `Iran` | [0.78, 0.88] |  |
| 2 | `test_missing_char` | `Germny` | `Germany` | [0.8, 0.92] |  |
| 3 | `test_extra_char` | `Australiaa` | `Australia` | [0.8, 0.92] |  |
| 4 | `test_swap_chars` | `Frnace` | `France` | [0.75, 0.9] |  |
| 5 | `test_multi_word_typo` | `Noth Korea` | `North Korea` | [0.78, 0.99] |  |
| 6 | `test_exact_beats_typo` | `Iran` | `Iran` | exact > typo |  |
| 7 | `test_exact_beats_typo` | `Iarn` | `Iran` | exact > typo |  |
| 8 | `test_1edit_beats_2edit` | `Germny` | `Germany` | one >= two * 0.9 |  |
| 9 | `test_1edit_beats_2edit` | `Grmany` | `Germany` | one >= two * 0.9 |  |

## EC-16 — DebugContract

*6 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_returns_dict` | `—` | `—` | see test |  |
| 2 | `test_has_final_score` | `—` | `—` | see test |  |
| 3 | `test_score_matches_match` | `Hirani` | `Iran` | see test |  |
| 4 | `test_has_token_scores_or_steps` | `—` | `—` | see test |  |
| 5 | `test_garbage_detected` | `—` | `—` | == 0.0 |  |
| 6 | `test_multi_token_debug` | `—` | `—` | >= 0.95 |  |

## EC-17 — ScoreOrdering

*18 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_exact_beats_abbreviation` | `United States` | `United States` | exact > abbrev |  |
| 2 | `test_exact_beats_abbreviation` | `USA` | `United States` | exact > abbrev |  |
| 3 | `test_exact_beats_alternate` | `Germany` | `Germany` | exact > alt |  |
| 4 | `test_exact_beats_alternate` | `Deutschland` | `Germany` | exact > alt |  |
| 5 | `test_exact_beats_fuzzy` | `France` | `France` | exact > fuzzy |  |
| 6 | `test_exact_beats_fuzzy` | `Frnace` | `France` | exact > fuzzy |  |
| 7 | `test_exact_token_beats_substring` | `Tehran, Iran` | `Iran` | exact > substr |  |
| 8 | `test_exact_token_beats_substring` | `Hirani` | `Iran` | exact > substr |  |
| 9 | `test_geo_context_beats_commercial` | `Paris, France` | `Paris` | geo > com |  |
| 10 | `test_geo_context_beats_commercial` | `Nice apartment for rent` | `Nice` | geo > com |  |
| 11 | `test_full_match_beats_partial` | `South Korea` | `South Korea` | full > partial |  |
| 12 | `test_full_match_beats_partial` | `Korea` | `South Korea` | full > partial |  |
| 13 | `test_clean_beats_noisy` | `Tehran, Iran` | `Iran` | clean > noisy |  |
| 14 | `test_clean_beats_noisy` | `Marine Irani Rd` | `Iran` | clean > noisy |  |
| 15 | `test_ordered_beats_reversed` | `North Korea` | `North Korea` | ordered > reversed_ |  |
| 16 | `test_ordered_beats_reversed` | `Korea North` | `North Korea` | ordered > reversed_ |  |
| 17 | `test_short_address_beats_long_for_exact` | `Iran` | `Iran` | short >= long |  |
| 18 | `test_short_address_beats_long_for_exact` | `10, Green Apt, Iran` | `Iran` | short >= long |  |

## EC-18 — PhoneticMatching

*4 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_eyran_iran` | `Eyran` | `Iran` | [0.55, 0.85] |  |
| 2 | `test_corea_korea` | `Corea` | `Korea` | [0.65, 0.88] |  |
| 3 | `test_phonetic_below_exact` | `Iran` | `Iran` | exact > phonetic |  |
| 4 | `test_phonetic_below_exact` | `Eyran` | `Iran` | exact > phonetic |  |

## EC-19 — MultiEntityIndependent

*8 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_all_three_high` | `addr` | `Manhattan` | >= 0.85 |  |
| 2 | `test_all_three_high` | `addr` | `New York` | >= 0.85 |  |
| 3 | `test_all_three_high` | `addr` | `United States` | >= 0.85 |  |
| 4 | `test_both_city_and_country_high` | `Paris, France` | `Paris` | >= 0.88 |  |
| 5 | `test_both_city_and_country_high` | `Paris, France` | `France` | >= 0.88 |  |
| 6 | `test_city_state_country_indian` | `addr` | `Bangalore` | >= 0.95 |  |
| 7 | `test_city_state_country_indian` | `addr` | `Karnataka` | >= 0.95 |  |
| 8 | `test_city_state_country_indian` | `addr` | `India` | >= 0.95 |  |

## EC-20 — PunctuationExtended

*9 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_slash_splits_both` | `Iran/Iraq` | `Iran` | >= 0.85 |  |
| 2 | `test_slash_splits_both` | `Iran/Iraq` | `Iraq` | >= 0.85 |  |
| 3 | `test_pipe_separator` | `France\|Germany` | `France` | [0.85, 1.0] |  |
| 4 | `test_backslash_separator` | `Korea\Japan` | `Korea` | [0.85, 1.0] |  |
| 5 | `test_semicolon_stripped` | `Iran;` | `Iran` | [0.92, 1.0] |  |
| 6 | `test_exclamation_stripped` | `Iran!` | `Iran` | [0.92, 1.0] |  |
| 7 | `test_brackets_stripped` | `[Iran]` | `Iran` | [0.92, 1.0] |  |
| 8 | `test_dot_as_separator` | `North.Korea` | `North Korea` | [0.8, 1.0] |  |
| 9 | `test_comma_no_space` | `Paris,France` | `France` | [0.88, 1.0] |  |

## EC-21 — ModerateCommercial

*4 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_victoria_secret` | `Victoria Secret outlet` | `Victoria` | [0.4, 0.7] |  |
| 2 | `test_panama_hat` | `Panama hat shop` | `Panama` | [0.4, 0.7] |  |
| 3 | `test_chile_pepper` | `Chile pepper sauce` | `Chile` | [0.4, 0.7] |  |
| 4 | `test_guinea_pig` | `Guinea pig pet store` | `Guinea` | [0.4, 0.7] |  |

## EC-22 — IdenticalStrings

*6 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_exact_same_single` | `Iran` | `Iran` | == 1.0 |  |
| 2 | `test_exact_same_multi` | `North Korea` | `North Korea` | == 1.0 |  |
| 3 | `test_exact_same_long` | `Los Angeles` | `Los Angeles` | [0.95, 1.0] |  |
| 4 | `test_case_only_diff` | `IRAN` | `Iran` | == 1.0 |  |
| 5 | `test_accent_only_diff` | `Réunion` | `Reunion` | [0.9, 1.0] |  |
| 6 | `test_whitespace_padded` | `  Iran  ` | `Iran` | [0.95, 1.0] |  |

## EC-23 — NonMatch

*8 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_absent_locations_zero` | `Paris, France` | `Tokyo` | <= 0.05 |  |
| 2 | `test_absent_locations_zero` | `Berlin, Germany` | `Moscow` | <= 0.05 |  |
| 3 | `test_absent_locations_zero` | `Mumbai, India` | `Lagos` | <= 0.05 |  |
| 4 | `test_absent_locations_zero` | `Sydney, Australia` | `Beijing` | <= 0.05 |  |
| 5 | `test_absent_locations_zero` | `Cairo, Egypt` | `Lima` | <= 0.05 |  |
| 6 | `test_absent_locations_zero` | `Toronto, Canada` | `Seoul` | <= 0.05 |  |
| 7 | `test_absent_locations_zero` | `Bangkok, Thailand` | `Madrid` | <= 0.05 |  |
| 8 | `test_absent_locations_zero` | `Nairobi, Kenya` | `Oslo` | <= 0.05 |  |

## EC-24 — RepeatedTokens

*4 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_triple_repeat` | `India India India` | `India` | [0.92, 1.0] |  |
| 2 | `test_duplicate_multi_word` | `North Korea North Korea` | `North Korea` | [0.92, 1.0] |  |
| 3 | `test_dedup_preserves_matching` | `France` | `France` | see test |  |
| 4 | `test_dedup_preserves_matching` | `France France` | `France` | see test |  |

## EC-25 — MixedAddressPatterns

*6 test case(s)*

| # | Test Method | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------------|-------|----------------|---------------------------|-------|
| 1 | `test_c_o_prefix` | `c/o Jane Doe, Manchester, England` | `Manchester` | [0.95, 1.0] |  |
| 2 | `test_attention_prefix` | `ATTENTION: Dr. Kumar, Chennai, India` | `Chennai` | [0.95, 1.0] |  |
| 3 | `test_ship_to_prefix` | `Ship to: Warehouse, Manila, Philippines` | `Manila` | [0.95, 1.0] |  |
| 4 | `test_delivery_instructions` | `Delivery to: Mumbai, India - URGENT` | `India` | [0.95, 1.0] |  |
| 5 | `test_po_box_with_country` | `P.O. Box 44, France` | `France` | [0.6, 0.7] |  |
| 6 | `test_zipcode_ignored` | `400001, Mumbai` | `Mumbai` | [0.9, 1.0] |  |
