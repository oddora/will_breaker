"""Regression tests for scripts/resolve_session041.py grading.

Pins the 2026-10-26 bug class: sealed picks use full team names
("Arizona Cardinals -1.5") while the box-score evaluator produced
abbreviation winners ("DEN") — the old string comparison therefore
graded every pick WRONG (published as a false 0/22). Grading must
normalize both sides to abbreviations, detect the ATS favorite by
abbreviation, and score exact-integer spreads as pushes.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "resolve_session041.py"


def _load():
    spec = importlib.util.spec_from_file_location("resolve_session041", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rs = _load()


def test_pick_abv_normalizes_full_names():
    assert rs.pick_abv("Arizona Cardinals -1.5") == "ARI"
    assert rs.pick_abv("Arizona Cardinals") == "ARI"
    assert rs.pick_abv("Oklahoma City Thunder -15.5") == "OKC"
    assert rs.pick_abv("Philadelphia 76ers") == "PHI"
    assert rs.pick_abv("Los Angeles Rams -3.0") == "LAR"
    assert rs.pick_abv("Kansas City Chiefs") == "KC"


def test_ml_pick_that_wins_grades_correct():
    # DEN 30 @ ARI 16: a Broncos ML pick must grade correct, Cardinals wrong.
    meta = {"away_team": "DEN", "home_team": "ARI", "market_spread": ""}
    box = rs.evaluate_box_score(meta, 30, 16)
    assert rs.pick_abv("Denver Broncos") == box["ml_winner"]
    assert rs.pick_abv("Arizona Cardinals") != box["ml_winner"]


def test_ats_home_favorite_cover_grades_correct():
    # Cardinals -1.5 at home, win 20-17 => cover.
    meta = {"away_team": "DEN", "home_team": "ARI", "market_spread": "Cardinals -1.5"}
    box = rs.evaluate_box_score(meta, 17, 20)
    assert box["ats_winner_abv"] == "ARI"
    assert box["ats_winner"] == "ARI -1.5"


def test_ats_underdog_pick_cover_grades_correct():
    # Pistons -1.5 at home win by 1 => 76ers (away dog) cover.
    meta = {"away_team": "PHI", "home_team": "DET", "market_spread": "Pistons -1.5"}
    box = rs.evaluate_box_score(meta, 100, 101)
    assert box["ats_winner_abv"] == "PHI"
    assert box["ats_winner"] == "PHI +1.5"
    assert rs.pick_abv("Philadelphia 76ers -1.5") == box["ats_winner_abv"]


def test_ats_exact_integer_spread_is_push():
    # Rams -3.0 away at Raiders, win by exactly 3 => push, not a cover.
    meta = {"away_team": "LAR", "home_team": "LV", "market_spread": "Rams -3.0"}
    box = rs.evaluate_box_score(meta, 24, 21)
    assert box["ats_winner_abv"] is None
    assert "PUSH" in box["ats_winner"]
