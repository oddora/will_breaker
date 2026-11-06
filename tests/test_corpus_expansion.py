"""
Tests for Corpus Expansion (Enochian, Qabalistic cross-system data)
"""

import json
import sys
import unittest
from pathlib import Path

wb_dir = Path(__file__).parent.parent
sys.path.insert(0, str(wb_dir))

from symbolic_engine.corpus_expansion import (
    ExpandedCorpus,
    ENOCHIAN_CATALOG,
    QABALISTIC_PATHS,
    EnochianEntity,
    QabalisticPath,
)
from symbolic_engine import GoeticCorpus


class TestEnochianCatalog(unittest.TestCase):
    """Verify Enochian catalog structure and completeness."""

    def test_catalog_type(self):
        """All catalog entries are EnochianEntity instances."""
        for entry in ENOCHIAN_CATALOG:
            self.assertIsInstance(entry, EnochianEntity)

    def test_catalog_nonempty(self):
        """Catalog has entries."""
        self.assertGreater(len(ENOCHIAN_CATALOG), 0)

    def test_required_fields_present(self):
        """Every entry has all required fields."""
        for entry in ENOCHIAN_CATALOG:
            self.assertTrue(bool(entry.name), "name required")
            self.assertTrue(bool(entry.system), "system required")
            self.assertTrue(bool(entry.metal), "metal required")
            self.assertTrue(bool(entry.direction), "direction required")
            self.assertTrue(len(entry.domains) > 0, "domains required")
            self.assertTrue(bool(entry.description), "description required")
            self.assertTrue(bool(entry.source), "source required")

    def test_unique_names(self):
        """All names in catalog are unique."""
        names = [e.name for e in ENOCHIAN_CATALOG]
        self.assertEqual(len(names), len(set(names)))


class TestQabalisticPaths(unittest.TestCase):
    """Verify Qabalistic path catalog."""

    def test_path_count(self):
        """22 paths on the Tree of Life."""
        self.assertEqual(len(QABALISTIC_PATHS), 22)

    def test_path_numbers_sequential(self):
        """Path numbers 1-22."""
        numbers = [p.path_number for p in QABALISTIC_PATHS]
        self.assertEqual(sorted(numbers), list(range(1, 23)))

    def test_required_fields_present(self):
        """Every path has all required fields."""
        for path in QABALISTIC_PATHS:
            self.assertTrue(bool(path.name), "name required")
            self.assertTrue(bool(path.from_sephira), "from_sephira required")
            self.assertTrue(bool(path.to_sephira), "to_sephira required")
            self.assertTrue(bool(path.planet), "planet required")
            self.assertTrue(bool(path.letter), "letter required")
            self.assertTrue(bool(path.element), "element required")
            self.assertTrue(len(path.domains) > 0, "domains required")

    def test_unique_path_numbers(self):
        """All path numbers are unique (names may repeat across sephiroth)."""
        numbers = [p.path_number for p in QABALISTIC_PATHS]
        self.assertEqual(len(numbers), len(set(numbers)))

    def test_sephira_coverage(self):
        """All 10 Sephiroth appear in paths."""
        sephiroth = set()
        for path in QABALISTIC_PATHS:
            sephiroth.add(path.from_sephira)
            sephiroth.add(path.to_sephira)
        expected = {"Kether", "Chokmah", "Binah", "Chesed", "Gevurah",
                    "Tiphareth", "Netzach", "Hod", "Yesod", "Malkuth"}
        self.assertEqual(sephiroth, expected)


class TestExpandedCorpus(unittest.TestCase):
    """Test ExpandedCorpus cross-system functionality."""

    def setUp(self):
        self.corpus = ExpandedCorpus()

    def test_goetic_count(self):
        """Goetic corpus has 72 entities."""
        self.assertEqual(len(self.corpus.goetic.records), 72)

    def test_enochian_count(self):
        """Enochian catalog has 12 entities."""
        self.assertEqual(len(self.corpus.enochian_map), 12)

    def test_qabalistic_count(self):
        """Qabalistic paths has 22 entries."""
        self.assertEqual(len(self.corpus.qabalistic_paths), 22)

    def test_get_enochian_by_name(self):
        """Enochian lookup by name."""
        e = self.corpus.get_enochian("Oriens")
        self.assertIsNotNone(e)
        self.assertEqual(e.system, "Enochian")
        self.assertEqual(e.direction, "East")

    def test_get_enochian_by_direction(self):
        """Enochian lookup by direction."""
        east_entities = self.corpus.get_enochian_by_direction("East")
        self.assertGreater(len(east_entities), 0)
        for e in east_entities:
            self.assertEqual(e.direction, "East")

    def test_get_qabalistic_path(self):
        """Qabalistic path lookup by number."""
        path = self.corpus.get_qabalistic_path(1)
        self.assertIsNotNone(path)
        self.assertEqual(path.name, "The Fool")
        self.assertEqual(path.from_sephira, "Kether")
        self.assertEqual(path.to_sephira, "Chokmah")

    def test_get_qabalistic_path_by_planet(self):
        """Qabalistic paths filtered by planet."""
        air_paths = self.corpus.get_qabalistic_path_by_planet("Air")
        self.assertGreater(len(air_paths), 0)
        for p in air_paths:
            self.assertEqual(p.planet, "Air")

    def test_cross_reference_vassago(self):
        """Cross-reference for Vassago finds matching entities."""
        ref = self.corpus.cross_reference("Vassago")
        self.assertIn("goetic", ref)
        self.assertEqual(ref["goetic"]["name"], "Vassago")
        self.assertIn("enochian_correspondences", ref)
        self.assertIn("qabalistic_paths", ref)

    def test_cross_reference_unknown_entity(self):
        """Cross-reference for unknown entity returns error."""
        ref = self.corpus.cross_reference("NonExistentSpirit99")
        self.assertIn("error", ref)
        self.assertIn("NonExistentSpirit99", ref["error"])

    def test_export_cross_reference_json(self, tmp_path=None):
        """Verify cross-reference export produces valid JSON."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            p = Path(f.name)
        out = self.corpus.export_cross_reference_json(str(p))
        self.assertTrue(Path(out).exists())
        data = json.loads(Path(out).read_text())
        self.assertGreater(len(data), 70)  # At least 70 Goetic entities
        self.assertIn("Vassago", data)
        p.unlink()


class TestExpandedCorpusIntegration(unittest.TestCase):
    """Integration test for corpus expansion with live endpoint."""

    def test_cross_reference_consistency(self):
        """Verify cross-reference data is internally consistent."""
        corpus = ExpandedCorpus()
        for rec in corpus.goetic.records[:10]:  # Sample first 10
            ref = corpus.cross_reference(rec.name)
            self.assertEqual(ref["goetic"]["name"], rec.name)
            self.assertEqual(ref["goetic"]["rank"], rec.rank)
            self.assertEqual(ref["goetic"]["metal"], rec.metal)
            # All enochian correspondences should have shared domains
            for eco in ref.get("enochian_correspondences", []):
                self.assertGreater(len(eco["shared_domains"]), 0)
            # All qabalistic paths should have shared domains
            for qp in ref.get("qabalistic_paths", []):
                self.assertGreater(len(qp["shared_domains"]), 0)


if __name__ == "__main__":
    import json
    unittest.main()
