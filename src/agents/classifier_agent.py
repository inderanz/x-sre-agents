from a2a_sdk import Agent, expose
import os
import subprocess
import logging
from src.schemas import Signal, Context
from typing import Tuple
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class ClassifierAgent(Agent):
    """
    A2A-enabled ClassifierAgent for production SRE workflows.
    Exposes classify as a JSON-RPC method for agentic interoperability.
    """
    def __init__(self, logger=None):
        super().__init__()
        self.logger = logger or logging.getLogger("classifier-agent")
        self.rules = [
            (lambda s, c: "scale" if "cpu" in s.message.lower() and c.severity == "critical" else None),
            (lambda s, c: "restart" if "unhealthy" in s.message.lower() else None),
            (lambda s, c: "investigate" if c.severity == "warning" else None),
        ]
        self.llm_enabled = True

    @expose
    def classify(self, signal: dict, context: dict) -> Tuple[str, dict]:
        signal = Signal(**signal)
        context = Context(**context)
        for rule in self.rules:
            result = rule(signal, context)
            if result:
                self._log_classification(signal, context, result, "rules_engine")
                return result, {"method": "rules_engine"}
        if self.llm_enabled:
            query_class = self._classify_with_llm(signal, context)
            self._log_classification(signal, context, query_class, "llm")
            return query_class, {"method": "llm"}
        self._log_classification(signal, context, "unknown", "default")
        return "unknown", {"method": "default"}

    def _classify_with_llm(self, signal: Signal, context: Context) -> str:
        prompt = f"""
        Incident: {signal.message}\n\nContext: {context.dict()}\n\nClassify this incident as one of: scale, restart, investigate, other.\nRespond with only the class name.
        """
        try:
            result = subprocess.run(
                ["gemini", "prompt", prompt],
                capture_output=True, text=True, check=True
            )
            response = result.stdout.strip().lower()
            for cls in ["scale", "restart", "investigate", "other"]:
                if cls in response:
                    return cls
            return "other"
        except Exception as e:
            self.logger.error(f"LLM classification failed: {e}")
            return "other"

    def _log_classification(self, signal, context, query_class, method):
        log_entry = {
            "event": "incident_classified",
            "incident_id": context.incident_id,
            "query_class": query_class,
            "method": method,
            "signal": signal.dict(),
            "context": context.dict(),
        }
        if hasattr(self.logger, "log_struct"):
            self.logger.log_struct(log_entry, severity="INFO")
        else:
            self.logger.info(log_entry)

    @staticmethod
    def get_agent_card():
        return {
            "id": "classifier-agent",
            "name": "ClassifierAgent",
            "endpoint": "<REPLACE_WITH_ENDPOINT>",
            "methods": ["classify_alert", "get_agent_card"],
            "description": "Classifies alerts using rules and LLM fallback.",
            "version": "1.0.0",
            "owner": "SRE Automation Team"
        }

    def get_agent_card_rpc(self, params=None):
        return self.get_agent_card()

class AgentCardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/agent_card":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            # Dynamically get the agent card from the running agent instance
            card = self.server.agent.get_agent_card()
            self.wfile.write(json.dumps(card).encode())
        else:
            self.send_response(404)
            self.end_headers()

def serve_agent_card(agent, port=9001):
    server = HTTPServer(("0.0.0.0", port), AgentCardHandler)
    server.agent = agent
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Agent Card HTTP endpoint running at http://0.0.0.0:{port}/agent_card")

if __name__ == "__main__":
    agent = ClassifierAgent()
    serve_agent_card(agent, port=9001)  # Agent Card HTTP endpoint
    agent.run(host="0.0.0.0", port=8001)  # A2A JSON-RPC server
