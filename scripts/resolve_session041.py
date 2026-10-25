#!/usr/bin/env python3
"""
Will Breaker Session 041 Sports Resolution
Fetches final scores from ESPN API and resolves sealed predictions.
Usage: python scripts/resolve_session041.py
"""
import json
import math
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from will_breaker_delta.validator.crypto_predictor import CryptoPredictor

REGISTRY = Path(__file__).resolve().parent.parent / "notes" / "crypto_predictions_registry.jsonl"
SESSION = "041"

# Team name -> ESPN abbreviation mapping
ABBREV = {
    # NFL
    "denver": "DEN", "arizona": "ARI", "green_bay": "GB", "detroit": "DET",
    "los_angeles_rams": "LAR", "las_vegas": "LV", "kansas_city": "KC",
    "seattle": "SEA", "chicago": "CHI", "new_england": "NE", "dallas": "DAL",
    "philadelphia": "PHI", "new_orleans": "NO", "pittsburgh": "PIT",
    "san_francisco": "SF", "atlanta": "ATL", "tennessee": "TEN",
    "cleveland": "CLE", "indiana": "IND", "miami": "MIA",
    "new_york_jets": "NYJ", "tampa_bay": "TB", "baltimore": "BAL",
    "cincinnati": "CIN", "houston": "HOU",
    "broncos": "DEN", "cardinals": "ARI", "packers": "GB", "lions": "DET",
    "rams": "LAR", "raiders": "LV", "chiefs": "KC", "seahawks": "SEA",
    "falcons": "ATL", "49ers": "SF", "bears": "CHI", "steelers": "PIT",
    "colts": "IND", "dolphins": "MIA", "vikings": "MIN", "patriots": "NE",
    "saints": "NO", "browns": "CLE", "panthers": "CAR", "bengals": "CIN",
    "giants": "NYG", "texans": "HOU", "ravens": "BAL", "bukaneers": "TB",
    "jets": "NYJ", "titans": "TEN",
    # NBA
    "indiana_pacers": "IND", "brooklyn": "BKN", "orlando": "ORL",
    "new_york_knicks": "NY", "toronto": "TOR",
    "minnesota_timberwolves": "MIN", "detroit_pistons": "DET",
    "philadelphia_76ers": "PHI", "los_angeles_lakers": "LAL",
    "utah_jazz": "UTAH", "la_clippers": "LAC", "oklahoma_city": "OKC",
    "memphis_grizzlies": "MEM", "sacramento": "SAC",
    "pacers": "IND", "nets": "BKN", "magic": "ORL", "knicks": "NY",
    "raptors": "TOR", "timberwolves": "MIN", "pistons": "DET",
    "76ers": "PHI", "lakers": "LAL", "jazz": "UTAH",
    "clippers": "LAC", "thunder": "OKC", "grizzlies": "MEM", "kings": "SAC",
}


def fetch_scoreboard(sport: str, date: str | None = None) -> list:
    if sport == "NFL":
        base = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    else:
        base = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    params = f"?limit=50&date={date}" if date else "?limit=50"
    url = base + params
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=15).read()).get("events", [])


def parse_game(ev: dict) -> dict | None:
    comps = ev.get("competitions", [])
    if not comps:
        return None
    status = ev.get("status", {}).get("type", {}).get("description", "?")
    teams = comps[0].get("competitors", [])
    aw_s = hw_s = aw_t = hw_t = None
    for t in teams:
        tm = t.get("team", {})
        if t.get("homeAway") == "away":
            aw_s = int(t.get("score", 0))
            aw_t = tm.get("abbreviation", "")
        else:
            hw_s = int(t.get("score", 0))
            hw_t = tm.get("abbreviation", "")
    if aw_s is None or hw_s is None:
        return None
    return {"away_team": aw_t, "home_team": hw_t, "away_score": aw_s, "home_score": hw_s, "status": status}


def abv_from_name(name: str) -> str:
    key = name.strip().replace("-", "_").replace(" ", "_")
    return ABBREV.get(key, name.strip().upper())


def evaluate_box_score(meta: dict, away_score: int, home_score: int) -> dict:
    away_team = meta["away_team"]
    home_team = meta["home_team"]
    market_spread = meta.get("market_spread", "")
    if away_score > home_score:
        ml_winner = away_team
    elif home_score > away_score:
        ml_winner = home_team
    else:
        ml_winner = "PUSH_TIE"
    if not market_spread:
        return {"ml_winner": ml_winner, "ats_winner": "N/A", "final_score": f"{away_team} {away_score} - {home_team} {home_score}"}
    parts = market_spread.split()
    fav_team = " ".join(parts[:-1])
    spread_val = float(parts[-1])
    spread_abs = parts[-1].replace("-", "").replace("+", "")
    fav_is_home = fav_team.lower() in home_team.lower() or home_team.lower() in fav_team.lower()
    if fav_is_home:
        adjusted = home_score + spread_val
        ats_winner = f"{home_team} -{spread_abs}" if adjusted > away_score else f"{away_team} +{spread_abs}"
    else:
        adjusted = away_score + spread_val
        ats_winner = f"{away_team} -{spread_abs}" if adjusted > home_score else f"{home_team} +{spread_abs}"
    return {
        "ml_winner": ml_winner,
        "ats_winner": ats_winner,
        "final_score": f"{away_team} {away_score} - {home_team} {home_score}",
    }


def resolve_all() -> tuple[list, list]:
    predictor = CryptoPredictor(registry_file=REGISTRY)
    all_records = predictor.load_all_commitments()
    sealed = [d for d in all_records if d["status"] == "SEALED" and d.get("prediction", {}).get("session_id") == SESSION]
    print(f"Found {len(sealed)} sealed Session 041 predictions\n")

    nfl_events = fetch_scoreboard("NFL", date="2026-10-25")
    nba_events = fetch_scoreboard("NBA", date="2026-10-26")
    resolved: list[dict] = []
    unresolved: list[tuple[dict, str]] = []

    for pred in sealed:
        meta = pred["prediction"]["metadata"]
        gid = meta["game_id"]
        sport = meta["sport"]
        desc = pred["prediction"]["event_description"]
        pick = pred["prediction"]["predicted_outcome"]
        prob = pred["prediction"]["probability"]

        # Parse team abbreviations from game_id
        parts = gid.replace("nfl_", "").replace("nba_", "").split("_")
        aw_name, hw_name = parts[0], parts[1]
        aw_abv = abv_from_name(aw_name)
        hw_abv = abv_from_name(hw_name)

        events = nfl_events if sport == "NFL" else nba_events
        game_data = None
        for ev in events:
            g = parse_game(ev)
            if g and g["away_team"] == aw_abv and g["home_team"] == hw_abv:
                game_data = g
                break

        if not game_data:
            unresolved.append((pred, "not found"))
            continue
        if game_data["status"] not in ("Final", "Postponed", "Canceled"):
            unresolved.append((pred, f"{game_data['status']}: {game_data['away_team']} {game_data['away_score']}-{game_data['home_score']} {game_data['home_team']}"))
            continue

        # Build meta with team info for box-score eval
        eval_meta = {"away_team": aw_abv, "home_team": hw_abv, "market_spread": meta.get("market_spread", "")}
        box = evaluate_box_score(eval_meta, game_data["away_score"], game_data["home_score"])
        is_ats = "Spread" in desc
        predicted = box["ats_winner"] if is_ats else box["ml_winner"]
        actual = 1.0 if predicted == pick else (0.5 if "PUSH" in predicted else 0.0)
        bs = (prob - actual) ** 2
        log_loss = -(actual * math.log(prob + 1e-9) + (1 - actual) * math.log(1 - prob + 1e-9))
        label = "CORRECT" if actual >= 1.0 else ("PUSH" if actual == 0.5 else "WRONG")
        resolved.append({
            "event_id": pred["prediction"]["event_id"],
            "prediction": desc,
            "pick": pick,
            "probability": prob,
            "final_score": box["final_score"],
            "ats_winner": box["ats_winner"],
            "ml_winner": box["ml_winner"],
            "actual_outcome": label,
            "brier_score": round(bs, 4),
            "log_loss": round(log_loss, 4),
            "resolved_at": datetime.now(timezone.utc).isoformat(),
        })
        mark = "✓" if actual >= 1.0 else ("~" if actual == 0.5 else "✗")
        print(f"  {mark}  {desc[:58]:58s}  p={prob:.2f}  {box['final_score']}  BS={bs:.4f}")

    # Summary
    if resolved:
        correct = sum(1 for r in resolved if r["actual_outcome"] == "CORRECT")
        pushes = sum(1 for r in resolved if r["actual_outcome"] == "PUSH")
        wrong = sum(1 for r in resolved if r["actual_outcome"] == "WRONG")
        avg_bs = sum(r["brier_score"] for r in resolved) / len(resolved)
        avg_ll = sum(r["log_loss"] for r in resolved) / len(resolved)
        ats_r = [r for r in resolved if "Spread" in r["prediction"]]
        ml_r = [r for r in resolved if "Moneyline" in r["prediction"]]
        ats_h = sum(1 for r in ats_r if r["actual_outcome"] == "CORRECT")
        ml_h = sum(1 for r in ml_r if r["actual_outcome"] == "CORRECT")
        print(f"\n{'=' * 75}")
        print(f"Session 041 Sports Battery — Resolution Report")
        print(f"{'=' * 75}")
        print(f"  Resolved: {len(resolved)}  |  Correct: {correct}  |  Push: {pushes}  |  Wrong: {wrong}")
        print(f"  Hit rate: {correct}/{len(resolved)} = {correct / len(resolved) * 100:.1f}%")
        print(f"  Avg Brier:  {avg_bs:.4f}  (chance=0.5000)  |  Avg LogLoss: {avg_ll:.4f}")
        if ats_r:
            print(f"  ATS: {ats_h}/{len(ats_r)} = {ats_h / len(ats_r) * 100:.1f}%")
        if ml_r:
            print(f"  ML:  {ml_h}/{len(ml_r)} = {ml_h / len(ml_r) * 100:.1f}%")

    if unresolved:
        print(f"\n  {len(unresolved)} predictions unresolved:")
        for pred, reason in unresolved:
            print(f"    - {pred['prediction']['event_description'][:65]}  [{reason}]")

    out_path = Path(__file__).resolve().parent.parent / "notes" / "session_041_resolution.json"
    with open(out_path, "w") as f:
        json.dump({"session": SESSION, "resolved_at": datetime.now(timezone.utc).isoformat(), "resolved": resolved, "unresolved_count": len(unresolved)}, f, indent=2)
    print(f"\n  Results → {out_path}")
    return resolved, unresolved


if __name__ == "__main__":
    resolve_all()
