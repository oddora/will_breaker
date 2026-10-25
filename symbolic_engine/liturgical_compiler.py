"""
Liturgical Compiler — Formal Slot-Filling & Constraint Validation Compiler
Translates natural language ritual intents and liturgical slots into typed,
executable RitualSchemas verified against Goetic canonical correspondences.
Integrates with local MoE LLM (KAT) for automated slot extraction.
"""

import json
import re
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Set, Optional, Any, Union

from .corpus_graph import GoeticCorpus, EntityRecord
from .ritual_engine import (
    RitualEngine,
    RitualSchema,
    RitualStep,
    RitualValidationResult,
    StepType,
    WorldState,
    FailureMode,
)


class RiteType(str, Enum):
    CONSECRATION = "consecration"
    EVOCATION = "evocation"
    HEALING = "healing"
    BANISHING = "banishing"
    DIVINATION = "divination"
    BINDING = "binding"


class SlotValidationError(Exception):
    """Raised when liturgical slot constraints are violated."""
    pass


@dataclass
class LiturgicalSlots:
    """Formal liturgical slot representation of a ritual working."""
    rite_type: RiteType
    target_entity: Optional[str] = None
    officiant: str = "purified_adept"
    matter: List[str] = field(default_factory=list)
    form: List[str] = field(default_factory=list)
    temporal_window: List[str] = field(default_factory=lambda: ["day"])
    formula_sequence: List[Dict[str, Any]] = field(default_factory=list)
    min_integrity: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompilationResult:
    """Result of compiling liturgical slots into an executable RitualSchema."""
    success: bool
    schema: Optional[RitualSchema] = None
    slots: Optional[LiturgicalSlots] = None
    diagnostics: List[str] = field(default_factory=list)
    source: str = "direct"
    entity_record: Optional[EntityRecord] = None


class LiturgicalCompiler:
    """
    Slot-filler compiler mapping ritual intent to typed RitualSchema definitions.
    Enforces canonical correspondences (Goetic rank, metal, direction, timing)
    and verifies slot completeness before generating state-machine steps.
    """

    KAT_SYSTEM_PROMPT = """You are a formal liturgical compiler for ceremonial magic systems.
Given a natural language ritual intent, parse and compile it into a strict JSON object with this exact schema:
{
  "rite_type": "evocation", // one of: "consecration", "evocation", "healing", "banishing", "divination", "binding"
  "target_entity": "Paimon", // string entity name or null
  "officiant": "purified_adept", // string role
  "matter": ["item1", "item2"], // list of string items (all lowercase snake_case)
  "form": ["inscription1"], // list of string inscriptions/seals (lowercase snake_case)
  "temporal_window": ["day"], // subset of ["day", "night", "twilight", "solstice"]
  "formula_sequence": [
    {
      "step_id": "step_1",
      "step_type": "purification", // one of: "purification", "consecration", "inscription", "invocation", "offering", "binding", "dismissal"
      "description": "Action description",
      "required_item": "item1", // item from matter or null
      "target_inscription": "inscription1", // inscription from form or null
      "integrity_cost": 0.05 // float between 0.0 and 0.5
    }
  ]
}
Output ONLY the raw JSON object, without extra conversational text.
"""

    # Canonical Rank-Metal Correspondences from historical Goetic manuscripts
    RANK_METALS = {
        "king": "gold",
        "president": "mercury",
        "duke": "copper",
        "prince": "tin",
        "marquis": "silver",
        "earl": "iron",
        "knight": "lead",
    }

    # Canonical Temporal Associations
    RANK_TEMPORAL_HOURS = {
        "king": {"day", "solstice"},
        "president": {"day", "twilight"},
        "duke": {"day", "twilight"},
        "prince": {"day", "night"},
        "marquis": {"night"},
        "earl": {"night", "twilight"},
        "knight": {"night"},
    }

    # Step type canonical synonyms for flexible LLM extraction
    STEP_TYPE_SYNONYMS = {
        "purification": StepType.PURIFICATION,
        "cleansing": StepType.PURIFICATION,
        "ablution": StepType.PURIFICATION,
        "banishing": StepType.PURIFICATION,
        "consecration": StepType.CONSECRATION,
        "sanctification": StepType.CONSECRATION,
        "inscription": StepType.INSCRIPTION,
        "drawing": StepType.INSCRIPTION,
        "sigil": StepType.INSCRIPTION,
        "invocation": StepType.INVOCATION,
        "evocation": StepType.INVOCATION,
        "conjuration": StepType.INVOCATION,
        "recitation": StepType.INVOCATION,
        "offering": StepType.OFFERING,
        "incense": StepType.OFFERING,
        "sacrifice": StepType.OFFERING,
        "binding": StepType.BINDING,
        "covenant": StepType.BINDING,
        "dismissal": StepType.DISMISSAL,
        "license_to_depart": StepType.DISMISSAL,
        "release": StepType.DISMISSAL,
    }

    def __init__(
        self,
        corpus: Optional[GoeticCorpus] = None,
        endpoint: str = "http://127.0.0.1:18283",
        model_name: str = "kat",
    ):
        self.corpus = corpus or GoeticCorpus()
        self.endpoint = endpoint.rstrip("/")
        self.model_name = model_name
        self.engine = RitualEngine()

    def is_endpoint_available(self) -> bool:
        """Check if LLM sidecar is reachable."""
        try:
            req = urllib.request.Request(
                f"{self.endpoint}/health",
                headers={"User-Agent": "WillBreaker-LiturgicalCompiler/1.0"}
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                return resp.getcode() == 200
        except Exception:
            return False

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract and sanitize JSON from model output text."""
        # 1. Strip <think>...</think> if present
        clean_text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()

        # 2. Extract from markdown code blocks if present
        code_block = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_text)
        candidate = code_block.group(1).strip() if code_block else clean_text

        # 3. Locate outer JSON brackets
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = candidate[start : end + 1]

        # 4. Remove trailing commas before closing braces/brackets
        candidate = re.sub(r",\s*([\]}])", r"\1", candidate)

        try:
            return json.loads(candidate)
        except json.JSONDecodeError as e:
            raise SlotValidationError(f"Failed to parse LLM JSON output: {e}\nRaw candidate: {candidate[:200]}")

    def query_kat(
        self,
        intent: str,
        temperature: float = 0.1,
        max_tokens: int = 1024,
        timeout: float = 60.0,
    ) -> Dict[str, Any]:
        """Send natural language ritual intent to KAT and extract raw slots."""
        payload = json.dumps({
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.KAT_SYSTEM_PROMPT},
                {"role": "user", "content": intent},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.endpoint}/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "WillBreaker-LiturgicalCompiler/1.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                choice = resp_data.get("choices", [{}])[0]
                content = choice.get("message", {}).get("content", "")
                return self._extract_json_from_text(content)
        except Exception as err:
            raise SlotValidationError(f"KAT endpoint error during slot extraction: {err}")

    def parse_slots_from_dict(self, data: Dict[str, Any]) -> LiturgicalSlots:
        """Parse and normalize a dictionary into LiturgicalSlots."""
        # Normalize rite_type
        raw_rite = data.get("rite_type", "evocation")
        try:
            rite_type = RiteType(str(raw_rite).lower().strip())
        except ValueError:
            raise SlotValidationError(f"Invalid rite_type '{raw_rite}'. Must be one of {[r.value for r in RiteType]}")

        target_entity = data.get("target_entity")
        if target_entity:
            target_entity = str(target_entity).strip()
            if target_entity.lower() in ("none", "null", ""):
                target_entity = None

        officiant = str(data.get("officiant", "purified_adept")).strip()

        # Normalize matter
        matter_raw = data.get("matter", [])
        if isinstance(matter_raw, str):
            matter_raw = [matter_raw]
        matter = [str(m).strip().lower().replace(" ", "_") for m in matter_raw if m]

        # Normalize form
        form_raw = data.get("form", [])
        if isinstance(form_raw, str):
            form_raw = [form_raw]
        form = [str(f).strip().lower().replace(" ", "_") for f in form_raw if f]

        # Normalize temporal_window
        tw_raw = data.get("temporal_window", ["day"])
        if isinstance(tw_raw, str):
            tw_raw = [tw_raw]
        valid_hours = {"day", "night", "twilight", "solstice"}
        temporal_window = [str(h).strip().lower() for h in tw_raw if str(h).strip().lower() in valid_hours]
        if not temporal_window:
            temporal_window = ["day"]

        # Normalize formula_sequence
        seq_raw = data.get("formula_sequence", [])
        formula_sequence = []
        for idx, step_dict in enumerate(seq_raw):
            step_id = step_dict.get("step_id", f"step_{idx+1}")
            raw_st = str(step_dict.get("step_type", "invocation")).lower().strip()
            if raw_st in self.STEP_TYPE_SYNONYMS:
                st = self.STEP_TYPE_SYNONYMS[raw_st]
            else:
                try:
                    st = StepType(raw_st)
                except ValueError:
                    raise SlotValidationError(f"Invalid step_type '{raw_st}' at step '{step_id}'. Valid: {[s.value for s in StepType]}")

            req_item = step_dict.get("required_item")
            if req_item:
                req_item = str(req_item).strip().lower().replace(" ", "_")
                if req_item in ("none", "null", ""):
                    req_item = None

            target_inscr = step_dict.get("target_inscription")
            if target_inscr:
                target_inscr = str(target_inscr).strip().lower().replace(" ", "_")
                if target_inscr in ("none", "null", ""):
                    target_inscr = None

            cost = float(step_dict.get("integrity_cost", 0.05))

            formula_sequence.append({
                "step_id": step_id,
                "step_type": st,
                "description": step_dict.get("description", f"Execute {st.value}"),
                "required_item": req_item,
                "target_inscription": target_inscr,
                "integrity_cost": cost,
            })

        min_integrity = float(data.get("min_integrity", 0.5))

        return LiturgicalSlots(
            rite_type=rite_type,
            target_entity=target_entity,
            officiant=officiant,
            matter=matter,
            form=form,
            temporal_window=temporal_window,
            formula_sequence=formula_sequence,
            min_integrity=min_integrity,
            metadata=data.get("metadata", {}),
        )

    def validate_slots(
        self,
        slots: LiturgicalSlots,
        strict_canonical: bool = False,
    ) -> List[str]:
        """
        Validate liturgical slots against structural and canonical constraints.
        Returns a list of diagnostic error strings (empty if valid).
        """
        errors = []

        # 1. Structural Validation
        if not slots.matter and slots.rite_type in (RiteType.EVOCATION, RiteType.CONSECRATION, RiteType.HEALING):
            errors.append(f"Rite '{slots.rite_type.value}' requires tangible matter (matter slot is empty).")

        if not slots.formula_sequence:
            errors.append("Formula sequence is empty; ritual must contain at least one step.")

        # Check required items in steps exist in matter
        matter_set = set(slots.matter)
        for step in slots.formula_sequence:
            req = step.get("required_item")
            if req and req not in matter_set:
                matched = any(req == m or req in m or m in req for m in matter_set)
                if not matched:
                    errors.append(
                        f"Step '{step.get('step_id')}' requires item '{req}' which is missing from declared matter."
                    )

        # Check inscriptions in steps exist in form (if form declared)
        if slots.form:
            form_set = set(slots.form)
            for step in slots.formula_sequence:
                inscr = step.get("target_inscription")
                if inscr and inscr not in form_set:
                    matched = any(inscr == f or inscr in f or f in inscr for f in form_set)
                    if not matched:
                        errors.append(
                            f"Step '{step.get('step_id')}' references inscription '{inscr}' not declared in form."
                        )

        # 2. Canonical Validation against Historical Goetic Corpus
        if slots.target_entity:
            record = self.corpus.get_by_name(slots.target_entity)
            if record is None:
                if strict_canonical:
                    errors.append(f"Target entity '{slots.target_entity}' not found in Goetic corpus.")
            else:
                expected_metal = self.RANK_METALS.get(record.rank.lower())
                if expected_metal:
                    # Check if matter contains correspondence with the metal
                    has_metal_correspondence = any(expected_metal in item.lower() for item in slots.matter)
                    # For presidents (Mercury), brass or herbs are also traditionally acceptable
                    if record.rank.lower() == "president" and any(m in ("brass_vessel", "laurel_leaves", "mercurial_incense") for m in slots.matter):
                        has_metal_correspondence = True

                    if not has_metal_correspondence:
                        errors.append(
                            f"Canonical mismatch: {record.rank} {record.name} requires {expected_metal.upper()} implement in matter."
                        )

                # Temporal correspondence check
                allowed_hours = self.RANK_TEMPORAL_HOURS.get(record.rank.lower())
                if allowed_hours:
                    overlap = set(slots.temporal_window).intersection(allowed_hours)
                    if not overlap:
                        errors.append(
                            f"Temporal misalignment: {record.rank} {record.name} requires hours {sorted(list(allowed_hours))}, but slot specified {slots.temporal_window}."
                        )

        return errors

    def compile(
        self,
        slots_or_dict: Union[LiturgicalSlots, Dict[str, Any]],
        strict_canonical: bool = False,
        source: str = "direct",
    ) -> CompilationResult:
        """
        Compile LiturgicalSlots or slot dict into an executable RitualSchema.
        """
        diagnostics = []
        try:
            if isinstance(slots_or_dict, dict):
                slots = self.parse_slots_from_dict(slots_or_dict)
            else:
                slots = slots_or_dict
        except SlotValidationError as e:
            return CompilationResult(
                success=False,
                diagnostics=[str(e)],
                source=source,
            )

        # Validate slots
        validation_errors = self.validate_slots(slots, strict_canonical=strict_canonical)
        if validation_errors:
            diagnostics.extend(validation_errors)
            return CompilationResult(
                success=False,
                slots=slots,
                diagnostics=diagnostics,
                source=source,
            )

        # Fetch canonical entity record if applicable
        entity_rec = None
        if slots.target_entity:
            entity_rec = self.corpus.get_by_name(slots.target_entity)

        # Construct RitualSteps
        steps = []
        for s in slots.formula_sequence:
            st = s["step_type"] if isinstance(s["step_type"], StepType) else StepType(s["step_type"])
            steps.append(
                RitualStep(
                    step_id=s["step_id"],
                    step_type=st,
                    description=s["description"],
                    required_item=s.get("required_item"),
                    target_inscription=s.get("target_inscription"),
                    integrity_cost=s.get("integrity_cost", 0.05),
                )
            )

        # Build RitualSchema
        entity_slug = (slots.target_entity or "consecration").lower().replace(" ", "_")
        ritual_id = f"rit_{slots.rite_type.value}_{entity_slug}"
        name = f"{slots.rite_type.value.capitalize()} of {slots.target_entity or 'Sacred Space'}"

        success_outcome = {
            "rite_type": slots.rite_type.value,
            "officiant": slots.officiant,
            "matter_used": list(slots.matter),
            "form_inscribed": list(slots.form),
        }
        if entity_rec:
            success_outcome["canonical_rank"] = entity_rec.rank
            success_outcome["canonical_metal"] = entity_rec.metal
            success_outcome["legions"] = entity_rec.legions
            success_outcome["domains"] = entity_rec.domains

        schema = RitualSchema(
            ritual_id=ritual_id,
            name=name,
            target_entity=slots.target_entity or "None",
            required_items=set(slots.matter),
            allowed_temporal_hours=set(slots.temporal_window),
            steps=steps,
            min_circle_integrity=slots.min_integrity,
            success_outcome=success_outcome,
        )

        return CompilationResult(
            success=True,
            schema=schema,
            slots=slots,
            diagnostics=[],
            source=source,
            entity_record=entity_rec,
        )

    def compile_from_intent(
        self,
        intent: str,
        strict_canonical: bool = False,
        timeout: float = 60.0,
    ) -> CompilationResult:
        """
        Extract slots using local MoE (KAT) and compile into RitualSchema.
        """
        try:
            raw_slots = self.query_kat(intent, timeout=timeout)
            return self.compile(raw_slots, strict_canonical=strict_canonical, source="kat_moe")
        except SlotValidationError as e:
            return CompilationResult(
                success=False,
                diagnostics=[str(e)],
                source="kat_moe_failed",
            )

    def execute(
        self,
        schema: RitualSchema,
        initial_state: WorldState,
    ) -> RitualValidationResult:
        """Delegate schema validation and execution to RitualEngine."""
        return self.engine.validate_and_execute(schema, initial_state)
