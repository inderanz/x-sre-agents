from a2a_sdk import Agent, expose
import logging
import requests
from typing import Any
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class NotificationAgent(Agent):
    """
    A2A-enabled NotificationAgent for production SRE workflows.
    Exposes notify as a JSON-RPC method for agentic interoperability.
    Sends escalations to Slack using the Slack API, with structured logging and error handling.
    """
    def __init__(self, slack_webhook_url: str, logger=None):
        super().__init__()
        self.slack_webhook_url = slack_webhook_url
        self.logger = logger or logging.getLogger("notification-agent")

    @expose
    def notify(self, incident: dict, reason: str) -> bool:
        message = self._build_slack_message(incident, reason)
        try:
            response = requests.post(
                self.slack_webhook_url,
                json={"text": message},
                timeout=5
            )
            response.raise_for_status()
            self._log_notification(incident, reason, True, response.text)
            return True
        except Exception as e:
            self.logger.error(f"Slack notification failed: {e}")
            self._log_notification(incident, reason, False, str(e))
            return False

    @expose
    def notify_with_solution(self, incident: dict, action_proposal: dict, policy_result: dict) -> bool:
        """
        Sends a Slack notification with the LLM-proposed solution when execution is denied by policy.
        """
        message = (
            f"🚨 Incident: {incident.get('message', 'N/A')}\n"
            f"🔍 Classification: {action_proposal.get('action', 'N/A')}\n"
            f"🤖 Proposed Solution (LLM):\n  {action_proposal.get('reason', 'N/A')}\n"
            f"❌ Action NOT auto-executed (policy: {policy_result.get('reason', 'N/A')})\n"
            "👤 Please review and approve or escalate."
        )
        try:
            response = requests.post(
                self.slack_webhook_url,
                json={"text": message},
                timeout=5
            )
            response.raise_for_status()
            self._log_notification(incident, action_proposal.get('reason', ''), True, response.text)
            return True
        except Exception as e:
            self.logger.error(f"Slack notification with solution failed: {e}")
            self._log_notification(incident, action_proposal.get('reason', ''), False, str(e))
            return False

    @staticmethod
    def get_agent_card():
        return {
            "id": "notification-agent",
            "name": "NotificationAgent",
            "endpoint": "<REPLACE_WITH_ENDPOINT>",
            "methods": ["send_notification", "get_agent_card"],
            "description": "Sends notifications and escalations (e.g., Slack).",
            "version": "1.0.0",
            "owner": "SRE Automation Team"
        }

    def get_agent_card_rpc(self, params=None):
        return self.get_agent_card()

    def _build_slack_message(self, incident: dict, reason: str) -> str:
        return (
            f":rotating_light: *SRE Escalation* :rotating_light:\n"
            f"Incident ID: {incident.get('incident_id', 'N/A')}\n"
            f"Severity: {incident.get('severity', 'N/A')}\n"
            f"Reason: {reason}\n"
            f"Details: {incident.get('message', '')}"
        )

    def _log_notification(self, incident, reason, success, details):
        log_entry = {
            "event": "notification_sent",
            "incident_id": incident.get('incident_id'),
            "severity": incident.get('severity'),
            "reason": reason,
            "success": success,
            "details": details,
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

def serve_agent_card(agent, port=9008):
    server = HTTPServer(("0.0.0.0", port), AgentCardHandler)
    server.agent = agent
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Agent Card HTTP endpoint running at http://0.0.0.0:{port}/agent_card")

if __name__ == "__main__":
    agent = NotificationAgent(slack_webhook_url="https://hooks.slack.com/services/your/webhook/url")
    serve_agent_card(agent, port=9008)  # Agent Card HTTP endpoint
    agent.run(host="0.0.0.0", port=8008)  # A2A JSON-RPC server
