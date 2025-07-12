from a2a_sdk import Agent, expose
import logging
from typing import List, Dict, Any
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class PersonalizationAgent(Agent):
    """
    A2A-enabled PersonalizationAgent for production SRE workflows.
    Exposes personalize as a JSON-RPC method for agentic interoperability.
    """
    def __init__(self, logger=None, example_fetch_fn=None):
        super().__init__()
        self.logger = logger or logging.getLogger("personalization-agent")
        self.example_fetch_fn = example_fetch_fn

    @expose
    def personalize(self, context: dict, grounding_snippets: list) -> List[Dict[str, Any]]:
        try:
            if self.example_fetch_fn:
                examples = self.example_fetch_fn(context, grounding_snippets)
            else:
                examples = [
                    {"example": "When CPU is high, scale up the node pool as per policy X."},
                    {"example": "If pod is unhealthy, restart using standard operating procedure Y."},
                ]
            self._log_personalization(context, grounding_snippets, examples)
            return examples
        except Exception as e:
            self.logger.error(f"Personalization failed: {e}")
            return []

    def _log_personalization(self, context, grounding_snippets, examples):
        log_entry = {
            "event": "personalization_injected",
            "incident_id": context.get('incident_id', None),
            "num_examples": len(examples),
            "examples": examples,
            "grounding_snippets": grounding_snippets,
        }
        if hasattr(self.logger, "log_struct"):
            self.logger.log_struct(log_entry, severity="INFO")
        else:
            self.logger.info(log_entry)

    @staticmethod
    def get_agent_card():
        return {
            "id": "personalization-agent",
            "name": "PersonalizationAgent",
            "endpoint": "<REPLACE_WITH_ENDPOINT>",
            "methods": ["inject_prompt", "get_agent_card"],
            "description": "Injects org-specific prompts and context.",
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

def serve_agent_card(agent, port=9003):
    server = HTTPServer(("0.0.0.0", port), AgentCardHandler)
    server.agent = agent
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Agent Card HTTP endpoint running at http://0.0.0.0:{port}/agent_card")

if __name__ == "__main__":
    agent = PersonalizationAgent()
    serve_agent_card(agent, port=9003)  # Agent Card HTTP endpoint
    agent.run(host="0.0.0.0", port=8003)  # A2A JSON-RPC server
