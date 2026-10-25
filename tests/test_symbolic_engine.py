"""
Verification Test Suite for Symbolic Engine (Procedural Sigils, Ritual State Machine, Corpus Graph)
"""

import sys
import unittest
from pathlib import Path

wb_dir = Path(__file__).parent.parent
sys.path.insert(0, str(wb_dir))

from symbolic_engine import (
    SigilGenerator, SigilConfig,
    RitualEngine, RitualSchema, RitualStep,
    GoeticCorpus, EntityRecord
)
from symbolic_engine.ritual_engine import StepType, WorldState, FailureMode


class TestSigilGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = SigilGenerator(SigilConfig(size=400, polygon_points=6))

    def test_svg_generation_valid_xml(self):
        """Verify SVG contains valid tags, viewBox, circles, and closing tag."""
        svg = self.generator.generate_svg("Bael")
        self.assertIn('<svg xmlns="http://www.w3.org/2000/svg"', svg)
        self.assertIn('viewBox="0 0 400 400"', svg)
        self.assertIn('BAEL', svg)
        self.assertIn('</svg>', svg)

    def test_deterministic_seed(self):
        """Verify same name produces identical SVG output."""
        svg1 = self.generator.generate_svg("Paimon", seed=42)
        svg2 = self.generator.generate_svg("Paimon", seed=42)
        self.assertEqual(svg1, svg2)

    def test_save_svg(self, tmp_path_factory=None):
        """Verify saving SVG to file."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            p = Path(f.name)
        out = self.generator.save_svg("Marbas", p)
        self.assertTrue(out.exists())
        self.assertGreater(out.stat().st_size, 200)
        p.unlink()


class TestRitualEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RitualEngine()

    def test_valid_ritual_execution(self):
        """Verify valid ritual executes all steps and transitions world state."""
        schema = RitualSchema(
            ritual_id="rit_buer_healing",
            name="Invocation of Buer",
            target_entity="Buer",
            required_items={"brass_vessel", "laurel_leaves", "consecrated_chalk"},
            allowed_temporal_hours={"day", "twilight"},
            steps=[
                RitualStep("s1", StepType.PURIFICATION, "Ablution and circle casting"),
                RitualStep("s2", StepType.INSCRIPTION, "Inscribing seal of Buer", target_inscription="seal_buer"),
                RitualStep("s3", StepType.INVOCATION, "Reciting formula of Buer", integrity_cost=0.1),
            ],
            min_circle_integrity=0.5,
        )
        init_state = WorldState(
            circle_integrity=1.0,
            temporal_hour="day",
            inventory={"brass_vessel", "laurel_leaves", "consecrated_chalk"},
        )
        result = self.engine.validate_and_execute(schema, init_state)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.status, "SAT_COMPLETED")
        self.assertEqual(result.executed_steps, 3)
        self.assertIn("Buer", result.final_world_state.bound_entities)
        self.assertIn("seal_buer", result.final_world_state.active_inscriptions)

    def test_missing_precondition_rejected(self):
        """Verify missing ritual item triggers UNSAT_PRECONDITIONS."""
        schema = RitualSchema(
            ritual_id="rit_paimon",
            name="Invocation of Paimon",
            target_entity="Paimon",
            required_items={"gold_lamen", "silver_bell"},
            allowed_temporal_hours={"day"},
            steps=[RitualStep("s1", StepType.INVOCATION, "Call Paimon")],
        )
        # Inventory lacks silver_bell
        state = WorldState(inventory={"gold_lamen"}, temporal_hour="day")
        res = self.engine.validate_and_execute(schema, state)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.failure_mode, FailureMode.PRECONDITION_UNMET)
        self.assertTrue(any("silver_bell" in e for e in res.errors))

    def test_containment_breach_detection(self):
        """Verify circle integrity drop below threshold triggers CONTAINMENT_BREACH."""
        schema = RitualSchema(
            ritual_id="rit_asmoday_perilous",
            name="Dangerous Evocation",
            target_entity="Asmoday",
            required_items={"obsidian_mirror"},
            allowed_temporal_hours={"night"},
            min_circle_integrity=0.6,
            steps=[
                RitualStep("s1", StepType.INVOCATION, "High-stress invocation", integrity_cost=0.5),
            ],
        )
        # Starting with 0.8 integrity; 0.8 - 0.5 = 0.3 < 0.6 threshold
        state = WorldState(circle_integrity=0.8, inventory={"obsidian_mirror"}, temporal_hour="night")
        res = self.engine.validate_and_execute(schema, state)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "CONTAINMENT_BREACH")
        self.assertEqual(res.failure_mode, FailureMode.INVARIANT_BREACH)


class TestGoeticCorpus(unittest.TestCase):
    def setUp(self):
        self.corpus = GoeticCorpus()

    def test_get_by_name(self):
        """Verify entity lookup by name."""
        entity = self.corpus.get_by_name("Bael")
        self.assertIsNotNone(entity)
        self.assertEqual(entity.rank, "King")
        self.assertEqual(entity.metal, "Gold")

    def test_filter_by_domain(self):
        """Verify domain querying returns matching entities."""
        healing_spirits = self.corpus.filter_by_domain("healing")
        names = [e.name for e in healing_spirits]
        self.assertIn("Marbas", names)
        self.assertIn("Buer", names)

    def test_filter_by_rank(self):
        """Verify filtering entities by rank."""
        kings = self.corpus.filter_by_rank("King")
        self.assertGreaterEqual(len(kings), 4)
        for k in kings:
            self.assertEqual(k.metal, "Gold")

    def test_knowledge_graph_structure(self):
        """Verify network graph generation has nodes and links."""
        graph = self.corpus.to_network_graph()
        self.assertIn("nodes", graph)
        self.assertIn("links", graph)
        self.assertEqual(len(graph["nodes"]), 72)
        self.assertGreater(len(graph["links"]), 100)

    def test_complete_72_corpus_taxonomies(self):
        """Verify all 72 entities and the 7 classical planetary metals."""
        self.assertEqual(len(self.corpus.records), 72)
        # Verify Knight rank and Lead metal
        furcas = self.corpus.get_by_name("Furcas")
        self.assertIsNotNone(furcas)
        self.assertEqual(furcas.rank, "Knight")
        self.assertEqual(furcas.metal, "Lead")

        # Verify all 7 metals exist in corpus
        metals = {r.metal for r in self.corpus.records}
        self.assertEqual(metals, {"Gold", "Copper", "Tin", "Silver", "Iron", "Mercury", "Lead"})

        # Verify spirit 72
        andromalius = self.corpus.get_by_number(72)
        self.assertIsNotNone(andromalius)
        self.assertEqual(andromalius.name, "Andromalius")


if __name__ == '__main__':
    unittest.main()
