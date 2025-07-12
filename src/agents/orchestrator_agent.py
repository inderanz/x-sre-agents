from a2a_sdk import Agent, expose
import logging
import time
from typing import Dict, Any
from google.cloud import bigquery
from src.schemas import MCPEnvelope
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class OrchestratorAgent(Agent):
    """
    A2A-enabled OrchestratorAgent for production SRE workflows.
    Exposes orchestrate as a JSON-RPC method for agentic interoperability.
    Handles MCP envelope creation, signing, and BigQuery persistence.
    """
    def __init__(self, logger=None, bq_client=None, signer_fn=None):
        super().__init__()
        self.logger = logger or logging.getLogger("orchestrator-agent")
        self.bq_client = bq_client or bigquery.Client()
        self.signer_fn = signer_fn
        self.bq_table = "sre_agent.mcp_envelopes"

    @expose
    def orchestrate(self, envelope_data: dict) -> dict:
        try:
            envelope = MCPEnvelope(
                envelope_id=envelope_data.get("envelope_id", f"env-{int(time.time())}"),
                created_at=envelope_data.get("created_at", time.strftime("%Y-%m-%dT%H:%M:%SZ")),
                agent=envelope_data.get("agent", "orchestrator"),
                payload=envelope_data.get("payload", {}),
            )
            if self.signer_fn:
                envelope.signature = self.signer_fn(envelope.dict())
            else:
                envelope.signature = f"signed-{envelope.envelope_id}"
            self._log_envelope(envelope)
            self._persist_to_bigquery(envelope)
            return envelope.dict()
        except Exception as e:
            self.logger.error(f"Orchestration failed: {e}")
            raise

    def _log_envelope(self, envelope: MCPEnvelope):
        log_entry = {
            "event": "mcp_envelope_created",
            "envelope_id": envelope.envelope_id,
            "agent": envelope.agent,
            "created_at": envelope.created_at,
            "signature": envelope.signature,
        }
        if hasattr(self.logger, "log_struct"):
            self.logger.log_struct(log_entry, severity="INFO")
        else:
            self.logger.info(log_entry)

    def _persist_to_bigquery(self, envelope: MCPEnvelope):
        try:
            table = self.bq_client.get_table(self.bq_table)
            row = envelope.dict()
            self.bq_client.insert_rows_json(table, [row])
        except Exception as e:
            self.logger.error(f"BigQuery persistence failed: {e}")

    @staticmethod
    def get_agent_card():
        return {
            "id": "orchestrator-agent",
            "name": "OrchestratorAgent",
            "endpoint": "<REPLACE_WITH_ENDPOINT>",
            "methods": ["route_task", "get_agent_card"],
            "description": "Orchestrates agent workflow and MCP envelope creation.",
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

def serve_agent_card(agent, port=9004):
    server = HTTPServer(("0.0.0.0", port), AgentCardHandler)
    server.agent = agent
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Agent Card HTTP endpoint running at http://0.0.0.0:{port}/agent_card")

if __name__ == "__main__":
    agent = OrchestratorAgent()
    serve_agent_card(agent, port=9004)  # Agent Card HTTP endpoint
    agent.run(host="0.0.0.0", port=8004)  # A2A JSON-RPC server
