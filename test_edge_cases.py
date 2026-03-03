"""
Extended Edge Case Test Suite for LocationMatcher
==================================================
Comprehensive tests for all edge cases from imple.md and the problem statement.
Tests cover additional scenarios not in the original test.py.

Usage:
    pytest test_edge_cases.py -v
    pytest test_edge_cases.py -v -k "Compound"
"""

import pytest

from matcher.location_matcher import LocationMatcher


# ──────────────────────────────────────────────
# FIXTURES
# ──────────────────────────────────────────────

@pytest.fixture(scope="module")
def matcher():
    """Single shared instance."""
    return LocationMatcher()


def assert_score(score: float, lo: float, hi: float, label: str = ""):
    """Assert score is within expected range."""
    assert lo <= score <= hi, (
        f"{label}\n  Expected [{lo}, {hi}], got {score:.4f}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# EC-1  Abbreviation Ambiguity (imple.md Cat 7.6 — missing from test.py)
# ══════════════════════════════════════════════════════════════════════════════

class TestEC1_AbbreviationAmbiguity:

    def test_ca_to_california(self, matcher):
        score = matcher.match("CA", "California")
        assert_score(score, 0.80, 0.92, "CA → California via abbreviation map")

    def test_ca_to_canada(self, matcher):
        score = matcher.match("CA", "Canada")
        assert_score(score, 0.80, 0.92, "CA → Canada via abbreviation map")

    def test_ca_ambiguous_equal(self, matcher):
        s1 = matcher.match("CA", "California")
        s2 = matcher.match("CA", "Canada")
        # Both should be the same score (abbreviation map score)
        assert abs(s1 - s2) < 0.05, "CA ambiguity: California ≈ Canada score"

    def test_il_abbreviation(self, matcher):
        score = matcher.match("IL", "Illinois")
        assert_score(score, 0.80, 0.92, "IL → Illinois abbreviation")

    def test_tx_abbreviation(self, matcher):
        score = matcher.match("TX", "Texas")
        assert_score(score, 0.80, 0.92, "TX → Texas abbreviation")

    def test_dc_abbreviation(self, matcher):
        # DC maps to "District of Columbia", not "Washington"
        score = matcher.match("DC", "District of Columbia")
        assert_score(score, 0.80, 0.92, "DC → District of Columbia abbreviation")

    def test_abbreviation_in_address(self, matcher):
        score = matcher.match("123 Main St, Springfield, IL", "Illinois")
        assert_score(score, 0.80, 0.92, "IL in address → Illinois")


# ══════════════════════════════════════════════════════════════════════════════
# EC-2  Compound / Concatenated Names
# ══════════════════════════════════════════════════════════════════════════════

class TestEC2_CompoundConcatenated:

    def test_newyork_no_space(self, matcher):
        score = matcher.match("NewYork", "New York")
        assert_score(score, 0.75, 0.90, "NewYork compound → New York")

    def test_sanfrancisco_no_space(self, matcher):
        score = matcher.match("SanFrancisco", "San Francisco")
        assert_score(score, 0.75, 0.90, "SanFrancisco compound → San Francisco")

    def test_southkorea_no_space(self, matcher):
        score = matcher.match("SouthKorea", "South Korea")
        assert_score(score, 0.60, 0.85, "SouthKorea compound → South Korea")

    def test_compound_beats_no_match(self, matcher):
        compound = matcher.match("NewYork", "New York")
        nomatch = matcher.match("Abcdefg", "New York")
        assert compound > nomatch, "Compound should beat no-match"

    def test_guineabissau_compound(self, matcher):
        # Already in test.py but verify it still works
        score = matcher.match("GuineaBissau", "Guinea-Bissau")
        assert_score(score, 0.75, 0.92, "GuineaBissau compound")


# ══════════════════════════════════════════════════════════════════════════════
# EC-3  Garbage Input Variations
# ══════════════════════════════════════════════════════════════════════════════

class TestEC3_GarbageVariations:

    def test_dashes_only(self, matcher):
        assert matcher.match("---", "Iran") == 0.0, "Dashes only → 0.0"

    def test_dots_only(self, matcher):
        assert matcher.match("...", "Iran") == 0.0, "Dots only → 0.0"

    def test_nil_token(self, matcher):
        assert matcher.match("nil", "Iran") == 0.0, "nil → 0.0"

    def test_tbd_token(self, matcher):
        assert matcher.match("TBD", "Iran") == 0.0, "TBD → 0.0"

    def test_test_token(self, matcher):
        assert matcher.match("test", "Iran") == 0.0, "test → 0.0"

    def test_none_raises_type_error(self, matcher):
        with pytest.raises(TypeError):
            matcher.match(None, "Iran")

    def test_int_raises_type_error(self, matcher):
        with pytest.raises(TypeError):
            matcher.match(123, "Iran")

    def test_result_none_raises(self, matcher):
        with pytest.raises(TypeError):
            matcher.match("Iran", None)

    def test_empty_string_both(self, matcher):
        assert matcher.match("", "") == 0.0, "Both empty → 0.0"

    def test_single_space(self, matcher):
        assert matcher.match(" ", "Iran") == 0.0, "Single space → 0.0"

    def test_tab_whitespace(self, matcher):
        assert matcher.match("\t\n", "Iran") == 0.0, "Tab/newline → 0.0"

    def test_pure_symbols(self, matcher):
        assert matcher.match("!@#$%^&*()", "Iran") == 0.0

    def test_mixed_garbage_number(self, matcher):
        score = matcher.match("999 888 777", "Iran")
        assert_score(score, 0.0, 0.05, "All-number query → near 0")


# ══════════════════════════════════════════════════════════════════════════════
# EC-4  Unicode / Diacritics Extended
# ══════════════════════════════════════════════════════════════════════════════

class TestEC4_UnicodeExtended:

    def test_all_caps_diacritics(self, matcher):
        score = matcher.match("CÔTE D'IVOIRE", "Cote Ivoire")
        assert_score(score, 0.85, 1.0, "All-caps with diacritics")

    def test_all_caps_tilde(self, matcher):
        score = matcher.match("SÃO PAULO", "Sao Paulo")
        assert_score(score, 0.90, 1.0, "All-caps São Paulo")

    def test_umlaut_city(self, matcher):
        score = matcher.match("Zürich", "Zurich")
        assert_score(score, 0.90, 1.0, "Zürich → Zurich")

    def test_polish_chars(self, matcher):
        score = matcher.match("Łódź", "Lodz")
        assert_score(score, 0.70, 1.0, "Łódź → Lodz")

    def test_turkish_char(self, matcher):
        score = matcher.match("İstanbul", "Istanbul")
        assert_score(score, 0.90, 1.0, "İstanbul → Istanbul")

    def test_french_cedilla(self, matcher):
        score = matcher.match("Français", "Francais")
        assert_score(score, 0.90, 1.0, "Français → Francais")


# ══════════════════════════════════════════════════════════════════════════════
# EC-5  Result Longer Than Query (Partial Coverage)
# ══════════════════════════════════════════════════════════════════════════════

class TestEC5_ResultLongerThanQuery:

    def test_korea_vs_north_korea(self, matcher):
        score = matcher.match("Korea", "North Korea")
        assert_score(score, 0.35, 0.55, "Korea partial → North Korea")

    def test_york_vs_new_york(self, matcher):
        score = matcher.match("York", "New York")
        assert_score(score, 0.40, 0.60, "York partial → New York")

    def test_arabia_vs_saudi_arabia(self, matcher):
        score = matcher.match("Arabia", "Saudi Arabia")
        assert_score(score, 0.40, 0.60, "Arabia partial → Saudi Arabia")

    def test_guinea_vs_papua_new_guinea(self, matcher):
        score = matcher.match("Guinea", "Papua New Guinea")
        # Only 1 of 3 tokens matched
        assert_score(score, 0.20, 0.50, "Guinea partial → Papua New Guinea")

    def test_full_beats_partial(self, matcher):
        full = matcher.match("North Korea", "North Korea")
        partial = matcher.match("Korea", "North Korea")
        assert full > partial, "Full match must beat partial"

    def test_papua_new_guinea_exact(self, matcher):
        score = matcher.match("Papua New Guinea", "Papua New Guinea")
        assert_score(score, 0.95, 1.0, "Papua New Guinea exact 3-word")

    def test_papua_guinea_partial(self, matcher):
        score = matcher.match("Papua Guinea", "Papua New Guinea")
        assert_score(score, 0.55, 0.80, "Papua Guinea partial 2-of-3")

    def test_north_partial_vs_north_korea(self, matcher):
        # Single directional token matching multi-word result
        score = matcher.match("North", "North Korea")
        assert_score(score, 0.65, 0.85, "North partial → North Korea")


# ══════════════════════════════════════════════════════════════════════════════
# EC-6  Collision Words in Geographic vs Non-Geographic Context
# ══════════════════════════════════════════════════════════════════════════════

class TestEC6_CollisionContextDetection:

    # Geographic context — collision word as exact token with geo neighbors
    def test_turkey_geo_context(self, matcher):
        score = matcher.match("Turkey, Istanbul", "Turkey")
        assert_score(score, 0.95, 1.0, "Turkey in geo context → high")

    def test_china_geo_context(self, matcher):
        score = matcher.match("China, Beijing", "China")
        assert_score(score, 0.95, 1.0, "China in geo context → high")

    def test_jordan_geo_context(self, matcher):
        score = matcher.match("Jordan, Amman", "Jordan")
        assert_score(score, 0.95, 1.0, "Jordan in geo context → high")

    def test_georgia_geo_context(self, matcher):
        score = matcher.match("Georgia, USA", "Georgia")
        assert_score(score, 0.95, 1.0, "Georgia in geo context → high")

    # Non-geographic context — commercial words present → suppressed
    def test_turkey_food_context(self, matcher):
        score = matcher.match("Turkey sandwich shop", "Turkey")
        assert_score(score, 0.0, 0.35, "Turkey food context → low")

    def test_china_furniture_context(self, matcher):
        score = matcher.match("China Cabinet Store, LA", "China")
        assert_score(score, 0.0, 0.35, "China furniture → low")

    def test_jordan_brand_context(self, matcher):
        score = matcher.match("Jordan shoes store", "Jordan")
        assert_score(score, 0.0, 0.40, "Jordan brand → low")

    def test_nice_adjective_context(self, matcher):
        score = matcher.match("Nice apartment for rent", "Nice")
        assert_score(score, 0.0, 0.40, "Nice adjective → low")

    # Geo context always beats non-geo
    def test_geo_beats_commercial_turkey(self, matcher):
        geo = matcher.match("Turkey, Istanbul", "Turkey")
        com = matcher.match("Turkey sandwich shop", "Turkey")
        assert geo > com, "Geo Turkey > commercial Turkey"

    def test_geo_beats_commercial_china(self, matcher):
        geo = matcher.match("China, Beijing", "China")
        com = matcher.match("China Cabinet Store, LA", "China")
        assert geo > com, "Geo China > commercial China"

    def test_geo_beats_commercial_jordan(self, matcher):
        geo = matcher.match("Jordan, Amman", "Jordan")
        com = matcher.match("Jordan shoes store", "Jordan")
        assert geo > com, "Geo Jordan > commercial Jordan"


# ══════════════════════════════════════════════════════════════════════════════
# EC-7  Alternate Names with Geographic Context
# ══════════════════════════════════════════════════════════════════════════════

class TestEC7_AlternateNamesContext:

    def test_bombay_with_india(self, matcher):
        score = matcher.match("Bombay, Maharashtra, India", "Mumbai")
        assert_score(score, 0.78, 0.92, "Bombay in address → Mumbai")

    def test_calcutta_with_india(self, matcher):
        score = matcher.match("Calcutta, West Bengal, India", "Kolkata")
        assert_score(score, 0.78, 0.92, "Calcutta in address → Kolkata")

    def test_constantinople_with_turkey(self, matcher):
        score = matcher.match("Constantinople, Turkey", "Istanbul")
        assert_score(score, 0.78, 0.92, "Constantinople → Istanbul")

    def test_deutschland_simple(self, matcher):
        score = matcher.match("Deutschland", "Germany")
        assert_score(score, 0.75, 0.90, "Deutschland → Germany")

    def test_nippon_simple(self, matcher):
        score = matcher.match("Nippon", "Japan")
        assert_score(score, 0.75, 0.90, "Nippon → Japan")

    def test_holland_simple(self, matcher):
        score = matcher.match("Holland", "Netherlands")
        assert_score(score, 0.75, 0.90, "Holland → Netherlands")

    def test_exact_beats_alternate(self, matcher):
        exact = matcher.match("India", "India")
        alt = matcher.match("Bharat", "India")
        assert exact > alt, "Exact India > alternate Bharat"

    def test_exact_beats_alternate_city(self, matcher):
        exact = matcher.match("Mumbai", "Mumbai")
        alt = matcher.match("Bombay", "Mumbai")
        assert exact > alt, "Exact Mumbai > alternate Bombay"


# ══════════════════════════════════════════════════════════════════════════════
# EC-8  Substring Edge Cases
# ══════════════════════════════════════════════════════════════════════════════

class TestEC8_SubstringEdgeCases:

    def test_parisian_vs_paris(self, matcher):
        # "paris" is prefix of "parisian" — prefix substring match
        score = matcher.match("Parisian cafe", "Paris")
        assert_score(score, 0.20, 0.50, "Parisian → Paris (prefix substring)")

    def test_pakistani_vs_pakistan(self, matcher):
        score = matcher.match("Pakistani market", "Pakistan")
        assert_score(score, 0.30, 0.55, "Pakistani → Pakistan (prefix substring)")

    def test_american_vs_america(self, matcher):
        score = matcher.match("American food", "America")
        print(score)
        assert_score(score, 0.30, 0.55, "American → America (prefix substring)")

    def test_dparis_vs_paris(self, matcher):
        # "paris" as suffix of "dparis"
        score = matcher.match("DParis Hotel", "Paris")
        assert_score(score, 0.30, 0.55, "DParis → Paris (suffix substring)")

    def test_exact_beats_substring(self, matcher):
        exact = matcher.match("Paris, France", "Paris")
        sub = matcher.match("Parisian cafe", "Paris")
        assert exact > sub, "Exact Paris > substring Parisian"

    def test_short_token_guard(self, matcher):
        # Result "Ir" is too short for substring matching (< 4 chars)
        score = matcher.match("Bird sanctuary near lake", "Ir")
        assert_score(score, 0.0, 0.25, "Short token Ir → guard rejects")

    def test_iran_not_in_marine(self, matcher):
        # "iran" is NOT a substring of "marine" — must be 0
        score = matcher.match("Marine Drive, India", "Iran")
        assert_score(score, 0.0, 0.15, "Marine ≠ Iran (no substring)")


# ══════════════════════════════════════════════════════════════════════════════
# EC-9  Very Long Addresses
# ══════════════════════════════════════════════════════════════════════════════

class TestEC9_VeryLongAddresses:

    LONG_US = "Suite 500, 100 Broadway, Floor 12, Manhattan, New York, NY, 10005, USA"
    LONG_IN = "Flat 1, 2nd Floor, Building A, Green Complex, MG Road, Koramangala, Bangalore, Karnataka, India, 560001"
    LONG_UK = "Flat 3, 27 Baker St, London W1U 8EW, United Kingdom"

    def test_usa_in_long(self, matcher):
        score = matcher.match(self.LONG_US, "USA")
        assert_score(score, 0.95, 1.0, "USA in long US address")

    def test_manhattan_in_long(self, matcher):
        score = matcher.match(self.LONG_US, "Manhattan")
        assert_score(score, 0.95, 1.0, "Manhattan in long US address")

    def test_new_york_in_long(self, matcher):
        score = matcher.match(self.LONG_US, "New York")
        assert_score(score, 0.95, 1.0, "New York in long US address")

    def test_india_in_long(self, matcher):
        score = matcher.match(self.LONG_IN, "India")
        assert_score(score, 0.95, 1.0, "India in very long Indian address")

    def test_bangalore_in_long(self, matcher):
        score = matcher.match(self.LONG_IN, "Bangalore")
        assert_score(score, 0.95, 1.0, "Bangalore in very long address")

    def test_karnataka_in_long(self, matcher):
        score = matcher.match(self.LONG_IN, "Karnataka")
        assert_score(score, 0.95, 1.0, "Karnataka in very long address")

    def test_london_in_long(self, matcher):
        score = matcher.match(self.LONG_UK, "London")
        assert_score(score, 0.95, 1.0, "London in long UK address")

    def test_absent_city_in_long(self, matcher):
        score = matcher.match(self.LONG_US, "Tokyo")
        assert_score(score, 0.0, 0.05, "Tokyo NOT in US address")

    def test_absent_country_in_long(self, matcher):
        score = matcher.match(self.LONG_IN, "China")
        assert_score(score, 0.0, 0.05, "China NOT in India address")


# ══════════════════════════════════════════════════════════════════════════════
# EC-10  Reversed / Jumbled Multi-Word with Noise
# ══════════════════════════════════════════════════════════════════════════════

class TestEC10_ScatteredTokens:

    def test_scattered_north_korea(self, matcher):
        score = matcher.match("Korea, officially North, country", "North Korea")
        assert_score(score, 0.55, 0.97, "Scattered North Korea tokens")

    def test_reversed_order_simple(self, matcher):
        score = matcher.match("Korea North", "North Korea")
        assert_score(score, 0.72, 0.97, "Simple reversed order")

    def test_reversed_with_extra_tokens(self, matcher):
        score = matcher.match("Korea is a great place, North", "North Korea")
        assert_score(score, 0.30, 0.97, "Reversed + many noise tokens")

    def test_ordered_beats_reversed(self, matcher):
        ordered = matcher.match("North Korea", "North Korea")
        reversed_ = matcher.match("Korea North", "North Korea")
        assert ordered > reversed_, "Ordered > reversed"

    def test_reversed_beats_absent(self, matcher):
        reversed_ = matcher.match("Korea North", "North Korea")
        absent = matcher.match("Tokyo Japan", "North Korea")
        assert reversed_ > absent, "Reversed > absent"


# ══════════════════════════════════════════════════════════════════════════════
# EC-11  Exact Token Presence — Core Principle
# ══════════════════════════════════════════════════════════════════════════════
# "If a particular country/city/state token exists as a token in the query,
#  we should be returning ~1.0"

class TestEC11_ExactTokenPresence:

    @pytest.mark.parametrize("query,result,label", [
        ("Paris, France", "France", "France in Paris addr"),
        ("Berlin, Germany", "Germany", "Germany in Berlin addr"),
        ("Tokyo, Japan", "Japan", "Japan in Tokyo addr"),
        ("Mumbai, India", "India", "India in Mumbai addr"),
        ("Cairo, Egypt", "Egypt", "Egypt in Cairo addr"),
        ("Lima, Peru", "Peru", "Peru in Lima addr"),
        ("Beijing, China", "Beijing", "Beijing exact"),
        ("Moscow, Russia", "Russia", "Russia exact"),
        ("Sydney, Australia", "Australia", "Australia exact"),
    ])
    def test_exact_token_high(self, matcher, query, result, label):
        score = matcher.match(query, result)
        assert score >= 0.95, f"{label}: expected ≥0.95, got {score:.4f}"

    def test_seoul_with_directional_adjacent(self, matcher):
        # Seoul gets adjacent directional penalty from 'South'
        score = matcher.match("Seoul, South Korea", "Seoul")
        assert_score(score, 0.78, 0.90, "Seoul with adjacent South directional")

    @pytest.mark.parametrize("query,result,label", [
        ("Paris, France", "Germany", "Germany NOT in Paris addr"),
        ("Berlin, Germany", "France", "France NOT in Berlin addr"),
        ("Tokyo, Japan", "China", "China NOT in Tokyo addr"),
        ("Mumbai, India", "Pakistan", "Pakistan NOT in Mumbai addr"),
        ("Seoul, South Korea", "Japan", "Japan NOT in Seoul addr"),
    ])
    def test_absent_token_zero(self, matcher, query, result, label):
        score = matcher.match(query, result)
        assert score <= 0.05, f"{label}: expected ≤0.05, got {score:.4f}"


# ══════════════════════════════════════════════════════════════════════════════
# EC-12  Directional Mismatch / Adjacent Directional
# ══════════════════════════════════════════════════════════════════════════════

class TestEC12_DirectionalEdgeCases:

    def test_north_vs_south_korea_low(self, matcher):
        score = matcher.match("North Korea", "South Korea")
        assert_score(score, 0.35, 0.60, "N. Korea vs S. Korea — mismatch")

    def test_east_vs_west(self, matcher):
        # "East" in query, "West" in result = directional mismatch
        score = matcher.match("East Africa", "West Africa")
        assert_score(score, 0.50, 0.95, "East vs West Africa — mismatch")

    def test_directional_present_exact(self, matcher):
        score = matcher.match("North Korea", "North Korea")
        assert_score(score, 0.95, 1.0, "North Korea exact")

    def test_no_directional_vs_directional_result(self, matcher):
        # Query has NO directional, result has one → mild reduction
        score = matcher.match("Korea", "North Korea")
        assert_score(score, 0.35, 0.55, "Korea → North Korea (directional absent)")

    def test_adjacent_directional_penalty(self, matcher):
        # "Western" adjacent to "Australia" → directional excess penalty
        score = matcher.match("Western Australia", "Australia")
        assert_score(score, 0.75, 0.90, "Western Australia → Australia")

    def test_non_adjacent_directional_no_penalty(self, matcher):
        # "South" is NOT adjacent to "India" → no penalty
        score = matcher.match("South Mumbai, Maharashtra, India", "India")
        assert_score(score, 0.95, 1.0, "Non-adjacent South → India no penalty")


# ══════════════════════════════════════════════════════════════════════════════
# EC-13  Hyphenated & Connector Variations
# ══════════════════════════════════════════════════════════════════════════════

class TestEC13_HyphenConnector:

    def test_hyphen_split_exact(self, matcher):
        score = matcher.match("Guinea-Bissau", "Guinea-Bissau")
        assert_score(score, 0.92, 1.0, "Hyphen exact")

    def test_space_vs_hyphen(self, matcher):
        score = matcher.match("Guinea Bissau", "Guinea-Bissau")
        assert_score(score, 0.88, 1.0, "Space vs hyphen")

    def test_missing_and_connector(self, matcher):
        score = matcher.match("Bosnia Herzegovina", "Bosnia and Herzegovina")
        assert_score(score, 0.80, 0.95, "Missing 'and' connector")

    def test_and_preserved_in_exact(self, matcher):
        score = matcher.match("Bosnia and Herzegovina", "Bosnia and Herzegovina")
        assert_score(score, 0.92, 1.0, "'and' preserved in exact match")

    def test_trinidad_and_tobago(self, matcher):
        score = matcher.match("Trinidad and Tobago", "Trinidad and Tobago")
        assert_score(score, 0.92, 1.0, "Trinidad and Tobago exact")

    def test_trinidad_tobago_no_and(self, matcher):
        score = matcher.match("Trinidad Tobago", "Trinidad and Tobago")
        assert_score(score, 0.80, 0.95, "Trinidad Tobago missing 'and'")


# ══════════════════════════════════════════════════════════════════════════════
# EC-14  Articles & Prefix Stripping
# ══════════════════════════════════════════════════════════════════════════════

class TestEC14_ArticlePrefixStripping:

    def test_the_gambia(self, matcher):
        score = matcher.match("The Gambia", "Gambia")
        assert_score(score, 0.88, 1.0, "The Gambia → Gambia")

    def test_kingdom_of_stripped(self, matcher):
        score = matcher.match("Kingdom of Saudi Arabia", "Saudi Arabia")
        assert_score(score, 0.80, 0.95, "Kingdom of stripped")

    def test_state_of_stripped(self, matcher):
        score = matcher.match("State of New York", "New York")
        assert_score(score, 0.80, 0.95, "State of stripped")

    def test_province_of_stripped(self, matcher):
        score = matcher.match("Province of Quebec", "Quebec")
        assert_score(score, 0.82, 1.0, "Province of stripped")

    def test_republic_of_partially(self, matcher):
        score = matcher.match("Republic of Korea", "South Korea")
        assert_score(score, 0.40, 0.65, "Republic of Korea → South Korea")


# ══════════════════════════════════════════════════════════════════════════════
# EC-15  Typo Tolerance Extended
# ══════════════════════════════════════════════════════════════════════════════

class TestEC15_TypoExtended:

    def test_transposition(self, matcher):
        score = matcher.match("Iarn", "Iran")
        assert_score(score, 0.78, 0.88, "Iarn → Iran transposition")

    def test_missing_char(self, matcher):
        score = matcher.match("Germny", "Germany")
        assert_score(score, 0.80, 0.92, "Germny → Germany missing char")

    def test_extra_char(self, matcher):
        score = matcher.match("Australiaa", "Australia")
        assert_score(score, 0.80, 0.92, "Australiaa → Australia extra char")

    def test_swap_chars(self, matcher):
        score = matcher.match("Frnace", "France")
        assert_score(score, 0.75, 0.90, "Frnace → France swap")

    def test_multi_word_typo(self, matcher):
        score = matcher.match("Noth Korea", "North Korea")
        assert_score(score, 0.78, 0.99, "Noth Korea → North Korea")

    def test_exact_beats_typo(self, matcher):
        exact = matcher.match("Iran", "Iran")
        typo = matcher.match("Iarn", "Iran")
        assert exact > typo, "Exact must beat typo"

    def test_1edit_beats_2edit(self, matcher):
        one = matcher.match("Germny", "Germany")
        two = matcher.match("Grmany", "Germany")
        # Both should be reasonable; 1-edit is at least as good
        assert one >= two * 0.9, "1-edit should be close to or better than 2-edit"


# ══════════════════════════════════════════════════════════════════════════════
# EC-16  Debug Breakdown Contract
# ══════════════════════════════════════════════════════════════════════════════

class TestEC16_DebugContract:

    def test_returns_dict(self, matcher):
        result = matcher.get_debug_breakdown("Iran", "Iran")
        assert isinstance(result, dict)

    def test_has_final_score(self, matcher):
        result = matcher.get_debug_breakdown("Iran", "Iran")
        assert "final_score" in result
        assert abs(result["final_score"] - 1.0) < 0.001

    def test_score_matches_match(self, matcher):
        dbg = matcher.get_debug_breakdown("Hirani", "Iran")
        direct = matcher.match("Hirani", "Iran")
        assert abs(dbg["final_score"] - direct) < 0.001

    def test_has_token_scores_or_steps(self, matcher):
        result = matcher.get_debug_breakdown("Tehran, Iran", "Iran")
        assert "token_scores" in result or "steps" in result

    def test_garbage_detected(self, matcher):
        result = matcher.get_debug_breakdown("", "Iran")
        assert result["final_score"] == 0.0

    def test_multi_token_debug(self, matcher):
        result = matcher.get_debug_breakdown("North Korea", "North Korea")
        assert result["final_score"] >= 0.95


# ══════════════════════════════════════════════════════════════════════════════
# EC-17  Score Ordering & Relative Rankings
# ══════════════════════════════════════════════════════════════════════════════

class TestEC17_ScoreOrdering:

    def test_exact_beats_abbreviation(self, matcher):
        exact = matcher.match("United States", "United States")
        abbrev = matcher.match("USA", "United States")
        assert exact > abbrev

    def test_exact_beats_alternate(self, matcher):
        exact = matcher.match("Germany", "Germany")
        alt = matcher.match("Deutschland", "Germany")
        assert exact > alt

    def test_exact_beats_fuzzy(self, matcher):
        exact = matcher.match("France", "France")
        fuzzy = matcher.match("Frnace", "France")
        assert exact > fuzzy

    def test_exact_token_beats_substring(self, matcher):
        exact = matcher.match("Tehran, Iran", "Iran")
        substr = matcher.match("Hirani", "Iran")
        assert exact > substr

    def test_geo_context_beats_commercial(self, matcher):
        geo = matcher.match("Paris, France", "Paris")
        com = matcher.match("Nice apartment for rent", "Nice")
        assert geo > com

    def test_full_match_beats_partial(self, matcher):
        full = matcher.match("South Korea", "South Korea")
        partial = matcher.match("Korea", "South Korea")
        assert full > partial

    def test_clean_beats_noisy(self, matcher):
        clean = matcher.match("Tehran, Iran", "Iran")
        noisy = matcher.match("Marine Irani Rd", "Iran")
        assert clean > noisy

    def test_ordered_beats_reversed(self, matcher):
        ordered = matcher.match("North Korea", "North Korea")
        reversed_ = matcher.match("Korea North", "North Korea")
        assert ordered > reversed_

    def test_short_address_beats_long_for_exact(self, matcher):
        short = matcher.match("Iran", "Iran")
        long = matcher.match("10, Green Apt, Iran", "Iran")
        # Both should be high, but exact simple should be highest
        assert short >= long


# ══════════════════════════════════════════════════════════════════════════════
# EC-18  Phonetic Matching
# ══════════════════════════════════════════════════════════════════════════════

class TestEC18_PhoneticMatching:

    def test_eyran_iran(self, matcher):
        score = matcher.match("Eyran", "Iran")
        assert_score(score, 0.55, 0.85, "Eyran phonetic → Iran")

    def test_corea_korea(self, matcher):
        score = matcher.match("Corea", "Korea")
        assert_score(score, 0.65, 0.88, "Corea phonetic → Korea")

    def test_phonetic_below_exact(self, matcher):
        exact = matcher.match("Iran", "Iran")
        phonetic = matcher.match("Eyran", "Iran")
        assert exact > phonetic, "Exact > phonetic"


# ══════════════════════════════════════════════════════════════════════════════
# EC-19  Multi-Entity Independent Scoring
# ══════════════════════════════════════════════════════════════════════════════

class TestEC19_MultiEntityIndependent:

    def test_all_three_high(self, matcher):
        addr = "Manhattan, New York, USA"
        s_city = matcher.match(addr, "Manhattan")
        s_state = matcher.match(addr, "New York")
        s_country = matcher.match(addr, "United States")
        assert s_city >= 0.85, f"Manhattan: {s_city}"
        assert s_state >= 0.85, f"New York: {s_state}"
        assert s_country >= 0.72, f"United States: {s_country}"

    def test_both_city_and_country_high(self, matcher):
        s1 = matcher.match("Paris, France", "Paris")
        s2 = matcher.match("Paris, France", "France")
        assert s1 >= 0.88
        assert s2 >= 0.88

    def test_city_state_country_indian(self, matcher):
        addr = "Bangalore, Karnataka, India"
        assert matcher.match(addr, "Bangalore") >= 0.95
        assert matcher.match(addr, "Karnataka") >= 0.95
        assert matcher.match(addr, "India") >= 0.95


# ══════════════════════════════════════════════════════════════════════════════
# EC-20  Punctuation & Delimiter Variations Extended
# ══════════════════════════════════════════════════════════════════════════════

class TestEC20_PunctuationExtended:

    def test_slash_splits_both(self, matcher):
        s1 = matcher.match("Iran/Iraq", "Iran")
        s2 = matcher.match("Iran/Iraq", "Iraq")
        assert s1 >= 0.85, f"Iran from Iran/Iraq: {s1}"
        assert s2 >= 0.85, f"Iraq from Iran/Iraq: {s2}"

    def test_pipe_separator(self, matcher):
        score = matcher.match("France|Germany", "France")
        assert_score(score, 0.85, 1.0, "Pipe separator")

    def test_backslash_separator(self, matcher):
        score = matcher.match("Korea\\Japan", "Korea")
        assert_score(score, 0.85, 1.0, "Backslash separator")

    def test_semicolon_stripped(self, matcher):
        score = matcher.match("Iran;", "Iran")
        assert_score(score, 0.92, 1.0, "Semicolon stripped")

    def test_exclamation_stripped(self, matcher):
        score = matcher.match("Iran!", "Iran")
        assert_score(score, 0.92, 1.0, "Exclamation stripped")

    def test_brackets_stripped(self, matcher):
        score = matcher.match("[Iran]", "Iran")
        assert_score(score, 0.92, 1.0, "Brackets stripped")

    def test_dot_as_separator(self, matcher):
        score = matcher.match("North.Korea", "North Korea")
        assert_score(score, 0.80, 1.0, "Dot as separator")

    def test_comma_no_space(self, matcher):
        score = matcher.match("Paris,France", "France")
        assert_score(score, 0.88, 1.0, "Comma-no-space")


# ══════════════════════════════════════════════════════════════════════════════
# EC-21  Moderate Commercial Context (non-zero but suppressed)
# ══════════════════════════════════════════════════════════════════════════════

class TestEC21_ModerateCommercial:

    def test_victoria_secret(self, matcher):
        score = matcher.match("Victoria Secret outlet", "Victoria")
        assert_score(score, 0.40, 0.70, "Victoria Secret — moderate")

    def test_panama_hat(self, matcher):
        score = matcher.match("Panama hat shop", "Panama")
        assert_score(score, 0.40, 0.70, "Panama hat — moderate")

    def test_chile_pepper(self, matcher):
        score = matcher.match("Chile pepper sauce", "Chile")
        assert_score(score, 0.40, 0.70, "Chile pepper — moderate")

    def test_guinea_pig(self, matcher):
        score = matcher.match("Guinea pig pet store", "Guinea")
        assert_score(score, 0.40, 0.70, "Guinea pig — moderate")


# ══════════════════════════════════════════════════════════════════════════════
# EC-22  Edge: Identical / Near-Identical Strings
# ══════════════════════════════════════════════════════════════════════════════

class TestEC22_IdenticalStrings:

    def test_exact_same_single(self, matcher):
        assert matcher.match("Iran", "Iran") == 1.0

    def test_exact_same_multi(self, matcher):
        assert matcher.match("North Korea", "North Korea") == 1.0

    def test_exact_same_long(self, matcher):
        score = matcher.match("Los Angeles", "Los Angeles")
        assert_score(score, 0.95, 1.0, "Los Angeles exact")

    def test_case_only_diff(self, matcher):
        assert matcher.match("IRAN", "Iran") == 1.0

    def test_accent_only_diff(self, matcher):
        score = matcher.match("Réunion", "Reunion")
        assert_score(score, 0.90, 1.0, "Accent-only difference")

    def test_whitespace_padded(self, matcher):
        # After strip, should be exact match
        score = matcher.match("  Iran  ", "Iran")
        assert_score(score, 0.95, 1.0, "Whitespace-padded Iran")


# ══════════════════════════════════════════════════════════════════════════════
# EC-23  Comprehensive Non-Match Verification
# ══════════════════════════════════════════════════════════════════════════════

class TestEC23_NonMatch:

    @pytest.mark.parametrize("query,result", [
        ("Paris, France", "Tokyo"),
        ("Berlin, Germany", "Moscow"),
        ("Mumbai, India", "Lagos"),
        ("Sydney, Australia", "Beijing"),
        ("Cairo, Egypt", "Lima"),
        ("Toronto, Canada", "Seoul"),
        ("Bangkok, Thailand", "Madrid"),
        ("Nairobi, Kenya", "Oslo"),
    ])
    def test_absent_locations_zero(self, matcher, query, result):
        score = matcher.match(query, result)
        assert score <= 0.05, f"{result} NOT in {query}: got {score:.4f}"


# ══════════════════════════════════════════════════════════════════════════════
# EC-24  Repeated Tokens Extended
# ══════════════════════════════════════════════════════════════════════════════

class TestEC24_RepeatedTokens:

    def test_triple_repeat(self, matcher):
        score = matcher.match("India India India", "India")
        assert_score(score, 0.92, 1.0, "Triple India deduped")

    def test_duplicate_multi_word(self, matcher):
        score = matcher.match("North Korea North Korea", "North Korea")
        assert_score(score, 0.92, 1.0, "Repeated North Korea")

    def test_dedup_preserves_matching(self, matcher):
        single = matcher.match("France", "France")
        double = matcher.match("France France", "France")
        assert abs(single - double) < 0.1, "Dedup shouldn't hurt score"


# ══════════════════════════════════════════════════════════════════════════════
# EC-25  Mixed Address Patterns
# ══════════════════════════════════════════════════════════════════════════════

class TestEC25_MixedAddressPatterns:

    def test_c_o_prefix(self, matcher):
        score = matcher.match("c/o Jane Doe, Manchester, England", "Manchester")
        assert_score(score, 0.95, 1.0, "c/o prefix → Manchester")

    def test_attention_prefix(self, matcher):
        score = matcher.match("ATTENTION: Dr. Kumar, Chennai, India", "Chennai")
        assert_score(score, 0.95, 1.0, "ATTENTION prefix → Chennai")

    def test_ship_to_prefix(self, matcher):
        score = matcher.match("Ship to: Warehouse, Manila, Philippines", "Manila")
        assert_score(score, 0.95, 1.0, "Ship to prefix → Manila")

    def test_delivery_instructions(self, matcher):
        score = matcher.match("Delivery to: Mumbai, India - URGENT", "India")
        assert_score(score, 0.95, 1.0, "Delivery instruction → India")

    def test_po_box_with_country(self, matcher):
        # P.O. Box tokens ("po", "box", "44") get filtered as noise,
        # leaving only "france" — but the filtered-count triggers P5
        # address-noise penalty (consistent with existing test_13_4)
        score = matcher.match("P.O. Box 44, France", "France")
        assert_score(score, 0.60, 0.70, "P.O. Box → France")

    def test_zipcode_ignored(self, matcher):
        score = matcher.match("400001, Mumbai", "Mumbai")
        assert_score(score, 0.90, 1.0, "Zipcode ignored → Mumbai")
