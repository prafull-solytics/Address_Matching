from matcher.location_matcher import LocationMatcher

if __name__ == "__main__":
    import sys

    matcher = LocationMatcher()

    demo_cases = [
        ("10, Green Apt, Iran",           "Iran",           0.95, 1.00),
        ("20, Hirani Apt, Blore",         "Iran",           0.35, 0.50),
        ("North Hirani Korea",            "North Korea",    0.55, 0.75),
        ("Korea North",                   "North Korea",    0.72, 0.88),
        ("IRAN",                          "Iran",           0.95, 1.00),
        ("Marine Drive, India",           "Iran",           0.00, 0.15),
        ("USA",                           "United States",  0.78, 0.92),
        ("Réunion Island",                "Reunion",        0.90, 1.00),
        ("Guinea-Bissau",                 "Guinea-Bissau",  0.95, 1.00),
        ("Republic of Korea",             "South Korea",    0.40, 0.65),
        ("Iarn",                          "Iran",           0.72, 0.88),
        ("Georgia",                       "Georgia",        0.95, 1.00),
        ("Turkey sandwich shop",          "Turkey",         0.00, 0.30),
        ("Manhattan, New York, USA",      "New York",       0.90, 1.00),
        ("North Korea",                   "South Korea",    0.35, 0.60),
    ]

    print("=" * 78)
    print("  LOCATION MATCHER — DEMO RUNS")
    print("=" * 78)
    all_pass = True
    for query, result, low, high in demo_cases:
        s = matcher.match(query, result)
        ok = low <= s <= high
        if not ok:
            all_pass = False
        print(f"  {'✅' if ok else '❌'}  match({query!r:42s}, {result!r:20s}) = {s:.4f}  [{low:.2f}–{high:.2f}]")
    print()
    print("  ALL PASSED ✅" if all_pass else "  SOME FAILED ❌")
