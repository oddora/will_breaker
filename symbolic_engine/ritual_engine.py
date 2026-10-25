"""
Ritual Engine — Constraint Satisfaction & State-Machine Logic for Ritual Systems
Models historical ritual frameworks as formal computational state machines with
typed preconditions, invariants, execution sequences, and failure modes.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Set, Optional, Any, Tuple


class StepType(Enum):
    PURIFICATION = "purification"       # e.g., ablution, banishing
    CONSECRATION = "consecration"       # e.g., sanctifying space or tools
    INSCRIPTION = "inscription"         # e.g., drawing circle, sigil display
    INVOCATION = "invocation"           # e.g., recitation of formal formula
    OFFERING = "offering"               # e.g., incense, symbolic sacrifice
    DISMISSAL = "dismissal"             # e.g., license to depart


class FailureMode(Enum):
    NONE = "none"
    PRECONDITION_UNMET = "precondition_unmet"
    INVARIANT_BREACH = "invariant_breach"
    SEQUENCE_VIOLATION = "sequence_violation"
    HERMENEUTIC_SCHISM = "hermeneutic_schism"


@dataclass
class WorldState:
    """Current state of the simulated game/narrative environment."""
    circle_integrity: float = 1.0       # 0.0 to 1.0 (breached if < 0.5)
    temporal_hour: str = "day"          # "day", "night", "twilight", "solstice"
    inventory: Set[str] = field(default_factory=set)
    active_inscriptions: Set[str] = field(default_factory=set)
    elemental_affinity: str = "neutral"
    bound_entities: Set[str] = field(default_factory=set)
    corruption_level: float = 0.0       # 0.0 to 1.0


@dataclass
class RitualStep:
    step_id: str
    step_type: StepType
    description: str
    required_item: Optional[str] = None
    target_inscription: Optional[str] = None
    integrity_cost: float = 0.05        # Stress on ritual boundary


@dataclass
class RitualSchema:
    ritual_id: str
    name: str
    target_entity: str
    required_items: Set[str]
    allowed_temporal_hours: Set[str]
    steps: List[RitualStep]
    min_circle_integrity: float = 0.5
    success_outcome: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RitualValidationResult:
    is_valid: bool
    status: str
    failure_mode: FailureMode
    errors: List[str]
    executed_steps: int
    final_world_state: WorldState
    outcome: Optional[Dict[str, Any]] = None


class RitualEngine:
    """Evaluates and executes rituals against formal world-state constraints."""

    def __init__(self):
        pass

    def validate_and_execute(self, schema: RitualSchema, initial_state: WorldState) -> RitualValidationResult:
        """
        Check all preconditions, invariants, and step executions.
        Returns detailed validation result with state transitions or failure modes.
        """
        errors = []
        state = WorldState(
            circle_integrity=initial_state.circle_integrity,
            temporal_hour=initial_state.temporal_hour,
            inventory=set(initial_state.inventory),
            active_inscriptions=set(initial_state.active_inscriptions),
            elemental_affinity=initial_state.elemental_affinity,
            bound_entities=set(initial_state.bound_entities),
            corruption_level=initial_state.corruption_level,
        )

        # 1. Precondition Checks: Items
        missing_items = schema.required_items - state.inventory
        if missing_items:
            errors.append(f"Missing required ceremonial items: {sorted(list(missing_items))}")

        # 2. Precondition Checks: Temporal Window
        if schema.allowed_temporal_hours and state.temporal_hour not in schema.allowed_temporal_hours:
            errors.append(
                f"Temporal misalignment: ritual requires hours {sorted(list(schema.allowed_temporal_hours))}, but current state is '{state.temporal_hour}'"
            )

        # 3. Precondition Checks: Circle Integrity
        if state.circle_integrity < schema.min_circle_integrity:
            errors.append(
                f"Circle integrity {state.circle_integrity:.2f} below minimum threshold {schema.min_circle_integrity:.2f}"
            )

        if errors:
            return RitualValidationResult(
                is_valid=False,
                status="UNSAT_PRECONDITIONS",
                failure_mode=FailureMode.PRECONDITION_UNMET,
                errors=errors,
                executed_steps=0,
                final_world_state=state,
                outcome=None,
            )

        # 4. Sequential Step Execution & Invariant Monitoring
        executed = 0
        has_banishing = False

        for step in schema.steps:
            # Check item required for specific step
            if step.required_item and step.required_item not in state.inventory:
                errors.append(f"Step '{step.step_id}' failed: missing '{step.required_item}'")
                return RitualValidationResult(
                    is_valid=False,
                    status=f"FAILED_AT_STEP_{executed}",
                    failure_mode=FailureMode.PRECONDITION_UNMET,
                    errors=errors,
                    executed_steps=executed,
                    final_world_state=state,
                    outcome=None,
                )

            # Apply state transition
            if step.step_type == StepType.PURIFICATION:
                state.corruption_level = max(0.0, state.corruption_level - 0.2)
                state.circle_integrity = min(1.0, state.circle_integrity + 0.1)
                has_banishing = True
            elif step.step_type == StepType.INSCRIPTION:
                if step.target_inscription:
                    state.active_inscriptions.add(step.target_inscription)
            elif step.step_type == StepType.INVOCATION:
                state.circle_integrity -= step.integrity_cost
                state.corruption_level += 0.05
            elif step.step_type == StepType.OFFERING:
                state.circle_integrity -= (step.integrity_cost * 0.5)

            # Invariant Check: Circle integrity must remain >= min threshold
            if state.circle_integrity < schema.min_circle_integrity:
                errors.append(
                    f"Invariant breach during step '{step.step_id}': circle integrity collapsed to {state.circle_integrity:.2f}"
                )
                state.corruption_level = min(1.0, state.corruption_level + 0.5)
                return RitualValidationResult(
                    is_valid=False,
                    status="CONTAINMENT_BREACH",
                    failure_mode=FailureMode.INVARIANT_BREACH,
                    errors=errors,
                    executed_steps=executed,
                    final_world_state=state,
                    outcome={"catastrophe": "Entity containment collapsed; liminal state triggered."},
                )

            executed += 1

        # 5. Success Resolution
        state.bound_entities.add(schema.target_entity)
        resolved_outcome = {
            "entity": schema.target_entity,
            "status": "BOUND",
            "narrative": f"The invocation of {schema.target_entity} succeeded. Inscriptions verified.",
            **schema.success_outcome,
        }

        return RitualValidationResult(
            is_valid=True,
            status="SAT_COMPLETED",
            failure_mode=FailureMode.NONE,
            errors=[],
            executed_steps=executed,
            final_world_state=state,
            outcome=resolved_outcome,
        )
