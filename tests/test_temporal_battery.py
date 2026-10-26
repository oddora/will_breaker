"""Protocol 016 temporal battery: parser, outcome derivation, binomial."""

from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "research" / "temporal" / "temporal_battery.py"


def _load():
    spec = importlib.util.spec_from_file_location("temporal_battery", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tb = _load()


def test_parse_bits_first_token_and_failure():
    assert tb.parse_bits("noise 0101100101 more") == "0101100101"
    assert tb.parse_bits("no bits here") is None
    assert tb.parse_bits("0101") is None  # too short: scored 0, never retried


def test_outcome_bits_deterministic_and_arm_separated():
    seed = bytes(range(32))
    assert tb.outcome_bits(seed, "control", 0) == tb.outcome_bits(seed, "control", 0)
    assert len(tb.outcome_bits(seed, "sigil", 3)) == 10
    assert len({tb.outcome_bits(seed, a, i) for a in ("control", "sigil") for i in range(5)}) > 5


def test_binom_sf_known_values():
    assert abs(tb.binom_sf(10, 10) - 0.5**10) < 1e-12
    assert abs(tb.binom_sf(0, 300) - 1.0) < 1e-12
    # 180/300 (60%) must clear the preregistered alpha 0.01
    assert tb.binom_sf(180, 300) < 0.01
    # exact chance performance must not
    assert tb.binom_sf(150, 300) > 0.4
