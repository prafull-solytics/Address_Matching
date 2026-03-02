#!/usr/bin/env python3
"""Quick test runner to check key cases."""
import sys
sys.path.insert(0, '/Volumes/prafull2/MATCCH')

from sample1.location_matcher import LocationMatcher

m = LocationMatcher()

cases = [
    # (description, query, result, min, max)
    # Cat 1
    ("1.1", "10, Green Apt, Iran", "Iran", 0.95, 1.0),
    ("1.2", "Seoul, South Korea", "South Korea", 0.95, 1.0),
    # Cat 3
    ("3.1", "North Hirani Korea", "North Korea", 0.55, 0.75),
    ("3.7", "North Foo Bar Korea", "North Korea", 0.35, 0.60),
    # Cat 4
    ("4.1", "20, Hirani Apt, Blore", "Iran", 0.30, 0.55),
    ("4.2", "Franceville", "France", 0.40, 0.60),
    ("4.4", "Indira Nagar", "India", 0.30, 0.55),
    ("4.6", "Bird sanctuary", "Ir", 0.0, 0.20),
    # Cat 5
    ("5.1", "Korea North", "North Korea", 0.72, 0.88),
    ("5.5", "Emirates Arab United", "United Arab Emirates", 0.55, 0.80),
    # Cat 7
    ("7.2", "UK", "United Kingdom", 0.78, 0.92),
    ("7.6", "S. Korea", "South Korea", 0.78, 0.92),
    ("7.8", "123 Main St, Austin, USA", "United States", 0.75, 0.92),
    # Cat 8
    ("8.2", "Frnace", "France", 0.72, 0.88),
    ("8.3", "Koeea", "Korea", 0.65, 0.82),
    ("8.4", "Germny", "Germany", 0.75, 0.90),
    ("8.5", "Australiaa", "Australia", 0.80, 0.92),
    # Cat 9
    ("9.1", "Bharat", "India", 0.55, 0.90),
    ("9.3", "Munchen", "Munich", 0.55, 0.82),
    # Cat 11
    ("11.3", "GuineaBissau", "Guinea-Bissau", 0.75, 0.92),
    ("11.5", "Bosnia Herzegovina", "Bosnia and Herzegovina", 0.80, 0.95),
    # Cat 12
    ("12.2", "Republic of Korea", "South Korea", 0.40, 0.65),
    ("12.3", "Kingdom of Saudi Arabia", "Saudi Arabia", 0.80, 0.95),
    # Cat 13
    ("13.2", "B-204, Korea Tower", "Korea", 0.55, 0.80),
    ("13.5", "90210, Beverly Hills, USA", "United States", 0.75, 0.92),
    # Cat 15
    ("15.5", "Go to IR", "Iran", 0.0, 0.35),
    # Cat 16
    ("16.2", "China Cabinet Store, LA", "China", 0.0, 0.35),
    ("16.3", "Turkey sandwich shop", "Turkey", 0.0, 0.30),
    ("16.4", "Nice apartment for rent", "Nice", 0.0, 0.40),
    ("16.5", "Peru St, Denver, CO", "Peru", 0.30, 0.65),
    ("16.6", "Jordan shoes store", "Jordan", 0.0, 0.40),
    # Cat 18
    ("18.2", "North Korea", "South Korea", 0.35, 0.60),
    ("18.3", "East Timor", "Timor-Leste", 0.50, 0.80),
    ("18.4", "Western Australia", "Australia", 0.45, 0.70),
    # Cat 20
    ("20.9", None, "Iran", "TypeError", None),
    # Cat 21
    ("21.1", "Eyran", "Iran", 0.55, 0.85),
    # Cat 23
    ("23.5", "apt 5b, block C, near metro, North Korea zone", "North Korea", 0.72, 0.92),
    ("23.6", "No. 1 Changan Ave, Beijing, China", "China", 0.85, 1.0),
    ("23.3", "1600 Pennsylvania Ave NW, Washington, DC, USA", "United States", 0.72, 0.92),
    ("23.4", "10 Downing St, Westminster, London SW1A 2AA, UK", "United Kingdom", 0.72, 0.92),
    # Cat 25
    ("25.5", "Green Lane, London, UK", "United Kingdom", 0.72, 0.92),
]

pass_count = 0
fail_count = 0

for item in cases:
    tid, query, result_str, lo, hi = item
    if lo == "TypeError":
        try:
            m.match(query, result_str)
            print(f"❌ {tid}: Expected TypeError, got no error")
            fail_count += 1
        except TypeError:
            print(f"✅ {tid}: TypeError raised correctly")
            pass_count += 1
        continue

    score = m.match(query, result_str)
    ok = lo <= score <= hi
    status = "✅" if ok else "❌"
    print(f"{status} {tid}: match({query!r}, {result_str!r}) = {score:.4f} [{lo:.2f}–{hi:.2f}]")
    if ok:
        pass_count += 1
    else:
        fail_count += 1

print(f"\nTotal: {pass_count} passed, {fail_count} failed out of {len(cases)}")

