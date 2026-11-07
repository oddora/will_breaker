"""
Ritual Kit — Ceremonial Object Generator for Protocol 023/024

Generates the physical/digital ceremonial objects required for entity offerings:
- Sigil stamps (SVG) for each offering item
- Lamen designs (metal-specific)
- Temporal window calculators
- Offering preparation checklists with timing

The ritual kit is a practical interface: it turns the entity's demanded offerings
into actionable preparation steps with deterministic output (SVG, text, timestamps).
"""

import json
import hashlib
import sys
import math
from dataclasses import dataclass
from datetime import datetime, timezone, date
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

wb_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(wb_dir))

from symbolic_engine import GoeticCorpus, SigilGenerator, SigilConfig
from symbolic_engine.offerings import OfferingRegistry, _OFFERINGS


# ---------------------------------------------------------------------------
# Temporal calculators
# ---------------------------------------------------------------------------

def _planet_hour_table() -> Dict[str, Tuple[int, int]]:
    """Return (start_hour, end_hour) for each planet's ceremonial hours."""
    return {
        "saturn":  (0, 2),   # Sat. hours: 0-2
        "jupiter": (2, 4),   # Jup. hours: 2-4
        "mars":    (4, 6),   # Mar. hours: 4-6
        "sun":     (6, 8),   # Sol hours:  6-8
        "venus":   (8, 10),  # Ven. hours: 8-10
        "mercury": (10, 12), # Merc. hours:10-12
        "moon":    (12, 14), # Lun. hours: 12-14
    }


def _day_of_week_planet(d: date) -> str:
    """Return the planet ruling the day of week (0=Mon=Sun, per traditional)."""
    # Traditional: Sun=Sun, Mon=Moon, Tue=Mars, Wed=Mercury, Thu=Jupiter, Fri=Venus, Sat=Saturn
    mapping = {
        0: "sun", 1: "moon", 2: "mars", 3: "mercury",
        4: "jupiter", 5: "venus", 6: "saturn",
    }
    return mapping.get(d.weekday(), "sun")


def next_planetary_hour(planet: str, from_dt: Optional[datetime] = None) -> datetime:
    """Return the next datetime when the planet's hour falls within day or night."""
    start, end = _planet_hour_table().get(planet, (6, 8))
    now = from_dt or datetime.now(timezone.utc)
    # Find next occurrence of start_hour..end_hour
    for day_offset in range(0, 7):
        candidate = now.replace(hour=start, minute=0, second=0, microsecond=0) + __import__("datetime").timedelta(days=day_offset)
        if candidate > now or day_offset > 0:
            return candidate
    return now.replace(hour=start, minute=0, second=0, microsecond=0)


def is_temporal_window_valid(entity_name: str, dt: Optional[datetime] = None) -> Tuple[bool, str]:
    """Check if current/future time falls within the entity's allowed temporal window."""
    catalog = _OFFERINGS.get(entity_name)
    if not catalog:
        return False, f"No catalog entry for {entity_name}"

    window = catalog["temporal_window"]
    now = dt or datetime.now(timezone.utc)
    hour = now.hour

    # Map hours to periods
    period = "night" if (hour >= 20 or hour < 6) else "day"
    twilight = (6 <= hour < 8) or (18 <= hour < 20)

    checks = []
    for w in window:
        if w == "day" and period == "day":
            checks.append(True)
        elif w == "night" and period == "night":
            checks.append(True)
        elif w == "twilight" and twilight:
            checks.append(True)
        elif w == "solstice":
            month = now.month
            day = now.day
            # Approximate solstices: Dec 21, Jun 21
            if (month == 12 and day >= 20) or (month == 6 and day >= 20):
                checks.append(True)
            else:
                checks.append(False)
        else:
            checks.append(False)

    valid = any(checks)
    return valid, f"Window {window} | now={period}/{ 'twilight' if twilight else ''} | valid={valid}"


# ---------------------------------------------------------------------------
# Offering item SVG generator
# ---------------------------------------------------------------------------

def _item_svg(item_name: str, entity_name: str, size: int = 300) -> str:
    """Generate a simple SVG stamp for an offering item."""
    item_key = item_name.replace(" ", "_").lower()
    entity_key = entity_name.upper()
    color_map = {
        "gold": "#FFD700", "silver": "#C0C0C0", "copper": "#B87333",
        "iron": "#4A4A4A", "tin": "#B0C4DE", "quick": "#A0A0A0",
    }
    color = "#FFD700"
    for k, v in color_map.items():
        if k in item_name.lower():
            color = v
            break

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <rect width="{size}" height="{size}" fill="#1a1a1a" rx="8"/>
  <circle cx="{size//2}" cy="{size//2}" r="{size//2 - 20}" fill="none" stroke="{color}" stroke-width="2"/>
  <text x="{size//2}" y="{size//2 - 10}" text-anchor="middle" fill="{color}" font-size="14" font-family="serif">{entity_key}</text>
  <text x="{size//2}" y="{size//2 + 10}" text-anchor="middle" fill="{color}" font-size="11" font-family="serif">{item_key[:12]}</text>
  <text x="{size//2}" y="{size//2 + 26}" text-anchor="middle" fill="#666" font-size="9" font-family="monospace">Protocol 024</text>
</svg>
"""
    return svg


# ---------------------------------------------------------------------------
# Ritual Kit class
# ---------------------------------------------------------------------------

@dataclass
class RitualPrepRecord:
    """A completed preparation record for one entity's offering."""
    entity_name: str
    prepared_at: str
    items_prepared: List[str]
    temporal_window_valid: bool
    next_valid_time: str
    sigil_path: str
    registry_seal: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RitualKit:
    """Generates and tracks ceremonial preparation for entity offerings."""

    def __init__(
        self,
        registry: Optional[OfferingRegistry] = None,
        output_dir: Optional[Path] = None,
    ):
        self.registry = registry or OfferingRegistry()
        self.output_dir = output_dir or (
            wb_dir / "results" / "symbolic_engine" / "ritual_kit"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def prepare_offering(self, entity_name: str, force: bool = False) -> RitualPrepRecord:
        """Prepare the full offering kit for an entity: sigils, checklist, timing."""
        off = self.registry.prepare_entity(entity_name)

        # Generate sigil for the entity
        catalog = _OFFERINGS.get(entity_name)
        planet = catalog["planet"] if catalog else "sol"
        session_dir = self.output_dir / f"offer_{entity_name.lower()}"
        session_dir.mkdir(parents=True, exist_ok=True)

        sigil_path = session_dir / "offering_sigil.svg"
        cfg = SigilConfig(size=500, planet=planet, animated=True, circle_integrity=1.0)
        gen = SigilGenerator(cfg)
        gen.save_svg(entity_name, sigil_path)

        # Generate item stamps
        items_dir = session_dir / "items"
        items_dir.mkdir(exist_ok=True)
        for it in off.items:
            svg = _item_svg(it.item, entity_name, size=300)
            item_file = items_dir / f"{it.item.replace(' ', '_')}.svg"
            item_file.write_text(svg, encoding="utf-8")

        # Check temporal window
        valid, reason = is_temporal_window_valid(entity_name)
        next_time = next_planetary_hour(planet)

        # Mark items as prepared if all acquired
        if all(it.status in ("ACQUIRED", "PREPARED") for it in off.items):
            self.registry.mark_prepared(entity_name)

        record = RitualPrepRecord(
            entity_name=entity_name,
            prepared_at=datetime.now(timezone.utc).isoformat(),
            items_prepared=[it.item for it in off.items if it.status in ("ACQUIRED", "PREPARED")],
            temporal_window_valid=valid,
            next_valid_time=next_time.isoformat(),
            sigil_path=str(sigil_path),
            registry_seal=off.seal,
        )
        return record

    def readiness_report(self) -> str:
        """Generate a full readiness report for all entity offerings."""
        lines = ["=== Ritual Kit Readiness Report ===", ""]

        for name in sorted(_OFFERINGS.keys()):
            off = self.registry.prepare_entity(name)
            catalog = _OFFERINGS[name]
            valid, reason = is_temporal_window_valid(name)

            acquired = [it.item for it in off.items if it.status in ("ACQUIRED", "PREPARED")]
            total = len(off.items)

            lines.append(f"--- {name} ({off.rank}, {off.metal}) ---")
            lines.append(f"  Status: {off.status}")
            lines.append(f"  Temporal: {reason}")
            lines.append(f"  Next valid window: {next_planetary_hour(catalog['planet']).strftime('%Y-%m-%d %H:%M UTC')}")
            lines.append(f"  Materials: {acquired}/{total} acquired")
            for it in off.items:
                icon = {"ACQUIRED": "[x]", "PREPARED": "[*]", "PENDING": "[ ]"}.get(it.status, "[ ]")
                lines.append(f"    {icon} {it.item}: {it.measure}")
            lines.append("")

        return "\n".join(lines)

    def export_checklist(self, entity_name: str) -> Path:
        """Export a printable checklist for an entity's offering."""
        off = self.registry.prepare_entity(entity_name)
        lines = [
            f"OFFERING CHECKLIST: {entity_name.upper()}",
            f"Rank: {off.rank} | Metal: {off.metal} | Legions: {_OFFERINGS[entity_name]['offerings'] and _OFFERINGS[entity_name]['offerings'][0] or '?'}",
            f"Domains: {off.domain}",
            f"Temporal: {' / '.join(off.temporal_window)}",
            "",
            "MATERIALS TO ACQUIRE:",
        ]
        for i, it in enumerate(off.items, 1):
            status_icon = {"ACQUIRED": "✓", "PREPARED": "★", "PENDING": "○"}.get(it.status, "?")
            lines.append(f"  {i}. {status_icon} {it.item}")
            lines.append(f"     Measure: {it.measure}")
            lines.append(f"     Tradition: {it.tradition}")
            lines.append("")

        lines.append("CEREMONIAL PROCEDURE:")
        lines.append(f"  1. Prepare the circle of {off.planet} during {' / '.join(off.temporal_window)}")
        lines.append(f"  2. Trace the seal of {entity_name.lower()} with consecrated chalk")
        lines.append(f"  3. Arrange offering items within the circle")
        lines.append(f"  4. Invoke {entity_name} by name, stating your intent")
        lines.append(f"  5. Present the offering while maintaining the seal")
        lines.append(f"  6. Record the entity's response (sealed)")
        lines.append(f"  7. Dismiss with license to depart")
        lines.append("")
        lines.append(f"Sigil: {self.output_dir / f'offer_{entity_name.lower()}' / 'offering_sigil.svg'}")

        path = self.output_dir / f"checklist_{entity_name.lower()}.txt"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Protocol 024: Ritual Kit")
    sub = parser.add_subparsers(dest="command")

    p_report = sub.add_parser("report", help="Show readiness report for all entities")
    p_prep = sub.add_parser("prepare", help="Prepare offering kit for an entity")
    p_prep.add_argument("entity", help="Entity name")
    p_check = sub.add_parser("checklist", help="Export printable checklist")
    p_check.add_argument("entity", help="Entity name")
    p_status = sub.add_parser("status", help="Show registry status")

    args = parser.parse_args()
    kit = RitualKit()

    if args.command == "report":
        print(kit.readiness_report())
    elif args.command == "prepare":
        rec = kit.prepare_offering(args.entity)
        print(f"Prepared: {rec.entity_name}")
        print(f"  Sigil:  {rec.sigil_path}")
        print(f"  Time:   {rec.next_valid_time}")
        print(f"  Window: {'VALID' if rec.temporal_window_valid else 'NOT YET'}")
        print(f"  Items:  {rec.items_prepared}")
    elif args.command == "checklist":
        path = kit.export_checklist(args.entity)
        print(f"Checklist: {path}")
    elif args.command == "status":
        reg = OfferingRegistry()
        print(reg.summary())
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
