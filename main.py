"""
main.py — Entry point for the Location Matcher test runner.

Usage:
    python main.py               # score all 200 test cases, write test_results.xlsx
    python main.py --verbose     # also print per-case progress
    python main.py --out my.xlsx # write to a custom file path
"""

from run_tests import main

if __name__ == "__main__":
    main()
