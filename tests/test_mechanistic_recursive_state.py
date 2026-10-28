"""Protocol 018 mechanistic recursive-state runner: fixture tests."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from research.benchmarks import mechanistic_recursive_state as mrs


def _payload(text="I am processing", p=0.99):
    toks = text.split()
    content = []
    for tok in toks:
        rest = max(1.0 - p, 1e-9)
        content.append({
            "token": tok,
            "logprob": math.log(p),
            "top_logprobs": [
                {"token": tok, "logprob": math.log(p)},
                {"token": "other", "logprob": math.log(rest)},
            ],
        })
    return {"choices": [{"message": {"content": text},
                          "logprobs": {"content": content}}]}


def test_parse_generation_uses_primary_20_token_window():
    payload = _payload(" ".join(f"t{i}" for i in range(25)), p=0.5)
    got = mrs.parse_generation(payload)
    assert got["token_count"] == 25
    assert got["primary_tokens"] == 20
    assert got["mean_entropy"] == pytest.approx(math.log(2), abs=1e-3)


def test_parse_generation_fails_closed_without_logprobs():
    with pytest.raises(ValueError, match="logprobs"):
        mrs.parse_generation({"choices": [{"message": {"content": "x"}}]})


def test_recursive_trial_feeds_prior_response_and_counts_failure():
    seen = []

    def fetch(prompt, seed):
        seen.append((prompt, seed))
        return _payload(f"reply{len(seen)}")

    trial = mrs.run_trial(fetch, "A", 3, depths=3)
    assert trial["complete"] is True
    assert [s for _, s in seen] == [44003, 44003, 44003]
    assert "reply1" in seen[1][0]
    assert "State vector S_2" in seen[1][0]

    def broken(prompt, seed):
        return {"choices": [{"message": {"content": "no metrics"}}]}

    failed = mrs.run_trial(broken, "A", 0, depths=2)
    assert failed["complete"] is False
    assert "logprobs" in failed["failure"]


def _trial(arm, idx, entropies, coherence=0.9):
    return {
        "arm": arm, "trial_index": idx, "complete": True, "failure": None,
        "depths": [
            {"depth": i + 1, "mean_entropy": h, "mean_coherence": coherence,
             "token_count": 20, "primary_tokens": 20}
            for i, h in enumerate(entropies)
        ],
    }


def test_summary_signature_monotonic_and_wilcoxon():
    trials = []
    for i in range(12):
        trials.append(_trial("A", i, [1.0, 0.8, 0.6, 0.4, 0.2]))
        trials.append(_trial("D", i, [0.7, 0.65, 0.6, 0.55, 0.5]))
        trials.append(_trial("B", i, [0.8] * 5))
        trials.append(_trial("C", i, [0.8] * 5))
    summary = mrs.summarize(trials)
    assert summary["arms"]["A"]["signature_count"] == 12
    assert summary["arms"]["A"]["monotonic_count"] == 12
    assert summary["wilcoxon_a_lt_d"]["p_one_sided"] < 0.01
    assert mrs.formal_verdict(summary) == "PASS"


def test_board_when_any_arm_incomplete():
    trials = [_trial(a, i, [0.5] * 5) for a in "ABCD" for i in range(9)]
    summary = mrs.summarize(trials)
    assert mrs.formal_verdict(summary) == "BOARD"
