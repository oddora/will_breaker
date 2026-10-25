"""
Interactive Ritual Simulator — Turn-Based State Machine & Dynamic Visual Feedback
Simulates interactive ceremonial operations with turn-by-turn risk management,
emergency counter-actions, and live procedural SVG integrity rendering.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Set, Optional, Any, Tuple

from .corpus_graph import GoeticCorpus, EntityRecord
from .sigil_generator import SigilGenerator, SigilConfig
from .ritual_engine import RitualEngine, RitualSchema, RitualStep, StepType, WorldState, FailureMode
from .liturgical_compiler import LiturgicalCompiler, LiturgicalSlots, RiteType


@dataclass
class ActionOutcome:
    action_type: str
    success: bool
    message: str
    integrity_delta: float
    corruption_delta: float
    items_consumed: List[str]
    current_integrity: float
    current_corruption: float
    svg_snapshot_path: Optional[str] = None


class InteractiveRitualSimulator:
    """Turn-based interactive state-machine for ritual containment operations."""

    def __init__(
        self,
        target_entity_name: str = "Paimon",
        output_dir: Optional[Path] = None,
        corpus: Optional[GoeticCorpus] = None,
    ):
        self.corpus = corpus or GoeticCorpus()
        self.entity: Optional[EntityRecord] = self.corpus.get_by_name(target_entity_name)
        if not self.entity:
            raise ValueError(f"Entity '{target_entity_name}' not found in Goetic corpus.")

        self.session_id = f"sim_{self.entity.name.lower()}_{uuid.uuid4().hex[:8]}"
        base_path = output_dir or (Path(__file__).resolve().parent.parent / "results" / "interactive_sessions")
        self.session_dir = base_path / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Map entity metal to planetary archetype
        metal_to_planet = {
            "gold": "sol",
            "silver": "luna",
            "mercury": "mercury",
            "copper": "venus",
            "iron": "mars",
            "tin": "jupiter",
            "lead": "saturn",
        }
        self.planet = metal_to_planet.get(self.entity.metal.lower(), "sol")

        # Compile standard liturgical schema for the entity
        compiler = LiturgicalCompiler(corpus=self.corpus)
        metal_item = f"{self.entity.metal.lower()}_lamen"
        raw_slots = {
            "rite_type": "evocation",
            "target_entity": self.entity.name,
            "officiant": "purified_adept",
            "matter": [metal_item, "consecrated_chalk", "frankincense", "salt"],
            "form": [f"circle_{self.planet}", f"seal_{self.entity.name.lower()}"],
            "temporal_window": ["day", "twilight"],
            "formula_sequence": [
                {
                    "step_id": "step_1_purify",
                    "step_type": "purification",
                    "description": "Purifying space with consecrated salt and circle casting",
                    "required_item": "consecrated_chalk",
                    "target_inscription": f"circle_{self.planet}",
                    "integrity_cost": 0.0,
                },
                {
                    "step_id": "step_2_inscribe",
                    "step_type": "inscription",
                    "description": f"Tracing planetary seal of {self.entity.name}",
                    "required_item": "consecrated_chalk",
                    "target_inscription": f"seal_{self.entity.name.lower()}",
                    "integrity_cost": 0.05,
                },
                {
                    "step_id": "step_3_censing",
                    "step_type": "offering",
                    "description": "Censing the northern boundary with frankincense",
                    "required_item": "frankincense",
                    "integrity_cost": 0.04,
                },
                {
                    "step_id": "step_4_invoke",
                    "step_type": "invocation",
                    "description": f"Reciting formal Goetic constraint for {self.entity.rank} {self.entity.name}",
                    "required_item": metal_item,
                    "target_inscription": f"seal_{self.entity.name.lower()}",
                    "integrity_cost": 0.22, # High stress step
                },
                {
                    "step_id": "step_5_binding",
                    "step_type": "binding",
                    "description": f"Imposing Solomonic covenant upon {self.entity.name}",
                    "required_item": metal_item,
                    "integrity_cost": 0.18, # Boundary strain
                },
                {
                    "step_id": "step_6_dismiss",
                    "step_type": "dismissal",
                    "description": f"Granting license to depart in peace to {self.entity.name}",
                    "required_item": None,
                    "integrity_cost": 0.0,
                },
            ],
            "min_integrity": 0.5,
        }

        compile_res = compiler.compile(raw_slots)
        self.schema: RitualSchema = compile_res.schema

        # Initialize Simulation WorldState
        self.world_state = WorldState(
            circle_integrity=1.0,
            temporal_hour="day",
            inventory={metal_item, "consecrated_chalk", "frankincense", "extra_incense", "salt"},
            active_inscriptions=set(),
            bound_entities=set(),
            corruption_level=0.0,
        )

        self.current_step_index: int = 0
        self.turn: int = 0
        self.is_active: bool = True
        self.is_breached: bool = False
        self.is_completed: bool = False
        self.offering_buff_active: bool = False
        self.action_history: List[ActionOutcome] = []

        # Export initial SVG
        self._export_visual_state("initial_setup")

    def _export_visual_state(self, step_label: str) -> Path:
        """Render and save dynamic SVG with current circle integrity strain."""
        cfg = SigilConfig(
            size=500,
            planet=self.planet,
            animated=True,
            circle_integrity=self.world_state.circle_integrity,
        )
        gen = SigilGenerator(cfg)
        svg_filename = f"turn_{self.turn:02d}_{step_label}.svg"
        out_path = self.session_dir / svg_filename
        gen.save_svg(self.entity.name, out_path)
        return out_path

    def advance_liturgical_step(self) -> ActionOutcome:
        """Execute the next planned step from the liturgical schema."""
        if not self.is_active:
            return ActionOutcome(
                action_type="advance_step",
                success=False,
                message="Session is no longer active.",
                integrity_delta=0.0,
                corruption_delta=0.0,
                items_consumed=[],
                current_integrity=self.world_state.circle_integrity,
                current_corruption=self.world_state.corruption_level,
            )

        if self.current_step_index >= len(self.schema.steps):
            self.is_active = False
            self.is_completed = True
            return ActionOutcome(
                action_type="advance_step",
                success=True,
                message="All liturgical steps already completed successfully.",
                integrity_delta=0.0,
                corruption_delta=0.0,
                items_consumed=[],
                current_integrity=self.world_state.circle_integrity,
                current_corruption=self.world_state.corruption_level,
            )

        self.turn += 1
        step = self.schema.steps[self.current_step_index]

        # 1. Precondition Check: Step item
        if step.required_item and step.required_item not in self.world_state.inventory:
            self.is_active = False
            return ActionOutcome(
                action_type="advance_step",
                success=False,
                message=f"Halted at '{step.step_id}': missing required item '{step.required_item}' in inventory.",
                integrity_delta=0.0,
                corruption_delta=0.0,
                items_consumed=[],
                current_integrity=self.world_state.circle_integrity,
                current_corruption=self.world_state.corruption_level,
            )

        # 2. Compute Integrity Cost
        cost = step.integrity_cost
        if self.offering_buff_active and step.step_type in (StepType.INVOCATION, StepType.BINDING):
            cost *= 0.5
            self.offering_buff_active = False

        prev_integrity = self.world_state.circle_integrity
        prev_corruption = self.world_state.corruption_level

        # 3. State Transitions
        if step.step_type == StepType.PURIFICATION:
            self.world_state.corruption_level = max(0.0, self.world_state.corruption_level - 0.2)
            self.world_state.circle_integrity = min(1.0, self.world_state.circle_integrity + 0.1)
        elif step.step_type == StepType.INSCRIPTION:
            if step.target_inscription:
                self.world_state.active_inscriptions.add(step.target_inscription)
        elif step.step_type == StepType.OFFERING:
            self.world_state.circle_integrity -= (cost * 0.5)
        elif step.step_type == StepType.INVOCATION:
            self.world_state.circle_integrity -= cost
            self.world_state.corruption_level += 0.05
        elif step.step_type == StepType.BINDING:
            self.world_state.circle_integrity -= cost
            self.world_state.bound_entities.add(self.entity.name)
        elif step.step_type == StepType.DISMISSAL:
            self.world_state.corruption_level = max(0.0, self.world_state.corruption_level - 0.1)

        self.current_step_index += 1

        # 4. Invariant Check (Circle Integrity >= 0.5)
        if self.world_state.circle_integrity < self.schema.min_circle_integrity:
            self.is_active = False
            self.is_breached = True
            self.world_state.corruption_level = min(1.0, self.world_state.corruption_level + 0.5)
            svg_path = self._export_visual_state(f"{step.step_id}_BREACH")
            outcome = ActionOutcome(
                action_type="advance_step",
                success=False,
                message=f"CONTAINMENT BREACH during '{step.step_id}'! Circle integrity fell to {self.world_state.circle_integrity:.2f} (< {self.schema.min_circle_integrity:.2f}).",
                integrity_delta=round(self.world_state.circle_integrity - prev_integrity, 3),
                corruption_delta=round(self.world_state.corruption_level - prev_corruption, 3),
                items_consumed=[],
                current_integrity=self.world_state.circle_integrity,
                current_corruption=self.world_state.corruption_level,
                svg_snapshot_path=str(svg_path),
            )
            self.action_history.append(outcome)
            return outcome

        # Completion check
        if self.current_step_index >= len(self.schema.steps):
            self.is_active = False
            self.is_completed = True
            msg = f"Step '{step.step_id}' executed. Ritual COMPLETED. {self.entity.name} bound successfully."
        else:
            msg = f"Step '{step.step_id}' executed: {step.description}."

        svg_path = self._export_visual_state(step.step_id)
        outcome = ActionOutcome(
            action_type="advance_step",
            success=True,
            message=msg,
            integrity_delta=round(self.world_state.circle_integrity - prev_integrity, 3),
            corruption_delta=round(self.world_state.corruption_level - prev_corruption, 3),
            items_consumed=[],
            current_integrity=round(self.world_state.circle_integrity, 3),
            current_corruption=round(self.world_state.corruption_level, 3),
            svg_snapshot_path=str(svg_path),
        )
        self.action_history.append(outcome)
        return outcome

    def emergency_banish(self) -> ActionOutcome:
        """Emergency banishing: consumes consecrated chalk/salt to reinforce circle boundary."""
        if not self.is_active:
            return ActionOutcome("emergency_banish", False, "Session not active.", 0, 0, [], self.world_state.circle_integrity, self.world_state.corruption_level)

        if "salt" not in self.world_state.inventory and "consecrated_chalk" not in self.world_state.inventory:
            return ActionOutcome("emergency_banish", False, "No salt or chalk available in inventory for banishing.", 0, 0, [], self.world_state.circle_integrity, self.world_state.corruption_level)

        self.turn += 1
        consumed = []
        if "salt" in self.world_state.inventory:
            self.world_state.inventory.remove("salt")
            consumed.append("salt")
        elif "consecrated_chalk" in self.world_state.inventory:
            self.world_state.inventory.remove("consecrated_chalk")
            consumed.append("consecrated_chalk")

        prev_integrity = self.world_state.circle_integrity
        prev_corruption = self.world_state.corruption_level

        # Reinforce boundary +0.25, reduce corruption -0.20
        self.world_state.circle_integrity = min(1.0, self.world_state.circle_integrity + 0.25)
        self.world_state.corruption_level = max(0.0, self.world_state.corruption_level - 0.20)

        svg_path = self._export_visual_state("emergency_banish")
        outcome = ActionOutcome(
            action_type="emergency_banish",
            success=True,
            message=f"Emergency banishing performed! Boundary reinforced (+0.25).",
            integrity_delta=round(self.world_state.circle_integrity - prev_integrity, 3),
            corruption_delta=round(self.world_state.corruption_level - prev_corruption, 3),
            items_consumed=consumed,
            current_integrity=round(self.world_state.circle_integrity, 3),
            current_corruption=round(self.world_state.corruption_level, 3),
            svg_snapshot_path=str(svg_path),
        )
        self.action_history.append(outcome)
        return outcome

    def offer_additional_incense(self) -> ActionOutcome:
        """Offers extra frankincense to stabilize atmospheric pressure, halving next step cost."""
        if not self.is_active:
            return ActionOutcome("offer_incense", False, "Session not active.", 0, 0, [], self.world_state.circle_integrity, self.world_state.corruption_level)

        consumed = []
        if "extra_incense" in self.world_state.inventory:
            self.world_state.inventory.remove("extra_incense")
            consumed.append("extra_incense")
        elif "frankincense" in self.world_state.inventory:
            self.world_state.inventory.remove("frankincense")
            consumed.append("frankincense")
        else:
            return ActionOutcome("offer_incense", False, "No incense remaining in inventory.", 0, 0, [], self.world_state.circle_integrity, self.world_state.corruption_level)

        self.turn += 1
        self.offering_buff_active = True

        svg_path = self._export_visual_state("extra_incense")
        outcome = ActionOutcome(
            action_type="offer_incense",
            success=True,
            message="Additional frankincense cast into censer. Atmospheric buffer active (next step integrity cost halved).",
            integrity_delta=0.0,
            corruption_delta=0.0,
            items_consumed=consumed,
            current_integrity=round(self.world_state.circle_integrity, 3),
            current_corruption=round(self.world_state.corruption_level, 3),
            svg_snapshot_path=str(svg_path),
        )
        self.action_history.append(outcome)
        return outcome

    def abort_early_dismissal(self) -> ActionOutcome:
        """Safely dismisses entity and closes circle prematurely to avert collapse."""
        if not self.is_active:
            return ActionOutcome("abort_dismissal", False, "Session not active.", 0, 0, [], self.world_state.circle_integrity, self.world_state.corruption_level)

        self.turn += 1
        self.is_active = False
        svg_path = self._export_visual_state("early_abort")
        outcome = ActionOutcome(
            action_type="abort_dismissal",
            success=True,
            message="License to depart pronounced early. Containment safely dissolved.",
            integrity_delta=0.0,
            corruption_delta=-0.1,
            items_consumed=[],
            current_integrity=round(self.world_state.circle_integrity, 3),
            current_corruption=round(self.world_state.corruption_level, 3),
            svg_snapshot_path=str(svg_path),
        )
        self.action_history.append(outcome)
        return outcome

    def get_summary(self) -> Dict[str, Any]:
        """Return comprehensive status report of the interactive session."""
        return {
            "session_id": self.session_id,
            "target_entity": self.entity.name,
            "canonical_rank": self.entity.rank,
            "planet": self.planet,
            "turns_taken": self.turn,
            "steps_completed": self.current_step_index,
            "total_steps": len(self.schema.steps),
            "circle_integrity": round(self.world_state.circle_integrity, 3),
            "corruption_level": round(self.world_state.corruption_level, 3),
            "is_completed": self.is_completed,
            "is_breached": self.is_breached,
            "bound_entities": list(self.world_state.bound_entities),
            "remaining_inventory": sorted(list(self.world_state.inventory)),
            "snapshots_dir": str(self.session_dir),
        }
