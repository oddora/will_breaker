"""
Verification Suite for Animated Sigil Enhancements & Interactive Ritual Simulator
"""

import sys
import unittest
import tempfile
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from symbolic_engine import (
    SigilGenerator,
    SigilConfig,
    PLANETARY_MATRICES,
    InteractiveRitualSimulator,
    ActionOutcome,
    StepType,
)


class TestAnimatedAndPlanetarySigils(unittest.TestCase):
    def test_planetary_matrix_presets(self):
        """Verify planetary presets apply correct sacred geometry and hues."""
        gen = SigilGenerator(SigilConfig(planet="mars"))
        svg_mars = gen.generate_svg("Bael")
        self.assertIn("#e74c3c", svg_mars)  # Mars red

        gen_sol = SigilGenerator(SigilConfig(planet="sol"))
        svg_sol = gen_sol.generate_svg("Paimon")
        self.assertIn("#f1c40f", svg_sol)  # Solar gold

    def test_animated_svg_elements(self):
        """Verify animated=True injects rotation and breathing glow tags."""
        gen = SigilGenerator(SigilConfig(animated=True))
        svg = gen.generate_svg("Agares")
        self.assertIn("<animateTransform", svg)
        self.assertIn('type="rotate"', svg)
        self.assertIn("<animate attributeName=", svg)

    def test_integrity_degradation_strain_overlay(self):
        """Verify integrity < 1.0 renders containment strain fissures and HUD."""
        gen_clean = SigilGenerator(SigilConfig(circle_integrity=1.0))
        svg_clean = gen_clean.generate_svg("Buer")
        self.assertNotIn("Containment Strain Overlay", svg_clean)

        gen_strained = SigilGenerator(SigilConfig(circle_integrity=0.6))
        svg_strained = gen_strained.generate_svg("Buer")
        self.assertIn("Containment Strain Overlay", svg_strained)
        self.assertIn("INTEGRITY: 60%", svg_strained)

        # Critical collapse (< 0.5)
        gen_breached = SigilGenerator(SigilConfig(circle_integrity=0.35))
        svg_breached = gen_breached.generate_svg("Buer")
        self.assertIn("#e74c3c", svg_breached)  # Critical red outer stroke


class TestInteractiveRitualSimulator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sim = InteractiveRitualSimulator(
            target_entity_name="Paimon",
            output_dir=Path(self.temp_dir.name),
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initial_simulation_state(self):
        """Verify initial session setup matches King Paimon and Solomonic correspondences."""
        self.assertEqual(self.sim.entity.name, "Paimon")
        self.assertEqual(self.sim.planet, "sol")
        self.assertEqual(self.sim.world_state.circle_integrity, 1.0)
        self.assertTrue(self.sim.is_active)
        self.assertFalse(self.sim.is_breached)
        self.assertIn("gold_lamen", self.sim.world_state.inventory)
        self.assertIn("salt", self.sim.world_state.inventory)

    def test_turn_by_turn_step_advancement(self):
        """Verify advancing steps updates integrity, inscriptions, and step progression."""
        # Step 1: Purification
        o1 = self.sim.advance_liturgical_step()
        self.assertTrue(o1.success)
        self.assertEqual(self.sim.current_step_index, 1)

        # Step 2: Inscription
        o2 = self.sim.advance_liturgical_step()
        self.assertTrue(o2.success)
        self.assertIn("seal_paimon", self.sim.world_state.active_inscriptions)

        # Step 3: Offering
        o3 = self.sim.advance_liturgical_step()
        self.assertTrue(o3.success)

        # Step 4: Invocation (High stress)
        o4 = self.sim.advance_liturgical_step()
        self.assertTrue(o4.success)
        self.assertLess(self.sim.world_state.circle_integrity, 0.9)

    def test_emergency_banishing_reinforces_integrity(self):
        """Verify emergency banishing consumes salt/chalk and restores integrity."""
        # Intentionally lower integrity
        self.sim.world_state.circle_integrity = 0.65
        o_banish = self.sim.emergency_banish()

        self.assertTrue(o_banish.success)
        self.assertIn("salt", o_banish.items_consumed)
        self.assertEqual(self.sim.world_state.circle_integrity, 0.90)  # 0.65 + 0.25 = 0.90
        self.assertNotIn("salt", self.sim.world_state.inventory)

    def test_offering_incense_buffs_next_step(self):
        """Verify offering additional incense halves integrity decay on next invocation."""
        o_buff = self.sim.offer_additional_incense()
        self.assertTrue(o_buff.success)
        self.assertTrue(self.sim.offering_buff_active)

        # Advance through steps to invocation
        self.sim.advance_liturgical_step()  # step 1
        self.sim.advance_liturgical_step()  # step 2
        self.sim.advance_liturgical_step()  # step 3
        
        # Next is invocation (base cost 0.22, buffered to 0.11)
        prev_int = self.sim.world_state.circle_integrity
        o_invoke = self.sim.advance_liturgical_step()
        self.assertTrue(o_invoke.success)
        # Expected drop: ~0.11 instead of 0.22
        expected_drop = 0.22 * 0.5
        self.assertAlmostEqual(prev_int - self.sim.world_state.circle_integrity, expected_drop, places=2)

    def test_early_abort_dismissal(self):
        """Verify early abort cleanly dissolves containment."""
        o_abort = self.sim.abort_early_dismissal()
        self.assertTrue(o_abort.success)
        self.assertFalse(self.sim.is_active)
        self.assertIn("License to depart pronounced early", o_abort.message)


if __name__ == "__main__":
    unittest.main()
