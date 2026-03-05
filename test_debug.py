#!/usr/bin/env python3
from matcher.location_matcher import LocationMatcher

m = LocationMatcher()

# Test case 41
dbg = m.get_debug_breakdown(
    "Office 77, Damascus Business Center, Damascus, 00010, XSyriaz",
    "Damascus"
)

with open("/Volumes/prafull2/MATCCH/test_debug_output.txt", "w") as f:
    for k, v in dbg.items():
        f.write(f"{k}: {v}\n")
    f.write(f"\nFinal Score: {dbg['final_score']}\n")

print("Done - check test_debug_output.txt")

