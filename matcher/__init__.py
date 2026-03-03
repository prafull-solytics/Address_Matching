from matcher.location_matcher import LocationMatcher

if __name__ == "__main__":
    import asyncio
    import time

    matcher = LocationMatcher()

    demo_cases = [
        # Exact and partial matches — Iran address
        ("hirani", "Iran"),
        ("10, Green Apt, Tehran, Iran", "Tehran"),
        ("10, Green Apt, Tehran, Iran", "Iran"),
        ("10, Green Apt, Tehran, Iran", "Mashhad"),
        ("10, Green Apt, Tehran, Iran", "Germany"),
        # US address
        ("221B, Baker Street, Los Angeles, California, USA", "USA"),
        ("221B, Baker Street, Los Angeles, California, USA", "California"),
        ("221B, Baker Street, Los Angeles, California, USA", "Los Angeles"),
        ("221B, Baker Street, Los Angeles, California, USA", "New York"),
        ("221B, Baker Street, Los Angeles, California, USA", "Texas"),
        ("15, Rue de Rivoli, Paris, France", "France"),
        ("15, Rue de Rivoli, Paris, France", "Paris"),
        ("15, Rue de Rivoli, Paris, France", "Lyon"),
        ("15, Rue de Rivoli, Paris, France", "Germany"),
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
