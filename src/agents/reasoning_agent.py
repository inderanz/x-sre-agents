from a2a_sdk import Agent, expose
import subprocess
import json
import logging
from typing import Dict, Any
from src.schemas import MCPEnvelope, ActionProposal
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class ReasoningAgent(Agent):
    """
    A2A-enabled ReasoningAgent for production SRE workflows.
    Exposes reason as a JSON-RPC method for agentic interoperability.
    Uses Gemini CLI for LLM-based reasoning.
    """
    def __init__(self, logger=None, gemini_cmd="gemini"):
        super().__init__()
        self.logger = logger or logging.getLogger("reasoning-agent")
        self.gemini_cmd = gemini_cmd

    @expose
    def reason(self, mcp_envelope: dict, grounding_snippets: list, personalization_examples: list) -> dict:
        mcp_envelope = MCPEnvelope(**mcp_envelope)
        prompt = self._build_prompt(mcp_envelope, grounding_snippets, personalization_examples)
        try:
            result = subprocess.run(
                [self.gemini_cmd, "prompt", prompt],
                capture_output=True, text=True, check=True
            )
            response = result.stdout.strip()
            action_proposal = self._parse_response(response)
            self._log_reasoning(mcp_envelope, action_proposal, prompt, response)
            return action_proposal.dict()
        except Exception as e:
            self.logger.error(f"Reasoning failed: {e}")
            return ActionProposal(action="none", reason=str(e), confidence=0).dict()

    @staticmethod
    def get_agent_card():
        return {
            "id": "reasoning-agent",
            "name": "ReasoningAgent",
            "endpoint": "<REPLACE_WITH_ENDPOINT>",
            "methods": ["reason_about_incident", "get_agent_card"],
            "description": "Performs LLM-based reasoning and remediation planning.",
            "version": "1.0.0",
            "owner": "SRE Automation Team"
        }

    def get_agent_card_rpc(self, params=None):
        return self.get_agent_card()

    def _build_prompt(self, mcp_envelope, grounding_snippets, personalization_examples) -> str:
        prompt = f"""
        You are an SRE agent.\n\n
        Incident: {json.dumps(mcp_envelope.payload.get('signal', {}))}\n\n
        Context: {json.dumps(mcp_envelope.payload.get('context', {}))}\n\n
        Query Class: {mcp_envelope.payload.get('query_class', '')}\n\n
        Relevant Docs: {json.dumps(grounding_snippets)}\n\n
        Examples: {json.dumps(personalization_examples)}\n\n
        Propose a safe, minimal action.\n\n
        Respond as JSON matching schema:\n
        {{ \"action\": \"...\", \"reason\": \"...\", \"confidence\": 0-100 }}
        """
        return prompt

    def _parse_response(self, response: str) -> ActionProposal:
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != -1:
                response_json = json.loads(response[start:end])
                return ActionProposal(
                    action=response_json.get("action", "none"),
                    reason=response_json.get("reason", "No reason provided"),
                    confidence=int(response_json.get("confidence", 0)),
                    metadata=response_json
                )
            else:
                raise ValueError("No JSON found in LLM response")
        except Exception as e:
            self.logger.error(f"Failed to parse LLM response: {e}")
            return ActionProposal(action="none", reason="Failed to parse LLM response", confidence=0)

    def _log_reasoning(self, mcp_envelope, action_proposal, prompt, response):
        log_entry = {
            "event": "action_proposed",
            "envelope_id": mcp_envelope.envelope_id,
            "action": action_proposal.action,
            "confidence": action_proposal.confidence,
            "reason": action_proposal.reason,
            "prompt": prompt,
            "llm_response": response,
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

def serve_agent_card(agent, port=9005):
    server = HTTPServer(("0.0.0.0", port), AgentCardHandler)
    server.agent = agent
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Agent Card HTTP endpoint running at http://0.0.0.0:{port}/agent_card")

if __name__ == "__main__":
    agent = ReasoningAgent()
    serve_agent_card(agent, port=9005)  # Agent Card HTTP endpoint
    agent.run(host="0.0.0.0", port=8005)  # A2A JSON-RPC server
