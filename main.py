import re
from rapidfuzz import fuzz

# Stopwords to ignore in addresses
STOPWORDS = {"street", "st", "road", "rd", "avenue", "ave",
             "apartment", "apt", "lane", "ln", "suite", "ste"}


def normalize(text):
    """Lowercase, remove punctuation, split into words."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)  # keep only alphanum + spaces
    words = [w for w in text.split() if w not in STOPWORDS]
    return words


def address_match_score(address, query, threshold=80):
    """
    Returns a matching score between 0 and 1, and matched words.
    Uses fuzzy matching with a threshold (default 80%).
    """
    address_words = normalize(address)
    query_words = normalize(query)

    matched_words = []

    for q_word in query_words:
        # Find best fuzzy match in address
        best_ratio = 0
        for a_word in address_words:
            ratio = fuzz.ratio(q_word, a_word)
            if ratio > best_ratio:
                best_ratio = ratio
        if best_ratio >= threshold:
            matched_words.append(q_word)

    score = len(matched_words) / len(query_words) if query_words else 0
    return score, matched_words


# -----------------------------
# Example usage
address = "123 Main Street, Apt 4B, Springfield"
query = "Main Street Springfield"

score, matched = address_match_score(address, query)
print(f"Score: {score:.2f}, Matched words: {matched}")