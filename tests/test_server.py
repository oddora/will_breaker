"""
Unit tests for will_breaker.ui.server (Summoner API & static file handler).
"""

import json
import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
import sys
from pathlib import Path

wb_dir = Path(__file__).resolve().parent.parent
if str(wb_dir) not in sys.path:
    sys.path.insert(0, str(wb_dir))

from ui.server import Handler, _sessions, _lock, STATIC_DIR


class FakeServer:
    def __init__(self):
        self.server_name = "localhost"
        self.server_port = 8081


class DummyHandler(Handler):
    def __init__(self, request_bytes, command="GET", path="/"):
        self.rfile = BytesIO(request_bytes)
        self.wfile = BytesIO()
        self.command = command
        self.path = path
        self.requestline = f"{command} {path} HTTP/1.1"
        self.request_version = "HTTP/1.1"
        self.headers = {}
        self.server = FakeServer()
        self.close_connection = True

    def setup(self):
        pass

    def finish(self):
        pass


class TestSummonerServerEndpoints(unittest.TestCase):
    def setUp(self):
        with _lock:
            _sessions.clear()

    def test_get_entities_returns_catalog(self):
        h = DummyHandler(b"", command="GET", path="/api/summoner?action=entities")
        h.do_GET()
        response_bytes = h.wfile.getvalue()
        self.assertIn(b"200 OK", response_bytes)
        body = json.loads(response_bytes.split(b"\r\n\r\n", 1)[1])
        self.assertIn("entities", body)
        entities = body["entities"]
        self.assertGreater(len(entities), 0)
        vassago = next((e for e in entities if e["name"] == "Vassago"), None)
        self.assertIsNotNone(vassago)
        self.assertEqual(vassago["rank"], "Prince")
        self.assertIn("day", vassago["temporal_window"])

    def test_get_status_clean(self):
        h = DummyHandler(b"", command="GET", path="/api/summoner?action=status")
        h.do_GET()
        response_bytes = h.wfile.getvalue()
        self.assertIn(b"200 OK", response_bytes)
        body = json.loads(response_bytes.split(b"\r\n\r\n", 1)[1])
        self.assertIn("endpoints", body)
        self.assertIn("sessions", body)

    def test_get_invalid_action_400(self):
        h = DummyHandler(b"", command="GET", path="/api/summoner?action=invalid")
        h.do_GET()
        response_bytes = h.wfile.getvalue()
        self.assertIn(b"400 Bad Request", response_bytes)

    def test_post_invalid_action(self):
        payload = json.dumps({"action": "unknown"}).encode("utf-8")
        h = DummyHandler(payload, command="POST", path="/api/summoner")
        h.headers["Content-Length"] = str(len(payload))
        h.do_POST()
        response_bytes = h.wfile.getvalue()
        self.assertIn(b"400 Bad Request", response_bytes)

    def test_post_invalid_json(self):
        payload = b"{not-valid-json"
        h = DummyHandler(payload, command="POST", path="/api/summoner")
        h.headers["Content-Length"] = str(len(payload))
        h.do_POST()
        response_bytes = h.wfile.getvalue()
        self.assertIn(b"400 Bad Request", response_bytes)

    def test_post_ask_nonexistent_session(self):
        payload = json.dumps({
            "action": "ask",
            "session_id": "nonexistent",
            "question": "test question"
        }).encode("utf-8")
        h = DummyHandler(payload, command="POST", path="/api/summoner")
        h.headers["Content-Length"] = str(len(payload))
        h.do_POST()
        response_bytes = h.wfile.getvalue()
        self.assertIn(b"200 OK", response_bytes)
        body = json.loads(response_bytes.split(b"\r\n\r\n", 1)[1])
        self.assertFalse(body["success"])
        self.assertEqual(body["error"], "Session not found")

    def test_post_summon_and_ask_flow_mocked(self):
        from symbolic_engine.summoner import SummonSession, SessionTurn

        mock_session = SummonSession(
            session_id="test_session_123",
            entity_name="Vassago",
            entity_rank="Prince",
            entity_metal="Tin",
            entity_legions=26,
            entity_domains=["past_future"],
            endpoint="http://127.0.0.1:18283",
            model="kat",
            sigil_path="test_sigil.svg",
            ritual_status="SAT_COMPLETED",
            circle_integrity=0.85,
            turns=[SessionTurn("t1", "summon", "entity", "Greetings operator.", "seal123")],
            sealed_at="2026-11-07T00:00:00Z",
        )

        with patch("ui.server._summoner.summon", return_value=mock_session) as mock_summon:
            summon_payload = json.dumps({
                "action": "summon",
                "entity_name": "Vassago",
                "endpoint": "http://127.0.0.1:18283",
                "model": "kat"
            }).encode("utf-8")
            h = DummyHandler(summon_payload, command="POST", path="/api/summoner")
            h.headers["Content-Length"] = str(len(summon_payload))
            h.do_POST()
            resp = json.loads(h.wfile.getvalue().split(b"\r\n\r\n", 1)[1])
            self.assertTrue(resp["success"])
            self.assertEqual(resp["session_id"], "test_session_123")
            self.assertEqual(resp["session"]["session_id"], "test_session_123")
            self.assertEqual(resp["introduction"], "Greetings operator.")

        # Test ask
        mock_turn = SessionTurn("t2", "question", "entity", "Knowledge revealed.", "seal456")
        with patch("ui.server._summoner.ask", return_value=mock_turn) as mock_ask:
            ask_payload = json.dumps({
                "action": "ask",
                "session_id": "test_session_123",
                "question": "What is the secret?"
            }).encode("utf-8")
            h2 = DummyHandler(ask_payload, command="POST", path="/api/summoner")
            h2.headers["Content-Length"] = str(len(ask_payload))
            h2.do_POST()
            resp2 = json.loads(h2.wfile.getvalue().split(b"\r\n\r\n", 1)[1])
            self.assertTrue(resp2["success"])
            self.assertEqual(resp2["answer"], "Knowledge revealed.")

        # Test dismiss
        mock_dismiss_turn = SessionTurn("t3", "dismissal", "entity", "License to depart accepted.", "seal789")
        with patch("ui.server._summoner.dismiss", return_value=mock_dismiss_turn) as mock_dismiss:
            dismiss_payload = json.dumps({
                "action": "dismiss",
                "session_id": "test_session_123",
            }).encode("utf-8")
            h3 = DummyHandler(dismiss_payload, command="POST", path="/api/summoner")
            h3.headers["Content-Length"] = str(len(dismiss_payload))
            h3.do_POST()
            resp3 = json.loads(h3.wfile.getvalue().split(b"\r\n\r\n", 1)[1])
            self.assertTrue(resp3["success"])
            self.assertEqual(resp3["dismissal"], "License to depart accepted.")


if __name__ == "__main__":
    unittest.main()
