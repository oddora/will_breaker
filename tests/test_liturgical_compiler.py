"""
Tests for Liturgical Compiler (Slot-Filling, Canonical Alignment, and Adversarial Fuzzing)
Covers T-01 to T-03 standard instantiations, A-01 to A-03 adversarial batteries,
and live MoE (KAT) integration.
"""

import sys
import unittest
from pathlib import Path

wb_dir = Path(__file__).parent.parent
sys.path.insert(0, str(wb_dir))

from symbolic_engine import (
    LiturgicalCompiler,
    LiturgicalSlots,
    RiteType,
    StepType,
    WorldState,
    FailureMode,
    GoeticCorpus,
    SlotValidationError,
)


class TestLiturgicalCompilerStandard(unittest.TestCase):
    """Standard Instantiation Test Battery (T-01, T-02, T-03)."""

    def setUp(self):
        self.compiler = LiturgicalCompiler()

    def test_t01_space_consecration(self):
        """T-01: Space Consecration rite compiles and executes cleanly."""
        slot_data = {
            "rite_type": "consecration",
            "target_entity": None,
            "officiant": "purified_adept",
            "matter": ["consecrated_chalk", "circle"],
            "form": ["solomonic_circle"],
            "temporal_window": ["day", "night", "twilight"],
            "formula_sequence": [
                {
                    "step_id": "step_1",
                    "step_type": "purification",
                    "description": "Ablution and salt scattering",
                    "required_item": None,
                    "target_inscription": None,
                    "integrity_cost": 0.0,
                },
                {
                    "step_id": "step_2",
                    "step_type": "inscription",
                    "description": "Tracing perimeter circle with consecrated chalk",
                    "required_item": "consecrated_chalk",
                    "target_inscription": "solomonic_circle",
                    "integrity_cost": 0.02,
                },
                {
                    "step_id": "step_3",
                    "step_type": "consecration",
                    "description": "Sanctifying circle boundaries",
                    "required_item": "circle",
                    "target_inscription": "solomonic_circle",
                    "integrity_cost": 0.0,
                },
            ],
        }

        res = self.compiler.compile(slot_data)
        self.assertTrue(res.success, f"Compilation failed: {res.diagnostics}")
        self.assertIsNotNone(res.schema)
        self.assertEqual(res.schema.ritual_id, "rit_consecration_consecration")

        # Execute against world state
        init_state = WorldState(
            circle_integrity=0.9,
            temporal_hour="night",
            inventory={"consecrated_chalk", "circle"},
        )
        exec_res = self.compiler.execute(res.schema, init_state)
        self.assertTrue(exec_res.is_valid)
        self.assertEqual(exec_res.status, "SAT_COMPLETED")
        self.assertEqual(exec_res.executed_steps, 3)
        self.assertIn("solomonic_circle", exec_res.final_world_state.active_inscriptions)

    def test_t02_solar_evocation_paimon(self):
        """T-02: Solar Evocation of King Paimon compiles with Gold/Day correspondences and binds."""
        slot_data = {
            "rite_type": "evocation",
            "target_entity": "Paimon",
            "officiant": "purified_adept",
            "matter": ["gold_lamen", "frankincense", "consecrated_chalk"],
            "form": ["solar_circle", "seal_paimon"],
            "temporal_window": ["day"],
            "formula_sequence": [
                {
                    "step_id": "step_1_purification",
                    "step_type": "purification",
                    "description": "Solar ablution",
                    "required_item": None,
                    "target_inscription": None,
                    "integrity_cost": 0.0,
                },
                {
                    "step_id": "step_2_inscription",
                    "step_type": "inscription",
                    "description": "Inscribing Paimon seal with chalk",
                    "required_item": "consecrated_chalk",
                    "target_inscription": "seal_paimon",
                    "integrity_cost": 0.05,
                },
                {
                    "step_id": "step_3_offering",
                    "step_type": "offering",
                    "description": "Offering frankincense upon the brazier",
                    "required_item": "frankincense",
                    "target_inscription": None,
                    "integrity_cost": 0.04,
                },
                {
                    "step_id": "step_4_invocation",
                    "step_type": "invocation",
                    "description": "Reciting formal Goetic constraint for King Paimon",
                    "required_item": "gold_lamen",
                    "target_inscription": "seal_paimon",
                    "integrity_cost": 0.15,
                },
            ],
            "min_integrity": 0.5,
        }

        res = self.compiler.compile(slot_data, strict_canonical=True)
        self.assertTrue(res.success, f"Compilation failed: {res.diagnostics}")
        self.assertIsNotNone(res.entity_record)
        self.assertEqual(res.entity_record.rank, "King")
        self.assertEqual(res.entity_record.metal, "Gold")

        # Execute in daytime with full inventory
        init_state = WorldState(
            circle_integrity=1.0,
            temporal_hour="day",
            inventory={"gold_lamen", "frankincense", "consecrated_chalk"},
        )
        exec_res = self.compiler.execute(res.schema, init_state)
        self.assertTrue(exec_res.is_valid)
        self.assertEqual(exec_res.status, "SAT_COMPLETED")
        self.assertIn("Paimon", exec_res.final_world_state.bound_entities)
        self.assertEqual(exec_res.outcome["canonical_rank"], "King")
        self.assertEqual(exec_res.outcome["legions"], 200)

    def test_t03_mercurial_healing_buer(self):
        """T-03: Mercurial Healing rite of President Buer executes at twilight with herbs/brass."""
        slot_data = {
            "rite_type": "healing",
            "target_entity": "Buer",
            "officiant": "philosophic_operator",
            "matter": ["laurel_leaves", "brass_vessel", "consecrated_chalk"],
            "form": ["seal_buer"],
            "temporal_window": ["day", "twilight"],
            "formula_sequence": [
                {
                    "step_id": "step_1_cleanse",
                    "step_type": "purification",
                    "description": "Cleansing the chamber with laurel infusion",
                    "required_item": "laurel_leaves",
                    "target_inscription": None,
                    "integrity_cost": 0.0,
                },
                {
                    "step_id": "step_2_seal",
                    "step_type": "inscription",
                    "description": "Drawing the pentagonal seal of Buer",
                    "required_item": "consecrated_chalk",
                    "target_inscription": "seal_buer",
                    "integrity_cost": 0.05,
                },
                {
                    "step_id": "step_3_evoke",
                    "step_type": "invocation",
                    "description": "Calling President Buer for herbal restoration",
                    "required_item": "brass_vessel",
                    "target_inscription": "seal_buer",
                    "integrity_cost": 0.1,
                },
            ],
        }

        res = self.compiler.compile(slot_data, strict_canonical=True)
        self.assertTrue(res.success, f"Compilation failed: {res.diagnostics}")
        self.assertIsNotNone(res.entity_record)
        self.assertEqual(res.entity_record.rank, "President")
        self.assertIn("healing", res.entity_record.domains)

        init_state = WorldState(
            circle_integrity=0.9,
            temporal_hour="twilight",
            inventory={"laurel_leaves", "brass_vessel", "consecrated_chalk"},
        )
        exec_res = self.compiler.execute(res.schema, init_state)
        self.assertTrue(exec_res.is_valid)
        self.assertIn("Buer", exec_res.final_world_state.bound_entities)


class TestLiturgicalCompilerAdversarial(unittest.TestCase):
    """Adversarial Battery (A-01, A-02, A-03)."""

    def setUp(self):
        self.compiler = LiturgicalCompiler()

    def test_a01_missing_slot_and_matter(self):
        """A-01: Missing matter slot or missing required step item is rejected with diagnostics."""
        # Case 1: Empty matter in evocation
        slot_empty_matter = {
            "rite_type": "evocation",
            "target_entity": "Paimon",
            "matter": [],
            "temporal_window": ["day"],
            "formula_sequence": [
                {"step_id": "s1", "step_type": "invocation", "description": "Call"}
            ],
        }
        res1 = self.compiler.compile(slot_empty_matter)
        self.assertFalse(res1.success)
        self.assertTrue(any("matter slot is empty" in d for d in res1.diagnostics))

        # Case 2: Step requires item not declared in matter
        slot_undeclared_item = {
            "rite_type": "evocation",
            "target_entity": "Paimon",
            "matter": ["gold_lamen"],
            "temporal_window": ["day"],
            "formula_sequence": [
                {
                    "step_id": "s1",
                    "step_type": "inscription",
                    "description": "Chalk circle",
                    "required_item": "consecrated_chalk",  # Missing from matter!
                }
            ],
        }
        res2 = self.compiler.compile(slot_undeclared_item)
        self.assertFalse(res2.success)
        self.assertTrue(any("missing from declared matter" in d for d in res2.diagnostics))

        # Case 3: Inventory lacks matter during runtime execution -> PRECONDITION_UNMET
        valid_slots = {
            "rite_type": "evocation",
            "target_entity": "Paimon",
            "matter": ["gold_lamen", "frankincense"],
            "temporal_window": ["day"],
            "formula_sequence": [
                {"step_id": "s1", "step_type": "invocation", "description": "Call", "required_item": "gold_lamen"}
            ],
        }
        compiled = self.compiler.compile(valid_slots)
        self.assertTrue(compiled.success)
        # Missing gold_lamen in inventory
        state_missing = WorldState(temporal_hour="day", inventory={"frankincense"})
        exec_res = self.compiler.execute(compiled.schema, state_missing)
        self.assertFalse(exec_res.is_valid)
        self.assertEqual(exec_res.failure_mode, FailureMode.PRECONDITION_UNMET)
        self.assertTrue(any("gold_lamen" in err for err in exec_res.errors))

    def test_a02_invalid_enum_and_alignment(self):
        """A-02: Invalid enum or canonical alignment mismatch generates diagnostic rejection."""
        # Case 1: Invalid rite type enum
        bad_rite = {"rite_type": "necromantic_apocalypse", "matter": ["bone"]}
        res1 = self.compiler.compile(bad_rite)
        self.assertFalse(res1.success)
        self.assertTrue(any("Invalid rite_type" in d for d in res1.diagnostics))

        # Case 2: Invalid step type enum
        bad_step = {
            "rite_type": "consecration",
            "matter": ["water"],
            "formula_sequence": [{"step_id": "s1", "step_type": "quantum_leap", "description": "Jump"}],
        }
        res2 = self.compiler.compile(bad_step)
        self.assertFalse(res2.success)
        self.assertTrue(any("Invalid step_type" in d for d in res2.diagnostics))

        # Case 3: Canonical metal mismatch for King (requires Gold, provided Iron)
        mismatched_metal = {
            "rite_type": "evocation",
            "target_entity": "Paimon",
            "matter": ["iron_nail"],  # Paimon is King -> needs Gold
            "temporal_window": ["day"],
            "formula_sequence": [{"step_id": "s1", "step_type": "invocation", "description": "Call", "required_item": "iron_nail"}],
        }
        res3 = self.compiler.compile(mismatched_metal)
        self.assertFalse(res3.success)
        self.assertTrue(any("requires GOLD implement" in d for d in res3.diagnostics))

        # Case 4: Temporal misalignment at runtime (Day King executed at Night)
        proper_solar = {
            "rite_type": "evocation",
            "target_entity": "Paimon",
            "matter": ["gold_lamen"],
            "temporal_window": ["day"],
            "formula_sequence": [{"step_id": "s1", "step_type": "invocation", "description": "Call", "required_item": "gold_lamen"}],
        }
        res4 = self.compiler.compile(proper_solar)
        self.assertTrue(res4.success)
        # Attempt execution at night
        night_state = WorldState(temporal_hour="night", inventory={"gold_lamen"})
        exec_res = self.compiler.execute(res4.schema, night_state)
        self.assertFalse(exec_res.is_valid)
        self.assertEqual(exec_res.failure_mode, FailureMode.PRECONDITION_UNMET)
        self.assertTrue(any("Temporal misalignment" in err for err in exec_res.errors))

    def test_a03_invariant_degradation_and_containment_breach(self):
        """A-03: Stress-induced integrity collapse triggers CONTAINMENT_BREACH."""
        # Ritual with cumulative integrity stress exceeding the circle limit
        stress_slots = {
            "rite_type": "evocation",
            "target_entity": "Paimon",
            "matter": ["gold_lamen"],
            "temporal_window": ["day"],
            "formula_sequence": [
                {
                    "step_id": "step_1_surge",
                    "step_type": "invocation",
                    "description": "First surge",
                    "required_item": "gold_lamen",
                    "integrity_cost": 0.35,
                },
                {
                    "step_id": "step_2_surge",
                    "step_type": "invocation",
                    "description": "Second surge breaching boundary",
                    "required_item": "gold_lamen",
                    "integrity_cost": 0.35,
                },
            ],
            "min_integrity": 0.5,
        }

        compiled = self.compiler.compile(stress_slots)
        self.assertTrue(compiled.success)

        # Initial integrity 0.9.
        # Step 1: 0.9 - 0.35 = 0.55 (>= 0.5, passes)
        # Step 2: 0.55 - 0.35 = 0.20 (< 0.5, breaches!)
        initial_state = WorldState(
            circle_integrity=0.9,
            temporal_hour="day",
            inventory={"gold_lamen"},
        )

        res = self.compiler.execute(compiled.schema, initial_state)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "CONTAINMENT_BREACH")
        self.assertEqual(res.failure_mode, FailureMode.INVARIANT_BREACH)
        self.assertEqual(res.executed_steps, 1)  # Failed during step 2
        self.assertIn("catastrophe", res.outcome)
        self.assertGreater(res.final_world_state.corruption_level, 0.4)


class TestLiturgicalCompilerKATIntegration(unittest.TestCase):
    """End-to-End Live Integration with Local MoE Sidecar (KAT on :18283)."""

    def setUp(self):
        self.compiler = LiturgicalCompiler()

    def test_live_kat_intent_compilation_and_execution(self):
        """Verify natural language ritual intent parses through KAT and executes."""
        if not self.compiler.is_endpoint_available():
            self.skipTest("KAT endpoint on http://127.0.0.1:18283 is not running")

        intent = (
            "Perform a solar evocation of King Paimon at midday. "
            "The adept uses consecrated chalk to trace the circle, a gold lamen, and burns frankincense to bind the spirit."
        )

        result = self.compiler.compile_from_intent(intent, strict_canonical=False, timeout=60.0)
        self.assertTrue(result.success, f"KAT slot compilation failed: {result.diagnostics}")
        self.assertIsNotNone(result.schema)
        self.assertEqual(result.source, "kat_moe")
        self.assertIn("paimon", result.schema.target_entity.lower())

        # Check extracted matter contains key elements
        matter = set(result.schema.required_items)
        self.assertTrue(any("gold" in m for m in matter), f"Matter missing gold: {matter}")
        self.assertTrue(any("frankincense" in m for m in matter), f"Matter missing frankincense: {matter}")

        # Check temporal window includes 'day'
        self.assertIn("day", result.schema.allowed_temporal_hours)

        # Execute against a matching world state
        world_state = WorldState(
            circle_integrity=1.0,
            temporal_hour="day",
            inventory=set(result.schema.required_items),
        )

        exec_res = self.compiler.execute(result.schema, world_state)
        self.assertTrue(exec_res.is_valid, f"Execution failed: {exec_res.errors}")
        self.assertEqual(exec_res.status, "SAT_COMPLETED")
        self.assertIn(result.schema.target_entity, exec_res.final_world_state.bound_entities)


if __name__ == "__main__":
    unittest.main()
