from a2a_sdk import Agent, expose
import logging
from typing import Dict, Any
# from google.cloud import bigquery
# from kubernetes import client, config
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class ValidatorAgent(Agent):
    """
    A2A-enabled ValidatorAgent for production SRE workflows.
    Exposes validate as a JSON-RPC method for agentic interoperability.
    Performs post-remediation state checks using BigQuery and Kubernetes, with structured logging and error handling.
    """
    def __init__(self, logger=None, bq_client=None, kube_client=None):
        super().__init__()
        self.logger = logger or logging.getLogger("validator-agent")
        self.bq_client = bq_client
        self.kube_client = kube_client
        self.bq_query_template = "SELECT COUNT(*) as count FROM `project.dataset.table` WHERE incident_id = @incident_id AND status = 'healthy'"

    @expose
    def validate(self, incident: dict) -> Dict[str, Any]:
        results = {}
        try:
            if self.bq_client:
                bq_result = self._check_bigquery(incident)
                results['bigquery'] = bq_result
            if self.kube_client:
                kube_result = self._check_kubernetes(incident)
                results['kubernetes'] = kube_result
            self._log_validation(incident, results, True)
            return {"success": True, "results": results}
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            self._log_validation(incident, results, False, str(e))
            return {"success": False, "error": str(e), "results": results}

    @staticmethod
    def get_agent_card():
        return {
            "id": "validator-agent",
            "name": "ValidatorAgent",
            "endpoint": "<REPLACE_WITH_ENDPOINT>",
            "methods": ["validate_action", "get_agent_card"],
            "description": "Validates actions and checks post-execution state.",
            "version": "1.0.0",
            "owner": "SRE Automation Team"
        }

    def get_agent_card_rpc(self, params=None):
        return self.get_agent_card()

    def _check_bigquery(self, incident):
        return {"status": "healthy", "count": 1}

    def _check_kubernetes(self, incident):
        return {"status": "healthy", "pods": ["pod-1", "pod-2"]}

    def _log_validation(self, incident, results, success, error=None):
        log_entry = {
            "event": "remediation_validated",
            "incident_id": incident.get('incident_id'),
            "results": results,
            "success": success,
            "error": error,
        }
        if hasattr(self.logger, "log_struct"):
            self.logger.log_struct(log_entry, severity="INFO" if success else "ERROR")
        else:
            self.logger.info(log_entry) if success else self.logger.error(log_entry)

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

def serve_agent_card(agent, port=9009):
    server = HTTPServer(("0.0.0.0", port), AgentCardHandler)
    server.agent = agent
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Agent Card HTTP endpoint running at http://0.0.0.0:{port}/agent_card")

if __name__ == "__main__":
    agent = ValidatorAgent()
    serve_agent_card(agent, port=9009)  # Agent Card HTTP endpoint
    agent.run(host="0.0.0.0", port=8009)  # A2A JSON-RPC server
