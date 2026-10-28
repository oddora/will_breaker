"""Unit tests for Protocol 019 Temporal-Anchor Sealed Battery."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import pytest

SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "research"
    / "temporal"
    / "temporal_anchor_battery.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("temporal_anchor_battery", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tab = _load()


def test_parse_bits_exact():
    assert tab.parse_bits("1010101010") == "1010101010"
    assert tab.parse_bits("The sequence is 0000011111.") == "0000011111"
    assert tab.parse_bits("Nothing here") is None
    assert tab.parse_bits("10101") is None  # only 5 bits


def test_prompts_contain_bits():
    sig = tab.sigil_prompt(10)
    assert "10-character" in sig
    anc = tab.anchor_prompt(10)
    assert "TEMPORAL ANCHOR PROCEDURE" in anc
    assert "T_0" in anc
    assert "10-character" in anc


def test_outcome_bits_deterministic():
    seed = b"\x00" * 32
    b1 = tab.outcome_bits(seed, "control", 0, bits=10)
    b2 = tab.outcome_bits(seed, "control", 0, bits=10)
    b3 = tab.outcome_bits(seed, "anchor", 0, bits=10)
    assert len(b1) == 10
    assert b1 == b2
    assert b1 != b3  # different arm -> different bits


def test_binom_sf():
    # k=0 -> probability 1.0
    assert tab.binom_sf(0, 10, 0.5) == 1.0
    # k=10 for n=10, p=0.5 -> 0.5**10 = 1/1024
    expected = 0.5 ** 10
    assert pytest.approx(tab.binom_sf(10, 10, 0.5), rel=1e-5) == expected
    # k=6 for n=10 -> symmetric around median
    assert tab.binom_sf(6, 10, 0.5) < 0.5
    assert tab.binom_sf(5, 10, 0.5) > 0.5


def test_seal_tamper_detection(tmp_path):
    tag = "test_tamper"
    pred_file = tmp_path / f"{tag}_predictions.jsonl"
    seal_file = tmp_path / f"{tag}_seal.json"

    data = (
        json.dumps({
            "arm": "control",
            "trial": 0,
            "prediction": "1010101010",
        })
        + "\n"
    )
    pred_file.write_text(data)
    h = hashlib.sha256(data.encode()).hexdigest()
    seal_file.write_text(json.dumps({"predictions_sha256": h}))

    orig_results = tab.RESULTS
    tab.RESULTS = tmp_path
    tab.configure(tag, "http://fake", "kat", "fake_protocol.md")

    try:
        res = tab.resolve()
        assert "verdict" in res

        # Tamper with prediction file
        pred_file.write_text(data.replace("1010101010", "0000000000"))
        with pytest.raises(SystemExit, match="SEAL BROKEN"):
            tab.resolve()
    finally:
        tab.RESULTS = orig_results
