from a2a_sdk import Agent, expose
import logging
from typing import List, Dict, Any
# from google.cloud import discoveryengine_v1beta as cloud_search  # For Google Cloud Search (if used)
# import faiss  # For FAISS vector search (if used)
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class GroundingAgent(Agent):
    """
    A2A-enabled GroundingAgent for production SRE workflows.
    Exposes ground as a JSON-RPC method for agentic interoperability.
    """
    def __init__(self, logger=None, vector_search_fn=None):
        super().__init__()
        self.logger = logger or logging.getLogger("grounding-agent")
        self.vector_search_fn = vector_search_fn

    @expose
    def ground(self, signal: dict, query_class: str) -> List[Dict[str, Any]]:
        try:
            if self.vector_search_fn:
                results = self.vector_search_fn(signal, query_class)
            else:
                results = [
                    {"doc_id": "runbook-123", "snippet": "Restart the affected pod...", "score": 0.95},
                    {"doc_id": "kb-456", "snippet": "Check CPU usage in GKE dashboard...", "score": 0.91},
                ]
            self._log_grounding(signal, query_class, results)
            return results
        except Exception as e:
            self.logger.error(f"Grounding failed: {e}")
            return []

    def _log_grounding(self, signal, query_class, results):
        log_entry = {
            "event": "grounding_retrieved",
            "signal": signal,
            "query_class": query_class,
            "num_results": len(results),
            "top_result": results[0] if results else None,
        }
        if hasattr(self.logger, "log_struct"):
            self.logger.log_struct(log_entry, severity="INFO")
        else:
            self.logger.info(log_entry)

    @staticmethod
    def get_agent_card():
        return {
            "id": "grounding-agent",
            "name": "GroundingAgent",
            "endpoint": "<REPLACE_WITH_ENDPOINT>",
            "methods": ["enrich_context", "get_agent_card"],
            "description": "Enriches alerts with context using vector search.",
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

def serve_agent_card(agent, port=9002):
    server = HTTPServer(("0.0.0.0", port), AgentCardHandler)
    server.agent = agent
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Agent Card HTTP endpoint running at http://0.0.0.0:{port}/agent_card")

if __name__ == "__main__":
    agent = GroundingAgent()
    serve_agent_card(agent, port=9002)  # Agent Card HTTP endpoint
    agent.run(host="0.0.0.0", port=8002)  # A2A JSON-RPC server
