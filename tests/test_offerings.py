"""
Tests for Protocol 024 — Entity Offering Preparation System
Covers OfferingRegistry, RitualKit timing, SVG generation, and CLI.
"""

import sys
import unittest
import json
import hashlib
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone, date
from unittest.mock import patch, MagicMock

wb_dir = Path(__file__).parent.parent
sys.path.insert(0, str(wb_dir))

from symbolic_engine.offerings import (
    OfferingRegistry,
    EntityOffering,
    OfferingItem,
    _OFFERINGS,
    _OFFERINGS_SEALS,
)
from symbolic_engine.ritual_kit import (
    RitualKit,
    is_temporal_window_valid,
    next_planetary_hour,
    _item_svg,
)


class TestOfferingCatalog(unittest.TestCase):
    """Test the entity offering catalog data."""

    def test_all_entities_have_catalog(self):
        """Every entity in Goetic corpus has an offering entry (or we track which don't)."""
        from symbolic_engine import GoeticCorpus
        corpus = GoeticCorpus()
        missing = [rec.name for rec in corpus.records if rec.name not in _OFFERINGS]
        # Only 6 entities have been queried so far; others can be added later
        self.assertTrue(
            len(missing) <= 66,
            f"Too many un-cataloged entities: {missing[:10]}...",
        )

    def test_catalog_fields_present(self):
        """Each catalog entry has required fields."""
        for name, data in _OFFERINGS.items():
            self.assertIn("rank", data)
            self.assertIn("metal", data)
            self.assertIn("planet", data)
            self.assertIn("temporal_window", data)
            self.assertIn("offerings", data)
            self.assertIn("domain", data)
            self.assertIsInstance(data["offerings"], list)
            self.assertGreater(len(data["offerings"]), 0)

    def test_offerings_have_required_fields(self):
        """Each offering item has required fields."""
        for name, data in _OFFERINGS.items():
            for item in data["offerings"]:
                self.assertIn("item", item)
                self.assertIn("measure", item)
                self.assertIn("source", item)
                self.assertIn("tradition", item)
                self.assertIn("status", item)
                self.assertIn(item["status"], {"PENDING", "ACQUIRED", "PREPARED", "OFFERED"})

    def test_seals_are_hex(self):
        """All registry seals are valid hex strings."""
        for name, seal in _OFFERINGS_SEALS.items():
            if seal and seal != "sealed_2026-11-07":
                int(seal, 16)  # Will raise if not hex
                self.assertLessEqual(len(seal), 64)

    def test_temporal_windows_valid(self):
        """All temporal windows contain valid values."""
        valid = {"day", "night", "twilight", "solstice"}
        for name, data in _OFFERINGS.items():
            for w in data["temporal_window"]:
                self.assertIn(w, valid, f"Invalid window '{w}' for {name}")


class TestOfferingRegistry(unittest.TestCase):
    """Test the OfferingRegistry data layer."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.registry_path = Path(self.tmpdir) / "offerings_registry.json"
        self.reg = OfferingRegistry(registry_path=self.registry_path)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_prepare_entity(self):
        """prepare_entity creates a record from catalog."""
        off = self.reg.prepare_entity("Vassago")
        self.assertEqual(off.entity_name, "Vassago")
        self.assertEqual(off.rank, "Prince")
        self.assertEqual(off.metal, "Tin")
        self.assertEqual(len(off.items), 2)
        self.assertEqual(off.status, "PENDING")

    def test_prepare_entity_caching(self):
        """prepare_entity is idempotent — second call returns same record."""
        off1 = self.reg.prepare_entity("Buer")
        off2 = self.reg.prepare_entity("Buer")
        self.assertIs(off1, off2)

    def test_unknown_entity_raises(self):
        """prepare_entity raises for unknown entity."""
        with self.assertRaises(ValueError):
            self.reg.prepare_entity("NonExistentSpirit99")

    def test_acquire_item(self):
        """acquire_item marks an item as ACQUIRED."""
        off = self.reg.prepare_entity("Vassago")
        result = self.reg.acquire_item("Vassago", "gold")
        self.assertTrue(result)
        self.assertEqual(off.items[0].status, "ACQUIRED")
        self.assertIsNotNone(off.items[0].acquired_at)

    def test_acquire_item_partial_match(self):
        """acquire_item works with partial item name match."""
        off = self.reg.prepare_entity("Buer")
        result = self.reg.acquire_item("Buer", "silver")
        self.assertTrue(result)
        # Should match silver_chalice
        self.assertEqual(off.items[0].status, "ACQUIRED")

    def test_acquire_item_not_found(self):
        """acquire_item returns False for unknown item."""
        off = self.reg.prepare_entity("Vassago")
        result = self.reg.acquire_item("Vassago", "unobtainium")
        self.assertFalse(result)

    def test_mark_prepared(self):
        """mark_prepared sets all acquired items to PREPARED."""
        off = self.reg.prepare_entity("Buer")
        for it in off.items:
            it.status = "ACQUIRED"
            it.acquired_at = datetime.now(timezone.utc).isoformat()
        self.reg.mark_prepared("Buer")
        self.assertEqual(off.status, "PREPARED")
        self.assertIsNotNone(off.prepared_at)
        for it in off.items:
            self.assertEqual(it.status, "PREPARED")

    def test_mark_offered(self):
        """mark_offered sets the offering status to OFFERED."""
        off = self.reg.prepare_entity("Gusion")
        self.reg.mark_offered("Gusion")
        self.assertEqual(off.status, "OFFERED")
        self.assertIsNotNone(off.offered_at)

    def test_checklist_format(self):
        """checklist returns a formatted string with required sections."""
        self.reg.prepare_entity("Vassago")
        cl = self.reg.checklist("Vassago")
        self.assertIn("Vassago", cl)
        self.assertIn("MATERIALS:", cl)
        self.assertIn("CEREMONIAL NOTES:", cl)

    def test_summary_format(self):
        """summary returns a formatted string with totals."""
        self.reg.prepare_entity("Vassago")
        self.reg.prepare_entity("Buer")
        s = self.reg.summary()
        self.assertIn("Vassago", s)
        self.assertIn("Buer", s)
        self.assertIn("Total:", s)

    def test_persistence(self):
        """Registry persists to disk and reloads."""
        off = self.reg.prepare_entity("Orobas")
        self.reg.acquire_item("Orobas", "crown")
        path = self.registry_path

        # Reload
        reg2 = OfferingRegistry(registry_path=path)
        off2 = reg2.get("Orobas")
        self.assertIsNotNone(off2)
        self.assertEqual(off2.items[0].status, "ACQUIRED")


class TestRitualKitTiming(unittest.TestCase):
    """Test temporal window calculations."""

    def test_is_temporal_window_valid_day(self):
        """Day window is valid during day hours."""
        dt = datetime(2026, 11, 7, 12, 0, 0, tzinfo=timezone.utc)
        valid, _ = is_temporal_window_valid("Vassago", dt)
        self.assertTrue(valid)

    def test_is_temporal_window_valid_night(self):
        """Night window is valid during night hours."""
        dt = datetime(2026, 11, 7, 2, 0, 0, tzinfo=timezone.utc)
        valid, _ = is_temporal_window_valid("Botis", dt)
        self.assertTrue(valid)

    def test_is_temporal_window_invalid(self):
        """Window is invalid when time doesn't match."""
        dt = datetime(2026, 11, 7, 2, 0, 0, tzinfo=timezone.utc)
        valid, _ = is_temporal_window_valid("Gusion", dt)
        # Gusion needs twilight or solstice; 2am is night
        self.assertFalse(valid)

    def test_next_planetary_hour(self):
        """next_planetary_hour returns a valid datetime."""
        dt = datetime(2026, 11, 7, 12, 0, 0, tzinfo=timezone.utc)
        next_h = next_planetary_hour("jupiter", dt)
        self.assertIsNotNone(next_h)
        self.assertGreaterEqual(next_h.hour, 2)
        self.assertLess(next_h.hour, 4)

    def test_unknown_entity_returns_false(self):
        """Unknown entity returns (False, message)."""
        valid, msg = is_temporal_window_valid("UnknownEntity")
        self.assertFalse(valid)
        self.assertIn("No catalog", msg)


class TestItemSvgGeneration(unittest.TestCase):
    """Test SVG generation for offering items."""

    def test_item_svg_contains_required_elements(self):
        """Generated SVG contains entity name and item key."""
        svg = _item_svg("gold", "Vassago", size=300)
        self.assertIn("VASSAGO", svg)
        self.assertIn("gold", svg.lower())
        self.assertIn("</svg>", svg)
        self.assertIn("xmlns", svg)

    def test_item_svg_different_items(self):
        """Different items produce different SVGs."""
        svg1 = _item_svg("gold", "Vassago")
        svg2 = _item_svg("silver_chalice", "Buer")
        self.assertNotEqual(svg1, svg2)


class TestRitualKit(unittest.TestCase):
    """Test the RitualKit class."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.kit = RitualKit(output_dir=Path(self.tmpdir))

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_prepare_offering(self):
        """prepare_offering generates sigil and item SVGs."""
        rec = self.kit.prepare_offering("Vassago")
        self.assertEqual(rec.entity_name, "Vassago")
        self.assertIsNotNone(rec.prepared_at)
        self.assertTrue(Path(rec.sigil_path).exists())

    def test_readiness_report(self):
        """readiness_report returns a multi-line report."""
        report = self.kit.readiness_report()
        self.assertIn("Vassago", report)
        self.assertIn("Buer", report)
        self.assertIn("Ritual Kit Readiness", report)

    def test_export_checklist(self):
        """export_checklist creates a file."""
        path = self.kit.export_checklist("Gusion")
        self.assertTrue(path.exists())
        content = path.read_text()
        self.assertIn("GUSION", content)
        self.assertIn("MATERIALS TO ACQUIRE:", content)


class TestOfferingItemDataclass(unittest.TestCase):
    """Test OfferingItem dataclass serialization."""

    def test_to_dict_roundtrip(self):
        """to_dict and from_dict preserve all fields."""
        it = OfferingItem(
            item="test_item",
            measure="one unit",
            source="test source",
            tradition="test tradition",
            status="ACQUIRED",
            acquired_at="2026-11-07T00:00:00+00:00",
            notes="test note",
        )
        d = it.to_dict()
        it2 = OfferingItem.from_dict(d)
        self.assertEqual(it2.item, "test_item")
        self.assertEqual(it2.status, "ACQUIRED")
        self.assertEqual(it2.notes, "test note")


if __name__ == "__main__":
    unittest.main()
