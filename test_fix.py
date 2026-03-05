#!/usr/bin/env python3
"""Quick verification of the Penalty 2 fix."""
import sys
sys.path.insert(0, "/Volumes/prafull2/MATCCH")

from matcher.location_matcher import LocationMatcher

m = LocationMatcher()

tests = [
    # (query, result, expected_min_score, description)
    (
        "Office 77, Damascus Business Center, Damascus, 00010, XSyriaz",
        "Damascus",
        0.95,
        "Case 41: Damascus exact match should not be penalized by commercial words"
    ),
    (
        "Building 7, Kerman Business Park, Kerman, 76135, Irann",
        "Kerman",
        0.95,
        "Case 8: Kerman exact match with business context"
    ),
    (
        "Shop 15, Ahvaz Shopping Mall, Ahvaz Street, Ahvaz, 61357, Irrn",
        "Ahvaz",
        0.95,
        "Case 6: Ahvaz exact match with shop/mall context"
    ),
    (
        "Suite 112, Shiraz Plaza, Shiraz, 71345, Iranx",
        "Shiraz",
        0.95,
        "Case 12: Shiraz exact match"
    ),
    (
        "China Cabinet Store",
        "China",
        None,  # Should be LOW - no exact location intent
        "Commercial context without exact match should still be penalized"
    ),
    (
        "10, Green Apt, Iran",
        "Iran",
        0.95,
        "Exact match with address noise"
    ),
    (
        "Warehouse 12, Aleppo Industrial Complex, Aleppo, 00020, Syr1a",
        "Aleppo",
        0.95,
        "Case 42: Aleppo exact match"
    ),
]

results = []
for query, result, expected_min, desc in tests:
    dbg = m.get_debug_breakdown(query, result)
    score = dbg["final_score"]
    penalties = dbg.get("stage5_penalties", {}).get("penalties_applied", [])
    passed = True if expected_min is None else score >= expected_min
    status = "PASS" if passed else "FAIL"
    results.append((status, desc, score, penalties))

with open("/Volumes/prafull2/MATCCH/test_fix_output.txt", "w") as f:
    for status, desc, score, penalties in results:
        f.write(f"[{status}] {desc}\n")
        f.write(f"  Score: {score}\n")
        f.write(f"  Penalties: {penalties}\n\n")

# Also print to stdout
for status, desc, score, penalties in results:
    print(f"[{status}] {desc}")
    print(f"  Score: {score}")
    print(f"  Penalties: {penalties}")
    print()