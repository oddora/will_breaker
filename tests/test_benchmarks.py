"""
Verification Suite for Benchmark Harness
"""

import unittest
import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from research.benchmarks.benchmark_kat import make_prompt


class TestBenchmarkHarness(unittest.TestCase):
    def test_make_prompt_word_count(self):
        """Verify prompt generator produces exact requested word count."""
        p_short = make_prompt(30)
        self.assertEqual(len(p_short.split()), 30)

        p_medium = make_prompt(200)
        self.assertEqual(len(p_medium.split()), 200)

        p_long = make_prompt(800)
        self.assertEqual(len(p_long.split()), 800)


if __name__ == "__main__":
    unittest.main()
