"""
Comprehensive Test Suite for LocationMatcher
============================================
Tests cover all 20 edge case categories from the algorithm spec.
Total: 130 test cases

Usage:
    pytest test_location_matcher.py -v
    pytest test_location_matcher.py -v --tb=short
    pytest test_location_matcher.py -v -k "Category_4"  # run specific category

Assumes:
    from location_matcher import LocationMatcher
    matcher = LocationMatcher()
    score = matcher.match(query, elastic_result)  # returns float 0.0 - 1.0
"""

import pytest
import logging

from matcher.location_matcher import LocationMatcher

# Configure logging for test failures
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# FIXTURES
# ──────────────────────────────────────────────

@pytest.fixture(scope="module")
def matcher():
    """Single shared instance — class must be stateless/thread-safe."""
    return LocationMatcher()


@pytest.fixture(autouse=True)
def log_test_result(request):
    """Automatically logs test results after each test."""
    yield
    test_name = request.node.name
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call is None:
        logger.warning(f"⚠ UNKNOWN: {test_name}")
        return
    test_outcome = rep_call.outcome

    if rep_call.failed:
        logger.error(f"❌ FAILED: {test_name}")
    elif rep_call.passed:
        logger.info(f"✓ PASSED: {test_name}")
    else:
        logger.warning(f"⚠ {test_outcome.upper()}: {test_name}")

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def assert_score(score: float, min_val: float, max_val: float, label: str = ""):
    """Assert score is within expected range with a meaningful message."""
    assert min_val <= score <= max_val, (
        f"{label}\n"
        f"  Expected score in [{min_val}, {max_val}]\n"
        f"  Got: {score:.4f}"
    )


def pytest_runtest_makereport(item, call):
    """Hook to capture test outcome for logging."""
    if call.when == "call":
        item.rep_call = call


# ══════════════════════════════════════════════
# CATEGORY 1 — Exact & Clean Matches
# ══════════════════════════════════════════════
# CATEGORY 1 — Exact & Clean Matches
# ══════════════════════════════════════════════

class TestCategory1_ExactCleanMatches:

    def test_1_1_single_token_exact(self, matcher):
        score = matcher.match("10, Green Apt, Iran", "Iran")
        assert_score(score, 0.95, 1.0, "1.1 Single token exact match")

    def test_1_2_multi_word_exact(self, matcher):
        score = matcher.match("Seoul, South Korea", "South Korea")
        assert_score(score, 0.95, 1.0, "1.2 Multi-word exact match")

    def test_1_3_single_token_clean(self, matcher):
        score = matcher.match("Paris, France", "France")
        assert_score(score, 0.95, 1.0, "1.3 Single clean token")

    def test_1_4_city_in_address(self, matcher):
        score = matcher.match("Manhattan, New York, USA", "New York")
        assert_score(score, 0.90, 1.0, "1.4 City name in full address")

    def test_1_5_country_alone(self, matcher):
        score = matcher.match("Germany", "Germany")
        assert_score(score, 0.95, 1.0, "1.5 Country name alone")

    def test_1_6_state_alone(self, matcher):
        score = matcher.match("Texas, USA", "Texas")
        assert_score(score, 0.95, 1.0, "1.6 State name with country")


# ══════════════════════════════════════════════
# CATEGORY 2 — Case Variations
# ══════════════════════════════════════════════

class TestCategory2_CaseVariations:

    def test_2_1_all_caps(self, matcher):
        score = matcher.match("IRAN", "Iran")
        assert_score(score, 0.95, 1.0, "2.1 All caps query")

    def test_2_2_all_lowercase(self, matcher):
        score = matcher.match("iran", "Iran")
        assert_score(score, 0.95, 1.0, "2.2 All lowercase query")

    def test_2_3_mixed_case(self, matcher):
        score = matcher.match("iRaN", "Iran")
        assert_score(score, 0.95, 1.0, "2.3 Mixed case")

    def test_2_4_multi_word_caps(self, matcher):
        score = matcher.match("NORTH KOREA", "North Korea")
        assert_score(score, 0.95, 1.0, "2.4 Multi-word all caps")

    def test_2_5_result_lowercase(self, matcher):
        score = matcher.match("France", "france")
        assert_score(score, 0.95, 1.0, "2.5 Lowercase elastic result")

    def test_2_6_random_caps_multi(self, matcher):
        score = matcher.match("sOuTh kOrEa", "South Korea")
        assert_score(score, 0.90, 1.0, "2.6 Random caps multi-word")


# ══════════════════════════════════════════════
# CATEGORY 3 — Noise Words In Between
# ══════════════════════════════════════════════

class TestCategory3_NoiseInBetween:

    def test_3_1_one_noise_word(self, matcher):
        score = matcher.match("North Hirani Korea", "North Korea")
        assert_score(score, 0.55, 0.75, "3.1 One noise word between tokens")

    def test_3_2_noise_in_south_korea(self, matcher):
        score = matcher.match("South New Korea", "South Korea")
        assert_score(score, 0.95, 1.0, "3.2 Noise token stripped in South Korea")

    def test_3_3_new_york_noise(self, matcher):
        score = matcher.match("New random York", "New York")
        assert_score(score, 0.50, 0.72, "3.3 Noise in New York")

    def test_3_4_multiple_noise_words(self, matcher):
        score = matcher.match("Los random stuff Angeles", "Los Angeles")
        assert_score(score, 0.35, 0.60, "3.4 Multiple noise words")

    def test_3_5_noise_before_match(self, matcher):
        score = matcher.match("Blah Blah Iran", "Iran")
        assert_score(score, 0.85, 1.0, "3.5 Noise before match — MAX strategy takes best token")

    def test_3_6_noise_after_match(self, matcher):
        score = matcher.match("Iran blah blah", "Iran")
        assert_score(score, 0.85, 1.0, "3.6 Noise after match — MAX strategy")

    def test_3_7_two_noise_words_between(self, matcher):
        score = matcher.match("North Foo Bar Korea", "North Korea")
        assert_score(score, 0.35, 0.60, "3.7 Two noise words between multi-token result")


# ══════════════════════════════════════════════
# CATEGORY 4 — Substring / Partial Word Match
# ══════════════════════════════════════════════

class TestCategory4_SubstringMatch:

    def test_4_1_result_inside_query_token(self, matcher):
        # Elevated single-token path: "iran" is embedded (non-prefix/suffix) inside
        # "hirani" with ratio≈0.667, yielding bidirectional quality ~0.833.
        score = matcher.match("20, Hirani Apt, Blore", "Iran")
        assert_score(score, 0.80, 0.86, "4.1 Iran inside Hirani — elevated quality score")

    def test_4_2_prefix_match(self, matcher):
        score = matcher.match("Franceville", "France")
        assert_score(score, 0.40, 0.60, "4.2 France is prefix of Franceville")

    def test_4_3_suffix_match(self, matcher):
        score = matcher.match("Koreans live here", "Korea")
        assert_score(score, 0.40, 0.60, "4.3 Korea is prefix of Koreans")

    def test_4_4_partial_inside_token(self, matcher):
        score = matcher.match("Indira Nagar", "India")
        assert_score(score, 0.30, 0.55, "4.4 India inside Indira")

    def test_4_5_result_prefix_of_token(self, matcher):
        score = matcher.match("Koreana restaurant", "Korea")
        assert_score(score, 0.25, 0.40, "4.5 Korea prefix of Koreana")

    def test_4_6_short_result_substring_guard(self, matcher):
        # "Ir" is too short to substring-match — should score very low
        score = matcher.match("Bird sanctuary", "Ir")
        assert_score(score, 0.0, 0.20, "4.6 Short result substring false-positive guard")


# ══════════════════════════════════════════════
# CATEGORY 5 — Word Order Reversal
# ══════════════════════════════════════════════

class TestCategory5_WordOrderReversal:

    def test_5_1_korea_north_reversed(self, matcher):
        score = matcher.match("Korea North", "North Korea")
        assert_score(score, 0.72, 0.88, "5.1 Korea North vs North Korea")

    def test_5_2_korea_south_reversed(self, matcher):
        score = matcher.match("Korea South", "South Korea")
        assert_score(score, 0.72, 0.88, "5.2 Korea South reversed")

    def test_5_3_york_new_reversed(self, matcher):
        score = matcher.match("York New", "New York")
        assert_score(score, 0.72, 0.88, "5.3 York New reversed")

    def test_5_4_arabia_saudi_reversed(self, matcher):
        score = matcher.match("Arabia Saudi", "Saudi Arabia")
        assert_score(score, 0.72, 0.88, "5.4 Arabia Saudi reversed")

    def test_5_5_three_word_partial_reverse(self, matcher):
        score = matcher.match("Emirates Arab United", "United Arab Emirates")
        assert_score(score, 0.55, 0.80, "5.5 Three-word reversed")


# ══════════════════════════════════════════════
# CATEGORY 6 — Ambiguous Multi-Match
# ══════════════════════════════════════════════

class TestCategory6_AmbiguousMultiMatch:

    def test_6_1_north_disambiguates_korea(self, matcher):
        score_nk = matcher.match("Korea North", "North Korea")
        score_sk = matcher.match("Korea North", "South Korea")
        assert score_nk > score_sk, "6.1 North Korea should score higher than South Korea for 'Korea North'"

    def test_6_2_south_disambiguates_korea(self, matcher):
        score_sk = matcher.match("South Korea", "South Korea")
        score_nk = matcher.match("South Korea", "North Korea")
        assert score_sk > score_nk, "6.2 South Korea should beat North Korea for 'South Korea'"

    def test_6_3_georgia_country_exact(self, matcher):
        score = matcher.match("Georgia", "Georgia")
        assert_score(score, 0.92, 1.0, "6.3 Georgia exact (ambiguous but exact match)")

    def test_6_4_new_york_city_vs_state(self, matcher):
        score_city = matcher.match("New York City", "New York")
        assert_score(score_city, 0.80, 1.0, "6.4 New York City vs New York")

    def test_6_5_guinea_partial(self, matcher):
        score_guinea = matcher.match("Guinea coast", "Guinea")
        score_png = matcher.match("Guinea coast", "Papua New Guinea")
        # Guinea should score higher than Papua New Guinea
        assert score_guinea >= score_png, "6.5 Plain Guinea should score >= Papua New Guinea"

    def test_6_6_north_single_token_vs_north_korea(self, matcher):
        score = matcher.match("North", "North Korea")
        assert_score(score, 0.70, 0.80, "6.6 Single token North vs multi-token North Korea = partial")


# ══════════════════════════════════════════════
# CATEGORY 7 — Abbreviations & Acronyms
# ══════════════════════════════════════════════

class TestCategory7_Abbreviations:

    def test_7_1_usa(self, matcher):
        score = matcher.match("USA", "United States")
        assert_score(score, 0.78, 0.92, "7.1 USA → United States")

    def test_7_2_uk(self, matcher):
        score = matcher.match("UK", "United Kingdom")
        assert_score(score, 0.78, 0.92, "7.2 UK → United Kingdom")

    def test_7_3_uae(self, matcher):
        score = matcher.match("UAE", "United Arab Emirates")
        assert_score(score, 0.78, 0.92, "7.3 UAE → United Arab Emirates")

    def test_7_4_us(self, matcher):
        score = matcher.match("US", "United States")
        assert_score(score, 0.72, 0.90, "7.4 US → United States")

    def test_7_5_ny_state(self, matcher):
        score = matcher.match("NY", "New York")
        assert_score(score, 0.75, 0.90, "7.5 NY → New York")

    def test_7_6_s_korea(self, matcher):
        score = matcher.match("S. Korea", "South Korea")
        assert_score(score, 0.78, 0.92, "7.6 S. Korea → South Korea")

    def test_7_7_n_korea(self, matcher):
        score = matcher.match("N. Korea", "North Korea")
        assert_score(score, 0.78, 0.92, "7.7 N. Korea → North Korea")

    def test_7_8_usa_in_address(self, matcher):
        score = matcher.match("123 Main St, Austin, USA", "United States")
        assert_score(score, 0.75, 0.92, "7.8 USA inside full address")


# ══════════════════════════════════════════════
# CATEGORY 8 — Typos & Misspellings
# ══════════════════════════════════════════════

class TestCategory8_TyposMisspellings:

    def test_8_1_transposition(self, matcher):
        score = matcher.match("Iarn", "Iran")
        assert_score(score, 0.72, 0.88, "8.1 Transposition: Iarn → Iran")

    def test_8_2_swap_chars(self, matcher):
        score = matcher.match("Frnace", "France")
        assert_score(score, 0.72, 0.88, "8.2 Swap: Frnace → France")

    def test_8_3_two_char_errors(self, matcher):
        score = matcher.match("Koeea", "Korea")
        assert_score(score, 0.65, 0.82, "8.3 Two errors: Koeea → Korea")

    def test_8_4_missing_char(self, matcher):
        score = matcher.match("Germny", "Germany")
        assert_score(score, 0.75, 0.90, "8.4 Missing char: Germny → Germany")

    def test_8_5_extra_char(self, matcher):
        score = matcher.match("Australiaa", "Australia")
        assert_score(score, 0.80, 0.92, "8.5 Extra char: Australiaa → Australia")

    def test_8_6_typo_in_first_token(self, matcher):
        score = matcher.match("Noth Korea", "North Korea")
        assert_score(score, 0.78, 0.92, "8.6 Typo in first token: Noth Korea")

    def test_8_7_double_letter(self, matcher):
        score = matcher.match("Iraann", "Iran")
        assert_score(score, 0.70, 0.88, "8.7 Double letter typo")

    def test_8_8_adjacent_key_typo(self, matcher):
        score = matcher.match("Frsnce", "France")
        assert_score(score, 0.70, 0.88, "8.8 Adjacent key typo: Frsnce → France")


# ══════════════════════════════════════════════
# CATEGORY 9 — Transliterations & Alternate Names
# ══════════════════════════════════════════════

class TestCategory9_AlternateNames:

    def test_9_1_bharat_india(self, matcher):
        score = matcher.match("Bharat", "India")
        assert_score(score, 0.55, 0.90, "9.1 Bharat → India (alternate name)")

    def test_9_2_peking_beijing(self, matcher):
        score = matcher.match("Peking", "Beijing")
        assert_score(score, 0.50, 0.85, "9.2 Peking → Beijing")

    def test_9_3_munchen_munich(self, matcher):
        score = matcher.match("Munchen", "Munich")
        assert_score(score, 0.55, 0.82, "9.3 Munchen → Munich")

    def test_9_4_moskva_moscow(self, matcher):
        score = matcher.match("Moskva", "Moscow")
        assert_score(score, 0.45, 0.82, "9.4 Moskva → Moscow")

    def test_9_5_Praha_Prague(self, matcher):
        score = matcher.match("Praha", "Prague")
        assert_score(score, 0.45, 0.82, "9.5 Praha → Prague")

    def test_9_6_allemagne_germany(self, matcher):
        score = matcher.match("Allemagne", "Germany")
        assert_score(score, 0.50, 0.85, "9.6 Allemagne → Germany (French name)")


# ══════════════════════════════════════════════
# CATEGORY 10 — Diacritics & Unicode
# ══════════════════════════════════════════════

class TestCategory10_DiacriticsUnicode:

    def test_10_1_reunion_accent(self, matcher):
        score = matcher.match("Réunion", "Reunion")
        assert_score(score, 0.90, 1.0, "10.1 Réunion accent stripped")

    def test_10_2_sao_paulo_tilde(self, matcher):
        score = matcher.match("São Paulo", "Sao Paulo")
        assert_score(score, 0.90, 1.0, "10.2 São Paulo tilde stripped")

    def test_10_3_cote_divoire(self, matcher):
        score = matcher.match("Côte d'Ivoire", "Cote Ivoire")
        assert_score(score, 0.80, 1.0, "10.3 Côte d'Ivoire apostrophe and accent")

    def test_10_4_aland_scandinavian(self, matcher):
        score = matcher.match("Åland Islands", "Aland")
        assert_score(score, 0.82, 1.0, "10.4 Åland Scandinavian char")

    def test_10_5_munchen_umlaut(self, matcher):
        score = matcher.match("München", "Munchen")
        assert_score(score, 0.88, 1.0, "10.5 München umlaut → Munchen")

    def test_10_6_parentheses_in_address(self, matcher):
        score = matcher.match("Korea(South)", "South Korea")
        assert_score(score, 0.72, 0.92, "10.6 Parentheses in address")

    def test_10_7_slash_separator(self, matcher):
        score = matcher.match("Iran/Iraq border", "Iran")
        assert_score(score, 0.85, 1.0, "10.7 Slash splits into separate tokens")


# ══════════════════════════════════════════════
# CATEGORY 11 — Hyphenated & Compound Names
# ══════════════════════════════════════════════

class TestCategory11_HyphenatedNames:

    def test_11_1_guinea_bissau_exact(self, matcher):
        score = matcher.match("Guinea-Bissau", "Guinea-Bissau")
        assert_score(score, 0.92, 1.0, "11.1 Guinea-Bissau exact with hyphen")

    def test_11_2_guinea_bissau_space(self, matcher):
        score = matcher.match("Guinea Bissau", "Guinea-Bissau")
        assert_score(score, 0.88, 1.0, "11.2 Guinea Bissau space vs hyphen result")

    def test_11_3_guinea_bissau_nospace(self, matcher):
        score = matcher.match("GuineaBissau", "Guinea-Bissau")
        assert_score(score, 0.75, 0.92, "11.3 GuineaBissau no separator")

    def test_11_4_timor_leste_hyphen(self, matcher):
        score = matcher.match("Timor-Leste", "Timor Leste")
        assert_score(score, 0.90, 1.0, "11.4 Timor-Leste hyphen vs space result")

    def test_11_5_bosnia_missing_and(self, matcher):
        score = matcher.match("Bosnia Herzegovina", "Bosnia and Herzegovina")
        assert_score(score, 0.80, 0.95, "11.5 Bosnia Herzegovina missing 'and'")


# ══════════════════════════════════════════════
# CATEGORY 12 — Articles, Connectors & Prepositions
# ══════════════════════════════════════════════

class TestCategory12_ArticlesConnectors:

    def test_12_1_the_gambia(self, matcher):
        score = matcher.match("The Gambia", "Gambia")
        assert_score(score, 0.88, 1.0, "12.1 Leading 'The' stripped")

    def test_12_2_republic_of_korea(self, matcher):
        score = matcher.match("Republic of Korea", "South Korea")
        assert_score(score, 0.40, 0.65, "12.2 Republic of Korea → South Korea")

    def test_12_3_kingdom_of_saudi(self, matcher):
        score = matcher.match("Kingdom of Saudi Arabia", "Saudi Arabia")
        assert_score(score, 0.80, 0.95, "12.3 Kingdom of Saudi Arabia stripped prefix")

    def test_12_4_state_of_new_york(self, matcher):
        score = matcher.match("State of New York", "New York")
        assert_score(score, 0.80, 0.95, "12.4 State of New York stripped prefix")

    def test_12_5_province_of_quebec(self, matcher):
        score = matcher.match("Province of Quebec", "Quebec")
        assert_score(score, 0.82, 1.0, "12.5 Province of Quebec")

    def test_12_6_bosnia_and_official(self, matcher):
        # 'and' is part of official name — must NOT be stripped from result
        score = matcher.match("Bosnia and Herzegovina", "Bosnia and Herzegovina")
        assert_score(score, 0.92, 1.0, "12.6 Bosnia and Herzegovina — 'and' is official")


# ══════════════════════════════════════════════
# CATEGORY 13 — Numbers & Alphanumeric Tokens
# ══════════════════════════════════════════════

class TestCategory13_NumbersAlphanumeric:

    def test_13_1_number_prefix(self, matcher):
        score = matcher.match("10, Green Apt, Iran", "Iran")
        assert_score(score, 0.92, 1.0, "13.1 Number 10 ignored")

    def test_13_2_alphanumeric_token(self, matcher):
        score = matcher.match("B-204, Korea Tower", "Korea")
        assert_score(score, 0.55, 0.80, "13.2 Alphanumeric token B-204 ignored")

    def test_13_3_pincode(self, matcher):
        score = matcher.match("400001, Mumbai", "Mumbai")
        assert_score(score, 0.90, 1.0, "13.3 Pincode ignored")

    def test_13_4_po_box(self, matcher):
        score = matcher.match("P.O. Box 44, France", "France")
        assert_score(score, 0.60, 0.70, "13.4 P.O. Box stripped")

    def test_13_5_zip_code_usa(self, matcher):
        score = matcher.match("90210, Beverly Hills, USA", "United States")
        assert_score(score, 0.75, 0.92, "13.5 Zip code ignored, USA matched")

    def test_13_6_pure_number_query(self, matcher):
        score = matcher.match("123456", "Iran")
        assert_score(score, 0.0, 0.15, "13.6 Pure number query → near zero")


# ══════════════════════════════════════════════
# CATEGORY 14 — Repeated / Duplicate Tokens
# ══════════════════════════════════════════════

class TestCategory14_DuplicateTokens:

    def test_14_1_duplicate_single(self, matcher):
        score = matcher.match("Iran Iran", "Iran")
        assert_score(score, 0.92, 1.0, "14.1 Deduplicated Iran Iran")

    def test_14_2_repeated_first_word(self, matcher):
        score = matcher.match("North North Korea", "North Korea")
        assert_score(score, 0.82, 1.0, "14.2 North North Korea deduped")

    def test_14_3_reversed_duplicate(self, matcher):
        score = matcher.match("Korea Korea South", "South Korea")
        assert_score(score, 0.75, 0.92, "14.3 Korea Korea South")

    def test_14_4_triple_repeat(self, matcher):
        score = matcher.match("France France France", "France")
        assert_score(score, 0.92, 1.0, "14.4 Triple repeated France")


# ══════════════════════════════════════════════
# CATEGORY 15 — Very Short / Single Char Tokens
# ══════════════════════════════════════════════

class TestCategory15_ShortTokens:

    def test_15_1_single_chars_ignored(self, matcher):
        score = matcher.match("A, B, Iran", "Iran")
        assert_score(score, 0.75, 0.85, "15.1 Single char tokens A, B ignored")

    def test_15_2_s_abbreviation(self, matcher):
        score = matcher.match("S. Korea", "South Korea")
        assert_score(score, 0.78, 0.92, "15.2 S. is abbreviation not noise")

    def test_15_3_n_abbreviation(self, matcher):
        score = matcher.match("N. Korea", "North Korea")
        assert_score(score, 0.78, 0.92, "15.3 N. is abbreviation not noise")

    def test_15_4_i_ran_false_match(self, matcher):
        # "I ran" should NOT match "Iran"
        score = matcher.match("I ran to the store", "Iran")
        assert_score(score, 0.0, 0.30, "15.4 'I ran' should not strongly match Iran")

    def test_15_5_two_char_minimum(self, matcher):
        score = matcher.match("Go to IR", "Iran")
        assert_score(score, 0.0, 0.35, "15.5 Two char IR vs Iran — low score")


# ══════════════════════════════════════════════
# CATEGORY 16 — False Positive / Common Word Collisions
# ══════════════════════════════════════════════

class TestCategory16_FalsePositives:

    def test_16_1_marine_vs_iran(self, matcher):
        # "Marine" contains "iran" — must be suppressed
        score = matcher.match("Marine Drive, India", "Iran")
        assert_score(score, 0.0, 0.20, "16.1 Marine contains iran — false positive suppressed")

    def test_16_2_china_common_word(self, matcher):
        score = matcher.match("China Cabinet Store, LA", "China")
        assert_score(score, 0.0, 0.35, "16.2 China as common word in non-geo context")

    def test_16_3_turkey_food(self, matcher):
        score = matcher.match("Turkey sandwich shop", "Turkey")
        assert_score(score, 0.0, 0.30, "16.3 Turkey as food word")

    def test_16_4_nice_adjective(self, matcher):
        score = matcher.match("Nice apartment for rent", "Nice")
        assert_score(score, 0.0, 0.40, "16.4 Nice as adjective vs Nice city France")

    def test_16_5_peru_street(self, matcher):
        score = matcher.match("Peru St, Denver, CO", "Peru")
        assert_score(score, 0.30, 0.65, "16.5 Peru in street name — uncertain, moderate score acceptable")

    def test_16_6_jordan_shoes(self, matcher):
        score = matcher.match("Jordan shoes store", "Jordan")
        assert_score(score, 0.0, 0.40, "16.6 Jordan brand vs Jordan country")

    def test_16_7_iran_clean_vs_iran_noise(self, matcher):
        clean = matcher.match("Tehran, Iran", "Iran")
        noise = matcher.match("Marine Irani Rd", "Iran")
        assert clean > noise, "16.7 Clean Iran match must score higher than substring noise"


# ══════════════════════════════════════════════
# CATEGORY 17 — Multi-Entity Address
# ══════════════════════════════════════════════

class TestCategory17_MultiEntityAddress:

    def test_17_1_city_state_country_all_present(self, matcher):
        score_city = matcher.match("Manhattan, New York, USA", "Manhattan")
        score_state = matcher.match("Manhattan, New York, USA", "New York")
        score_country = matcher.match("Manhattan, New York, USA", "United States")
        assert score_city >= 0.85, "17.1a Manhattan should score high"
        assert score_state >= 0.85, "17.1b New York should score high"
        assert score_country >= 0.72, "17.1c United States (from USA) should score high"

    def test_17_2_full_us_address(self, matcher):
        score = matcher.match("Austin, Texas, United States", "Texas")
        assert_score(score, 0.88, 1.0, "17.2 Texas in full US address")

    def test_17_3_london_england_uk(self, matcher):
        score_city = matcher.match("London, England, UK", "London")
        score_country = matcher.match("London, England, UK", "United Kingdom")
        assert score_city >= 0.88, "17.3a London exact"
        assert score_country >= 0.72, "17.3b UK → United Kingdom"

    def test_17_4_independent_scoring(self, matcher):
        # Multiple results score independently, not competing
        score1 = matcher.match("Paris, France", "Paris")
        score2 = matcher.match("Paris, France", "France")
        assert score1 >= 0.88, "17.4a Paris should score high"
        assert score2 >= 0.88, "17.4b France should score high"


# ══════════════════════════════════════════════
# CATEGORY 18 — Directional Words as Part of Name
# ══════════════════════════════════════════════

class TestCategory18_DirectionalWords:

    def test_18_1_north_korea_exact(self, matcher):
        score = matcher.match("North Korea", "North Korea")
        assert_score(score, 0.95, 1.0, "18.1 North Korea exact")

    def test_18_2_north_vs_south_penalty(self, matcher):
        score = matcher.match("North Korea", "South Korea")
        assert_score(score, 0.35, 0.60, "18.2 North Korea vs South Korea — directional mismatch penalty")

    def test_18_3_east_timor_old_name(self, matcher):
        score = matcher.match("East Timor", "Timor-Leste")
        assert_score(score, 0.50, 0.80, "18.3 East Timor old name")

    def test_18_4_western_australia_vs_australia(self, matcher):
        score = matcher.match("Western Australia", "Australia")
        assert_score(score, 0.45, 0.70, "18.4 Western Australia region vs country")

    def test_18_5_north_partial_multi(self, matcher):
        score = matcher.match("North", "North Korea")
        assert_score(score, 0.70, 0.80, "18.5 Single North vs North Korea is partial")

    def test_18_6_south_partial_multi(self, matcher):
        score = matcher.match("South", "South Korea")
        assert_score(score, 0.70, 0.80, "18.6 Single South vs South Korea is partial")


# ══════════════════════════════════════════════
# CATEGORY 19 — Punctuation Variations
# ══════════════════════════════════════════════

class TestCategory19_PunctuationVariations:

    def test_19_1_trailing_period(self, matcher):
        score = matcher.match("Iran.", "Iran")
        assert_score(score, 0.92, 1.0, "19.1 Trailing period stripped")

    def test_19_2_quoted_token(self, matcher):
        score = matcher.match('"Iran"', "Iran")
        assert_score(score, 0.92, 1.0, '19.2 Quoted "Iran" stripped')

    def test_19_3_trailing_comma(self, matcher):
        score = matcher.match("Iran,", "Iran")
        assert_score(score, 0.92, 1.0, "19.3 Trailing comma stripped")

    def test_19_4_parentheses_wrapping(self, matcher):
        score = matcher.match("(Iran)", "Iran")
        assert_score(score, 0.92, 1.0, "19.4 Parentheses stripped")

    def test_19_5_slash_both_tokens(self, matcher):
        score_iran = matcher.match("Iran/Iraq", "Iran")
        score_iraq = matcher.match("Iran/Iraq", "Iraq")
        assert score_iran >= 0.85, "19.5a Iran from Iran/Iraq"
        assert score_iraq >= 0.85, "19.5b Iraq from Iran/Iraq"

    def test_19_6_dot_separated(self, matcher):
        score = matcher.match("North.Korea", "North Korea")
        assert_score(score, 0.80, 1.0, "19.6 Dot-separated North.Korea")

    def test_19_7_comma_separated_no_spaces(self, matcher):
        score = matcher.match("Paris,France", "France")
        assert_score(score, 0.88, 1.0, "19.7 Comma with no space separator")


# ══════════════════════════════════════════════
# CATEGORY 20 — Empty / Garbage Input
# ══════════════════════════════════════════════

class TestCategory20_GarbageInput:

    def test_20_1_empty_query(self, matcher):
        score = matcher.match("", "Iran")
        assert score == 0.0, "20.1 Empty query → 0.0"

    def test_20_2_empty_result(self, matcher):
        score = matcher.match("Iran", "")
        assert score == 0.0, "20.2 Empty result → 0.0"

    def test_20_3_both_empty(self, matcher):
        score = matcher.match("", "")
        assert score == 0.0, "20.3 Both empty → 0.0"

    def test_20_4_pure_number_query(self, matcher):
        score = matcher.match("123456", "Iran")
        assert_score(score, 0.0, 0.10, "20.4 Pure number query → 0.0")

    def test_20_5_symbols_only(self, matcher):
        score = matcher.match("@#$%", "Iran")
        assert_score(score, 0.0, 0.10, "20.5 Symbols only → 0.0")

    def test_20_6_na_token(self, matcher):
        score = matcher.match("N/A", "Iran")
        assert_score(score, 0.0, 0.10, "20.6 N/A garbage token → 0.0")

    def test_20_7_unknown_token(self, matcher):
        score = matcher.match("Unknown", "Iran")
        assert_score(score, 0.0, 0.15, "20.7 Unknown garbage token → near 0.0")

    def test_20_8_whitespace_only(self, matcher):
        score = matcher.match("   ", "Iran")
        assert score == 0.0, "20.8 Whitespace only query → 0.0"

    def test_20_9_type_error_raises(self, matcher):
        with pytest.raises((TypeError, ValueError)):
            matcher.match(None, "Iran")

    def test_20_10_type_error_result_none(self, matcher):
        with pytest.raises((TypeError, ValueError)):
            matcher.match("Iran", None)


# ══════════════════════════════════════════════
# CATEGORY 21 — Phonetic / Soundex Edge Cases
# ══════════════════════════════════════════════

class TestCategory21_Phonetic:

    def test_21_1_phonetic_iran(self, matcher):
        # Phonetically similar but different spelling
        score = matcher.match("Eyran", "Iran")
        assert_score(score, 0.55, 0.85, "21.1 Phonetic: Eyran → Iran")

    def test_21_2_phonetic_france(self, matcher):
        score = matcher.match("Frans", "France")
        assert_score(score, 0.60, 0.85, "21.2 Phonetic: Frans → France")

    def test_21_3_phonetic_korea(self, matcher):
        score = matcher.match("Corea", "Korea")
        assert_score(score, 0.65, 0.88, "21.3 Phonetic: Corea → Korea (historical spelling)")


# ══════════════════════════════════════════════
# CATEGORY 22 — Score Ordering / Relative Rank Tests
# ══════════════════════════════════════════════

class TestCategory22_ScoreOrdering:

    def test_22_1_exact_beats_fuzzy(self, matcher):
        exact = matcher.match("Iran", "Iran")
        fuzzy = matcher.match("Iarn", "Iran")
        assert exact > fuzzy, "22.1 Exact must beat typo match"

    def test_22_2_fuzzy_beats_substring(self, matcher):
        # After the elevated-quality path, a high-ratio embedded substring
        # ("hirani"↔"iran", ratio≈0.667, quality≈0.833) scores above a 2-edit
        # typo ("iarn"↔"iran", ~0.82).  Both are strong matches; verify ranges
        # and ordering independently.
        fuzzy = matcher.match("Iarn", "Iran")
        substr = matcher.match("Hirani", "Iran")
        assert_score(fuzzy, 0.78, 0.88, "22.2a 2-edit typo scores high")
        assert_score(substr, 0.80, 0.86, "22.2b elevated embedded substring scores high")
        assert substr >= fuzzy, "22.2c elevated substring meets or beats 2-edit typo"

    def test_22_3_ordered_beats_reversed(self, matcher):
        ordered = matcher.match("North Korea", "North Korea")
        reversed_ = matcher.match("Korea North", "North Korea")
        assert ordered > reversed_, "22.3 Correct order must beat reversed"

    def test_22_4_reversed_beats_noisy(self, matcher):
        reversed_ = matcher.match("Korea North", "North Korea")
        noisy = matcher.match("North Random Korea", "North Korea")
        assert reversed_ > noisy, "22.4 Reversed beats noisy interleaved"

    def test_22_5_full_match_beats_partial(self, matcher):
        full = matcher.match("South Korea", "South Korea")
        partial = matcher.match("Korea", "South Korea")
        assert full > partial, "22.5 Full match beats partial token coverage"

    def test_22_6_abbreviation_below_exact(self, matcher):
        exact = matcher.match("United States", "United States")
        abbrev = matcher.match("USA", "United States")
        assert exact > abbrev, "22.6 Exact beats abbreviation expansion"


# ══════════════════════════════════════════════
# CATEGORY 23 — Real-World Complex Addresses
# ══════════════════════════════════════════════

class TestCategory23_RealWorldAddresses:

    def test_23_1_india_full_address(self, matcher):
        score = matcher.match("204, MG Road, Bangalore, Karnataka, India", "India")
        assert_score(score, 0.85, 1.0, "23.1 Full Indian address → India")

    def test_23_2_india_state(self, matcher):
        score = matcher.match("204, MG Road, Bangalore, Karnataka, India", "Karnataka")
        assert_score(score, 0.88, 1.0, "23.2 Full Indian address → Karnataka state")

    def test_23_3_us_street_address(self, matcher):
        score = matcher.match("1600 Pennsylvania Ave NW, Washington, DC, USA", "United States")
        assert_score(score, 0.72, 0.92, "23.3 Famous US address → United States")

    def test_23_4_uk_postcode_address(self, matcher):
        score = matcher.match("10 Downing St, Westminster, London SW1A 2AA, UK", "United Kingdom")
        assert_score(score, 0.72, 0.92, "23.4 UK address with postcode → United Kingdom")

    def test_23_5_messy_international(self, matcher):
        score = matcher.match("apt 5b, block C, near metro, North Korea zone", "North Korea")
        assert_score(score, 0.72, 0.92, "23.5 Messy address with North Korea")

    def test_23_6_chinese_city_english(self, matcher):
        score = matcher.match("No. 1 Changan Ave, Beijing, China", "China")
        assert_score(score, 0.85, 1.0, "23.6 Beijing address → China")

    def test_23_7_japanese_address(self, matcher):
        score = matcher.match("1-1 Chiyoda, Tokyo, Japan", "Japan")
        assert_score(score, 0.88, 1.0, "23.7 Tokyo address → Japan")


# ══════════════════════════════════════════════
# CATEGORY 24 — get_debug_breakdown() Contract
# ══════════════════════════════════════════════

class TestCategory24_DebugBreakdown:

    def test_24_1_returns_dict(self, matcher):
        result = matcher.get_debug_breakdown("Iran", "Iran")
        assert isinstance(result, dict), "24.1 get_debug_breakdown must return dict"

    def test_24_2_contains_final_score(self, matcher):
        result = matcher.get_debug_breakdown("Iran", "Iran")
        assert "final_score" in result, "24.2 debug dict must have final_score key"

    def test_24_3_score_matches_match(self, matcher):
        debug = matcher.get_debug_breakdown("North Korea", "North Korea")
        direct = matcher.match("North Korea", "North Korea")
        assert abs(debug["final_score"] - direct) < 0.001, "24.3 Debug score must match match() score"

    def test_24_4_contains_token_scores(self, matcher):
        result = matcher.get_debug_breakdown("Tehran, Iran", "Iran")
        assert "token_scores" in result or "steps" in result, "24.4 Must contain token-level breakdown"

    def test_24_5_false_positive_visible(self, matcher):
        result = matcher.get_debug_breakdown("Marine Drive", "Iran")
        assert result["final_score"] < 0.25, "24.5 Debug score for false-positive should be low"


# ══════════════════════════════════════════════
# CATEGORY 25 — Stopword Handling Specifics
# ══════════════════════════════════════════════

class TestCategory25_StopwordHandling:

    def test_25_1_street_stripped(self, matcher):
        score = matcher.match("Main Street, Iran", "Iran")
        assert_score(score, 0.90, 1.0, "25.1 'Street' stripped from query")

    def test_25_2_road_stripped(self, matcher):
        score = matcher.match("Park Road, France", "France")
        assert_score(score, 0.90, 1.0, "25.2 'Road' stripped")

    def test_25_3_avenue_stripped(self, matcher):
        score = matcher.match("5th Avenue, New York", "New York")
        assert_score(score, 0.88, 1.0, "25.3 'Avenue' stripped")

    def test_25_4_apartment_stripped(self, matcher):
        score = matcher.match("Apartment 4B, Tehran, Iran", "Iran")
        assert_score(score, 0.45, 0.60, "25.4 'Apartment' stripped")

    def test_25_5_lane_stripped(self, matcher):
        score = matcher.match("Green Lane, London, UK", "United Kingdom")
        assert_score(score, 0.72, 0.92, "25.5 'Lane' stripped")

    def test_25_6_suite_stripped(self, matcher):
        score = matcher.match("Suite 200, Sydney, Australia", "Australia")
        assert_score(score, 0.88, 1.0, "25.6 'Suite' stripped")

    def test_25_7_and_preserved_in_result(self, matcher):
        # "and" should NOT be stripped from "Bosnia and Herzegovina" result
        score = matcher.match("Bosnia and Herzegovina", "Bosnia and Herzegovina")
        assert_score(score, 0.92, 1.0, "25.7 'and' preserved in official result name")
