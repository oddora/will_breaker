"""
Will Breaker — Summoner API Server (no external dependencies)

Serves the static UI and provides a REST API for Protocol 023 entity
summoning and dialogue. Uses only Python stdlib — no Flask required.
"""

import json
import sys
import time
import hashlib
import threading
from pathlib import Path
from datetime import datetime, timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request

wb_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(wb_dir))

from symbolic_engine import GoeticCorpus, LiturgicalCompiler, WorldState, SigilGenerator, SigilConfig
from symbolic_engine.summoner import EntitySummoner, SUMMONING_CHARGE_TEMPLATE
from symbolic_engine.offerings import OfferingRegistry, _OFFERINGS


# Global state
_compiler = LiturgicalCompiler()
_summoner = EntitySummoner(compiler=_compiler)
_registry = OfferingRegistry()
_sessions = {}
_lock = threading.Lock()


STATIC_DIR = str(Path(__file__).resolve().parent / "public" / "ui")


class Handler(SimpleHTTPRequestHandler):
    """Serve static files + API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/summoner":
            qs = parse_qs(parsed.query)
            action = qs.get("action", [""])[0]
            if action == "entities":
                return self._json_response({"entities": self._get_entities()})
            if action == "status":
                return self._json_response({
                    "endpoints": {
                        "primary": _compiler.endpoint,
                        "model": _compiler.model_name,
                        "fallback": _compiler.active_endpoints[-1][0] if _compiler.active_endpoints else None,
                    },
                    "sessions": {sid: {
                        "entity": s["entity"],
                        "status": s.get("ritual_status"),
                        "turns": len(s.get("turns", [])),
                        "sealed_at": s.get("sealed_at"),
                    } for sid, s in _sessions.items()},
                })
            return self._json_response({"error": f"Unknown or missing action: {action}"}, 400)
        # Serve static files
        path = parsed.path.lstrip("/")
        if path == "" or path == "index.html":
            path = "index.html"
        try:
            return SimpleHTTPRequestHandler.do_GET(self)
        except FileNotFoundError:
            self.send_error(404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/summoner":
            return SimpleHTTPRequestHandler.do_POST(self)

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return self._json_response({"error": "Invalid JSON"}, 400)

        action = payload.get("action", "")
        try:
            if action == "summon":
                result = self._handle_summon(payload)
            elif action == "ask":
                result = self._handle_ask(payload)
            elif action == "dismiss":
                result = self._handle_dismiss(payload)
            else:
                return self._json_response({"error": f"Unknown action: {action}"}, 400)
            return self._json_response(result)
        except Exception as e:
            return self._json_response({"error": str(e), "success": False}, 500)

    # ---- API handlers ----

    def _handle_summon(self, payload):
        entity_name = payload.get("entity_name", "")
        if not entity_name:
            return {"error": "entity_name required", "success": False}

        endpoint = payload.get("endpoint")
        model = payload.get("model")
        prefer_ep = (endpoint, model) if endpoint and model else None
        if prefer_ep:
            _compiler.active_endpoints = [prefer_ep]
            _compiler.endpoint = endpoint
            _compiler.model_name = model

        session = _summoner.summon(entity_name, prefer_endpoint=prefer_ep)

        with _lock:
            _sessions[session.session_id] = {
                "entity": session.entity_name,
                "entity_rank": session.entity_rank,
                "entity_metal": session.entity_metal,
                "entity_legions": session.entity_legions,
                "entity_domains": session.entity_domains,
                "ritual_status": session.ritual_status,
                "circle_integrity": session.circle_integrity,
                "endpoint": session.endpoint,
                "model": session.model,
                "sigil_path": session.sigil_path,
                "sealed_at": session.sealed_at,
                "turns": [self._turn_to_dict(t) for t in session.turns],
            }

        return {
            "success": True,
            "session_id": session.session_id,
            "session": {"session_id": session.session_id},
            "ritual_status": session.ritual_status,
            "circle_integrity": session.circle_integrity,
            "introduction": session.turns[0].content if session.turns else "",
            "seal": session.turns[0].seal if session.turns else "",
            "endpoint": session.endpoint,
            "model": session.model,
        }

    def _handle_ask(self, payload):
        session_id = payload.get("session_id", "")
        question = payload.get("question", "")
        if not session_id or not question:
            return {"error": "session_id and question required", "success": False}

        with _lock:
            session = _sessions.get(session_id)
        if not session:
            return {"error": "Session not found", "success": False}

        from symbolic_engine.summoner import SummonSession, SessionTurn
        turn_list = [SessionTurn(**t) for t in session.get("turns", [])]
        sess = SummonSession(
            session_id=session_id,
            entity_name=session.get("entity", ""),
            entity_rank=session.get("entity_rank", ""),
            entity_metal=session.get("entity_metal", ""),
            entity_legions=session.get("entity_legions", 0),
            entity_domains=session.get("entity_domains", []),
            endpoint=session.get("endpoint", "http://127.0.0.1:18284"),
            model=session.get("model", "wb-agent"),
            sigil_path=session.get("sigil_path", ""),
            ritual_status=session.get("ritual_status", "SAT_COMPLETED"),
            circle_integrity=session.get("circle_integrity", 1.0),
            turns=turn_list,
            sealed_at=session.get("sealed_at", ""),
        )

        turn = _summoner.ask(sess, question)

        with _lock:
            session["turns"] = [self._turn_to_dict(t) for t in sess.turns]
            session["endpoint"] = sess.endpoint
            session["model"] = sess.model
            _sessions[session_id] = session

        return {
            "success": True,
            "turn": len(sess.turns),
            "answer": turn.content,
            "seal": turn.seal,
            "endpoint": sess.endpoint,
        }

    def _handle_dismiss(self, payload):
        session_id = payload.get("session_id", "")
        if not session_id:
            return {"error": "session_id required", "success": False}

        with _lock:
            session = _sessions.get(session_id)
        if not session:
            return {"error": "Session not found", "success": False}

        from symbolic_engine.summoner import SummonSession, SessionTurn
        turn_list = [SessionTurn(**t) for t in session.get("turns", [])]
        sess = SummonSession(
            session_id=session_id,
            entity_name=session.get("entity", ""),
            entity_rank=session.get("entity_rank", ""),
            entity_metal=session.get("entity_metal", ""),
            entity_legions=session.get("entity_legions", 0),
            entity_domains=session.get("entity_domains", []),
            endpoint=session.get("endpoint", "http://127.0.0.1:18284"),
            model=session.get("model", "wb-agent"),
            sigil_path=session.get("sigil_path", ""),
            ritual_status=session.get("ritual_status", "SAT_COMPLETED"),
            circle_integrity=session.get("circle_integrity", 1.0),
            turns=turn_list,
            sealed_at=session.get("sealed_at", ""),
        )

        turn = _summoner.dismiss(sess)

        with _lock:
            session["turns"] = [self._turn_to_dict(t) for t in sess.turns]
            session["endpoint"] = sess.endpoint
            session["model"] = sess.model
            session["resolved_at"] = datetime.now(timezone.utc).isoformat()
            _sessions[session_id] = session

        return {
            "success": True,
            "dismissal": turn.content,
            "seal": turn.seal,
        }

    # ---- Helpers ----

    def _get_entities(self):
        corpus = GoeticCorpus()
        entities = []
        for rec in corpus.records:
            off = _registry.get(rec.name)
            if off:
                offering_items = [it.item for it in off.items]
                offering_status = off.status
                temporal_win = off.temporal_window
            else:
                cat = _OFFERINGS.get(rec.name)
                if cat:
                    offering_items = [it["item"] for it in cat.get("offerings", [])]
                    offering_status = "PENDING"
                    temporal_win = cat.get("temporal_window", [])
                else:
                    offering_items = []
                    offering_status = "NOT_CATALOGED"
                    temporal_win = getattr(rec, "temporal_window", [])
            entities.append({
                "name": rec.name,
                "rank": rec.rank,
                "metal": rec.metal,
                "planet": _summoner._metal_to_planet(rec.metal).capitalize(),
                "legions": rec.legions,
                "domains": rec.domains,
                "temporal_window": temporal_win,
                "offerings": offering_items,
                "offeringStatus": offering_status,
            })
        return entities

    def _turn_to_dict(self, turn):
        if hasattr(turn, "to_dict"):
            return turn.to_dict()
        return {
            "turn_id": getattr(turn, "turn_id", ""),
            "turn_type": getattr(turn, "turn_type", ""),
            "speaker": getattr(turn, "speaker", ""),
            "content": getattr(turn, "content", ""),
            "seal": getattr(turn, "seal", ""),
            "timestamp": getattr(turn, "timestamp", ""),
        }

    def _json_response(self, data, status=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Quiet logs
        pass


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Will Breaker Summoner Server")
    parser.add_argument("--port", type=int, default=8081, help="Port to serve on")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), Handler)
    print(f"Will Breaker Summoner UI  →  http://{args.host}:{args.port}/")
    print(f"API                        →  http://{args.host}:{args.port}/api/summoner")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    import os
    main()
