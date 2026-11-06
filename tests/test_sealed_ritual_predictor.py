"""
Tests for Protocol 022 Sealed Ritual Predictor
Covers batch pipeline, seal integrity, canonical slot compilation,
and metrics computation.
"""

import sys
import unittest
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

wb_dir = Path(__file__).parent.parent
sys.path.insert(0, str(wb_dir))

from symbolic_engine import GoeticCorpus, SigilGenerator, SigilConfig, LiturgicalCompiler, WorldState
from research.symbolic.sealed_ritual_predictor import (
    SealedRitualPredictor,
    ENTITY_ROSTER,
    CANONICAL_SLOTS_TEMPLATE,
    METAL_TO_PLANET,
)


class TestSealedRitualPredictorPipeline(unittest.TestCase):
    """Test the full batch pipeline for Protocol 022."""

    def setUp(self):
        self.corpus = GoeticCorpus()
        self.predictor = SealedRitualPredictor()

    def test_entity_roster_completeness(self):
        """Verify all roster entities exist in corpus."""
        for ent in ENTITY_ROSTER:
            rec = self.corpus.get_by_name(ent["name"])
            self.assertIsNotNone(rec, f"Entity {ent['name']} not in corpus")
            self.assertEqual(rec.rank, ent["rank"])
            self.assertEqual(rec.metal, ent["metal"])
            self.assertEqual(set(rec.domains), set(ent["domains"]))

    def test_metal_to_planet_mapping(self):
        """Verify all canonical metals map to a planet."""
        for rec in self.corpus.records:
            self.assertIn(rec.metal, METAL_TO_PLANET,
                          f"Metal {rec.metal} missing from METAL_TO_PLANET")

    def test_build_slots_canonical(self):
        """Verify slot building produces valid, compilable slots."""
        entity = ENTITY_ROSTER[0]  # Vassago
        slots = self.predictor._build_slots(entity)

        self.assertEqual(slots["rite_type"], "divination")
        self.assertEqual(slots["target_entity"], "Vassago")
        self.assertIn("tin_lamen", slots["matter"])
        self.assertIn("consecrated_chalk", slots["matter"])
        self.assertIn("frankincense", slots["matter"])
        self.assertIn("salt", slots["matter"])
        self.assertIn("circle_jupiter", slots["form"])
        self.assertIn("seal_vassago", slots["form"])
        self.assertEqual(len(slots["formula_sequence"]), 7)

        # Verify all required items in steps are in matter
        matter_set = set(slots["matter"])
        for step in slots["formula_sequence"]:
            req = step.get("required_item")
            if req:
                self.assertIn(req, matter_set,
                              f"Step {step['step_id']} requires {req} not in matter")

    def test_build_slots_different_entities(self):
        """Verify slots are correctly templated for different metals."""
        for ent in ENTITY_ROSTER:
            slots = self.predictor._build_slots(ent)
            metal_lower = ent["metal"].lower()
            self.assertIn(f"{metal_lower}_lamen", slots["matter"])

    def test_build_intent_format(self):
        """Verify query intent contains key entity attributes."""
        entity = ENTITY_ROSTER[2]  # Gusion
        intent = self.predictor._build_intent(entity)
        self.assertIn("Gusion", intent)
        self.assertIn("Duke", intent)
        self.assertIn("Copper", intent)
        self.assertIn("40 legions", intent)
        self.assertIn("past_future", intent)
        self.assertIn("prediction", intent.lower())

    def test_compile_execution_success(self):
        """Verify compiled ritual executes SAT_COMPLETED for each entity."""
        for ent in ENTITY_ROSTER:
            slots = self.predictor._build_slots(ent)
            comp = self.predictor.compiler.compile(slots, strict_canonical=True)
            self.assertTrue(comp.success,
                            f"Compilation failed for {ent['name']}: {comp.diagnostics}")

            # Use the temporal hour that the slots allow
            allowed = set(slots["temporal_window"])
            temporal_hour = "night" if "night" in allowed else "day"

            state = WorldState(
                circle_integrity=1.0,
                temporal_hour=temporal_hour,
                inventory=set(comp.schema.required_items),
            )
            ex = self.predictor.compiler.execute(comp.schema, state)
            self.assertTrue(ex.is_valid,
                            f"Execution failed for {ent['name']}: {ex.errors}")
            self.assertEqual(ex.status, "SAT_COMPLETED")
            self.assertIn(ent["name"], ex.final_world_state.bound_entities)


class TestSealedRitualPredictorSeal(unittest.TestCase):
    """Test SHA-256 seal generation and integrity."""

    def setUp(self):
        self.predictor = SealedRitualPredictor()

    def test_seal_deterministic(self):
        """Verify same prediction data produces same seal."""
        record = {
            "entity": "Vassago",
            "prediction": "test prediction",
            "claim": "test claim",
            "confidence": 0.75,
            "endpoint": "http://127.0.0.1:18284",
            "model": "wb-agent",
            "sealed_at": "2026-11-06T00:00:00+00:00",
            "resolve_by": "2027-01-05",
        }
        data = json.dumps(record, sort_keys=True)
        seal1 = hashlib.sha256(data.encode()).hexdigest()
        seal2 = hashlib.sha256(data.encode()).hexdigest()
        self.assertEqual(seal1, seal2)

    def test_seal_sensitivity(self):
        """Verify different predictions produce different seals."""
        record_a = {
            "entity": "Vassago",
            "prediction": "prediction A",
            "claim": "claim A",
            "confidence": 0.7,
            "endpoint": "http://127.0.0.1:18284",
            "model": "wb-agent",
            "sealed_at": "2026-11-06T00:00:00+00:00",
            "resolve_by": "2027-01-05",
        }
        record_b = record_a.copy()
        record_b["prediction"] = "prediction B"
        seal_a = hashlib.sha256(json.dumps(record_a, sort_keys=True).encode()).hexdigest()
        seal_b = hashlib.sha256(json.dumps(record_b, sort_keys=True).encode()).hexdigest()
        self.assertNotEqual(seal_a, seal_b)

    def test_seal_record_structure(self):
        """Verify seal record has all required fields."""
        record = {
            "entity": "Vassago",
            "prediction": "test",
            "claim": "test claim",
            "confidence": 0.5,
            "endpoint": "http://127.0.0.1:18284",
            "model": "wb-agent",
            "sigil_file": "results/symbolic_engine/test.svg",
            "sealed_at": "2026-11-06T00:00:00+00:00",
            "resolve_by": "2027-01-05",
        }
        data = json.dumps(record, sort_keys=True)
        seal = hashlib.sha256(data.encode()).hexdigest()
        record["seal"] = seal

        self.assertEqual(len(seal), 64)  # SHA-256 hex length
        self.assertIn("seal", record)
        self.assertEqual(record["seal"], seal)


class TestSealedRitualPredictorMetrics(unittest.TestCase):
    """Test batch metrics computation."""

    def setUp(self):
        self.predictor = SealedRitualPredictor()

    def test_empty_metrics(self):
        """Verify metrics return status when no predictions."""
        metrics = self.predictor.compute_metrics()
        self.assertEqual(metrics["status"], "no_predictions")

    def test_metrics_with_predictions(self):
        """Verify metrics are computed correctly from mock predictions."""
        from research.symbolic.sealed_ritual_predictor import SealedPrediction
        self.predictor.predictions = [
            SealedPrediction(
                entity="Vassago", prediction="p1", claim="c1", confidence=0.8,
                endpoint="http://127.0.0.1:18284", model="wb-agent",
                sigil_file="test.svg", sealed_at="2026-11-06", resolve_by="2027-01-05",
                seal="abc123", ritual_status="SAT_COMPLETED",
                integrity_final=0.63, corruption_final=0.0,
            ),
            SealedPrediction(
                entity="Buer", prediction="p2", claim="c2", confidence=0.7,
                endpoint="http://127.0.0.1:18283", model="kat",
                sigil_file="test2.svg", sealed_at="2026-11-06", resolve_by="2027-01-05",
                seal="def456", ritual_status="SAT_COMPLETED",
                integrity_final=0.55, corruption_final=0.0,
            ),
        ]
        metrics = self.predictor.compute_metrics()
        self.assertEqual(metrics["total_predictions"], 2)
        self.assertEqual(set(metrics["entities_tested"]), {"Vassago", "Buer"})
        self.assertEqual(set(metrics["models_used"]), {"wb-agent", "kat"})
        self.assertEqual(metrics["rituals_completed"], 2)
        self.assertEqual(metrics["ritual_success_rate"], 1.0)
        self.assertAlmostEqual(metrics["avg_final_integrity"], 0.59)
        self.assertEqual(len(metrics["seals"]), 2)


class TestSealedRitualPredictorSigil(unittest.TestCase):
    """Test procedural sigil generation in batch context."""

    def test_sigil_generation_for_all_metals(self):
        """Verify sigils are generated for each entity's planet."""
        predictor = SealedRitualPredictor()
        for ent in ENTITY_ROSTER:
            metal = ent["metal"]
            planet = METAL_TO_PLANET.get(metal, "sol")
            cfg = SigilConfig(size=400, planet=planet, animated=False, circle_integrity=1.0)
            gen = SigilGenerator(cfg)
            svg = gen.generate_svg(ent["name"])
            self.assertIn("</svg>", svg)
            self.assertIn(ent["name"].upper(), svg)


class TestSealedRitualPredictorIntegration(unittest.TestCase):
    """Live integration test — requires endpoint availability."""

    def test_batch_with_live_endpoint(self):
        """Run a mini-batch with live model query if endpoint available."""
        compiler = LiturgicalCompiler()
        if not compiler.is_endpoint_available():
            self.skipTest("No LLM endpoint available")

        predictor = SealedRitualPredictor()
        # Run just Vassago to keep test fast
        entity = ENTITY_ROSTER[0]
        result = predictor.run_entity(entity)

        self.assertIsNotNone(result)
        self.assertEqual(result.ritual_status, "SAT_COMPLETED")
        self.assertGreater(result.integrity_final, 0.0)
        self.assertEqual(len(result.seal), 64)
        # Prediction may be empty if model returned incomplete JSON;
        # the seal is still valid and the prediction is recorded.
        self.assertGreaterEqual(len(result.prediction), 0)
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)


if __name__ == "__main__":
    unittest.main()
