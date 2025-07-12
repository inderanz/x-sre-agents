from a2a_sdk import Agent, expose
import requests
import logging
from typing import Dict, Any
from src.schemas import ActionProposal
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class PolicyAgent(Agent):
    """
    A2A-enabled PolicyAgent for production SRE workflows.
    Exposes policy_check as a JSON-RPC method for agentic interoperability.
    Integrates with OPA Gatekeeper for policy gating.
    """
    def __init__(self, opa_url: str, logger=None):
        super().__init__()
        self.opa_url = opa_url
        self.logger = logger or logging.getLogger("policy-agent")

    @expose
    def policy_check(self, action_proposal: dict) -> Dict[str, Any]:
        action_proposal = ActionProposal(**action_proposal)
        payload = {"input": action_proposal.dict()}
        try:
            response = requests.post(self.opa_url, json=payload, timeout=5)
            response.raise_for_status()
            result = response.json()
            admit = result.get("result", {}).get("admit", False)
            reason = result.get("result", {}).get("reason", "No reason provided")
            confidence = result.get("result", {}).get("confidence", 0)
            self._log_policy_verdict(action_proposal, admit, reason, confidence, result)
            return {
                "admit": admit,
                "reason": reason,
                "confidence": confidence,
                "opa_result": result
            }
        except Exception as e:
            self.logger.error(f"Policy check failed: {e}")
            self._log_policy_verdict(action_proposal, False, str(e), 0, {})
            return {
                "admit": False,
                "reason": str(e),
                "confidence": 0,
                "opa_result": {}
            }

    @staticmethod
    def get_agent_card():
        return {
            "id": "policy-agent",
            "name": "PolicyAgent",
            "endpoint": "<REPLACE_WITH_ENDPOINT>",
            "methods": ["check_policy", "get_agent_card"],
            "description": "Validates actions against OPA policies.",
            "version": "1.0.0",
            "owner": "SRE Automation Team"
        }

    def get_agent_card_rpc(self, params=None):
        return self.get_agent_card()

    def _log_policy_verdict(self, action_proposal, admit, reason, confidence, opa_result):
        log_entry = {
            "event": "policy_verdict",
            "action": action_proposal.action,
            "admit": admit,
            "reason": reason,
            "confidence": confidence,
            "opa_result": opa_result,
        }
        if hasattr(self.logger, "log_struct"):
            self.logger.log_struct(log_entry, severity="INFO")
        else:
            self.logger.info(log_entry)

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

def serve_agent_card(agent, port=9006):
    server = HTTPServer(("0.0.0.0", port), AgentCardHandler)
    server.agent = agent
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Agent Card HTTP endpoint running at http://0.0.0.0:{port}/agent_card")

if __name__ == "__main__":
    agent = PolicyAgent(opa_url="http://opa-gatekeeper/v1/data/sre/policy")
    serve_agent_card(agent, port=9006)  # Agent Card HTTP endpoint
    agent.run(host="0.0.0.0", port=8006)  # A2A JSON-RPC server
