from a2a_sdk import Agent, expose
import logging
from typing import Dict, Any
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class LLMJudgeAgent(Agent):
    """
    A2A-enabled LLMJudgeAgent for production SRE workflows.
    Exposes judge as a JSON-RPC method for agentic interoperability.
    In CI/CD, replays sample flows and uses judge prompts to score correctness and improve the system.
    """
    def __init__(self, logger=None):
        super().__init__()
        self.logger = logger or logging.getLogger("llmjudge-agent")

    @expose
    def judge(self, flow: dict) -> Dict[str, Any]:
        # TODO: Implement LLM-based evaluation logic
        # For now, return a mock result
        self.logger.info(f"Judging flow: {flow}")
        return {"score": 95, "comments": "LLM evaluation passed."}

    @staticmethod
    def get_agent_card():
        return {
            "id": "llmjudge-agent",
            "name": "LLMJudgeAgent",
            "endpoint": "<REPLACE_WITH_ENDPOINT>",
            "methods": ["evaluate_workflow", "get_agent_card"],
            "description": "Evaluates workflows for CI/CD and quality.",
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

def serve_agent_card(agent, port=9011):
    server = HTTPServer(("0.0.0.0", port), AgentCardHandler)
    server.agent = agent
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Agent Card HTTP endpoint running at http://0.0.0.0:{port}/agent_card")

if __name__ == "__main__":
    agent = LLMJudgeAgent()
    serve_agent_card(agent, port=9011)  # Agent Card HTTP endpoint
    agent.run(host="0.0.0.0", port=8011)  # A2A JSON-RPC server 