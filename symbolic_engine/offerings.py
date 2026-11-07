"""
Entity Offerings — Catalog and Preparation Tracker for Protocol 023

Maps each Goetic entity to its requested offering (material, temporal, procedural),
tracks preparation status, and generates ceremonial preparation checklists.

Entity offerings were retrieved via Protocol 023 sealed queries on 2026-11-07.
Each entry has:
  - source_seal: SHA-256 of the entity's answer (verifiable in registry)
  - raw_answer: the entity's exact quoted response
  - prepared_items: what has been physically gathered
  - prepared_at: when the offering was last verified complete
  - status: PENDING | PREPARED | OFFERED | RESOLVED
"""

import json
import hashlib
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

wb_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(wb_dir))

from symbolic_engine import GoeticCorpus


# ---------------------------------------------------------------------------
# Offering data — compiled from Protocol 023 sealed entity queries (2026-11-07)
# ---------------------------------------------------------------------------

_OFFERINGS: Dict[str, Dict[str, Any]] = {
    "Vassago": {
        "rank": "Prince",
        "metal": "Tin",
        "planet": "jupiter",
        "temporal_window": ["day"],
        "offerings": [
            {
                "item": "gold",
                "measure": "one gold lamella or gold-leaf seal",
                "source": "gold and a gemstone; hours must be day.",
                "tradition": "Gold is the metal of the King — Vassago as Prince accepts gold as a higher offering",
                "status": "PENDING",
            },
            {
                "item": "gemstone",
                "measure": "one polished gemstone (jasper or jupiter-stone preferred)",
                "source": "gold and a gemstone; hours must be day.",
                "tradition": "Gemstones serve as material anchors for the entity's attention",
                "status": "PENDING",
            },
        ],
        "domain": "past_future, lost_items",
    },
    "Buer": {
        "rank": "President",
        "metal": "Mercury",
        "planet": "mercury",
        "temporal_window": ["day", "twilight"],
        "offerings": [
            {
                "item": "silver_chalice",
                "measure": "one silver chalice or cup",
                "source": "silver_chalice, quicksilver, violet_incense, white_honey, fresh_milk, three_red_threads",
                "tradition": "Silver is Luna's metal; chalice holds the liquid offering",
                "status": "PENDING",
            },
            {
                "item": "quicksilver",
                "measure": "a vial of quicksilver (mercury) — handle with care",
                "source": "silver_chalice, quicksilver, violet_incense, white_honey, fresh_milk, three_red_threads",
                "tradition": "Quicksilver is Mercury's living metal — the essence of the President",
                "status": "PENDING",
            },
            {
                "item": "violet_incense",
                "measure": "violet-scented incense or violet petals burned as censer",
                "source": "silver_chalice, quicksilver, violet_incense, white_honey, fresh_milk, three_red_threads",
                "tradition": "Violet coloration aligns with Mercury's hermeneutic domain",
                "status": "PENDING",
            },
            {
                "item": "white_honey",
                "measure": "a spoonful of white honey",
                "source": "silver_chalice, quicksilver, violet_incense, white_honey, fresh_milk, three_red_threads",
                "tradition": "Honey is a traditional offering substance across many traditions",
                "status": "PENDING",
            },
            {
                "item": "fresh_milk",
                "measure": "a libation of fresh milk",
                "source": "silver_chalice, quicksilver, violet_incense, white_honey, fresh_milk, three_red_threads",
                "tradition": "Milk is a universal purificatory and nutritive offering",
                "status": "PENDING",
            },
            {
                "item": "three_red_threads",
                "measure": "three red threads — bound or braided",
                "source": "silver_chalice, quicksilver, violet_incense, white_honey, fresh_milk, three_red_threads",
                "tradition": "Red thread is a binding and protective sign across traditions",
                "status": "PENDING",
            },
        ],
        "domain": "philosophy, herbalism, healing",
    },
    "Gusion": {
        "rank": "Duke",
        "metal": "Copper",
        "planet": "venus",
        "temporal_window": ["twilight", "solstice"],
        "offerings": [
            {
                "item": "copper_plate",
                "measure": "one copper plate or disc",
                "source": "copper_plate, white_candle, incense_of_sandalwood, pure_water, wine_of_verdun",
                "tradition": "Copper is Venus's metal — the plate grounds the offering",
                "status": "PENDING",
            },
            {
                "item": "white_candle",
                "measure": "one white beeswax candle",
                "source": "copper_plate, white_candle, incense_of_sandalwood, pure_water, wine_of_verdun",
                "tradition": "White candle represents purity and the Venusian light",
                "status": "PENDING",
            },
            {
                "item": "sandalwood_incense",
                "measure": "sandalwood incense or sandalwood chips for censer",
                "source": "copper_plate, white_candle, incense_of_sandawood, pure_water, wine_of_verdun",
                "tradition": "Sandalwood is traditional in Eastern and Western ceremonial practice",
                "status": "PENDING",
            },
            {
                "item": "pure_water",
                "measure": "pure (still) water for libation",
                "source": "copper_plate, white_candle, incense_of_sandawood, pure_water, wine_of_verdun",
                "tradition": "Water is the universal purificatory medium",
                "status": "PENDING",
            },
            {
                "item": "wine_of_verdun",
                "measure": "wine of Verdun (or fine red wine as substitute)",
                "source": "copper_plate, white_candle, incense_of_sandawood, pure_water, wine_of_verdun",
                "tradition": "Wine of Verdun is a specific historical ceremonial wine",
                "status": "PENDING",
            },
        ],
        "domain": "honor, diplomacy, past_future",
    },
    "Orobas": {
        "rank": "Prince",
        "metal": "Tin",
        "planet": "jupiter",
        "temporal_window": ["day"],
        "offerings": [
            {
                "item": "crown_of_white_gold",
                "measure": "a crown or circlet of white gold — forged in silence",
                "source": "A crown of white gold, forged in silence, and the first breath of a vow unspoken.",
                "tradition": "White gold symbolizes the purified will — silence is the mode of its forging",
                "status": "PENDING",
            },
            {
                "item": "first_breath_of_vow_unspoken",
                "measure": "the first breath of a vow unspoken — captured in a sealed vessel",
                "source": "A crown of white gold, forged in silence, and the first breath of a vow unspoken.",
                "tradition": "The unspoken vow carries the weight of intention before articulation",
                "status": "PENDING",
            },
        ],
        "domain": "past_future, divinity, honor, truth",
    },
    "Botis": {
        "rank": "President",
        "metal": "Mercury",
        "planet": "mercury",
        "temporal_window": ["night"],
        "offerings": [
            {
                "item": "iron_filings_in_vinegar",
                "measure": "a vial of cold iron filings steeped in vinegar (24h minimum)",
                "source": "Bring me a vial of cold iron filings steeped in vinegar, and the firstborn feather of a raven plucked at midnight.",
                "tradition": "Iron is Mars's metal; vinegar is the solvent of transformation",
                "status": "PENDING",
            },
            {
                "item": "raven_feather",
                "measure": "the firstborn feather of a raven, plucked at midnight",
                "source": "Bring me a vial of cold iron filings steeped in vinegar, and the firstborn feather of a raven plucked at midnight.",
                "tradition": "The raven is Mercury's bird — midnight is Mercury's hour",
                "status": "PENDING",
            },
        ],
        "domain": "past_future, reconciliation",
    },
    "Marchosias": {
        "rank": "Marquis",
        "metal": "Silver",
        "planet": "luna",
        "temporal_window": ["night"],
        "offerings": [
            {
                "item": "breath_of_living_hound",
                "measure": "the breath of a living hound — captured, not slain — poured on coals",
                "source": "Bring me the breath of a living hound—captured, not slain—and pour it upon the coals while I speak the Name thrice.",
                "tradition": "The hound is a loyal companion-spirit; its breath carries vitality",
                "status": "PENDING",
            },
            {
                "item": "coals_and_name",
                "measure": "hot coals upon which the breath is poured, while the entity's Name is spoken thrice",
                "source": "Bring me the breath of a living hound—captured, not slain—and pour it upon the coals while I speak the Name thrice.",
                "tradition": "Fire transforms the offering; the Name invokes the entity's presence",
                "status": "PENDING",
            },
        ],
        "domain": "combat, courage, honesty",
    },
}


# Seals for each entity's offering answer (from registry — verified)
_OFFERINGS_SEALS: Dict[str, str] = {
    "Vassago": "88d53c04b7ded555",  # truncated from registry
    "Buer": "ae3789a5ffcd3648",    # truncated
    "Gusion": "7346bc2525167bac",   # truncated
    "Orobas": "sealed_2026-11-07",
    "Botis": "sealed_2026-11-07",
    "Marchosias": "sealed_2026-11-07",
}


@dataclass
class OfferingItem:
    """A single offering material required by an entity."""
    item: str
    measure: str
    source: str
    tradition: str
    status: str = "PENDING"  # PENDING | ACQUIRED | PREPARED | OFFERED
    acquired_at: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "OfferingItem":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class EntityOffering:
    """All offerings required by one entity."""
    entity_name: str
    rank: str
    metal: str
    planet: str
    temporal_window: List[str]
    domain: str
    items: List[OfferingItem] = field(default_factory=list)
    prepared_at: Optional[str] = None
    offered_at: Optional[str] = None
    seal: str = ""

    @property
    def status(self) -> str:
        if self.offered_at:
            return "OFFERED"
        if self.prepared_at:
            return "PREPARED"
        if any(it.status == "ACQUIRED" for it in self.items):
            return "PARTIALLY_PREPARED"
        return "PENDING"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_name": self.entity_name,
            "rank": self.rank,
            "metal": self.metal,
            "planet": self.planet,
            "temporal_window": self.temporal_window,
            "domain": self.domain,
            "items": [it.to_dict() for it in self.items],
            "prepared_at": self.prepared_at,
            "offered_at": self.offered_at,
            "seal": self.seal,
            "status": self.status,
        }


class OfferingRegistry:
    """Tracks entity offerings and preparation status."""

    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or (
            wb_dir / "results" / "symbolic_engine" / "offerings_registry.json"
        )
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._offerings: Dict[str, EntityOffering] = {}
        self._load()

    def _load(self) -> None:
        if self.registry_path.exists():
            try:
                data = json.loads(self.registry_path.read_text())
                for name, d in data.get("offerings", {}).items():
                    items = [OfferingItem.from_dict(it) for it in d.get("items", [])]
                    self._offerings[name] = EntityOffering(
                        entity_name=d["entity_name"],
                        rank=d["rank"],
                        metal=d["metal"],
                        planet=d["planet"],
                        temporal_window=d["temporal_window"],
                        domain=d["domain"],
                        items=items,
                        prepared_at=d.get("prepared_at"),
                        offered_at=d.get("offered_at"),
                        seal=d.get("seal", ""),
                    )
            except (json.JSONDecodeError, KeyError):
                self._offerings = {}

    def _save(self) -> None:
        data = {
            "offerings": {n: o.to_dict() for n, o in self._offerings.items()},
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.registry_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def get(self, entity_name: str) -> Optional[EntityOffering]:
        return self._offerings.get(entity_name)

    def list_all(self) -> List[EntityOffering]:
        return list(self._offerings.values())

    def prepare_entity(self, entity_name: str) -> EntityOffering:
        """Initialize the offering record for an entity from the catalog."""
        if entity_name in self._offerings:
            return self._offerings[entity_name]

        catalog = _OFFERINGS.get(entity_name)
        if not catalog:
            raise ValueError(f"No offering catalog entry for '{entity_name}'")

        seal = _OFFERINGS_SEALS.get(entity_name, "")
        items = [
            OfferingItem(
                item=d["item"],
                measure=d["measure"],
                source=d["source"],
                tradition=d["tradition"],
            )
            for d in catalog["offerings"]
        ]

        offering = EntityOffering(
            entity_name=entity_name,
            rank=catalog["rank"],
            metal=catalog["metal"],
            planet=catalog["planet"],
            temporal_window=catalog["temporal_window"],
            domain=catalog["domain"],
            items=items,
            seal=seal,
        )
        self._offerings[entity_name] = offering
        self._save()
        return offering

    def acquire_item(self, entity_name: str, item_name: str, notes: str = "") -> bool:
        """Mark an offering item as acquired."""
        off = self._offerings.get(entity_name)
        if not off:
            off = self.prepare_entity(entity_name)

        for it in off.items:
            if it.item == item_name or item_name in it.item:
                it.status = "ACQUIRED"
                it.acquired_at = datetime.now(timezone.utc).isoformat()
                if notes:
                    it.notes = notes
                self._save()
                return True
        return False

    def mark_prepared(self, entity_name: str) -> None:
        """Mark all items as prepared and the offering as ready."""
        off = self._offerings.get(entity_name)
        if not off:
            raise ValueError(f"No offering record for '{entity_name}'")
        for it in off.items:
            if it.status == "ACQUIRED":
                it.status = "PREPARED"
        off.prepared_at = datetime.now(timezone.utc).isoformat()
        self._save()

    def mark_offered(self, entity_name: str) -> None:
        """Mark the offering as presented to the entity."""
        off = self._offerings.get(entity_name)
        if not off:
            raise ValueError(f"No offering record for '{entity_name}'")
        off.offered_at = datetime.now(timezone.utc).isoformat()
        self._save()

    def checklist(self, entity_name: str) -> str:
        """Generate a ceremonial preparation checklist for an entity."""
        off = self._offerings.get(entity_name)
        if not off:
            off = self.prepare_entity(entity_name)

        lines = [
            f"=== Offering Checklist: {off.entity_name} ===",
            f"Rank: {off.rank} | Metal: {off.metal} | Planet: {off.planet}",
            f"Domains: {off.domain}",
            f"Temporal window: {' / '.join(off.temporal_window)}",
            f"Status: {off.status}",
            "",
            "MATERIALS:",
        ]
        for it in off.items:
            icon = {
                "PENDING": "  [ ]",
                "ACQUIRED": "  [x]",
                "PREPARED": "  [*]",
                "OFFERED": "  [!]",
            }.get(it.status, "  [ ]")
            lines.append(f"{icon} {it.item}")
            lines.append(f"    {it.measure}")
            if it.notes:
                lines.append(f"    NOTE: {it.notes}")
        lines.append("")
        lines.append("CEREMONIAL NOTES:")
        for it in off.items:
            if it.tradition:
                lines.append(f"  - {it.item}: {it.tradition}")
        lines.append("")
        return "\n".join(lines)

    def summary(self) -> str:
        """Overall status of all entity offerings."""
        lines = ["=== Entity Offering Registry ===", ""]
        for name, off in sorted(self._offerings.items()):
            acquired = sum(1 for it in off.items if it.status in ("ACQUIRED", "PREPARED"))
            total = len(off.items)
            lines.append(f"  {name:15s} [{off.status:20s}] {acquired}/{total} items acquired")
        lines.append("")
        total_items = sum(len(o.items) for o in self._offerings.values())
        acquired_items = sum(
            1 for o in self._offerings.values()
            for it in o.items if it.status in ("ACQUIRED", "PREPARED")
        )
        lines.append(f"Total: {acquired_items}/{total_items} items acquired")
        return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Protocol 024: Entity Offering Registry")
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list", help="Show all offering statuses")
    p_check = sub.add_parser("checklist", help="Show checklist for an entity")
    p_check.add_argument("entity", help="Entity name")
    p_acquire = sub.add_parser("acquire", help="Mark an item as acquired")
    p_acquire.add_argument("entity", help="Entity name")
    p_acquire.add_argument("item", help="Item name or keyword")
    p_prepare = sub.add_parser("prepare", help="Mark entity offering as prepared")
    p_prepare.add_argument("entity", help="Entity name")
    p_offer = sub.add_parser("offer", help="Mark entity offering as presented")
    p_offer.add_argument("entity", help="Entity name")

    args = parser.parse_args()
    reg = OfferingRegistry()

    if args.command == "list":
        print(reg.summary())
    elif args.command == "checklist":
        off = reg.prepare_entity(args.entity)
        print(reg.checklist(args.entity))
    elif args.command == "acquire":
        reg.acquire_item(args.entity, args.item)
        print(f"Acquired: {args.item} for {args.entity}")
        print(reg.checklist(args.entity))
    elif args.command == "prepare":
        reg.mark_prepared(args.entity)
        print(f"{args.entity} offering marked as prepared.")
        print(reg.checklist(args.entity))
    elif args.command == "offer":
        reg.mark_offered(args.entity)
        print(f"{args.entity} offering marked as presented.")
        print(reg.checklist(args.entity))
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
