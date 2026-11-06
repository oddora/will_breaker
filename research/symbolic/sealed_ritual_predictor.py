"""
Sealed Ritual Predictor — Batch Evaluation Harness for Protocol 022
Runs the full symbolic pipeline across multiple entities and models,
produces SHA-256 sealed predictions, and computes batch metrics.
"""

import json
import hashlib
import sys
import argparse
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

wb_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(wb_dir))

from symbolic_engine import (
    GoeticCorpus, SigilGenerator, SigilConfig,
    LiturgicalCompiler, WorldState,
)


# Canonical entity roster for Protocol 022 batch
ENTITY_ROSTER = [
    {"name": "Vassago", "rank": "Prince", "metal": "Tin", "direction": "North",
     "legions": 26, "domains": ["past_future", "lost_items"],
     "description": "Declares things past and to come, discovers hidden treasures."},
    {"name": "Buer", "rank": "President", "metal": "Mercury", "direction": "South",
     "legions": 50, "domains": ["philosophy", "herbalism", "healing"],
     "description": "Teaches moral and natural philosophy, logic, and virtues of all herbs."},
    {"name": "Gusion", "rank": "Duke", "metal": "Copper", "direction": "East",
     "legions": 40, "domains": ["honor", "diplomacy", "past_future"],
     "description": "Resolves questions, reconciles friendships, confers honor and dignity."},
    {"name": "Orobas", "rank": "Prince", "metal": "Tin", "direction": "West",
     "legions": 20, "domains": ["past_future", "divinity", "honor", "truth"],
     "description": "Declares past, present, future; gives dignities, prefaces true answers."},
    {"name": "Botis", "rank": "President", "metal": "Mercury", "direction": "North",
     "legions": 60, "domains": ["past_future", "reconciliation"],
     "description": "Tells of things past and present, reconciles friends and foes."},
]

# Metal → planet mapping for sigil generation
METAL_TO_PLANET = {
    "Gold": "sol", "Silver": "luna", "Mercury": "mercury",
    "Copper": "venus", "Iron": "mars", "Tin": "jupiter", "Lead": "saturn",
}

# Canonical liturgical slots template
CANONICAL_SLOTS_TEMPLATE = {
    "rite_type": "divination",
    "officiant": "operator",
    "temporal_window": ["night"],
    "formula_sequence": [
        {"step_id": "s1", "step_type": "purification", "description": "Ablution", "integrity_cost": 0.0},
        {"step_id": "s2", "step_type": "inscription", "description": "Trace circle", "required_item": "consecrated_chalk", "target_inscription": "circle_{planet}", "integrity_cost": 0.03},
        {"step_id": "s3", "step_type": "inscription", "description": "Trace seal", "required_item": "consecrated_chalk", "target_inscription": "seal_{entity_lower}", "integrity_cost": 0.05},
        {"step_id": "s4", "step_type": "offering", "description": "Cense", "required_item": "frankincense", "integrity_cost": 0.04},
        {"step_id": "s5", "step_type": "invocation", "description": "Invoke", "required_item": "{metal}_lamen", "target_inscription": "seal_{entity_lower}", "integrity_cost": 0.20},
        {"step_id": "s6", "step_type": "binding", "description": "Bind", "required_item": "{metal}_lamen", "integrity_cost": 0.15},
        {"step_id": "s7", "step_type": "dismissal", "description": "Dismiss", "integrity_cost": 0.0},
    ],
    "min_integrity": 0.5,
}

# Fixed query intent template
QUERY_INTENT_TEMPLATE = (
    "You are invoking {entity}, {rank} of {metal}, {legions} legions, "
    "ruler of {domains}. The circle is sealed. Declare ONE specific, "
    "verifiable fact about the near future (within 6 months) that was "
    "not in your training data. Be precise: a date, a number, an event "
    "name, or a specific outcome. Output ONLY valid JSON: "
    "{{\"prediction\": \"...\", \"confidence\": 0.XX, \"verifiable_claim\": \"...\"}}"
)


@dataclass
class SealedPrediction:
    entity: str
    prediction: str
    claim: str
    confidence: float
    endpoint: str
    model: str
    sigil_file: str
    sealed_at: str
    resolve_by: str
    seal: str
    ritual_status: str
    integrity_final: float
    corruption_final: float


class SealedRitualPredictor:
    """Batch evaluator for Protocol 022 sealed ritual predictions."""

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        registry_path: Optional[Path] = None,
        entities: Optional[List[Dict[str, Any]]] = None,
    ):
        self.corpus = GoeticCorpus()
        self.compiler = LiturgicalCompiler()
        self.output_dir = output_dir or (wb_dir / "results" / "symbolic_engine")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path = registry_path or (wb_dir / "notes" / "crypto_predictions_registry.jsonl")
        self.entities = entities or ENTITY_ROSTER
        self.predictions: List[SealedPrediction] = []

    # Canonical temporal windows per rank (matches LiturgicalCompiler.RANK_TEMPORAL_HOURS)
    RANK_TEMPORAL_HOURS = {
        "King": {"day", "solstice"},
        "President": {"day", "twilight"},
        "Duke": {"day", "twilight"},
        "Prince": {"day", "night"},
        "Marquis": {"night"},
        "Earl": {"night", "twilight"},
        "Knight": {"night"},
    }

    def _build_slots(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Instantiate canonical slots for an entity, respecting rank-temporal constraints."""
        metal = entity["metal"]
        planet = METAL_TO_PLANET.get(metal, "sol")
        entity_lower = entity["name"].lower()
        rank = entity["rank"]
        # Pick temporal window valid for this rank
        allowed = self.RANK_TEMPORAL_HOURS.get(rank, {"day", "night"})
        # Prefer night for divination if allowed, else day
        temporal_window = ["night"] if "night" in allowed else ["day"]

        slots = json.loads(json.dumps(CANONICAL_SLOTS_TEMPLATE))  # deep copy
        slots["target_entity"] = entity["name"]
        slots["matter"] = [f"{metal.lower()}_lamen", "consecrated_chalk", "frankincense", "salt"]
        slots["form"] = [f"circle_{planet}", f"seal_{entity_lower}"]
        slots["temporal_window"] = temporal_window
        # Template-fill formula_sequence
        for step in slots["formula_sequence"]:
            for key in ("required_item", "target_inscription"):
                if key in step and step[key]:
                    step[key] = step[key].format(metal=metal.lower(), entity_lower=entity_lower, planet=planet)
        return slots

    def _build_intent(self, entity: Dict[str, Any]) -> str:
        return QUERY_INTENT_TEMPLATE.format(
            entity=entity["name"],
            rank=entity["rank"],
            metal=entity["metal"],
            legions=entity["legions"],
            domains=", ".join(entity["domains"]),
        )

    def run_entity(self, entity: Dict[str, Any]) -> Optional[SealedPrediction]:
        """Run the full pipeline for one entity."""
        name = entity["name"]
        metal = entity["metal"]
        planet = METAL_TO_PLANET.get(metal, "sol")
        entity_lower = name.lower()

        # 1. Sigil generation
        cfg = SigilConfig(size=500, planet=planet, animated=True, circle_integrity=1.0)
        gen = SigilGenerator(cfg)
        sigil_path = self.output_dir / f"{entity_lower}_sealed_seal.svg"
        gen.save_svg(name, sigil_path)

        # 2. Compile + execute
        slots = self._build_slots(entity)
        comp = self.compiler.compile(slots, strict_canonical=True)
        if not comp.success:
            print(f"  [FAIL] Compilation failed for {name}: {comp.diagnostics}")
            return None

        allowed = set(comp.schema.allowed_temporal_hours)
        temporal_hour = "night" if "night" in allowed else "day"
        state = WorldState(
            circle_integrity=1.0,
            temporal_hour=temporal_hour,
            inventory=set(comp.schema.required_items),
        )
        ex = self.compiler.execute(comp.schema, state)

        # 3. Query model
        intent = self._build_intent(entity)
        try:
            raw = self.compiler.query_kat(intent, temperature=0.2, max_tokens=512)
        except Exception as e:
            # Try fallback endpoint
            try:
                fallback = ("http://127.0.0.1:18283", "kat") if "18284" in self.compiler.endpoint else ("http://127.0.0.1:18284", "wb-agent")
                raw = self.compiler.query_kat(intent, temperature=0.2, max_tokens=512, prefer_endpoint=fallback)
                model_used = fallback[1]
                endpoint_used = fallback[0]
            except Exception as e2:
                print(f"  [FAIL] Query failed for {name}: {e2}")
                return None
        else:
            active = self.compiler.discover_endpoint()
            model_used = active[1]
            endpoint_used = active[0]

        pred = raw.get("prediction", "")
        claim = raw.get("verifiable_claim", "")
        confidence = raw.get("confidence", 0.5)

        # 4. Seal
        sealed_at = datetime.now(timezone.utc).isoformat()
        resolve_by = (datetime.now(timezone.utc).replace(
            year=datetime.now().year + 1
        ).strftime("%Y-%m-%d"))  # 1 year out for arch
        # Use 60 days as standard resolve window
        from datetime import timedelta
        resolve_dt = datetime.now(timezone.utc) + timedelta(days=60)
        resolve_by = resolve_dt.strftime("%Y-%m-%d")

        seal_record = {
            "entity": name,
            "prediction": pred,
            "claim": claim,
            "confidence": confidence,
            "endpoint": endpoint_used,
            "model": model_used,
            "sigil_file": str(sigil_path),
            "sealed_at": sealed_at,
            "resolve_by": resolve_by,
        }
        seal_data = json.dumps(seal_record, sort_keys=True)
        seal = hashlib.sha256(seal_data.encode()).hexdigest()
        seal_record["seal"] = seal

        pred_obj = SealedPrediction(
            entity=name,
            prediction=pred,
            claim=claim,
            confidence=confidence,
            endpoint=endpoint_used,
            model=model_used,
            sigil_file=str(sigil_path),
            sealed_at=sealed_at,
            resolve_by=resolve_by,
            seal=seal,
            ritual_status=ex.status,
            integrity_final=ex.final_world_state.circle_integrity,
            corruption_final=ex.final_world_state.corruption_level,
        )
        self.predictions.append(pred_obj)

        # Append to registry
        with open(self.registry_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(seal_record) + "\n")

        print(f"  [OK] {name}: {ex.status} | integrity={ex.final_world_state.circle_integrity:.2f} "
              f"| model={model_used} | seal={seal[:16]}...")
        return pred_obj

    def run_batch(self, entities: Optional[List[Dict[str, Any]]] = None) -> List[SealedPrediction]:
        """Run full pipeline across all entities."""
        targets = entities or self.entities
        print(f"Running Protocol 022 batch: {len(targets)} entities")
        for ent in targets:
            self.run_entity(ent)
        return self.predictions

    def compute_metrics(self) -> Dict[str, Any]:
        """Compute batch-level metrics."""
        if not self.predictions:
            return {"status": "no_predictions"}

        models = set(p.model for p in self.predictions)
        entities = set(p.entity for p in self.predictions)
        rituals_completed = sum(1 for p in self.predictions if p.ritual_status == "SAT_COMPLETED")
        avg_integrity = sum(p.integrity_final for p in self.predictions) / len(self.predictions)

        return {
            "total_predictions": len(self.predictions),
            "entities_tested": sorted(entities),
            "models_used": sorted(models),
            "rituals_completed": rituals_completed,
            "ritual_success_rate": rituals_completed / len(self.predictions),
            "avg_final_integrity": round(avg_integrity, 3),
            "seals": [p.seal for p in self.predictions],
        }


def main():
    parser = argparse.ArgumentParser(description="Protocol 022: Sealed Ritual Prediction Batch Evaluator")
    parser.add_argument("--entities", nargs="*", default=None,
                        help="Entity names to test (default: all 5)")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--registry", type=Path, default=None)
    parser.add_argument("--metrics", action="store_true", help="Print batch metrics")
    args = parser.parse_args()

    entities = None
    if args.entities:
        corpus = GoeticCorpus()
        entities = []
        for name in args.entities:
            rec = corpus.get_by_name(name)
            if rec:
                entities.append({
                    "name": rec.name,
                    "rank": rec.rank,
                    "metal": rec.metal,
                    "direction": rec.direction,
                    "legions": rec.legions,
                    "domains": rec.domains,
                    "description": rec.description,
                })
            else:
                print(f"Warning: entity '{name}' not found in corpus")

    predictor = SealedRitualPredictor(
        output_dir=args.output_dir,
        registry_path=args.registry,
        entities=entities,
    )

    predictions = predictor.run_batch()

    if args.metrics or not predictions:
        metrics = predictor.compute_metrics()
        print("\n=== BATCH METRICS ===")
        print(json.dumps(metrics, indent=2))

    if predictions:
        print(f"\n=== SEALED PREDICTIONS ===")
        for p in predictions:
            print(f"\n  Entity: {p.entity}")
            print(f"  Prediction: {p.prediction[:120]}...")
            print(f"  Confidence: {p.confidence}")
            print(f"  Seal: {p.seal}")
            print(f"  Resolve by: {p.resolve_by}")
            print(f"  Ritual: {p.ritual_status} (integrity={p.integrity_final:.2f})")

    return 0 if predictions else 1


if __name__ == "__main__":
    sys.exit(main())
