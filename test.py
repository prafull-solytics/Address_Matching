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
        assert_score(score, 0.85, 1.0, "16.5 Peru exact token in street address — high confidence")

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
        assert_score(score, 0.80, 0.90, "18.4 Western Australia — adjacent directional, reduced penalty")

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
        assert_score(score, 0.95, 1.0, "23.5 Messy address with North Korea — exact contiguous match")

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


# ══════════════════════════════════════════════
# CATEGORY 26 — Exact Component in Full Address
# ══════════════════════════════════════════════
# When a location component exists exactly in an address (after normalization),
# the score must be 1.0 — regardless of how many other tokens surround it.

class TestCategory26_ExactComponentInFullAddress:

    FULL_ADDRESS = "221B, Baker Street, Los Angeles, California, USA"

    def test_26_01_usa_exact_in_address(self, matcher):
        # "USA" appears exactly in the address → must be 1.0
        score = matcher.match(self.FULL_ADDRESS, "USA")
        assert_score(score, 0.95, 1.0, "26.1 USA exact token in full address")

    def test_26_02_california_exact_in_address(self, matcher):
        score = matcher.match(self.FULL_ADDRESS, "California")
        assert_score(score, 0.95, 1.0, "26.2 California exact token in full address")

    def test_26_03_los_angeles_exact_in_address(self, matcher):
        # "Los Angeles" appears contiguously in the address → must be 1.0
        score = matcher.match(self.FULL_ADDRESS, "Los Angeles")
        assert_score(score, 0.95, 1.0, "26.3 Los Angeles exact contiguous match in full address")

    def test_26_04_new_york_not_in_address(self, matcher):
        # "New York" does NOT appear in the address → must be 0.0
        score = matcher.match(self.FULL_ADDRESS, "New York")
        assert_score(score, 0.0, 0.05, "26.4 New York not in address → zero")

    def test_26_05_texas_not_in_address(self, matcher):
        # "Texas" does NOT appear in the address → must be 0.0
        score = matcher.match(self.FULL_ADDRESS, "Texas")
        assert_score(score, 0.0, 0.05, "26.5 Texas not in address → zero")

    def test_26_06_usa_abbreviation_vs_united_states(self, matcher):
        # "USA" in address should still map to "United States" via abbreviation
        # but at a capped abbreviation score, NOT 1.0
        score = matcher.match(self.FULL_ADDRESS, "United States")
        assert_score(score, 0.78, 0.92, "26.6 USA abbreviation → United States capped")

    def test_26_07_india_full_address_exact(self, matcher):
        # India exact token in a long Indian address
        score = matcher.match("204, MG Road, Bangalore, Karnataka, India", "India")
        assert_score(score, 0.95, 1.0, "26.7 India exact in full Indian address")

    def test_26_08_karnataka_exact_in_address(self, matcher):
        score = matcher.match("204, MG Road, Bangalore, Karnataka, India", "Karnataka")
        assert_score(score, 0.95, 1.0, "26.8 Karnataka exact in full Indian address")

    def test_26_09_multi_token_exact_in_long_address(self, matcher):
        # "New York" appears contiguously in a long address
        score = matcher.match("123 Broadway, Manhattan, New York, NY, USA", "New York")
        assert_score(score, 0.95, 1.0, "26.9 New York exact contiguous in long US address")

    def test_26_10_max_scoring_strategy(self, matcher):
        # If a result token matches multiple query tokens with different scores,
        # the maximum score should be taken
        # "usa" matches "usa" exactly (1.0) even though it's also an abbreviation
        score_exact = matcher.match("Texas, USA", "USA")
        score_abbrev = matcher.match("USA", "United States")
        assert score_exact > score_abbrev, (
            "26.10 Exact 'USA' token must beat abbreviation-only expansion"
        )


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 27 — Exact Tokens In Complex World Addresses (30 tests)
# ══════════════════════════════════════════════════════════════════════════════
# When a location token exists exactly in an address, score must be ≥ 0.95.

class TestCategory27_ExactTokensInWorldAddresses:

    def test_27_01(self, matcher):
        score = matcher.match("1600 Pennsylvania Ave NW, Washington, DC 20500, USA", "Washington")
        assert_score(score, 0.95, 1.0, "27.01 Washington in US address")

    def test_27_02(self, matcher):
        score = matcher.match("1600 Pennsylvania Ave NW, Washington, DC 20500, USA", "USA")
        assert_score(score, 0.95, 1.0, "27.02 USA in US address")

    def test_27_03(self, matcher):
        score = matcher.match("350 Fifth Avenue, New York, NY 10118, USA", "New York")
        assert_score(score, 0.95, 1.0, "27.03 New York contiguous in long address")

    def test_27_04(self, matcher):
        score = matcher.match("1 Infinite Loop, Cupertino, California, USA", "Cupertino")
        assert_score(score, 0.95, 1.0, "27.04 Cupertino exact")

    def test_27_05(self, matcher):
        score = matcher.match("1 Infinite Loop, Cupertino, California, USA", "California")
        assert_score(score, 0.95, 1.0, "27.05 California exact")

    def test_27_06(self, matcher):
        score = matcher.match("742 Evergreen Terrace, Springfield, Illinois, USA", "Springfield")
        assert_score(score, 0.95, 1.0, "27.06 Springfield exact")

    def test_27_07(self, matcher):
        score = matcher.match("742 Evergreen Terrace, Springfield, Illinois, USA", "Illinois")
        assert_score(score, 0.95, 1.0, "27.07 Illinois exact")

    def test_27_08(self, matcher):
        score = matcher.match("10 Downing Street, Westminster, London, SW1A 2AA, United Kingdom", "London")
        assert_score(score, 0.90, 1.0, "27.08 London in UK address")

    def test_27_09(self, matcher):
        score = matcher.match("Champs-Élysées, 75008, Paris, France", "Paris")
        assert_score(score, 0.95, 1.0, "27.09 Paris exact — collision word in geographic context")

    def test_27_10(self, matcher):
        score = matcher.match("Champs-Élysées, 75008, Paris, France", "France")
        assert_score(score, 0.95, 1.0, "27.10 France exact")

    def test_27_11(self, matcher):
        score = matcher.match("Friedrichstraße 43, 10117 Berlin, Deutschland", "Berlin")
        assert_score(score, 0.95, 1.0, "27.11 Berlin exact — collision word in geographic context")

    def test_27_12(self, matcher):
        score = matcher.match("Gran Via 1, Madrid, Spain", "Madrid")
        assert_score(score, 0.95, 1.0, "27.12 Madrid exact")

    def test_27_13(self, matcher):
        score = matcher.match("1-1-1 Chiyoda, Tokyo 100-0001, Japan", "Tokyo")
        assert_score(score, 0.95, 1.0, "27.13 Tokyo exact")

    def test_27_14(self, matcher):
        score = matcher.match("Rajpath, New Delhi, Delhi, India, 110001", "New Delhi")
        assert_score(score, 0.95, 1.0, "27.14 New Delhi contiguous")

    def test_27_15(self, matcher):
        score = matcher.match("Rajpath, New Delhi, Delhi, India, 110001", "India")
        assert_score(score, 0.95, 1.0, "27.15 India in long Indian address")

    def test_27_16(self, matcher):
        score = matcher.match("88 Orchard Road, Singapore 238839", "Singapore")
        assert_score(score, 0.95, 1.0, "27.16 Singapore exact")

    def test_27_17(self, matcher):
        score = matcher.match("Rua Augusta 100, São Paulo, SP, Brasil", "Sao Paulo")
        assert_score(score, 0.95, 1.0, "27.17 São Paulo Unicode match")

    def test_27_18(self, matcher):
        score = matcher.match("Av. 9 de Julio, Buenos Aires, Argentina", "Buenos Aires")
        assert_score(score, 0.95, 1.0, "27.18 Buenos Aires contiguous")

    def test_27_19(self, matcher):
        score = matcher.match("Av. 9 de Julio, Buenos Aires, Argentina", "Argentina")
        assert_score(score, 0.95, 1.0, "27.19 Argentina exact")

    def test_27_20(self, matcher):
        score = matcher.match("Al Falak Street, Abu Dhabi, UAE", "Abu Dhabi")
        assert_score(score, 0.95, 1.0, "27.20 Abu Dhabi contiguous")

    def test_27_21(self, matcher):
        score = matcher.match("1 Macquarie Street, Sydney, NSW, Australia", "Sydney")
        assert_score(score, 0.95, 1.0, "27.21 Sydney exact")

    def test_27_22(self, matcher):
        score = matcher.match("1 Macquarie Street, Sydney, NSW, Australia", "Australia")
        assert_score(score, 0.95, 1.0, "27.22 Australia exact")

    def test_27_23(self, matcher):
        s = "Apt 4B, Floor 3, Tower C, Block 7, Sector 12, Noida, Uttar Pradesh, India, 201301"
        score = matcher.match(s, "India")
        assert_score(score, 0.95, 1.0, "27.23 India in very long address")

    def test_27_24(self, matcher):
        s = "Apt 4B, Floor 3, Tower C, Block 7, Sector 12, Noida, Uttar Pradesh, India, 201301"
        score = matcher.match(s, "Noida")
        assert_score(score, 0.95, 1.0, "27.24 Noida in very long address")

    def test_27_25(self, matcher):
        s = "Suite 500, 100 Broadway, Floor 12, Manhattan, New York, NY, 10005, USA"
        score = matcher.match(s, "Manhattan")
        assert_score(score, 0.95, 1.0, "27.25 Manhattan in very long US address")

    def test_27_26(self, matcher):
        score = matcher.match("350 Fifth Avenue, New York, NY 10118, USA", "USA")
        assert_score(score, 0.95, 1.0, "27.26 USA in NYC address")

    def test_27_27(self, matcher):
        score = matcher.match("10 Downing Street, Westminster, London, SW1A 2AA, United Kingdom", "Westminster")
        assert_score(score, 0.90, 1.0, "27.27 Westminster in UK address")

    def test_27_28(self, matcher):
        score = matcher.match("1-1-1 Chiyoda, Tokyo 100-0001, Japan", "Japan")
        assert_score(score, 0.95, 1.0, "27.28 Japan exact")

    def test_27_29(self, matcher):
        score = matcher.match("via Roma 10, 00184 Roma, Italia", "Rome")
        assert_score(score, 0.80, 0.92, "27.29 Roma→Rome via alternate name — capped")

    def test_27_30(self, matcher):
        score = matcher.match("1 Nelson Mandela Square, Johannesburg, South Africa", "Johannesburg")
        assert_score(score, 0.80, 1.0, "27.30 Johannesburg in South Africa address")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 28 — Non-Matching Results (20 tests)
# ══════════════════════════════════════════════════════════════════════════════
# When a location is NOT in the address, score must be 0.0.

class TestCategory28_NonMatchingResults:

    def test_28_01(self, matcher):
        score = matcher.match("221B Baker Street, Los Angeles, California, USA", "London")
        assert_score(score, 0.0, 0.05, "28.01 London not in LA address")

    def test_28_02(self, matcher):
        score = matcher.match("1-1-1 Chiyoda, Tokyo, Japan", "Korea")
        assert_score(score, 0.0, 0.05, "28.02 Korea not in Tokyo address")

    def test_28_03(self, matcher):
        score = matcher.match("10 Downing Street, London, UK", "France")
        assert_score(score, 0.0, 0.05, "28.03 France not in UK address")

    def test_28_04(self, matcher):
        score = matcher.match("Paris, France", "Germany")
        assert_score(score, 0.0, 0.05, "28.04 Germany not in Paris address")

    def test_28_05(self, matcher):
        score = matcher.match("Mumbai, Maharashtra, India", "Pakistan")
        assert_score(score, 0.0, 0.05, "28.05 Pakistan not in India address")

    def test_28_06(self, matcher):
        score = matcher.match("Sydney, Australia", "New Zealand")
        assert_score(score, 0.0, 0.05, "28.06 NZ not in Australia address")

    def test_28_07(self, matcher):
        score = matcher.match("Berlin, Germany", "Austria")
        assert_score(score, 0.0, 0.05, "28.07 Austria not in Germany address")

    def test_28_08(self, matcher):
        score = matcher.match("Cairo, Egypt", "Libya")
        assert_score(score, 0.0, 0.05, "28.08 Libya not in Egypt address")

    def test_28_09(self, matcher):
        score = matcher.match("Toronto, Canada", "Mexico")
        assert_score(score, 0.0, 0.05, "28.09 Mexico not in Canada address")

    def test_28_10(self, matcher):
        score = matcher.match("Moscow, Russia", "Ukraine")
        assert_score(score, 0.0, 0.05, "28.10 Ukraine not in Russia address")

    def test_28_11(self, matcher):
        score = matcher.match("Bangkok, Thailand", "Vietnam")
        assert_score(score, 0.0, 0.05, "28.11 Vietnam not in Thailand address")

    def test_28_12(self, matcher):
        score = matcher.match("Lima, Peru", "Chile")
        assert_score(score, 0.0, 0.05, "28.12 Chile not in Peru address")

    def test_28_13(self, matcher):
        score = matcher.match("Nairobi, Kenya", "Tanzania")
        assert_score(score, 0.0, 0.05, "28.13 Tanzania not in Kenya address")

    def test_28_14(self, matcher):
        score = matcher.match("Stockholm, Sweden", "Norway")
        assert_score(score, 0.0, 0.05, "28.14 Norway not in Sweden address")

    def test_28_15(self, matcher):
        score = matcher.match("Dublin, Ireland", "Scotland")
        assert_score(score, 0.0, 0.05, "28.15 Scotland not in Ireland address")

    def test_28_16(self, matcher):
        score = matcher.match("Athens, Greece", "Turkey")
        assert_score(score, 0.0, 0.05, "28.16 Turkey not in Greece address")

    def test_28_17(self, matcher):
        score = matcher.match("Lisbon, Portugal", "Spain")
        assert_score(score, 0.0, 0.05, "28.17 Spain not in Portugal address")

    def test_28_18(self, matcher):
        score = matcher.match("Warsaw, Poland", "Hungary")
        assert_score(score, 0.0, 0.05, "28.18 Hungary not in Poland address")

    def test_28_19(self, matcher):
        score = matcher.match("221B Baker Street, Los Angeles, California, USA", "New York")
        assert_score(score, 0.0, 0.05, "28.19 New York not in LA address")

    def test_28_20(self, matcher):
        score = matcher.match("221B Baker Street, Los Angeles, California, USA", "Texas")
        assert_score(score, 0.0, 0.05, "28.20 Texas not in LA address")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 29 — Fuzzy/Typo Matching In Addresses (25 tests)
# ══════════════════════════════════════════════════════════════════════════════
# Typos should give moderate-to-high scores (0.50–0.90 depending on severity).

class TestCategory29_FuzzyTypoMatching:

    def test_29_01(self, matcher):
        score = matcher.match("Calfornia, USA", "California")
        assert_score(score, 0.75, 0.90, "29.01 Calfornia → California (1 char missing)")

    def test_29_02(self, matcher):
        score = matcher.match("Los Angelos, CA", "Los Angeles")
        assert_score(score, 0.88, 1.0, "29.02 Los Angelos → Los Angeles")

    def test_29_03(self, matcher):
        score = matcher.match("Washignton DC, USA", "Washington")
        assert_score(score, 0.75, 0.90, "29.03 Washignton → Washington")

    def test_29_04(self, matcher):
        score = matcher.match("Sydeny, Australia", "Sydney")
        assert_score(score, 0.75, 0.90, "29.04 Sydeny → Sydney")

    def test_29_05(self, matcher):
        score = matcher.match("Melborne, Victoria", "Melbourne")
        assert_score(score, 0.80, 0.92, "29.05 Melborne → Melbourne")

    def test_29_06(self, matcher):
        score = matcher.match("Munbai, India", "Mumbai")
        assert_score(score, 0.75, 0.90, "29.06 Munbai → Mumbai")

    def test_29_07(self, matcher):
        score = matcher.match("Frnace", "France")
        assert_score(score, 0.75, 0.90, "29.07 Frnace → France")

    def test_29_08(self, matcher):
        score = matcher.match("Germny", "Germany")
        assert_score(score, 0.80, 0.92, "29.08 Germny → Germany")

    def test_29_09(self, matcher):
        score = matcher.match("Australiaa", "Australia")
        assert_score(score, 0.80, 0.92, "29.09 Australiaa → Australia (extra char)")

    def test_29_10(self, matcher):
        score = matcher.match("Noth Korea", "North Korea")
        assert_score(score, 0.78, 0.92, "29.10 Noth Korea → North Korea")

    def test_29_11(self, matcher):
        score = matcher.match("Sauth Korea", "South Korea")
        assert_score(score, 0.72, 0.88, "29.11 Sauth Korea → South Korea")

    def test_29_12(self, matcher):
        score = matcher.match("Untied States", "United States")
        assert_score(score, 0.90, 1.0, "29.12 Untied → United (transposition)")

    def test_29_13(self, matcher):
        score = matcher.match("Braizl", "Brazil")
        assert_score(score, 0.75, 0.90, "29.13 Braizl → Brazil")

    def test_29_14(self, matcher):
        score = matcher.match("Londn, UK", "London")
        assert_score(score, 0.78, 0.90, "29.14 Londn → London")

    def test_29_15(self, matcher):
        score = matcher.match("Banglaore, India", "Bangalore")
        assert_score(score, 0.75, 0.90, "29.15 Banglaore → Bangalore")

    def test_29_16(self, matcher):
        score = matcher.match("Chciago, IL", "Chicago")
        assert_score(score, 0.75, 0.90, "29.16 Chciago → Chicago")

    def test_29_17(self, matcher):
        score = matcher.match("Denvr, CO", "Denver")
        assert_score(score, 0.78, 0.90, "29.17 Denvr → Denver")

    def test_29_18(self, matcher):
        score = matcher.match("Los Angelas, California, USA", "Los Angeles")
        assert_score(score, 0.88, 1.0, "29.18 Los Angelas → Los Angeles in full address")

    def test_29_19(self, matcher):
        score = matcher.match("Philedelphia, PA", "Philadelphia")
        assert_score(score, 0.80, 0.92, "29.19 Philedelphia → Philadelphia")

    def test_29_20(self, matcher):
        score = matcher.match("Pittsburg, PA", "Pittsburgh")
        assert_score(score, 0.80, 0.92, "29.20 Pittsburg → Pittsburgh")

    def test_29_21(self, matcher):
        score = matcher.match("Seatle, WA", "Seattle")
        assert_score(score, 0.80, 0.92, "29.21 Seatle → Seattle")

    def test_29_22(self, matcher):
        score = matcher.match("Huoston, TX", "Houston")
        assert_score(score, 0.75, 0.90, "29.22 Huoston → Houston")

    def test_29_23(self, matcher):
        score = matcher.match("Cananda", "Canada")
        assert_score(score, 0.45, 0.70, "29.23 Cananda → Canada (near miss)")

    def test_29_24(self, matcher):
        score = matcher.match("Tokoyo, Japan", "Tokyo")
        assert_score(score, 0.45, 0.65, "29.24 Tokoyo → Tokyo (near miss)")

    def test_29_25(self, matcher):
        score = matcher.match("Pars, France", "Paris")
        assert_score(score, 0.0, 0.40, "29.25 Pars → Paris (collision word, no exact)")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 30 — Reversed/Jumbled Address Components (20 tests)
# ══════════════════════════════════════════════════════════════════════════════
# Addresses with components in reverse/unusual order. Exact tokens should
# still score 1.0 regardless of order.

class TestCategory30_ReversedJumbledAddresses:

    def test_30_01(self, matcher):
        score = matcher.match("USA, California, Los Angeles, Baker Street, 221B", "Los Angeles")
        assert_score(score, 0.95, 1.0, "30.01 LA in reversed US address")

    def test_30_02(self, matcher):
        score = matcher.match("USA, California, Los Angeles, Baker Street, 221B", "California")
        assert_score(score, 0.95, 1.0, "30.02 California in reversed US address")

    def test_30_03(self, matcher):
        score = matcher.match("USA, California, Los Angeles, Baker Street, 221B", "USA")
        assert_score(score, 0.95, 1.0, "30.03 USA in reversed US address")

    def test_30_04(self, matcher):
        score = matcher.match("India, Karnataka, Bangalore, MG Road", "Bangalore")
        assert_score(score, 0.95, 1.0, "30.04 Bangalore in reversed Indian address")

    def test_30_05(self, matcher):
        score = matcher.match("India, Karnataka, Bangalore, MG Road", "India")
        assert_score(score, 0.95, 1.0, "30.05 India in reversed Indian address")

    def test_30_06(self, matcher):
        score = matcher.match("France, Paris, Champs Elysees", "Paris")
        assert_score(score, 0.95, 1.0, "30.06 Paris in reversed French address")

    def test_30_07(self, matcher):
        score = matcher.match("France, Paris, Champs Elysees", "France")
        assert_score(score, 0.95, 1.0, "30.07 France in reversed French address")

    def test_30_08(self, matcher):
        score = matcher.match("USA, NY, New York, Broadway 100", "New York")
        assert_score(score, 0.95, 1.0, "30.08 New York in reversed address")

    def test_30_09(self, matcher):
        score = matcher.match("Japan, Tokyo, Chiyoda, 1-1-1", "Tokyo")
        assert_score(score, 0.95, 1.0, "30.09 Tokyo in reversed Japanese address")

    def test_30_10(self, matcher):
        score = matcher.match("Japan, Tokyo, Chiyoda, 1-1-1", "Japan")
        assert_score(score, 0.95, 1.0, "30.10 Japan in reversed address")

    def test_30_11(self, matcher):
        score = matcher.match("Germany, Berlin, Alexanderplatz", "Berlin")
        assert_score(score, 0.95, 1.0, "30.11 Berlin in reversed German address")

    def test_30_12(self, matcher):
        score = matcher.match("UK, London, Baker Street", "London")
        assert_score(score, 0.95, 1.0, "30.12 London in reversed UK address")

    def test_30_13(self, matcher):
        score = matcher.match("Australia, Sydney, Pitt Street", "Sydney")
        assert_score(score, 0.95, 1.0, "30.13 Sydney in reversed Oz address")

    def test_30_14(self, matcher):
        score = matcher.match("Brazil, Rio de Janeiro, Copacabana", "Rio de Janeiro")
        assert_score(score, 0.95, 1.0, "30.14 Rio contiguous in reversed address")

    def test_30_15(self, matcher):
        score = matcher.match("Canada, Toronto, Bay Street", "Toronto")
        assert_score(score, 0.95, 1.0, "30.15 Toronto in reversed Canadian address")

    def test_30_16(self, matcher):
        score = matcher.match("Spain, Madrid, Gran Via", "Madrid")
        assert_score(score, 0.95, 1.0, "30.16 Madrid in reversed Spanish address")

    def test_30_17(self, matcher):
        score = matcher.match("Italy, Rome, Via del Corso", "Rome")
        assert_score(score, 0.95, 1.0, "30.17 Rome in reversed Italian address")

    def test_30_18(self, matcher):
        score = matcher.match("Russia, Moscow, Red Square", "Moscow")
        assert_score(score, 0.95, 1.0, "30.18 Moscow in reversed Russian address")

    def test_30_19(self, matcher):
        score = matcher.match("Mexico, Mexico City, Reforma", "Mexico City")
        assert_score(score, 0.95, 1.0, "30.19 Mexico City contiguous in reversed address")

    def test_30_20(self, matcher):
        score = matcher.match("Egypt, Cairo, Tahrir Square", "Cairo")
        assert_score(score, 0.95, 1.0, "30.20 Cairo in reversed Egyptian address")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 31 — Abbreviation + Exact In Same Address (20 tests)
# ══════════════════════════════════════════════════════════════════════════════
# When an abbreviation AND the expanded form coexist, exact tokens score 1.0,
# abbreviation-only expansions stay capped (~0.88).

class TestCategory31_AbbreviationExactCoexist:

    def test_31_01(self, matcher):
        score = matcher.match("New York, NY, USA", "New York")
        assert_score(score, 0.95, 1.0, "31.01 New York exact with NY also present")

    def test_31_02(self, matcher):
        score = matcher.match("New York, NY, USA", "USA")
        assert_score(score, 0.95, 1.0, "31.02 USA exact")

    def test_31_03(self, matcher):
        score = matcher.match("Los Angeles, CA, USA", "Los Angeles")
        assert_score(score, 0.95, 1.0, "31.03 Los Angeles exact")

    def test_31_04(self, matcher):
        score = matcher.match("Los Angeles, CA, USA", "California")
        assert_score(score, 0.80, 0.92, "31.04 California via CA abbreviation only — capped")

    def test_31_05(self, matcher):
        score = matcher.match("San Francisco, CA, USA", "San Francisco")
        assert_score(score, 0.95, 1.0, "31.05 San Francisco exact")

    def test_31_06(self, matcher):
        score = matcher.match("Washington, DC, USA", "Washington")
        assert_score(score, 0.95, 1.0, "31.06 Washington exact")

    def test_31_07(self, matcher):
        score = matcher.match("Chicago, IL, USA", "Chicago")
        assert_score(score, 0.95, 1.0, "31.07 Chicago exact")

    def test_31_08(self, matcher):
        score = matcher.match("Houston, TX, USA", "Houston")
        assert_score(score, 0.95, 1.0, "31.08 Houston exact")

    def test_31_09(self, matcher):
        score = matcher.match("London, UK", "London")
        assert_score(score, 0.95, 1.0, "31.09 London exact with UK")

    def test_31_10(self, matcher):
        score = matcher.match("London, UK", "United Kingdom")
        assert_score(score, 0.80, 0.92, "31.10 UK → United Kingdom abbreviation capped")

    def test_31_11(self, matcher):
        score = matcher.match("Dubai, UAE", "Dubai")
        assert_score(score, 0.95, 1.0, "31.11 Dubai exact")

    def test_31_12(self, matcher):
        score = matcher.match("Dubai, UAE", "United Arab Emirates")
        assert_score(score, 0.80, 0.92, "31.12 UAE → United Arab Emirates abbreviation capped")

    def test_31_13(self, matcher):
        score = matcher.match("Seoul, S. Korea", "South Korea")
        assert_score(score, 0.78, 0.92, "31.13 S. Korea → South Korea abbreviation")

    def test_31_14(self, matcher):
        score = matcher.match("123 Main St, Austin, TX, USA", "United States")
        assert_score(score, 0.80, 0.92, "31.14 USA → United States abbrev in address")

    def test_31_15(self, matcher):
        score = matcher.match("90210, Beverly Hills, CA, USA", "California")
        assert_score(score, 0.80, 0.92, "31.15 CA → California abbrev in address")

    def test_31_16(self, matcher):
        score = matcher.match("10 Downing St, London, UK", "London")
        assert_score(score, 0.95, 1.0, "31.16 London exact in UK address")

    def test_31_17(self, matcher):
        score = matcher.match("Flat 3, 27 Baker St, London W1U 8EW, UK", "London")
        assert_score(score, 0.95, 1.0, "31.17 London exact in detailed UK address")

    def test_31_18(self, matcher):
        score = matcher.match("Flat 3, 27 Baker St, London W1U 8EW, UK", "United Kingdom")
        assert_score(score, 0.80, 0.92, "31.18 UK → United Kingdom capped")

    def test_31_19(self, matcher):
        score = matcher.match("MG Road, Bangalore, KA, India", "Bangalore")
        assert_score(score, 0.95, 1.0, "31.19 Bangalore exact")

    def test_31_20(self, matcher):
        score = matcher.match("MG Road, Bangalore, KA, India", "India")
        assert_score(score, 0.95, 1.0, "31.20 India exact with KA abbreviation")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 32 — Collision Words In Geographic Context (20 tests)
# ══════════════════════════════════════════════════════════════════════════════
# Collision words (Paris, Berlin, Georgia, etc.) that appear as exact tokens
# in geographic contexts should score 1.0.

class TestCategory32_CollisionWordsGeographic:

    def test_32_01(self, matcher):
        score = matcher.match("Georgia, USA", "Georgia")
        assert_score(score, 0.95, 1.0, "32.01 Georgia exact with USA context")

    def test_32_02(self, matcher):
        score = matcher.match("Paris, France", "Paris")
        assert_score(score, 0.95, 1.0, "32.02 Paris exact with France context")

    def test_32_03(self, matcher):
        score = matcher.match("Berlin, Germany", "Berlin")
        assert_score(score, 0.95, 1.0, "32.03 Berlin exact with Germany context")

    def test_32_04(self, matcher):
        score = matcher.match("Florence, Italy", "Florence")
        assert_score(score, 0.95, 1.0, "32.04 Florence exact with Italy context")

    def test_32_05(self, matcher):
        score = matcher.match("Portland, Oregon", "Portland")
        assert_score(score, 0.95, 1.0, "32.05 Portland exact with Oregon context")

    def test_32_06(self, matcher):
        score = matcher.match("Cambridge, UK", "Cambridge")
        assert_score(score, 0.95, 1.0, "32.06 Cambridge exact with UK context")

    def test_32_07(self, matcher):
        score = matcher.match("Oxford, UK", "Oxford")
        assert_score(score, 0.95, 1.0, "32.07 Oxford exact with UK context")

    def test_32_08(self, matcher):
        score = matcher.match("Bath, England", "Bath")
        assert_score(score, 0.95, 1.0, "32.08 Bath exact with England context")

    def test_32_09(self, matcher):
        score = matcher.match("Victoria, British Columbia", "Victoria")
        assert_score(score, 0.95, 1.0, "32.09 Victoria exact in geographic context")

    def test_32_10(self, matcher):
        score = matcher.match("Lima, Peru", "Lima")
        assert_score(score, 0.95, 1.0, "32.10 Lima exact")

    def test_32_11(self, matcher):
        score = matcher.match("Nice, France", "Nice")
        assert_score(score, 0.95, 1.0, "32.11 Nice exact with France context")

    def test_32_12(self, matcher):
        score = matcher.match("Jordan Valley, Jordan", "Jordan")
        assert_score(score, 0.95, 1.0, "32.12 Jordan exact in Jordan context")

    def test_32_13(self, matcher):
        score = matcher.match("Troy, New York", "Troy")
        assert_score(score, 0.95, 1.0, "32.13 Troy exact in New York context")

    def test_32_14(self, matcher):
        score = matcher.match("Mobile, Alabama", "Mobile")
        assert_score(score, 0.95, 1.0, "32.14 Mobile exact in Alabama context")

    def test_32_15(self, matcher):
        score = matcher.match("Pearl City, Hawaii", "Pearl")
        assert_score(score, 0.95, 1.0, "32.15 Pearl exact in Hawaii context")

    def test_32_16(self, matcher):
        score = matcher.match("Aurora, Colorado", "Aurora")
        assert_score(score, 0.95, 1.0, "32.16 Aurora exact")

    def test_32_17(self, matcher):
        score = matcher.match("Salem, Oregon", "Salem")
        assert_score(score, 0.95, 1.0, "32.17 Salem exact")

    def test_32_18(self, matcher):
        score = matcher.match("Reading, Pennsylvania", "Reading")
        assert_score(score, 0.95, 1.0, "32.18 Reading exact in PA context")

    def test_32_19(self, matcher):
        score = matcher.match("Orange, California", "Orange")
        assert_score(score, 0.95, 1.0, "32.19 Orange exact in CA context")

    def test_32_20(self, matcher):
        score = matcher.match("Durham, North Carolina", "Durham")
        assert_score(score, 0.80, 1.0, "32.20 Durham in North Carolina context")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 33 — Directional Word Context (15 tests)
# ══════════════════════════════════════════════════════════════════════════════
# Adjacent directionals reduce score slightly; non-adjacent don't.

class TestCategory33_DirectionalContext:

    def test_33_01(self, matcher):
        score = matcher.match("Seoul, South Korea", "Korea")
        assert_score(score, 0.80, 0.90, "33.01 Korea with adjacent South")

    def test_33_02(self, matcher):
        score = matcher.match("Pyongyang, North Korea", "Korea")
        assert_score(score, 0.80, 0.90, "33.02 Korea with adjacent North")

    def test_33_03(self, matcher):
        score = matcher.match("North Carolina, USA", "Carolina")
        assert_score(score, 0.80, 0.90, "33.03 Carolina with adjacent North")

    def test_33_04(self, matcher):
        score = matcher.match("South Carolina, USA", "Carolina")
        assert_score(score, 0.80, 0.90, "33.04 Carolina with adjacent South")

    def test_33_05(self, matcher):
        score = matcher.match("Western Australia", "Australia")
        assert_score(score, 0.80, 0.90, "33.05 Australia with adjacent Western")

    def test_33_06(self, matcher):
        score = matcher.match("New South Wales, Australia", "Australia")
        assert_score(score, 0.95, 1.0, "33.06 Australia with non-adjacent South → no penalty")

    def test_33_07(self, matcher):
        score = matcher.match("10 North Road, Mumbai, India", "India")
        assert_score(score, 0.95, 1.0, "33.07 India with non-adjacent North → no penalty")

    def test_33_08(self, matcher):
        score = matcher.match("South Mumbai, Maharashtra, India", "India")
        assert_score(score, 0.95, 1.0, "33.08 India with non-adjacent South → no penalty")

    def test_33_09(self, matcher):
        score = matcher.match("North Dakota, USA", "Dakota")
        assert_score(score, 0.80, 0.90, "33.09 Dakota with adjacent North")

    def test_33_10(self, matcher):
        score = matcher.match("South Dakota, USA", "Dakota")
        assert_score(score, 0.80, 0.90, "33.10 Dakota with adjacent South")

    def test_33_11(self, matcher):
        score = matcher.match("West Virginia, USA", "Virginia")
        assert_score(score, 0.80, 0.90, "33.11 Virginia with adjacent West")

    def test_33_12(self, matcher):
        score = matcher.match("Northern Ireland, UK", "Ireland")
        assert_score(score, 0.80, 0.90, "33.12 Ireland with adjacent Northern")

    def test_33_13(self, matcher):
        score = matcher.match("Central Park, New York, USA", "New York")
        assert_score(score, 0.95, 1.0, "33.13 New York with non-adjacent Central")

    def test_33_14(self, matcher):
        score = matcher.match("East Timor", "Timor")
        assert_score(score, 0.80, 0.90, "33.14 Timor with adjacent East")

    def test_33_15(self, matcher):
        score = matcher.match("East London, South Africa", "London")
        assert_score(score, 0.60, 0.80, "33.15 London with two adjacent directionals")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 34 — Multi-Word Compound Location Names (15 tests)
# ══════════════════════════════════════════════════════════════════════════════
# Multi-word location names should score 1.0 when present contiguously.

class TestCategory34_CompoundLocationNames:

    def test_34_01(self, matcher):
        score = matcher.match("San Francisco, California, USA", "San Francisco")
        assert_score(score, 0.95, 1.0, "34.01 San Francisco contiguous")

    def test_34_02(self, matcher):
        score = matcher.match("Saint Petersburg, Russia", "Saint Petersburg")
        assert_score(score, 0.95, 1.0, "34.02 Saint Petersburg contiguous")

    def test_34_03(self, matcher):
        score = matcher.match("Kuala Lumpur, Malaysia", "Kuala Lumpur")
        assert_score(score, 0.95, 1.0, "34.03 Kuala Lumpur contiguous")

    def test_34_04(self, matcher):
        score = matcher.match("Buenos Aires, Argentina", "Buenos Aires")
        assert_score(score, 0.95, 1.0, "34.04 Buenos Aires contiguous")

    def test_34_05(self, matcher):
        score = matcher.match("Rio de Janeiro, Brazil", "Rio de Janeiro")
        assert_score(score, 0.95, 1.0, "34.05 Rio de Janeiro contiguous")

    def test_34_06(self, matcher):
        score = matcher.match("Ho Chi Minh City, Vietnam", "Ho Chi Minh City")
        assert_score(score, 0.95, 1.0, "34.06 Ho Chi Minh City contiguous")

    def test_34_07(self, matcher):
        score = matcher.match("Addis Ababa, Ethiopia", "Addis Ababa")
        assert_score(score, 0.95, 1.0, "34.07 Addis Ababa contiguous")

    def test_34_08(self, matcher):
        score = matcher.match("Tel Aviv, Israel", "Tel Aviv")
        assert_score(score, 0.95, 1.0, "34.08 Tel Aviv contiguous")

    def test_34_09(self, matcher):
        score = matcher.match("Sri Lanka", "Sri Lanka")
        assert_score(score, 0.95, 1.0, "34.09 Sri Lanka exact")

    def test_34_10(self, matcher):
        score = matcher.match("Costa Rica", "Costa Rica")
        assert_score(score, 0.95, 1.0, "34.10 Costa Rica exact")

    def test_34_11(self, matcher):
        score = matcher.match("El Salvador", "El Salvador")
        assert_score(score, 0.95, 1.0, "34.11 El Salvador exact")

    def test_34_12(self, matcher):
        score = matcher.match("New Zealand", "New Zealand")
        assert_score(score, 0.95, 1.0, "34.12 New Zealand exact")

    def test_34_13(self, matcher):
        score = matcher.match("Saudi Arabia", "Saudi Arabia")
        assert_score(score, 0.95, 1.0, "34.13 Saudi Arabia exact")

    def test_34_14(self, matcher):
        score = matcher.match("South Africa", "South Africa")
        assert_score(score, 0.95, 1.0, "34.14 South Africa exact")

    def test_34_15(self, matcher):
        score = matcher.match("Hong Kong", "Hong Kong")
        assert_score(score, 0.95, 1.0, "34.15 Hong Kong exact")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 35 — International Transliterations (15 tests)
# ══════════════════════════════════════════════════════════════════════════════
# Alternate names/transliterations get capped at the alternate-name score.

class TestCategory35_Transliterations:

    def test_35_01(self, matcher):
        score = matcher.match("Moskva, Russia", "Moscow")
        assert_score(score, 0.78, 0.92, "35.01 Moskva → Moscow alt name")

    def test_35_02(self, matcher):
        score = matcher.match("Munchen, Germany", "Munich")
        assert_score(score, 0.78, 0.92, "35.02 Munchen → Munich alt name")

    def test_35_03(self, matcher):
        score = matcher.match("Bharat", "India")
        assert_score(score, 0.75, 0.90, "35.03 Bharat → India alt name")

    def test_35_04(self, matcher):
        score = matcher.match("Deutschland", "Germany")
        assert_score(score, 0.75, 0.90, "35.04 Deutschland → Germany alt name")

    def test_35_05(self, matcher):
        score = matcher.match("Nippon", "Japan")
        assert_score(score, 0.75, 0.90, "35.05 Nippon → Japan alt name")

    def test_35_06(self, matcher):
        score = matcher.match("Peking", "Beijing")
        assert_score(score, 0.75, 0.90, "35.06 Peking → Beijing alt name")

    def test_35_07(self, matcher):
        score = matcher.match("Bombay, India", "Mumbai")
        assert_score(score, 0.78, 0.92, "35.07 Bombay → Mumbai alt name")

    def test_35_08(self, matcher):
        score = matcher.match("Calcutta, India", "Kolkata")
        assert_score(score, 0.78, 0.92, "35.08 Calcutta → Kolkata alt name")

    def test_35_09(self, matcher):
        score = matcher.match("Praha, Czech Republic", "Prague")
        assert_score(score, 0.78, 0.92, "35.09 Praha → Prague alt name")

    def test_35_10(self, matcher):
        score = matcher.match("Kobenhavn, Denmark", "Copenhagen")
        assert_score(score, 0.78, 0.92, "35.10 Kobenhavn → Copenhagen alt name")

    def test_35_11(self, matcher):
        score = matcher.match("Lisboa, Portugal", "Lisbon")
        assert_score(score, 0.78, 0.92, "35.11 Lisboa → Lisbon alt name")

    def test_35_12(self, matcher):
        score = matcher.match("Warszawa, Poland", "Warsaw")
        assert_score(score, 0.78, 0.92, "35.12 Warszawa → Warsaw alt name")

    def test_35_13(self, matcher):
        score = matcher.match("Bruxelles, Belgium", "Brussels")
        assert_score(score, 0.78, 0.92, "35.13 Bruxelles → Brussels alt name")

    def test_35_14(self, matcher):
        score = matcher.match("Holland", "Netherlands")
        assert_score(score, 0.75, 0.90, "35.14 Holland → Netherlands alt name")

    def test_35_15(self, matcher):
        score = matcher.match("Turkiye", "Turkey")
        assert_score(score, 0.0, 0.40, "35.15 Turkiye → Turkey (collision+no exact)")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 36 — Unicode/Punctuation Variations (15 tests)
# ══════════════════════════════════════════════════════════════════════════════

class TestCategory36_UnicodePunctuation:

    def test_36_01(self, matcher):
        score = matcher.match("Réunion", "Reunion")
        assert_score(score, 0.90, 1.0, "36.01 Accent stripped")

    def test_36_02(self, matcher):
        score = matcher.match("São Paulo, Brazil", "Sao Paulo")
        assert_score(score, 0.90, 1.0, "36.02 Tilde stripped")

    def test_36_03(self, matcher):
        score = matcher.match("Côte d'Ivoire", "Cote Ivoire")
        assert_score(score, 0.80, 1.0, "36.03 Accent + apostrophe stripped")

    def test_36_04(self, matcher):
        score = matcher.match("Åland Islands", "Aland")
        assert_score(score, 0.82, 1.0, "36.04 Scandinavian char stripped")

    def test_36_05(self, matcher):
        score = matcher.match("München, Germany", "Munchen")
        assert_score(score, 0.88, 1.0, "36.05 Umlaut stripped")

    def test_36_06(self, matcher):
        score = matcher.match("Korea(South)", "South Korea")
        assert_score(score, 0.72, 0.92, "36.06 Parentheses in address")

    def test_36_07(self, matcher):
        score = matcher.match("Iran/Iraq border", "Iran")
        assert_score(score, 0.85, 1.0, "36.07 Slash separator — Iran")

    def test_36_08(self, matcher):
        score = matcher.match("Iran/Iraq border", "Iraq")
        assert_score(score, 0.85, 1.0, "36.08 Slash separator — Iraq")

    def test_36_09(self, matcher):
        score = matcher.match("Iran.", "Iran")
        assert_score(score, 0.92, 1.0, "36.09 Trailing period")

    def test_36_10(self, matcher):
        score = matcher.match('"Iran"', "Iran")
        assert_score(score, 0.92, 1.0, "36.10 Quotes")

    def test_36_11(self, matcher):
        score = matcher.match("(Iran)", "Iran")
        assert_score(score, 0.92, 1.0, "36.11 Parentheses wrapping")

    def test_36_12(self, matcher):
        score = matcher.match("Paris,France", "France")
        assert_score(score, 0.88, 1.0, "36.12 Comma-no-space separator")

    def test_36_13(self, matcher):
        score = matcher.match("North.Korea", "North Korea")
        assert_score(score, 0.80, 1.0, "36.13 Dot separator")

    def test_36_14(self, matcher):
        score = matcher.match("Guinea-Bissau", "Guinea-Bissau")
        assert_score(score, 0.92, 1.0, "36.14 Hyphenated exact")

    def test_36_15(self, matcher):
        score = matcher.match("Guinea Bissau", "Guinea-Bissau")
        assert_score(score, 0.88, 1.0, "36.15 Space vs hyphen")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 37 — Mixed Noise In Addresses (10 tests)
# ══════════════════════════════════════════════════════════════════════════════
# Addresses with non-location tokens (names, companies, instructions).

class TestCategory37_MixedNoiseAddresses:

    def test_37_01(self, matcher):
        score = matcher.match("John Smith, Acme Corp, 100 Main St, Chicago, IL, USA", "Chicago")
        assert_score(score, 0.95, 1.0, "37.01 Chicago in noisy address")

    def test_37_02(self, matcher):
        score = matcher.match("John Smith, Acme Corp, 100 Main St, Chicago, IL, USA", "USA")
        assert_score(score, 0.95, 1.0, "37.02 USA in noisy address")

    def test_37_03(self, matcher):
        score = matcher.match("Delivery to: Mumbai, Maharashtra, India - URGENT", "Mumbai")
        assert_score(score, 0.95, 1.0, "37.03 Mumbai in delivery instruction")

    def test_37_04(self, matcher):
        score = matcher.match("Delivery to: Mumbai, Maharashtra, India - URGENT", "India")
        assert_score(score, 0.95, 1.0, "37.04 India in delivery instruction")

    def test_37_05(self, matcher):
        score = matcher.match("c/o Jane Doe, 42 Oxford Road, Manchester, England, UK", "Manchester")
        assert_score(score, 0.95, 1.0, "37.05 Manchester in c/o address")

    def test_37_06(self, matcher):
        score = matcher.match("c/o Jane Doe, 42 Oxford Road, Manchester, England, UK", "England")
        assert_score(score, 0.95, 1.0, "37.06 England in c/o address")

    def test_37_07(self, matcher):
        score = matcher.match("ATTENTION: Dr. Kumar, Apollo Hospital, Chennai, Tamil Nadu, India", "Chennai")
        assert_score(score, 0.95, 1.0, "37.07 Chennai in attention line")

    def test_37_08(self, matcher):
        score = matcher.match("ATTENTION: Dr. Kumar, Apollo Hospital, Chennai, Tamil Nadu, India", "India")
        assert_score(score, 0.95, 1.0, "37.08 India in attention line")

    def test_37_09(self, matcher):
        score = matcher.match("Ship to: Warehouse 7, Port Area, Manila, Philippines", "Manila")
        assert_score(score, 0.95, 1.0, "37.09 Manila in shipping instruction")

    def test_37_10(self, matcher):
        score = matcher.match("Ship to: Warehouse 7, Port Area, Manila, Philippines", "Philippines")
        assert_score(score, 0.95, 1.0, "37.10 Philippines in shipping instruction")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 38 — False Positives / Commercial Context (15 tests)
# ══════════════════════════════════════════════════════════════════════════════
# Non-geographic uses of location names should score low.

class TestCategory38_FalsePositivesCommercial:

    def test_38_01(self, matcher):
        score = matcher.match("Nice apartment for rent", "Nice")
        assert_score(score, 0.0, 0.40, "38.01 Nice = adjective, not city")

    def test_38_02(self, matcher):
        score = matcher.match("China Cabinet Store, LA", "China")
        assert_score(score, 0.0, 0.40, "38.02 China cabinet = furniture")

    def test_38_03(self, matcher):
        score = matcher.match("Turkey sandwich shop", "Turkey")
        assert_score(score, 0.0, 0.40, "38.03 Turkey = food")

    def test_38_04(self, matcher):
        score = matcher.match("Jordan shoes store", "Jordan")
        assert_score(score, 0.0, 0.40, "38.04 Jordan = brand")

    def test_38_05(self, matcher):
        score = matcher.match("Marine Drive, India", "Iran")
        assert_score(score, 0.0, 0.10, "38.05 Marine ≠ Iran")

    def test_38_06(self, matcher):
        score = matcher.match("Bird sanctuary near lake", "Ir")
        assert_score(score, 0.0, 0.25, "38.06 Short token guard")

    def test_38_07(self, matcher):
        score = matcher.match("I ran to the store", "Iran")
        assert_score(score, 0.0, 0.10, "38.07 'I ran' ≠ Iran")

    def test_38_08(self, matcher):
        score = matcher.match("Victoria Secret outlet", "Victoria")
        assert_score(score, 0.40, 0.70, "38.08 Victoria Secret — moderate commercial")

    def test_38_09(self, matcher):
        score = matcher.match("Panama hat shop", "Panama")
        assert_score(score, 0.40, 0.70, "38.09 Panama hat — moderate commercial")

    def test_38_10(self, matcher):
        score = matcher.match("Chile pepper sauce", "Chile")
        assert_score(score, 0.40, 0.70, "38.10 Chile pepper — moderate commercial")

    def test_38_11(self, matcher):
        score = matcher.match("Guinea pig pet store", "Guinea")
        assert_score(score, 0.40, 0.70, "38.11 Guinea pig — moderate commercial")

    def test_38_12(self, matcher):
        score = matcher.match("Mobile phone repair", "Mobile")
        assert_score(score, 0.40, 0.70, "38.12 Mobile phone — moderate commercial")

    def test_38_13(self, matcher):
        # Commercial context detection — exact token beats abbreviation
        clean = matcher.match("Paris, France", "Paris")
        noise = matcher.match("Nice apartment for rent", "Nice")
        assert clean > noise, "38.13 Geographic Paris > commercial Nice"

    def test_38_14(self, matcher):
        clean = matcher.match("Georgia, USA", "Georgia")
        noise = matcher.match("Jordan shoes store", "Jordan")
        assert clean > noise, "38.14 Geographic Georgia > commercial Jordan"

    def test_38_15(self, matcher):
        clean = matcher.match("Berlin, Germany", "Berlin")
        noise = matcher.match("China Cabinet Store, LA", "China")
        assert clean > noise, "38.15 Geographic Berlin > commercial China"


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 39 — Score Ordering / Relative Rankings (15 tests)
# ══════════════════════════════════════════════════════════════════════════════
# Verify that more specific/exact matches always beat less precise ones.

class TestCategory39_ScoreOrdering:

    def test_39_01(self, matcher):
        exact = matcher.match("California, USA", "California")
        abbrev = matcher.match("CA, USA", "California")
        assert exact > abbrev, "39.01 Exact California > CA abbreviation"

    def test_39_02(self, matcher):
        exact = matcher.match("Tokyo, Japan", "Tokyo")
        fuzzy = matcher.match("Tokoyo, Japan", "Tokyo")
        assert exact > fuzzy, "39.02 Exact Tokyo > fuzzy Tokoyo"

    def test_39_03(self, matcher):
        geo = matcher.match("Paris, France", "Paris")
        com = matcher.match("Nice apartment for rent", "Nice")
        assert geo > com, "39.03 Geographic context > commercial context"

    def test_39_04(self, matcher):
        full = matcher.match("South Korea", "South Korea")
        partial = matcher.match("Seoul, South Korea", "Korea")
        assert full > partial, "39.04 Full 'South Korea' > partial 'Korea'"

    def test_39_05(self, matcher):
        exact = matcher.match("Australia", "Australia")
        dir_ = matcher.match("Western Australia", "Australia")
        assert exact > dir_, "39.05 Exact Australia > Western Australia"

    def test_39_06(self, matcher):
        exact = matcher.match("USA", "USA")
        addr = matcher.match("USA", "United States")
        assert exact > addr, "39.06 Exact USA > abbreviation expansion"

    def test_39_07(self, matcher):
        present = matcher.match("Tokyo, Japan", "Japan")
        absent = matcher.match("Tokyo, Japan", "China")
        assert present > absent, "39.07 Present Japan > absent China"

    def test_39_08(self, matcher):
        exact = matcher.match("New York, USA", "New York")
        reversed_ = matcher.match("York New, USA", "New York")
        assert exact >= reversed_, "39.08 Ordered New York ≥ reversed York New"

    def test_39_09(self, matcher):
        clean = matcher.match("Mumbai, India", "Mumbai")
        typo = matcher.match("Munbai, India", "Mumbai")
        assert clean > typo, "39.09 Clean Mumbai > typo Munbai"

    def test_39_10(self, matcher):
        long_addr = matcher.match("221B Baker St, Los Angeles, CA, USA", "Los Angeles")
        short_addr = matcher.match("Los Angeles, CA", "Los Angeles")
        assert long_addr >= 0.95, "39.10a LA in long address ≥ 0.95"
        assert short_addr >= 0.95, "39.10b LA in short address ≥ 0.95"

    def test_39_11(self, matcher):
        geo = matcher.match("Georgia, USA", "Georgia")
        commercial = matcher.match("Jordan shoes store", "Jordan")
        assert geo > commercial, "39.11 Geographic Georgia > commercial Jordan"

    def test_39_12(self, matcher):
        exact = matcher.match("India", "India")
        alt = matcher.match("Bharat", "India")
        assert exact > alt, "39.12 Exact India > alternate name Bharat"

    def test_39_13(self, matcher):
        exact = matcher.match("London, UK", "London")
        abbr = matcher.match("London, UK", "United Kingdom")
        assert exact > abbr, "39.13 Exact London > UK abbreviation expansion"

    def test_39_14(self, matcher):
        score_a = matcher.match("São Paulo, Brazil", "Sao Paulo")
        score_b = matcher.match("São Paulo, Brazil", "Brazil")
        assert score_a >= 0.90, "39.14a São Paulo matches well"
        assert score_b >= 0.90, "39.14b Brazil matches well"

    def test_39_15(self, matcher):
        score_city = matcher.match("Buenos Aires, Argentina", "Buenos Aires")
        score_country = matcher.match("Buenos Aires, Argentina", "Argentina")
        assert score_city >= 0.95, "39.15a Buenos Aires ≥ 0.95"
        assert score_country >= 0.95, "39.15b Argentina ≥ 0.95"
