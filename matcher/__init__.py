"""
matcher/__init__.py — Public API for the Location Matcher package.

Exports:
    LocationMatcher        — main class; call .match(query, result) -> float
    score_with_variants    — score a query against a name + all its aliases/codes
    score_batch            — score one query against a list of Elastic result dicts
    trace_stages           — debug utility: pretty-print the full scoring pipeline
"""

import json

from matcher.location_matcher import LocationMatcher, score_batch, score_with_variants


def trace_stages(query: str, result: str) -> None:
    """
    Pretty-print every pipeline stage for a (query, result) pair.

    Usage:
        from matcher import trace_stages
        trace_stages("dparis", "Paris")
    """
    matcher = LocationMatcher()
    dbg = matcher.get_debug_breakdown(query, result)

    SEP  = "─" * 70
    SEP2 = "═" * 70

    def _fmt(val) -> str:
        if isinstance(val, (dict, list)):
            return json.dumps(val, indent=4, ensure_ascii=False)
        return str(val)

    print(SEP2)
    print(f"  TRACE  query={query!r}  →  result={result!r}")
    print(SEP2)

    stages = [
        ("INPUT",                 {"query": dbg.get("raw_query"),    "result": dbg.get("raw_result")}),
        ("STAGE 1 — Normalize",   dbg.get("stage1_normalized", {})),
        ("STAGE 1 — Tokens",      dbg.get("stage1_tokens",     {})),
        ("STAGE 2 — Enriched",    dbg.get("stage2_enriched",   [])),
        ("STAGE 3 — Token scores",dbg.get("token_scores",      [])),
        ("STAGE 4 — Raw score",   dbg.get("stage4_raw",        "n/a")),
        ("STAGE 4 — Best detail", dbg.get("stage4_detail",     {})),
        ("STAGE 5 — Adjusted",    dbg.get("stage5_adjusted",   "n/a")),
        ("STAGE 5 — Penalties",   dbg.get("stage5_penalties",  {})),
        ("STAGE 6 — Final score", dbg.get("final_score",       "n/a")),
    ]

    for label, value in stages:
        print(f"\n  ▶  {label}")
        print(SEP)
        for line in _fmt(value).splitlines():
            print(f"     {line}")

    print(f"\n{SEP2}\n")




if __name__ == '__main__':
    matcher = LocationMatcher()
    print(matcher.match("Room 202, Block C, Tabriz Avenue, North Side, Tabriz, 51367, Ira-n", "Iran"))

