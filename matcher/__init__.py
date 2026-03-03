from matcher.location_matcher import LocationMatcher
import json


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
        ("INPUT",          {"query": dbg.get("raw_query"),   "result": dbg.get("raw_result")}),
        ("STAGE 1 — Normalize",  dbg.get("stage1_normalized", {})),
        ("STAGE 1 — Tokens",     dbg.get("stage1_tokens",     {})),
        ("STAGE 2 — Enriched tokens", dbg.get("stage2_enriched", [])),
        ("STAGE 3 — Token scores",    dbg.get("token_scores",    [])),
        ("STAGE 4 — Raw score",       dbg.get("stage4_raw",      "n/a")),
        ("STAGE 4 — Best detail",     dbg.get("stage4_detail",   {})),
        ("STAGE 5 — After penalties", dbg.get("stage5_adjusted", "n/a")),
        ("STAGE 5 — Penalties",       dbg.get("stage5_penalties",{})),
        ("STAGE 6 — Final score",     dbg.get("final_score",     "n/a")),
    ]

    for label, value in stages:
        print(f"\n  ▶  {label}")
        print(SEP)
        # indent each line for readability
        for line in _fmt(value).splitlines():
            print(f"     {line}")

    print(f"\n{SEP2}\n")

if __name__ == "__main__":
    import asyncio
    import time

    matcher = LocationMatcher()
    trace_stages('parisi', 'Paris')
    demo_cases = [
        # Exact and partial matches — Iran address
        # ('10, Green Apt, Hirani', 'Iran'),
        ('parisi', 'Paris'),
        # ("10, Green Apt, Tehran, Iran", "Tehran"),
        # ("10, Green Apt, Tehran, Iran", "Iran"),
        # ("10, Green Apt, Tehran, Iran", "Mashhad"),
        # ("10, Green Apt, Tehran, Iran", "Germany"),
        # # US address
        # ("221B, Baker Street, Los Angeles, California, USA", "USA"),
        # ("221B, Baker Street, Los Angeles, California, USA", "California"),
        # ("221B, Baker Street, Los Angeles, California, USA", "Los Angeles"),
        # ("221B, Baker Street, Los Angeles, California, USA", "Los Angeles"),
        # ("221B, Baker Street, Los Angeles, California, USA", "Texas"),
        # ("15, Rue de Rivoli, Paris, France", "France"),
        # ("usa", "united states of america"),
        # ("15, Rue de Rivoli, Paris, France", "Lyon"),
        # ("15, Rue de Rivoli, Paris, France", "Germany"),
        # Germany address
    ]

    async def run_match(query, result, loop):
        start = time.perf_counter()
        s = await loop.run_in_executor(None, matcher.match, query, result)
        elapsed = time.perf_counter() - start  # includes suspension time, not just executor time
        return query, result, s, elapsed

    async def main():
        loop = asyncio.get_event_loop()
        print("=" * 90)
        print("  LOCATION MATCHER — DEMO RUNS (10 cases, same query)")
        print("=" * 90)

        total_start = time.perf_counter()
        tasks = [run_match(query, result, loop) for query, result in demo_cases]
        results = await asyncio.gather(*tasks)
        total_elapsed = time.perf_counter() - total_start

        final = 0
        for query, result, s, elapsed in results:
            print(
                f"  match({query!r:25s}, {result!r:35s}) "
                f"= {s:.4f}  | time: {elapsed*1000:.3f} ms"
            )
            final += elapsed * 1000

        print(f"\nSum of individual times : {final:.3f} ms")
        print(f"Total wall-clock time   : {total_elapsed*1000:.3f} ms")

    asyncio.run(main())


