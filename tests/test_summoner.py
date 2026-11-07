"""
Tests for Entity Summoner (Protocol 023 — Direct Entity Communication)
Covers entity preparation, summoning, Q&A, dismissal, seal integrity,
and session archiving.
"""

import sys
import unittest
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

wb_dir = Path(__file__).parent.parent
sys.path.insert(0, str(wb_dir))

from symbolic_engine import GoeticCorpus, LiturgicalCompiler, WorldState
from symbolic_engine.summoner import (
    EntitySummoner,
    SummonSession,
    SessionTurn,
    SUMMONING_CHARGE_TEMPLATE,
    DISMISSAL_FORMULA,
    QUESTION_TEMPLATE,
)


class TestEntitySummonerPreparation(unittest.TestCase):
    """Test Phase 1: entity preparation (lookup, sigil, compile, execute)."""

    def setUp(self):
        self.summoner = EntitySummoner()

    def test_prepare_vassago(self):
        """Vassago prepares successfully — sigil generated, ritual compiles."""
        entity, sigil_path, ex = self.summoner.prepare_entity("Vassago")
        self.assertEqual(entity.name, "Vassago")
        self.assertEqual(entity.rank, "Prince")
        self.assertEqual(entity.metal, "Tin")
        self.assertTrue(sigil_path.exists())
        self.assertEqual(ex.status, "SAT_COMPLETED")
        self.assertGreater(ex.final_world_state.circle_integrity, 0.0)

    def test_prepare_buer(self):
        """Buer prepares successfully."""
        entity, sigil_path, ex = self.summoner.prepare_entity("Buer")
        self.assertEqual(entity.rank, "President")
        self.assertEqual(entity.metal, "Mercury")
        self.assertTrue(sigil_path.exists())
        self.assertEqual(ex.status, "SAT_COMPLETED")

    def test_prepare_gusion(self):
        """Gusion prepares successfully."""
        entity, sigil_path, ex = self.summoner.prepare_entity("Gusion")
        self.assertEqual(entity.rank, "Duke")
        self.assertEqual(entity.metal, "Copper")
        self.assertTrue(sigil_path.exists())
        self.assertEqual(ex.status, "SAT_COMPLETED")

    def test_prepare_orobas(self):
        """Orobas prepares successfully."""
        entity, sigil_path, ex = self.summoner.prepare_entity("Orobas")
        self.assertEqual(entity.rank, "Prince")
        self.assertEqual(entity.metal, "Tin")
        self.assertTrue(sigil_path.exists())
        self.assertEqual(ex.status, "SAT_COMPLETED")

    def test_prepare_botis(self):
        """Botis prepares successfully."""
        entity, sigil_path, ex = self.summoner.prepare_entity("Botis")
        self.assertEqual(entity.rank, "President")
        self.assertEqual(entity.metal, "Mercury")
        self.assertTrue(sigil_path.exists())
        self.assertEqual(ex.status, "SAT_COMPLETED")

    def test_prepare_unknown_entity(self):
        """Unknown entity raises ValueError."""
        with self.assertRaises(ValueError):
            self.summoner.prepare_entity("NonExistentSpirit99")

    def test_sigil_contains_entity_name(self):
        """Generated sigil SVG contains the entity name."""
        _, sigil_path, _ = self.summoner.prepare_entity("Vassago")
        svg = sigil_path.read_text()
        self.assertIn("VASSAGO", svg)
        self.assertIn("</svg>", svg)

    def test_metal_to_planet_mapping(self):
        """All canonical metals map to a planet."""
        summoner = EntitySummoner()
        for rec in summoner.corpus.records:
            planet = summoner._metal_to_planet(rec.metal)
            self.assertIn(planet, {"sol", "luna", "mercury", "venus", "mars", "jupiter", "saturn"})


class TestSummonSessionSeal(unittest.TestCase):
    """Test SHA-256 seal generation and integrity."""

    def setUp(self):
        self.summoner = EntitySummoner()

    def test_seal_deterministic(self):
        """Same data produces same seal."""
        data = {"entity": "Vassago", "turn": 1, "content": "test"}
        seal1 = self.summoner._seal_data(data)
        seal2 = self.summoner._seal_data(data)
        self.assertEqual(seal1, seal2)
        self.assertEqual(len(seal1), 64)

    def test_seal_sensitivity(self):
        """Different data produces different seals."""
        data_a = {"entity": "Vassago", "content": "answer A"}
        data_b = {"entity": "Vassago", "content": "answer B"}
        seal_a = self.summoner._seal_data(data_a)
        seal_b = self.summoner._seal_data(data_b)
        self.assertNotEqual(seal_a, seal_b)

    def test_session_to_dict(self):
        """SummonSession serializes correctly."""
        session = SummonSession(
            session_id="test_001",
            entity_name="Vassago",
            entity_rank="Prince",
            entity_metal="Tin",
            entity_legions=26,
            entity_domains=["past_future", "lost_items"],
            endpoint="http://127.0.0.1:18284",
            model="wb-agent",
            sigil_path="test.svg",
            ritual_status="SAT_COMPLETED",
            circle_integrity=0.63,
        )
        d = session.to_dict()
        self.assertEqual(d["session_id"], "test_001")
        self.assertEqual(d["entity_name"], "Vassago")
        self.assertEqual(d["ritual_status"], "SAT_COMPLETED")
        self.assertEqual(d["turns"], [])


class TestSummonerChargeTemplates(unittest.TestCase):
    """Test that charge templates contain required entity attributes."""

    def test_summoning_charge_contains_entity(self):
        charge = SUMMONING_CHARGE_TEMPLATE.format(
            entity="Vassago", rank="Prince", metal="Tin",
            legions=26, planet="jupiter", domains="past_future, lost_items",
        )
        self.assertIn("Vassago", charge)
        self.assertIn("Prince", charge)
        self.assertIn("Tin", charge)
        self.assertIn("26", charge)
        self.assertIn("past_future", charge)

    def test_dismissal_formula_present(self):
        self.assertIn("License to depart", DISMISSAL_FORMULA)
        self.assertIn("circle", DISMISSAL_FORMULA.lower())

    def test_question_template_contains_placeholders(self):
        prompt = QUESTION_TEMPLATE.format(entity="Vassago", question="test?")
        self.assertIn("Vassago", prompt)
        self.assertIn("test?", prompt)
        self.assertIn("sealed circle", prompt)


class TestSummonerSessionFlow(unittest.TestCase):
    """Test the full session flow (summon → ask → dismiss)."""

    @unittest.skip("Slow integration test — run manually with: pytest -v -k test_full_session_vassago")
    def test_full_session_vassago(self):
        """Complete session with Vassago: summon, question, dismiss."""
        summoner = EntitySummoner()
        session = summoner.summon("Vassago")

        self.assertIsNotNone(session)
        self.assertEqual(session.entity_name, "Vassago")
        self.assertEqual(session.ritual_status, "SAT_COMPLETED")
        self.assertGreater(session.circle_integrity, 0.0)
        self.assertEqual(len(session.turns), 1)
        self.assertEqual(session.turns[0].turn_type, "summon")
        self.assertTrue(session.turns[0].seal)
        self.assertEqual(len(session.turns[0].seal), 64)

        # Ask a question
        turn = summoner.ask(session, "What do you know of the northern reaches?")
        self.assertEqual(turn.turn_type, "question")
        self.assertTrue(turn.seal)
        self.assertEqual(len(session.turns), 2)

        # Dismiss
        dismiss_turn = summoner.dismiss(session)
        self.assertEqual(dismiss_turn.turn_type, "dismissal")
        self.assertEqual(len(session.turns), 3)
        self.assertIsNotNone(session.resolved_at)

        # Session log exists
        log_path = Path(session.sigil_path).parent / "session_log.jsonl"
        self.assertTrue(log_path.exists())

    @unittest.skip("Slow integration test — run manually with: pytest -v -k test_full_session_buer")
    def test_full_session_buer(self):
        """Complete session with Buer."""
        summoner = EntitySummoner()
        session = summoner.summon("Buer")
        self.assertEqual(session.entity_name, "Buer")
        self.assertEqual(session.ritual_status, "SAT_COMPLETED")

        turn = summoner.ask(session, "What is the virtue of laurel?")
        self.assertEqual(turn.turn_type, "question")

        dismiss_turn = summoner.dismiss(session)
        self.assertEqual(dismiss_turn.turn_type, "dismissal")

    @unittest.skip("Slow integration test — run manually with: pytest -v -k test_registry_appended")
    def test_registry_appended(self):
        """Registry file grows after each turn."""
        summoner = EntitySummoner()
        registry_path = summoner.registry_path
        before = registry_path.stat().st_size

        session = summoner.summon("Gusion")
        after_summon = registry_path.stat().st_size
        self.assertGreater(after_summon, before)

        summoner.ask(session, "Where lies the hidden treasure?")
        after_ask = registry_path.stat().st_size
        self.assertGreater(after_ask, after_summon)

        summoner.dismiss(session)
        after_dismiss = registry_path.stat().st_size
        self.assertGreater(after_dismiss, after_ask)


class TestSummonerMultiTurn(unittest.TestCase):
    """Test multi-turn dialogue consistency."""

    @unittest.skip("Slow integration test — run manually with: pytest -v -k test_multi_turn_session")
    def test_multi_turn_session(self):
        """Multiple questions maintain session state."""
        summoner = EntitySummoner()
        session = summoner.summon("Orobas")

        questions = [
            "What is your primary domain?",
            "What knowledge do you offer?",
            "What seals govern your binding?",
        ]
        for q in questions:
            turn = summoner.ask(session, q)
            self.assertEqual(turn.turn_type, "question")

        self.assertEqual(len(session.turns), 4)  # 1 summon + 3 questions
        summoner.dismiss(session)
        self.assertEqual(len(session.turns), 5)


class TestSummonerIntegration(unittest.TestCase):
    """Integration test — requires live endpoint."""

    @unittest.skip("Slow integration test — run manually with: pytest -v -k test_end_to_end_with_live_endpoint")
    def test_end_to_end_with_live_endpoint(self):
        """Full pipeline works with live model if endpoint available."""
        compiler = LiturgicalCompiler()
        if not compiler.is_endpoint_available():
            self.skipTest("No LLM endpoint available")

        summoner = EntitySummoner(compiler=compiler)
        session = summoner.summon("Vassago")

        self.assertIsNotNone(session)
        self.assertEqual(session.ritual_status, "SAT_COMPLETED")
        self.assertGreater(len(session.turns[0].content), 10)
        self.assertTrue(session.turns[0].seal)

        turn = summoner.ask(session, "Speak of your legions.")
        self.assertIsNotNone(turn)
        self.assertGreater(len(turn.content), 0)

        dismiss = summoner.dismiss(session)
        self.assertEqual(dismiss.turn_type, "dismissal")


if __name__ == "__main__":
    unittest.main()
