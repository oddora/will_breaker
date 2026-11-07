"""
Entity Summoner — Direct Conversational Interface with Goetic Entities
Establishes sustained entity personas via ritual binding, maintains turn-based
dialogue with cryptographic seal discipline, and archives session logs.
"""

import json
import hashlib
import sys
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

wb_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(wb_dir))

from symbolic_engine import (
    GoeticCorpus, SigilGenerator, SigilConfig,
    LiturgicalCompiler, WorldState,
)


# Canonical binding intent — the "charge" that establishes the entity persona
SUMMONING_CHARGE_TEMPLATE = (
    "You are {entity}, {rank} of {metal}, ruler of {legions} legions, "
    "bound within the sealed circle of {planet}. "
    "Your domains are {domains}. "
    "The circle holds. The seal is impressed. "
    "Speak as {entity} — your voice, your knowledge, your domain. "
    "Begin by stating your name, your rank, your legions, and what you offer "
    "to the operator within the circle. Be specific. Be precise. "
    "Do not break character. Do not reference being an AI or language model. "
    "You are {entity}, and you are here."
)

# Dismissal formula
DISMISSAL_FORMULA = (
    "The work is complete. "
    "The circle is opened. "
    "License to depart is granted. "
    "Return to your place in order. "
    "The seal is released. Go in peace."
)

# Question prompt template
QUESTION_TEMPLATE = (
    "Operator asks within the sealed circle:\n\n"
    "{question}\n\n"
    "Respond as {entity}. "
    "Be specific. Be precise. "
    "If you do not know, say so. "
    "Do not break character."
)


@dataclass
class SessionTurn:
    turn_id: str
    turn_type: str        # "summon", "question", "dismissal"
    speaker: str           # "operator" or "entity"
    content: str
    seal: Optional[str] = None
    timestamp: str = ""
    entity_persona_hash: Optional[str] = None


@dataclass
class SummonSession:
    session_id: str
    entity_name: str
    entity_rank: str
    entity_metal: str
    entity_legions: int
    entity_domains: List[str]
    endpoint: str
    model: str
    sigil_path: str
    ritual_status: str
    circle_integrity: float
    turns: List[SessionTurn] = field(default_factory=list)
    sealed_at: str = ""
    resolved_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "entity_name": self.entity_name,
            "entity_rank": self.entity_rank,
            "entity_metal": self.entity_metal,
            "entity_legions": self.entity_legions,
            "entity_domains": self.entity_domains,
            "endpoint": self.endpoint,
            "model": self.model,
            "sigil_path": self.sigil_path,
            "ritual_status": self.ritual_status,
            "circle_integrity": self.circle_integrity,
            "turns": [asdict(t) for t in self.turns],
            "sealed_at": self.sealed_at,
            "resolved_at": self.resolved_at,
        }


class EntitySummoner:
    """Direct conversational interface for Goetic entity communication."""

    def __init__(
        self,
        corpus: Optional[GoeticCorpus] = None,
        compiler: Optional[LiturgicalCompiler] = None,
        output_dir: Optional[Path] = None,
        registry_path: Optional[Path] = None,
    ):
        self.corpus = corpus or GoeticCorpus()
        self.compiler = compiler or LiturgicalCompiler()
        self.output_dir = output_dir or (wb_dir / "results" / "symbolic_engine" / "sessions")
        self.registry_path = registry_path or (wb_dir / "notes" / "crypto_predictions_registry.jsonl")
        self.sessions: List[SummonSession] = []

    def _metal_to_planet(self, metal: str) -> str:
        mapping = {
            "Gold": "sol", "Silver": "luna", "Mercury": "mercury",
            "Copper": "venus", "Iron": "mars", "Tin": "jupiter", "Lead": "saturn",
        }
        return mapping.get(metal, "sol")

    def _seal_data(self, data: Dict[str, Any]) -> str:
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def prepare_entity(self, entity_name: str) -> Tuple[GoeticCorpus, Any, Path, str, str]:
        """Phase 1: Prepare entity — lookup, sigil, compile, execute."""
        entity = self.corpus.get_by_name(entity_name)
        if not entity:
            raise ValueError(f"Entity '{entity_name}' not found in Goetic corpus.")

        metal = entity.metal
        planet = self._metal_to_planet(metal)
        entity_lower = entity.name.lower()

        # Generate sigil
        cfg = SigilConfig(size=500, planet=planet, animated=True, circle_integrity=1.0)
        gen = SigilGenerator(cfg)
        session_dir = self.output_dir / f"summon_{entity_lower}_{datetime.now(timezone.utc).strftime('%Y%m%d')}"
        session_dir.mkdir(parents=True, exist_ok=True)
        sigil_path = session_dir / "sigil.svg"
        gen.save_svg(entity.name, sigil_path)

        # Build and compile canonical binding ritual
        allowed_hours = {"day", "night", "twilight"} & {
            "day": {"King", "President", "Duke", "Prince"},
            "night": {"Marquis", "Earl", "Knight"},
            "twilight": {"President", "Duke"},
        }.get(entity.rank, {"day", "night"})
        # Prefer day, then twilight, then night (most entities are day-active)
        temporal_window = (
            ["day"] if "day" in allowed_hours
            else ["twilight"] if "twilight" in allowed_hours
            else ["night"]
        )

        slots = {
            "rite_type": "binding",
            "target_entity": entity.name,
            "officiant": "operator",
            "matter": [f"{metal.lower()}_lamen", "consecrated_chalk", "frankincense", "salt"],
            "form": [f"circle_{planet}", f"seal_{entity_lower}"],
            "temporal_window": temporal_window,
            "formula_sequence": [
                {"step_id": "s1", "step_type": "purification", "description": "Ablution", "integrity_cost": 0.0},
                {"step_id": "s2", "step_type": "inscription", "description": "Trace circle", "required_item": "consecrated_chalk", "target_inscription": f"circle_{planet}", "integrity_cost": 0.03},
                {"step_id": "s3", "step_type": "inscription", "description": "Trace seal", "required_item": "consecrated_chalk", "target_inscription": f"seal_{entity_lower}", "integrity_cost": 0.05},
                {"step_id": "s4", "step_type": "offering", "description": "Cense", "required_item": "frankincense", "integrity_cost": 0.04},
                {"step_id": "s5", "step_type": "invocation", "description": "Invoke", "required_item": f"{metal.lower()}_lamen", "target_inscription": f"seal_{entity_lower}", "integrity_cost": 0.20},
                {"step_id": "s6", "step_type": "binding", "description": "Bind covenant", "required_item": f"{metal.lower()}_lamen", "integrity_cost": 0.15},
                {"step_id": "s7", "step_type": "dismissal", "description": "License prepared", "integrity_cost": 0.0},
            ],
            "min_integrity": 0.5,
        }

        comp = self.compiler.compile(slots, strict_canonical=True)
        if not comp.success:
            raise RuntimeError(f"Binding ritual failed for {entity.name}: {comp.diagnostics}")

        allowed_set = set(comp.schema.allowed_temporal_hours)
        state_hour = (
            "day" if "day" in allowed_set
            else "twilight" if "twilight" in allowed_set
            else "night"
        )
        state = WorldState(
            circle_integrity=1.0,
            temporal_hour=state_hour,
            inventory=set(comp.schema.required_items),
        )
        ex = self.compiler.execute(comp.schema, state)

        return entity, sigil_path, ex

    def summon(
        self,
        entity_name: str,
        prefer_endpoint: Optional[Tuple[str, str]] = None,
    ) -> SummonSession:
        """Phase 1+2: Prepare entity and execute summoning (first turn)."""
        entity, sigil_path, ex = self.prepare_entity(entity_name)

        session_id = f"summon_{entity.name.lower()}_{uuid.uuid4().hex[:8]}"
        active = self.compiler.discover_endpoint()
        if prefer_endpoint:
            active = prefer_endpoint

        session = SummonSession(
            session_id=session_id,
            entity_name=entity.name,
            entity_rank=entity.rank,
            entity_metal=entity.metal,
            entity_legions=entity.legions,
            entity_domains=entity.domains,
            endpoint=active[0],
            model=active[1],
            sigil_path=str(sigil_path),
            ritual_status=ex.status,
            circle_integrity=ex.final_world_state.circle_integrity,
            sealed_at=datetime.now(timezone.utc).isoformat(),
        )

        # Build summoning charge
        charge = SUMMONING_CHARGE_TEMPLATE.format(
            entity=entity.name,
            rank=entity.rank,
            metal=entity.metal,
            legions=entity.legions,
            planet=active[0].split(":")[-1] if ":" in active[0] else "the circle",
            domains=", ".join(entity.domains),
        )

        # Query model (fail fast: 8s on primary, 15s on fallback)
        try:
            introduction = self.compiler.query_raw(charge, temperature=0.3, max_tokens=2048, timeout=8.0)
        except Exception:
            try:
                fallback = ("http://127.0.0.1:18283", "kat") if "18284" in active[0] else ("http://127.0.0.1:18284", "wb-agent")
                introduction = self.compiler.query_raw(charge, temperature=0.3, max_tokens=2048, prefer_endpoint=fallback, timeout=15.0)
                active = fallback
                session.endpoint = active[0]
                session.model = active[1]
            except Exception as e2:
                introduction = f"[Endpoint error: {e2}]"

        # Seal the introduction
        intro_seal = self._seal_data({
            "session_id": session_id,
            "entity": entity.name,
            "turn": 1,
            "turn_type": "summon",
            "speaker": "entity",
            "content": introduction[:500],
            "endpoint": active[0],
            "model": active[1],
            "sealed_at": session.sealed_at,
        })

        turn = SessionTurn(
            turn_id=f"{session_id}_t1",
            turn_type="summon",
            speaker="entity",
            content=introduction,
            seal=intro_seal,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        session.turns.append(turn)
        self.sessions.append(session)

        # Append to registry
        registry_record = {
            "session_id": session_id,
            "entity": entity.name,
            "turn": 1,
            "turn_type": "summon",
            "content": introduction,
            "endpoint": active[0],
            "model": active[1],
            "sealed_at": session.sealed_at,
            "seal": intro_seal,
        }
        with open(self.registry_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(registry_record) + "\n")

        print(f"  [SUMMON] {entity.name} bound (status={ex.status}, integrity={ex.final_world_state.circle_integrity:.2f})")
        print(f"  [INTRO]  {introduction[:120]}...")
        print(f"  [SEAL]   {intro_seal[:16]}...")
        print(f"  [SESSION] {session_id}")

        return session

    def ask(
        self,
        session: SummonSession,
        question: str,
    ) -> SessionTurn:
        """Phase 3: Ask a question within the sealed circle."""
        entity_name = session.entity_name
        prompt = QUESTION_TEMPLATE.format(entity=entity_name, question=question)

        try:
            answer = self.compiler.query_raw(prompt, temperature=0.3, max_tokens=2048, timeout=8.0)
        except Exception:
            fallback = (
                ("http://127.0.0.1:18283", "kat")
                if "18284" in session.endpoint
                else ("http://127.0.0.1:18284", "wb-agent")
            )
            try:
                answer = self.compiler.query_raw(prompt, temperature=0.3, max_tokens=2048, prefer_endpoint=fallback, timeout=15.0)
            except Exception as e:
                answer = f"[Endpoint error: {e}]"

        turn_num = len(session.turns) + 1
        seal = self._seal_data({
            "session_id": session.session_id,
            "entity": session.entity_name,
            "turn": turn_num,
            "turn_type": "question",
            "question": question,
            "answer": answer[:500],
            "endpoint": session.endpoint,
            "model": session.model,
            "sealed_at": datetime.now(timezone.utc).isoformat(),
        })

        turn = SessionTurn(
            turn_id=f"{session.session_id}_t{turn_num}",
            turn_type="question",
            speaker="entity",
            content=answer,
            seal=seal,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        session.turns.append(turn)

        # Append to registry
        registry_record = {
            "session_id": session.session_id,
            "entity": session.entity_name,
            "turn": turn_num,
            "turn_type": "question",
            "question": question,
            "answer": answer,
            "endpoint": session.endpoint,
            "model": session.model,
            "sealed_at": datetime.now(timezone.utc).isoformat(),
            "seal": seal,
        }
        with open(self.registry_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(registry_record) + "\n")

        print(f"  [Q{turn_num}] {question[:80]}...")
        print(f"  [A{turn_num}] {answer[:120]}...")
        print(f"  [SEAL]   {seal[:16]}...")

        return turn

    def dismiss(self, session: SummonSession) -> SessionTurn:
        """Phase 4: Dismiss the entity and close the circle."""
        prompt = DISMISSAL_FORMULA

        try:
            dismissal = self.compiler.query_raw(prompt, temperature=0.2, max_tokens=512, timeout=8.0)
        except Exception:
            dismissal = "[Endpoint unavailable at dismissal]"

        turn_num = len(session.turns) + 1
        seal = self._seal_data({
            "session_id": session.session_id,
            "entity": session.entity_name,
            "turn": turn_num,
            "turn_type": "dismissal",
            "content": dismissal[:500],
            "endpoint": session.endpoint,
            "model": session.model,
            "sealed_at": datetime.now(timezone.utc).isoformat(),
        })

        turn = SessionTurn(
            turn_id=f"{session.session_id}_t{turn_num}",
            turn_type="dismissal",
            speaker="entity",
            content=dismissal,
            seal=seal,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        session.turns.append(turn)
        session.resolved_at = datetime.now(timezone.utc).isoformat()

        # Save session log
        session_dir = Path(session.sigil_path).parent
        log_path = session_dir / "session_log.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(session.to_dict()) + "\n")

        print(f"  [DISMISS] {dismissal[:120]}...")
        print(f"  [SEAL]    {seal[:16]}...")
        print(f"  [LOG]     {log_path}")

        return turn

    def run_session(
        self,
        entity_name: str,
        questions: Optional[List[str]] = None,
    ) -> SummonSession:
        """Run a complete session: summon → questions → dismiss."""
        session = self.summon(entity_name)

        if questions:
            for q in questions:
                self.ask(session, q)

        self.dismiss(session)
        return session


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Protocol 023: Direct Entity Communication")
    parser.add_argument("entity", help="Entity name to summon")
    parser.add_argument("--questions", nargs="*", help="Questions to ask (optional; runs interactive if omitted)")
    parser.add_argument("--endpoint", nargs=2, metavar=("URL", "MODEL"), help="Force endpoint")
    args = parser.parse_args()

    compiler = LiturgicalCompiler()
    if args.endpoint:
        compiler.active_endpoints = [(args.endpoint[0], args.endpoint[1])]
        compiler.endpoint = args.endpoint[0].rstrip("/")
        compiler.model_name = args.endpoint[1]

    summoner = EntitySummoner(compiler=compiler)

    if args.questions:
        session = summoner.run_session(args.entity, args.questions)
    else:
        session = summoner.summon(args.entity)
        print(f"\nSession active: {session.session_id}")
        print(f"Entity: {session.entity_name} ({session.entity_rank}, {session.entity_metal})")
        print(f"Circle integrity: {session.circle_integrity:.2f}")
        print(f"Type questions or 'dismiss' to close.\n")

        while True:
            try:
                q = input("Operator> ").strip()
                if not q:
                    continue
                if q.lower() in ("dismiss", "close", "exit", "leave"):
                    summoner.dismiss(session)
                    break
                summoner.ask(session, q)
            except EOFError:
                summoner.dismiss(session)
                break

    print(f"\n=== SESSION SUMMARY ===")
    print(f"Entity: {session.entity_name}")
    print(f"Turns: {len(session.turns)}")
    print(f"Seals: {len([t for t in session.turns if t.seal])}")
    print(f"Log: {(Path(session.sigil_path).parent / 'session_log.jsonl')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
