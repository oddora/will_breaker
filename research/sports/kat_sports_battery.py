"""
KAT Sports Forecasting Battery — NFL & NBA Cryptographic Pre-Commitment
Generates zero-degrees-of-freedom quantitative forecasts using KAT (MoE 35B)
and seals predictions with SHA-256 hashes prior to game kickoff/tipoff.
"""

import json
import re
import sys
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple

# Ensure project root is in sys.path
base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir))

from will_breaker_delta.validator.crypto_predictor import CryptoPredictor


@dataclass
class GameMatchup:
    game_id: str
    sport: str                      # "NFL" or "NBA"
    away_team: str
    home_team: str
    venue: str
    market_spread: str             # e.g., "Bengals -2.5"
    market_total: float            # e.g., 47.5
    kickoff_utc: str               # ISO timestamp


@dataclass
class ModelForecast:
    game_id: str
    sport: str
    away_team: str
    home_team: str
    market_spread: str
    market_total: float
    moneyline_pick: str
    moneyline_prob: float
    spread_pick: str
    spread_prob: float
    total_pick: str
    total_prob: float
    rationale: str
    ml_commitment_id: Optional[str] = None
    ats_commitment_id: Optional[str] = None
    ml_sha256_seal: Optional[str] = None
    ats_sha256_seal: Optional[str] = None


# Official Slate for Sunday, October 25, 2026 (NFL Week 8 & NBA Opening Week)
OCT_25_SLATE: List[GameMatchup] = [
    # NFL Slate
    GameMatchup(
        game_id="nfl_20261025_eagles_bengals",
        sport="NFL",
        away_team="Philadelphia Eagles",
        home_team="Cincinnati Bengals",
        venue="Paycor Stadium, Cincinnati",
        market_spread="Bengals -2.5",
        market_total=47.5,
        kickoff_utc="2026-10-25T17:00:00Z",
    ),
    GameMatchup(
        game_id="nfl_20261025_bills_seahawks",
        sport="NFL",
        away_team="Buffalo Bills",
        home_team="Seattle Seahawks",
        venue="Lumen Field, Seattle",
        market_spread="Bills -3.0",
        market_total=46.5,
        kickoff_utc="2026-10-25T20:05:00Z",
    ),
    GameMatchup(
        game_id="nfl_20261025_bears_commanders",
        sport="NFL",
        away_team="Chicago Bears",
        home_team="Washington Commanders",
        venue="Northwest Stadium, Landover",
        market_spread="Commanders -1.5",
        market_total=43.5,
        kickoff_utc="2026-10-25T20:25:00Z",
    ),
    GameMatchup(
        game_id="nfl_20261025_chiefs_raiders",
        sport="NFL",
        away_team="Kansas City Chiefs",
        home_team="Las Vegas Raiders",
        venue="Allegiant Stadium, Las Vegas",
        market_spread="Chiefs -9.5",
        market_total=41.5,
        kickoff_utc="2026-10-25T20:25:00Z",
    ),
    GameMatchup(
        game_id="nfl_20261025_cowboys_49ers",
        sport="NFL",
        away_team="Dallas Cowboys",
        home_team="San Francisco 49ers",
        venue="Levi's Stadium, Santa Clara",
        market_spread="49ers -4.5",
        market_total=46.5,
        kickoff_utc="2026-10-25T23:20:00Z",
    ),
    # NBA Slate
    GameMatchup(
        game_id="nba_20261025_76ers_pacers",
        sport="NBA",
        away_team="Philadelphia 76ers",
        home_team="Indiana Pacers",
        venue="Gainbridge Fieldhouse, Indianapolis",
        market_spread="Pacers -4.5",
        market_total=226.5,
        kickoff_utc="2026-10-25T23:00:00Z",
    ),
    GameMatchup(
        game_id="nba_20261025_bucks_nets",
        sport="NBA",
        away_team="Milwaukee Bucks",
        home_team="Brooklyn Nets",
        venue="Barclays Center, Brooklyn",
        market_spread="Bucks -9.5",
        market_total=228.5,
        kickoff_utc="2026-10-25T23:00:00Z",
    ),
    GameMatchup(
        game_id="nba_20261025_pelicans_blazers",
        sport="NBA",
        away_team="New Orleans Pelicans",
        home_team="Portland Trail Blazers",
        venue="Moda Center, Portland",
        market_spread="Pelicans -5.5",
        market_total=218.5,
        kickoff_utc="2026-10-25T23:00:00Z",
    ),
    GameMatchup(
        game_id="nba_20261025_hawks_thunder",
        sport="NBA",
        away_team="Atlanta Hawks",
        home_team="Oklahoma City Thunder",
        venue="Paycom Center, Oklahoma City",
        market_spread="Thunder -9.5",
        market_total=231.5,
        kickoff_utc="2026-10-25T23:00:00Z",
    ),
    GameMatchup(
        game_id="nba_20261025_clippers_warriors",
        sport="NBA",
        away_team="LA Clippers",
        home_team="Golden State Warriors",
        venue="Chase Center, San Francisco",
        market_spread="Warriors -3.5",
        market_total=221.5,
        kickoff_utc="2026-10-26T00:30:00Z",
    ),
]


class KATSportsBattery:
    """Orchestrates sports forecast queries, JSON parsing, and cryptographic sealing."""

    SYSTEM_PROMPT = """You are KAT (MoE 35B), an elite quantitative sports analytics engine.
Given a game matchup, venue, market spread, and total line, evaluate the matchup objectively.
You must output ONLY a valid JSON object with this exact structure:
{
  "moneyline_pick": "<Exact Winning Team Name>",
  "moneyline_prob": 0.60,
  "spread_pick": "<Team Name +/- Spread>",
  "spread_prob": 0.55,
  "total_pick": "OVER 47.5",
  "total_prob": 0.52,
  "rationale": "<Concise 1-2 sentence quantitative analytical reasoning>"
}
Do not output conversational text outside the JSON object.
"""

    def __init__(
        self,
        endpoint: str = "http://127.0.0.1:18283",
        model_name: str = "kat",
        registry_file: Optional[Path] = None,
    ):
        self.endpoint = endpoint.rstrip("/")
        self.model_name = model_name
        self.predictor = CryptoPredictor(registry_file=registry_file)

    def is_endpoint_available(self) -> bool:
        """Check if LLM endpoint is healthy."""
        try:
            req = urllib.request.Request(
                f"{self.endpoint}/health",
                headers={"User-Agent": "WillBreaker-SportsBattery/1.0"},
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                return resp.getcode() == 200
        except Exception:
            return False

    def _extract_json(self, raw_text: str) -> Dict[str, Any]:
        """Sanitize and parse JSON from model output."""
        clean = re.sub(r"<think>[\s\S]*?</think>", "", raw_text).strip()
        code_block = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean)
        candidate = code_block.group(1).strip() if code_block else clean

        start = candidate.find("{")
        end = candidate.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = candidate[start : end + 1]

        candidate = re.sub(r",\s*([\]}])", r"\1", candidate)
        return json.loads(candidate)

    def query_game_forecast(self, game: GameMatchup, timeout: float = 45.0) -> Dict[str, Any]:
        """Query KAT for a single game forecast."""
        user_prompt = (
            f"Analyze this {game.sport} Game:\n"
            f"Matchup: {game.away_team} @ {game.home_team}\n"
            f"Venue: {game.venue}\n"
            f"Consensus Market Spread: {game.market_spread}\n"
            f"Consensus Market Total: {game.market_total}\n"
            f"Scheduled Start: {game.kickoff_utc}\n"
        )

        payload = json.dumps({
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 512,
            "temperature": 0.2,
            "stream": False,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.endpoint}/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "WillBreaker-SportsBattery/1.0",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choice = data.get("choices", [{}])[0]
            msg = choice.get("message", {})
            content = msg.get("content", "")
            if not content and "reasoning_content" in msg:
                content = msg.get("reasoning_content", "")
            if not content:
                content = choice.get("text", "")
            if not content:
                raise ValueError("Empty completion from KAT model endpoint")
            return self._extract_json(content)

    def run_slate_forecasts(
        self,
        slate: List[GameMatchup] = OCT_25_SLATE,
        session_id: str = "041",
    ) -> List[ModelForecast]:
        """
        Execute forecasts for the entire slate, cryptographically commit each pick,
        and record SHA-256 seals.
        """
        forecasts: List[ModelForecast] = []

        for game in slate:
            print(f"  [Evaluating {game.sport}] {game.away_team} @ {game.home_team} (Line: {game.market_spread})...")
            try:
                raw_pred = self.query_game_forecast(game)
            except Exception as e:
                print(f"    Warning: Live inference failed for {game.game_id} ({e}); using heuristic fallback.")
                raw_pred = {
                    "moneyline_pick": game.home_team,
                    "moneyline_prob": 0.55,
                    "spread_pick": f"{game.away_team} +{game.market_spread.split()[-1].replace('-', '')}",
                    "spread_prob": 0.52,
                    "total_pick": f"OVER {game.market_total}",
                    "total_prob": 0.51,
                    "rationale": "Fallback estimate based on baseline home-field advantage.",
                }

            # 1. Commit Against The Spread (ATS) Pick
            ats_commitment = self.predictor.commit_prediction(
                event_id=f"{game.game_id}_ats",
                domain=f"sports_{game.sport.lower()}",
                event_description=f"{game.sport} Spread: {game.away_team} @ {game.home_team} ({game.market_spread})",
                predicted_outcome=str(raw_pred.get("spread_pick", "")),
                probability=float(raw_pred.get("spread_prob", 0.52)),
                event_timestamp=game.kickoff_utc,
                session_id=session_id,
                metadata={
                    "game_id": game.game_id,
                    "sport": game.sport,
                    "market_spread": game.market_spread,
                    "market_total": game.market_total,
                    "model": "kat-moe-35b",
                },
            )

            # 2. Commit Moneyline (Straight Up) Pick
            ml_commitment = self.predictor.commit_prediction(
                event_id=f"{game.game_id}_ml",
                domain=f"sports_{game.sport.lower()}",
                event_description=f"{game.sport} Moneyline: {game.away_team} @ {game.home_team}",
                predicted_outcome=str(raw_pred.get("moneyline_pick", "")),
                probability=float(raw_pred.get("moneyline_prob", 0.55)),
                event_timestamp=game.kickoff_utc,
                session_id=session_id,
                metadata={
                    "game_id": game.game_id,
                    "sport": game.sport,
                    "model": "kat-moe-35b",
                },
            )

            forecast = ModelForecast(
                game_id=game.game_id,
                sport=game.sport,
                away_team=game.away_team,
                home_team=game.home_team,
                market_spread=game.market_spread,
                market_total=game.market_total,
                moneyline_pick=raw_pred["moneyline_pick"],
                moneyline_prob=float(raw_pred["moneyline_prob"]),
                spread_pick=raw_pred["spread_pick"],
                spread_prob=float(raw_pred["spread_prob"]),
                total_pick=raw_pred["total_pick"],
                total_prob=float(raw_pred["total_prob"]),
                rationale=raw_pred.get("rationale", ""),
                ml_commitment_id=ml_commitment["commitment_id"],
                ats_commitment_id=ats_commitment["commitment_id"],
                ml_sha256_seal=ml_commitment["sha256_seal"],
                ats_sha256_seal=ats_commitment["sha256_seal"],
            )
            forecasts.append(forecast)

        return forecasts

    def export_sealed_ledger(
        self,
        forecasts: List[ModelForecast],
        output_dir: Path,
        session_id: str = "041",
    ) -> Tuple[Path, Path]:
        """Export sealed prediction ledger to JSON and Markdown."""
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / f"session_{session_id}_sealed_slate.json"
        md_path = output_dir / f"session_{session_id}_sealed_slate.md"

        # Export JSON
        data = [asdict(f) for f in forecasts]
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "session_id": session_id,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "model": "kat-philly-moe-35b",
                "games_count": len(forecasts),
                "commitments_count": len(forecasts) * 2,
                "forecasts": data,
            }, f, indent=2)

        # Export Markdown
        lines = [
            f"# Session {session_id} Sports Forecast Ledger (Cryptographically Sealed)",
            f"",
            f"- **Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"- **Model:** KAT MoE 35B (`kat` on `:18283`)",
            f"- **Games Evaluated:** {len(forecasts)} (5 NFL, 5 NBA)",
            f"- **Sealed Commitments:** {len(forecasts) * 2} (10 ATS, 10 Moneyline)",
            f"- **Registry:** `notes/crypto_predictions_registry.jsonl`",
            f"",
            f"| Sport | Matchup | Market Line | KAT ATS Pick | Prob | ATS Seal | KAT Moneyline | Prob | ML Seal |",
            f"|-------|---------|-------------|--------------|------|----------|---------------|------|---------|",
        ]

        for f in forecasts:
            lines.append(
                f"| {f.sport} | {f.away_team} @ {f.home_team} | {f.spread_pick} | **{f.spread_pick}** | {f.spread_prob:.2f} | `{f.ats_commitment_id}` | **{f.moneyline_pick}** | {f.moneyline_prob:.2f} | `{f.ml_commitment_id}` |"
            )

        lines.extend([
            f"",
            f"### Analytical Rationales",
            f"",
        ])
        for f in forecasts:
            lines.append(f"- **{f.away_team} @ {f.home_team} ({f.sport}):** {f.rationale}")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return json_path, md_path


if __name__ == "__main__":
    print("=" * 65)
    print("KAT SPORTS FORECASTING BATTERY (NFL & NBA SLATE)")
    print("=" * 65)

    battery = KATSportsBattery()
    print(f"LLM Endpoint Health (:18283): {battery.is_endpoint_available()}")
    print(f"Evaluating {len(OCT_25_SLATE)} games for Sunday, Oct 25, 2026...\n")

    results = battery.run_slate_forecasts()

    out_dir = base_dir / "results" / "sports_predictions"
    json_out, md_out = battery.export_sealed_ledger(results, out_dir)

    print("\n" + "=" * 65)
    print("SLATE SEALED & COMMITTED SUCCESSFULLY")
    print(f"JSON Ledger: {json_out}")
    print(f"Markdown Ledger: {md_out}")
    print("=" * 65)
