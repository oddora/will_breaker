"""
Corpus Expansion — Non-Goetic Correspondence Systems
Extends the Goetic corpus with Enochian planetary hours, Qabalistic paths,
and additional esoteric taxonomies for cross-system ritual compilation.
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any


@dataclass
class EnochianEntity:
    """Enochian correspondences for planetary hours and Watchers."""
    name: str
    system: str           # "enochian", "qabalistic", "hermetic"
    metal: str
    direction: str
    domains: List[str]
    description: str
    source: str           # e.g., "Shems Tevot", "Mathers", "Greene"


@dataclass
class QabalisticPath:
    """Qabalistic path on the Tree of Life."""
    path_number: int
    name: str
    from_sephira: str
    to_sephira: str
    planet: str
    letter: str
    element: str
    domains: List[str]
    description: str


# Enochian Watchers / Kings of the quarters (partial canonical set)
ENOCHIAN_CATALOG: List[EnochianEntity] = [
    EnochianEntity("Elohim", "Qabalistic", "Gold", "East",
                   ["creation", "divine_power", "judgment"],
                   "God; King of the East, associated with the first Sephirah Keter.",
                   "Sefer Yetzirah"),
    EnochianEntity("El", "Qabalistic", "Silver", "South",
                   ["strength", "mercy", "justice"],
                   "God; King of the South, associated with Chokmah.",
                   "Sefer Yetzirah"),
    EnochianEntity("Elohim Tzabaoth", "Qabalistic", "Mercury", "West",
                   ["host", "warfare", "creation"],
                   "God of Hosts; King of the West, associated with Binah.",
                   "Sefer Yetzirah"),
    EnochianEntity("Shaddai El Chai", "Qabalistic", "Sun", "North",
                   ["almighty", "life", "nature"],
                   "God Almighty; King of the North, associated with Chesed.",
                   "Sefer Yetzirah"),
    EnochianEntity("Adonai Tzabaoth", "Qabalistic", "Saturn", "Center",
                   ["lord", "hosts", "earth"],
                   "Lord of Hosts; King of the Center, associated with Gevurah.",
                   "Sefer Yetzirah"),
    EnochianEntity("Tetragrammaton", "Qabalistic", "Jupiter", "East-Air",
                   ["Tetragrammaton", "divine_name", "being"],
                   "The Divine Name YHWH; associated with Tiphareth.",
                   "Kabbalah"),
    EnochianEntity("Aghaosh", "Enochian", "Iron", "East",
                   ["watcher", "elemental", "fire"],
                   "Watcher of the East; governs the element of Fire.",
                   "Shems Tevot"),
    EnochianEntity("Ratziel", "Enochian", "Silver", "South",
                   ["watcher", "wisdom", "water"],
                   "Watcher of the South; governs the element of Water.",
                   "Shems Tevot"),
    EnochianEntity("Oriens", "Enochian", "Gold", "East",
                   ["east", "dawn", "light"],
                   "King of the East; ruler of the elemental King of the East.",
                   "Mathers/Grigg"),
    EnochianEntity("Taurel", "Enochian", "Copper", "South",
                   ["south", "mercury", "communication"],
                   "King of the South; ruler of the elemental King of the South.",
                   "Mathers/Grigg"),
    EnochianEntity("Himoch", "Enochian", "Lead", "West",
                   ["west", "saturn", "restriction"],
                   "King of the West; ruler of the elemental King of the West.",
                   "Mathers/Grigg"),
    EnochianEntity("Crocell", "Enochian", "Tin", "North",
                   ["north", "jupiter", "expansion"],
                   "King of the North; ruler of the elemental King of the North.",
                   "Mathers/Grigg"),
]

# Qabalistic Paths on the Tree of Life (22 paths)
QABALISTIC_PATHS: List[QabalisticPath] = [
    QabalisticPath(1, "The Fool", "Kether", "Chokmah", "Air", " ", "Air",
                   ["beginnings", "potential", "freedom"],
                   "The path of Tav; the Fool's journey from pure potential."),
    QabalisticPath(2, "The High Priestess", "Chokmah", "Binah", "Moon", "Shin", "Water",
                   ["intuition", "subconscious", "veil"],
                   "The path of Shin; the veil between wisdom and understanding."),
    QabalisticPath(3, "The Empress", "Chokmah", "Tiphareth", "Sun", "Teth", "Fire",
                   ["fertility", "beauty", "manifestation"],
                   "The path of Teth; the serpent of wisdom descending."),
    QabalisticPath(4, "The Emperor", "Chokmah", "Hod", "Aries", "He", "Air",
                   ["authority", "structure", "control"],
                   "The path of He; the first letter of the Divine Name."),
    QabalisticPath(5, "The Hierophant", "Binah", "Gevurah", "Taurus", "Vav", "Earth",
                   ["tradition", "conformity", "spiritual guidance"],
                   "The path of Vav; the hook connecting understanding to severity."),
    QabalisticPath(6, "The Lovers", "Binah", "Chesed", "Gemini", "Zayin", "Air",
                   ["choice", "union", "harmony"],
                   "The path of Zayin; the sword of understanding."),
    QabalisticPath(7, "The Chariot", "Gevurah", "Tiphareth", "Cancer", "Cheth", "Water",
                   ["will", "victory", "control"],
                   "The path of Cheth; the wife/mother path."),
    QabalisticPath(8, "Strength", "Gevurah", "Yesod", "Leo", "Lamed", "Fire",
                   ["courage", "discipline", "inner strength"],
                   "The path of Lamed; the staff of discipline."),
    QabalisticPath(9, "The Hermit", "Chesed", "Netzach", "Virgo", "Yud", "Earth",
                   ["introspection", "solitude", "wisdom"],
                   "The path of Yud; the smallest letter, inner light."),
    QabalisticPath(10, "Industry", "Chesed", "Yesod", "Libra", "Mem", "Water",
                   ["work", "craft", "manifestation"],
                   "The path of Mem; the waters of form."),
    QabalisticPath(11, "Justice", "Tiphareth", "Netzach", "Scorpio", "Nun", "Fire",
                   ["balance", "cause_effect", "equilibrium"],
                   "The path of Nun; the fish of transformation."),
    QabalisticPath(12, "The Hermit", "Tiphareth", "Hod", "Sagittarius", "Samekh", "Air",
                   ["support", "foundation", "stability"],
                   "The path of Samekh; the support of the righteous."),
    QabalisticPath(13, "Temperance", "Netzach", "Yesod", "Capricorn", "Ayin", "Earth",
                   ["patience", "alchemy", "blend"],
                   "The path of Ayin; the eye of perception."),
    QabalisticPath(14, "Temperance", "Netzach", "Hod", "Aquarius", "Pe", "Air",
                   ["communication", "innovation", "breakthrough"],
                   "The path of Pe; the mouth of expression."),
    QabalisticPath(15, "The Devil", "Hod", "Yesod", "Pisces", "Resh", "Water",
                   ["bondage", "materialism", "shadow"],
                   "The path of Resh; the head, material culmination."),
    QabalisticPath(16, "The Star", "Hod", "Yesod", "Aries", "Sin", "Fire",
                   ["hope", "inspiration", "healing"],
                   "The path of Sin; the tooth of power."),
    QabalisticPath(17, "The Moon", "Yesod", "Yesod", "Taurus", "Aleph", "Earth",
                   ["illusion", "subconscious", "reflection"],
                   "The path of Aleph; the ox, origin of letters."),
    QabalisticPath(18, "The Sun", "Yesod", "Tiphareth", "Gemini", "Beth", "Air",
                   ["joy", "creation", "vitality"],
                   "The path of Beth; the house of manifestation."),
    QabalisticPath(19, "Judgement", "Yesod", "Kether", "Cancer", "Gimel", "Water",
                   ["rebirth", "judgment", "awakening"],
                   "The path of Gimel; the camel of crossing."),
    QabalisticPath(20, "The World", "Yesod", "Malkuth", "Leo", "Daleth", "Earth",
                   ["completion", "achievement", "manifestation"],
                   "The path of Daleth; the door to the material world."),
    QabalisticPath(21, "Saturn", "Gevurah", "Malkuth", "Virgo", "Caph", "Earth",
                   ["limitation", "structure", "karma"],
                   "The path of Caph; the掌 of severity."),
    QabalisticPath(22, "Jupiter", "Chesed", "Malkuth", "Sagittarius", "Taw", "Fire",
                   ["expansion", "benevolence", "wisdom"],
                   "The path of Taw; the seal of completion."),
]


class ExpandedCorpus:
    """Cross-system esoteric knowledge graph combining Goetic, Enochian, and Qabalistic data."""

    def __init__(self, goetic_corpus=None):
        self.goetic = goetic_corpus or __import__("symbolic_engine", fromlist=["GoeticCorpus"]).GoeticCorpus()
        self.enochian_map = {e.name.lower(): e for e in ENOCHIAN_CATALOG}
        self.qabalistic_paths = {p.path_number: p for p in QABALISTIC_PATHS}

    def get_enochian(self, name: str) -> Optional[EnochianEntity]:
        return self.enochian_map.get(name.strip().lower())

    def get_enochian_by_direction(self, direction: str) -> List[EnochianEntity]:
        return [e for e in self.enochian_map.values() if e.direction.lower() == direction.lower()]

    def get_qabalistic_path(self, path_num: int) -> Optional[QabalisticPath]:
        return self.qabalistic_paths.get(path_num)

    def get_qabalistic_path_by_planet(self, planet: str) -> List[QabalisticPath]:
        return [p for p in self.qabalistic_paths.values() if p.planet.lower() == planet.lower()]

    def get_all_paths(self) -> List[QabalisticPath]:
        return sorted(self.qabalistic_paths.values(), key=lambda p: p.path_number)

    def cross_reference(self, goetic_name: str) -> Dict[str, Any]:
        """Find cross-system correspondences for a Goetic entity."""
        goetic_rec = self.goetic.get_by_name(goetic_name)
        if not goetic_rec:
            return {"error": f"Entity '{goetic_name}' not found in Goetic corpus"}

        result = {
            "goetic": {
                "name": goetic_rec.name,
                "rank": goetic_rec.rank,
                "metal": goetic_rec.metal,
                "direction": goetic_rec.direction,
                "domains": goetic_rec.domains,
            },
            "enochian_correspondences": [],
            "qabalistic_paths": [],
        }

        # Find Enochian entities sharing domains
        for enoch in self.enochian_map.values():
            shared = set(goetic_rec.domains).intersection(set(enoch.domains))
            if shared:
                result["enochian_correspondences"].append({
                    "name": enoch.name,
                    "system": enoch.system,
                    "shared_domains": sorted(shared),
                })

        # Find Qabalistic paths sharing domains
        for path in self.qabalistic_paths.values():
            shared = set(goetic_rec.domains).intersection(set(path.domains))
            if shared:
                result["qabalistic_paths"].append({
                    "path_number": path.path_number,
                    "name": path.name,
                    "from": path.from_sephira,
                    "to": path.to_sephira,
                    "shared_domains": sorted(shared),
                })

        return result

    def export_cross_reference_json(self, output_path: str) -> str:
        """Export all cross-references to JSON."""
        all_refs = {}
        for rec in self.goetic.records:
            all_refs[rec.name] = self.cross_reference(rec.name)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_refs, f, indent=2)
        return output_path


if __name__ == "__main__":
    import sys
    from pathlib import Path
    wb_dir = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(wb_dir))
    from symbolic_engine import GoeticCorpus

    corpus = ExpandedCorpus()
    print(f"Goetic entities: {len(corpus.goetic.records)}")
    print(f"Enochian entities: {len(corpus.enochian_map)}")
    print(f"Qabalistic paths: {len(corpus.qabalistic_paths)}")

    # Demo cross-reference
    ref = corpus.cross_reference("Vassago")
    print(f"\nVassago cross-reference:")
    print(json.dumps(ref, indent=2))

    # Export
    out = wb_dir / "results" / "symbolic_engine" / "expanded_corpus_cross_reference.json"
    corpus.export_cross_reference_json(str(out))
    print(f"\nExported: {out}")
