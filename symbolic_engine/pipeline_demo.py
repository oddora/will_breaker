"""
End-to-End Pipeline Demo for Symbolic Engine
Sequentially executes:
1. Historical Corpus Lookup & Taxonomy Mining
2. Procedural Parametric Vector Sigil Generation (SVG output)
3. Formal Ritual Constraint Satisfaction & State-Machine Execution
4. Relational Knowledge Graph Export
"""

import sys
from pathlib import Path

# Add project root to path
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from symbolic_engine import (
    SigilGenerator, SigilConfig,
    RitualEngine, RitualSchema, RitualStep,
    GoeticCorpus
)
from symbolic_engine.ritual_engine import StepType, WorldState


def run_demo():
    print("=" * 65)
    print("SYMBOLIC ENGINE — END-TO-END DEMO PIPELINE")
    print("=" * 65)

    out_dir = base_dir / "results" / "symbolic_engine"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # STEP 1: Corpus Query & Taxonomy Mining
    # ---------------------------------------------------------
    print("\n[STEP 1] Querying Historical Goetic Corpus...")
    corpus = GoeticCorpus()
    target_name = "Paimon"
    entity = corpus.get_by_name(target_name)
    print(f"  Target: {entity.name} (Rank: {entity.rank}, Metal: {entity.metal})")
    print(f"  Direction: {entity.direction} | Legions: {entity.legions}")
    print(f"  Domains: {', '.join(entity.domains)}")
    print(f"  Description: {entity.description}")

    # Related spirits in same domains
    related = corpus.filter_by_domain("sciences")
    print(f"  Related spirits ruling over 'sciences': {[e.name for e in related]}")

    # ---------------------------------------------------------
    # STEP 2: Procedural Vector Sigil Synthesis
    # ---------------------------------------------------------
    print(f"\n[STEP 2] Procedurally Generating Vector Sigil for {entity.name}...")
    cfg = SigilConfig(
        size=500,
        polygon_points=6,  # Hexagonal Solomonic geometry
        bg_color="#0d1117",
        primary_color="#c9d1d9",
        accent_color="#58a6ff",
        gold_color="#d29922",
    )
    generator = SigilGenerator(cfg)
    sigil_path = out_dir / f"{entity.name.lower()}_seal.svg"
    generator.save_svg(entity.name, sigil_path)
    print(f"  SVG Sigil generated and saved: {sigil_path}")
    print(f"  File size: {sigil_path.stat().st_size} bytes")

    # Generate a second seal for Buer (healing)
    buer_path = out_dir / "buer_seal.svg"
    generator.save_svg("Buer", buer_path)
    print(f"  SVG Sigil for Buer generated: {buer_path}")

    # ---------------------------------------------------------
    # STEP 3: Ritual Constraint Satisfaction & State Machine
    # ---------------------------------------------------------
    print(f"\n[STEP 3] Evaluating Ritual Logic via Constraint State Machine...")
    engine = RitualEngine()

    schema = RitualSchema(
        ritual_id="rit_paimon_evocation",
        name="Ceremonial Assembly of Paimon",
        target_entity="Paimon",
        required_items={"gold_lamen", "frankincense", "consecrated_circle", "bell"},
        allowed_temporal_hours={"day", "twilight"},
        min_circle_integrity=0.6,
        steps=[
            RitualStep("s1", StepType.PURIFICATION, "Casting banishing circle and bell chiming"),
            RitualStep("s2", StepType.INSCRIPTION, "Presenting procedurally generated seal of Paimon", target_inscription="seal_paimon"),
            RitualStep("s3", StepType.OFFERING, "Offering frankincense to northern quarter", integrity_cost=0.05),
            RitualStep("s4", StepType.INVOCATION, "Reciting primary formal constraint formula", integrity_cost=0.15),
            RitualStep("s5", StepType.DISMISSAL, "License to depart with bound pacification"),
        ],
        success_outcome={
            "boon": "Attained mastery of philosophical sciences",
            "entity_alignment": "Paimon obedient to royal covenant",
        }
    )

    # Test 3a: Flawed state (Missing items)
    flawed_state = WorldState(
        circle_integrity=1.0,
        temporal_hour="night",  # Wrong hour!
        inventory={"gold_lamen"},  # Missing bell, frankincense, circle!
    )
    flawed_res = engine.validate_and_execute(schema, flawed_state)
    print(f"  [Run 3a: Missing Preconditions]")
    print(f"    Status: {flawed_res.status} (Valid: {flawed_res.is_valid})")
    print(f"    Failure Mode: {flawed_res.failure_mode.value}")
    for err in flawed_res.errors:
        print(f"      - {err}")

    # Test 3b: Valid state (All type-checks pass)
    valid_state = WorldState(
        circle_integrity=1.0,
        temporal_hour="day",
        inventory={"gold_lamen", "frankincense", "consecrated_circle", "bell"},
    )
    valid_res = engine.validate_and_execute(schema, valid_state)
    print(f"\n  [Run 3b: Satisfied Preconditions & Invariants]")
    print(f"    Status: {valid_res.status} (Valid: {valid_res.is_valid})")
    print(f"    Steps Executed: {valid_res.executed_steps}/{len(schema.steps)}")
    print(f"    Final Circle Integrity: {valid_res.final_world_state.circle_integrity:.2f}")
    print(f"    Bound Entities: {list(valid_res.final_world_state.bound_entities)}")
    print(f"    Outcome: {valid_res.outcome['narrative']}")

    # ---------------------------------------------------------
    # STEP 4: Relational Knowledge Graph Export
    # ---------------------------------------------------------
    print(f"\n[STEP 4] Exporting Relational Goetic Knowledge Graph...")
    graph_path = out_dir / "goetic_knowledge_graph.json"
    corpus.export_graph_json(str(graph_path))
    graph_data = corpus.to_network_graph()
    print(f"  Knowledge graph exported: {graph_path}")
    print(f"  Total Entities (Nodes): {graph_data['metadata']['total_entities']}")
    print(f"  Total Relationships (Links): {graph_data['metadata']['total_relationships']}")
    print(f"  Taxonomic Domains: {len(graph_data['metadata']['domains'])}")

    print("\n" + "=" * 65)
    print("ALL 3 PHASES COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    run_demo()
