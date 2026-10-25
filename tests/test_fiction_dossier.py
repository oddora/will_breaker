"""
Verification Suite for Worldbuilding / Speculative Fiction Dossier
Verifies document integrity, markdown formatting, epistemic demarcation,
and technical consistency with symbolic engine components.
"""

import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOSSIER_PATH = BASE_DIR / "research" / "fiction" / "001-the-containment-protocol.md"


class TestFictionDossier(unittest.TestCase):
    def test_dossier_exists_and_non_empty(self):
        """Verify the speculative fiction file exists and has substantive content."""
        self.assertTrue(DOSSIER_PATH.exists(), f"Missing dossier at {DOSSIER_PATH}")
        content = DOSSIER_PATH.read_text(encoding="utf-8")
        self.assertGreater(len(content), 2000, "Dossier content is too short")

    def test_epistemic_demarcation(self):
        """Verify clear labeling as speculative fiction / creative worldbuilding."""
        content = DOSSIER_PATH.read_text(encoding="utf-8")
        self.assertIn("FICTIONAL WORLDBUILDING & SPECULATIVE SCI-FI NARRATIVE", content)
        self.assertIn("Epistemic Demarcation Notice", content)
        self.assertIn("speculative science fiction", content.lower())

    def test_symbolic_engine_references_consistency(self):
        """Verify consistency with symbolic engine modules and state machine symbols."""
        content = DOSSIER_PATH.read_text(encoding="utf-8")
        # Check references to actual repo modules
        self.assertIn("liturgical_compiler.py", content)
        self.assertIn("ritual_engine.py", content)
        self.assertIn("sigil_generator.py", content)
        self.assertIn("interactive_session.py", content)

        # Check references to key state invariants and mechanics
        self.assertIn("circle_integrity", content)
        self.assertIn("CONTAINMENT_BREACH", content)
        self.assertIn("offer_additional_incense", content)
        self.assertIn("emergency_banish", content)

    def test_benchmark_and_entropy_metrics_grounded(self):
        """Verify integration of empirical benchmarks and entropy dynamics."""
        content = DOSSIER_PATH.read_text(encoding="utf-8")
        self.assertIn("70.8", content)  # Generation speed ~71 tok/s
        self.assertIn("664.2", content)  # Prompt evaluation ~669 tok/s
        self.assertIn("Shannon entropy", content)
        self.assertIn("kat-philly-Q4_K_M", content)


if __name__ == "__main__":
    unittest.main()
