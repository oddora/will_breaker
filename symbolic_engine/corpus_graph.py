"""
Corpus Graph — Knowledge Graph & Query Engine for Historical Goetic Manuscripts
Encodes structured profiles, ranks, planetary correspondences, and domain taxonomies
for historical entities in the Ars Goetia / Lesser Key of Solomon.
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Optional, Any


@dataclass
class EntityRecord:
    number: int
    name: str
    rank: str               # King, Duke, Prince, Marquis, Earl, President, Knight
    metal: str              # Gold, Copper, Tin, Silver, Iron, Mercury, Lead
    direction: str          # East, West, North, South
    legions: int
    domains: List[str]      # e.g., ["languages", "sciences", "invisibility", "lost_items"]
    description: str


# Core historical taxonomy based on the 17th-century Ars Goetia catalog
HISTORICAL_GOETIC_CATALOG: List[EntityRecord] = [
    EntityRecord(1, "Bael", "King", "Gold", "East", 66, ["invisibility", "wisdom"], "First Principal Spirit; rules in the East, teaches invisibility and wisdom."),
    EntityRecord(2, "Agares", "Duke", "Copper", "East", 31, ["languages", "earthquakes", "retrieval"], "Causes earthquakes, teaches all languages instantly, returns runaways."),
    EntityRecord(3, "Vassago", "Prince", "Tin", "North", 26, ["past_future", "lost_items"], "Declares things past and to come, discovers hidden treasures."),
    EntityRecord(4, "Gamigin", "Marquis", "Silver", "South", 30, ["liberal_sciences", "necromancy"], "Teaches liberal sciences, gives accounts of souls deceased in sin."),
    EntityRecord(5, "Marbas", "President", "Mercury", "East", 36, ["healing", "mechanical_arts", "shapeshifting"], "Answers truly concerning hidden secrets, cures diseases, gives skill in mechanics."),
    EntityRecord(6, "Valefor", "Duke", "Copper", "North", 10, ["theft", "familiar"], "A good familiar who induces persons to steal."),
    EntityRecord(7, "Amon", "Marquis", "Silver", "North", 40, ["reconciliation", "past_future"], "Reconciles feuds between friends, narrates past and future."),
    EntityRecord(8, "Barbatos", "Duke", "Copper", "South", 30, ["animal_speech", "hidden_treasures"], "Understands the singing of birds and the barking of dogs; knows treasure."),
    EntityRecord(9, "Paimon", "King", "Gold", "North", 200, ["sciences", "arts", "binding"], "Great King obedient to Lucifer; teaches all arts, sciences, and secret things."),
    EntityRecord(10, "Buer", "President", "Mercury", "South", 50, ["philosophy", "herbalism", "healing"], "Teaches moral and natural philosophy, logic, and virtues of all herbs."),
    EntityRecord(11, "Gusion", "Duke", "Copper", "East", 40, ["honor", "diplomacy", "past_future"], "Resolves questions, reconciles friendships, confers honor and dignity."),
    EntityRecord(12, "Sitri", "Prince", "Tin", "North", 60, ["love", "desire", "secrets"], "Inflames men with women's love, compels disclosure of hidden secrets."),
    EntityRecord(13, "Beleth", "King", "Gold", "North", 85, ["love", "passion"], "Mighty King who procures love of men and women until desire is satisfied."),
    EntityRecord(14, "Leraje", "Marquis", "Silver", "North", 30, ["archery", "battles", "wounds"], "Causes great battles and contests; causes putrefaction in arrow wounds."),
    EntityRecord(15, "Eligos", "Duke", "Copper", "South", 60, ["military_strategy", "hidden_affairs"], "Discovers hidden things, knows things to come, commands loyalty in war."),
    EntityRecord(16, "Zepar", "Duke", "Copper", "West", 26, ["love", "barrenness"], "Causes women to love men, can bring about barrenness."),
    EntityRecord(17, "Botis", "President", "Mercury", "North", 60, ["past_future", "reconciliation"], "Tells of things past and present, reconciles friends and foes."),
    EntityRecord(18, "Bathin", "Duke", "Copper", "East", 30, ["herbalism", "gemstones", "teleportation"], "Knows virtue of herbs and stones; transports persons swiftly."),
    EntityRecord(19, "Saleos", "Duke", "Copper", "South", 30, ["love", "pacifism"], "Promotes mutual affection and peaceful coexistence between people."),
    EntityRecord(20, "Purson", "King", "Gold", "South", 22, ["hidden_treasures", "cosmology"], "Knows hidden treasures, reveals things past, present, and divine creation."),
    EntityRecord(21, "Morax", "Earl", "Iron", "South", 36, ["astronomy", "herbalism", "sciences"], "Teaches astronomy and liberal sciences; gives good familiars."),
    EntityRecord(22, "Ipos", "Earl", "Iron", "North", 36, ["wit", "courage", "past_future"], "Makes men witty and bold, reveals past, present, and future events."),
    EntityRecord(23, "Aim", "Duke", "Copper", "North", 26, ["wit", "cunning", "fire"], "Gives shrewdness and witty answers, makes men firebrands in intellect."),
    EntityRecord(24, "Naberius", "Marquis", "Silver", "South", 19, ["rhetoric", "dignity", "arts"], "Makes men cunning in all arts and sciences, restores lost dignities."),
    EntityRecord(25, "Glasya-Labolas", "President", "Mercury", "North", 36, ["bloodshed", "sciences", "invisibility"], "Teaches all arts and sciences in an instant, incites manslaughter, causes invisibility."),
    EntityRecord(26, "Bune", "Duke", "Copper", "West", 30, ["wealth", "eloquence", "wisdom"], "Changes the places of the dead, makes men rich, gives eloquence and wisdom."),
    EntityRecord(27, "Ronove", "Marquis", "Silver", "East", 19, ["rhetoric", "languages", "familiars"], "Teaches rhetoric, arts, knowledge of tongues, confers favor of friends and foes."),
    EntityRecord(28, "Berith", "Duke", "Copper", "North", 26, ["alchemy", "dignity", "past_future"], "Turns all metals into gold, confers dignities, answers past and future."),
    EntityRecord(29, "Astaroth", "Duke", "Copper", "West", 40, ["liberal_sciences", "fall_of_angels"], "Answers of things past, present, and future; declares fall of angels."),
    EntityRecord(30, "Forneus", "Marquis", "Silver", "North", 29, ["rhetoric", "languages", "reputation"], "Teaches rhetoric, makes men beloved of friends and enemies alike."),
    EntityRecord(31, "Foras", "President", "Mercury", "North", 29, ["herbalism", "logic", "invisibility"], "Teaches virtues of herbs and gems, logic and ethics, makes men invisible."),
    EntityRecord(32, "Asmoday", "King", "Gold", "East", 72, ["astronomy", "geometry", "invincibility"], "Great King; teaches arithmetic, geometry, astronomy, makes men invincible."),
    EntityRecord(33, "Gaap", "President", "Mercury", "South", 66, ["philosophy", "teleportation", "familiar"], "Rules southern region; causes love or hate, transports men across realms."),
    EntityRecord(34, "Furfur", "Earl", "Iron", "South", 26, ["storms", "love", "divine_secrets"], "Incites love, causes thunder and storms, tells secret divine matters."),
    EntityRecord(35, "Marchosias", "Marquis", "Silver", "South", 30, ["combat", "courage", "honesty"], "Strong fighter, answers all questions truly, faithful to the operator."),
    EntityRecord(36, "Stolas", "Prince", "Tin", "North", 26, ["astronomy", "herbalism", "gemstones"], "Teaches astronomy, virtues of precious stones and plants."),
    EntityRecord(37, "Phenex", "Marquis", "Silver", "East", 20, ["poetry", "sciences", "music"], "Marquis of great wonder; sings sweet notes, teaches sciences, excellent poet, obedient to operator."),
    EntityRecord(38, "Halphas", "Earl", "Iron", "East", 26, ["fortifications", "weapons", "warfare"], "Builds towers and provides weapons, sends men to war."),
    EntityRecord(39, "Malphas", "President", "Mercury", "South", 40, ["construction", "enemy_secrets", "architecture"], "Builds houses and high towers, reveals enemies' desires and thoughts."),
    EntityRecord(40, "Raum", "Earl", "Iron", "North", 30, ["theft", "reconciliation", "past_future"], "Steals treasures out of kings' houses, reconciles friends and foes, speaks of past and future."),
    EntityRecord(41, "Focalor", "Duke", "Copper", "West", 30, ["winds", "storms", "drowning"], "Commands seas and winds, sinks warships and drowns men, hopes to return to the Seventh Throne."),
    EntityRecord(42, "Vepar", "Duke", "Copper", "North", 29, ["naval_guidance", "wounds", "storms"], "Guides naval ships, causes putrefying sores and death within three days."),
    EntityRecord(43, "Sabnock", "Marquis", "Silver", "South", 50, ["fortresses", "architecture", "gangrene"], "Builds towers and castles, afflicts men with gangrenous wounds."),
    EntityRecord(44, "Shax", "Marquis", "Silver", "East", 30, ["sight_deprivation", "theft", "discovery"], "Takes away sight, hearing, and understanding; discovers hidden items."),
    EntityRecord(45, "Vine", "King", "Gold", "North", 36, ["hidden_things", "witchcraft", "towers"], "Discovers hidden things, witches, and future events; builds towers and breaks stones."),
    EntityRecord(46, "Bifrons", "Earl", "Iron", "South", 26, ["geometry", "astronomy", "necromancy", "herbalism"], "Teaches geometry, astrology, virtues of herbs, gems, and woods; moves corpses."),
    EntityRecord(47, "Vual", "Duke", "Copper", "North", 37, ["love", "past_future", "diplomacy"], "Procures love of women, declares things past, present, and to come; wins friendships."),
    EntityRecord(48, "Haagenti", "President", "Mercury", "South", 33, ["alchemy", "transmutation", "wisdom"], "Makes men wise, instructs in transmutation of metals into gold and water into wine."),
    EntityRecord(49, "Crocell", "Duke", "Copper", "North", 48, ["geometry", "sciences", "warm_waters"], "Speaks of things hidden, teaches geometry and liberal arts, warms bodies of water."),
    EntityRecord(50, "Furcas", "Knight", "Lead", "North", 20, ["philosophy", "astronomy", "logic", "rhetoric", "chiromancy"], "Cruel knight; teaches philosophy, astrology, rhetoric, logic, and chiromancy."),
    EntityRecord(51, "Balam", "King", "Gold", "North", 40, ["past_future", "wit", "invisibility"], "Terrible King; gives true answers of past, present, future; makes men witty and invisible."),
    EntityRecord(52, "Alloces", "Duke", "Copper", "South", 36, ["astronomy", "liberal_arts", "familiars"], "Teaches astronomy and liberal arts; gives good familiars."),
    EntityRecord(53, "Camio", "President", "Mercury", "South", 30, ["animal_speech", "water_sounds", "future"], "Teaches the languages of birds, lowing of bullocks, barking of dogs, and sound of waters."),
    EntityRecord(54, "Murmur", "Duke", "Copper", "South", 30, ["philosophy", "necromancy", "souls"], "Teaches philosophy perfectly, constrains departed souls to answer questions."),
    EntityRecord(55, "Orobas", "Prince", "Tin", "West", 20, ["past_future", "divinity", "honor", "truth"], "Declares past, present, future; gives dignities, prefaces true answers concerning the creation."),
    EntityRecord(56, "Gremory", "Duke", "Copper", "South", 26, ["past_future", "hidden_treasures", "love"], "Tells of all things past, present, future; reveals hidden treasures and procures love."),
    EntityRecord(57, "Ose", "President", "Mercury", "North", 30, ["liberal_sciences", "transformation", "secrets"], "Teaches liberal sciences, gives answers to secret divine things, transforms human appearance."),
    EntityRecord(58, "Amy", "President", "Mercury", "South", 36, ["astrology", "liberal_sciences", "familiars"], "Teaches astrology and liberal sciences, gives wonderful familiars, reveals treasures."),
    EntityRecord(59, "Orias", "Marquis", "Silver", "East", 30, ["astronomy", "astrology", "dignity", "transformation"], "Teaches virtues of stars and planets, gives dignities and prelacies, changes shapes."),
    EntityRecord(60, "Vapula", "Duke", "Copper", "South", 36, ["mechanics", "handicrafts", "philosophy"], "Makes men knowing in all handicraft and mechanics, philosophy and sciences."),
    EntityRecord(61, "Zagan", "King", "Gold", "North", 33, ["wit", "alchemy", "transmutation"], "Makes men witty, turns wine into water and blood into wine, turns all metals into coin."),
    EntityRecord(62, "Valac", "President", "Mercury", "West", 38, ["hidden_treasures", "serpents"], "Gives true answers of hidden treasures, reveals where serpents may be found."),
    EntityRecord(63, "Andras", "Marquis", "Silver", "East", 30, ["discord", "feuds", "combat"], "Sows discords and strife, destroys foes and masters if not circumspect."),
    EntityRecord(64, "Haures", "Duke", "Copper", "South", 36, ["past_future", "fire", "divinity"], "Speaks truly of past, present, future; destroys and burns adversaries with fire."),
    EntityRecord(65, "Andrealphus", "Marquis", "Silver", "North", 30, ["geometry", "astronomy", "mensuration"], "Teaches geometry and mensuration perfectly, makes men subtle in astronomy."),
    EntityRecord(66, "Cimejes", "Marquis", "Silver", "North", 20, ["grammar", "logic", "rhetoric", "retrieval"], "Rules all spirits in Africa; teaches grammar, logic, rhetoric; discovers lost items."),
    EntityRecord(67, "Amdusias", "Duke", "Copper", "North", 29, ["music", "instruments", "familiars"], "Commands trees to bend, causes musical instruments to sound without being touched."),
    EntityRecord(68, "Belial", "King", "Gold", "South", 80, ["dignity", "senatorships", "favor_of_friends"], "Created next after Lucifer; distributes senatorships, gives good familiars."),
    EntityRecord(69, "Decarabia", "Marquis", "Silver", "East", 30, ["herbalism", "gemstones", "birds"], "Knows virtues of all herbs and precious stones, makes birds fly before the operator."),
    EntityRecord(70, "Seere", "Prince", "Tin", "East", 26, ["swiftness", "teleportation", "retrieval"], "Under Amaymon; brings things swiftly to pass, transports persons in the blink of an eye."),
    EntityRecord(71, "Dantalion", "Duke", "Copper", "South", 36, ["arts_sciences", "thought_reading", "mind_influence"], "Teaches all arts and sciences, knows secret thoughts of all men and women and changes them."),
    EntityRecord(72, "Andromalius", "Earl", "Iron", "South", 36, ["retrieval", "theft_punishment", "hidden_treasures"], "Brings back both a thief and stolen goods, punishes thieves, discovers underhanded dealings."),
]


class GoeticCorpus:
    """Query, search, and knowledge-graph engine for historical Goetic entities."""

    def __init__(self, records: Optional[List[EntityRecord]] = None):
        self.records = records or HISTORICAL_GOETIC_CATALOG
        self._by_name = {r.name.lower(): r for r in self.records}
        self._by_number = {r.number: r for r in self.records}

    def get_by_name(self, name: str) -> Optional[EntityRecord]:
        return self._by_name.get(name.strip().lower())

    def get_by_number(self, num: int) -> Optional[EntityRecord]:
        return self._by_number.get(num)

    def filter_by_rank(self, rank: str) -> List[EntityRecord]:
        return [r for r in self.records if r.rank.lower() == rank.strip().lower()]

    def filter_by_domain(self, domain_keyword: str) -> List[EntityRecord]:
        kw = domain_keyword.strip().lower()
        return [r for r in self.records if any(kw in d.lower() for d in r.domains)]

    def filter_by_metal(self, metal: str) -> List[EntityRecord]:
        return [r for r in self.records if r.metal.lower() == metal.strip().lower()]

    def get_all_domains(self) -> Set[str]:
        domains = set()
        for r in self.records:
            domains.update(r.domains)
        return domains

    def to_network_graph(self) -> Dict[str, Any]:
        """
        Generate nodes and links for relational knowledge graph visualization.
        Links connect entities sharing ranks, metals, directions, and domains.
        """
        nodes = []
        links = []

        for r in self.records:
            nodes.append({
                "id": r.name,
                "label": f"{r.name} ({r.rank})",
                "number": r.number,
                "group": r.rank,
                "metal": r.metal,
                "direction": r.direction,
                "legions": r.legions,
                "domains": r.domains,
            })

        # Connect entities that share common domains
        for i, a in enumerate(self.records):
            for j, b in enumerate(self.records):
                if i < j:
                    shared_domains = set(a.domains).intersection(set(b.domains))
                    if shared_domains:
                        links.append({
                            "source": a.name,
                            "target": b.name,
                            "relationship": "shares_domain",
                            "weight": len(shared_domains),
                            "domains": sorted(list(shared_domains)),
                        })
                    elif a.rank == b.rank and a.direction == b.direction:
                        links.append({
                            "source": a.name,
                            "target": b.name,
                            "relationship": "same_office_and_direction",
                            "weight": 1,
                            "domains": [],
                        })

        return {
            "metadata": {
                "total_entities": len(self.records),
                "total_relationships": len(links),
                "domains": sorted(list(self.get_all_domains())),
            },
            "nodes": nodes,
            "links": links,
        }

    def export_graph_json(self, output_path: str) -> str:
        data = self.to_network_graph()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return output_path
