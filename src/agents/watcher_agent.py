from a2a_sdk import Agent, expose
import os
import json
import time
from google.cloud import pubsub_v1, logging as gcp_logging
from src.schemas import Signal, Context
from typing import Callable
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class WatcherAgent(Agent):
    """
    A2A-enabled WatcherAgent for production SRE workflows.
    Exposes ingest as a JSON-RPC method for agentic interoperability.
    Listens for incoming alerts from Pub/Sub and can be triggered via A2A.
    """
    def __init__(self, subscription_name: str, project_id: str, downstream_callback: Callable, logger=None):
        super().__init__()
        self.project_id = project_id
        self.subscription_path = f"projects/{project_id}/subscriptions/{subscription_name}"
        self.subscriber = pubsub_v1.SubscriberClient()
        self.logger = logger or gcp_logging.Client().logger("watcher-agent")
        self.downstream_callback = downstream_callback

    @expose
    def ingest(self, raw_data: dict = None):
        """
        Ingest a message from Pub/Sub (if raw_data is None) or directly via A2A (if raw_data is provided).
        """
        if raw_data is not None:
            self._process_message(raw_data)
            return {"status": "processed via A2A"}
        else:
            def callback(message):
                try:
                    data = json.loads(message.data.decode("utf-8"))
                    self._process_message(data)
                    message.ack()
                except Exception as e:
                    self.logger.log_struct({
                        "event": "alert_processing_error",
                        "error": str(e),
                        "raw_message": message.data.decode("utf-8")
                    }, severity="ERROR")
                    message.nack()
            streaming_pull_future = self.subscriber.subscribe(self.subscription_path, callback=callback)
            print(f"WatcherAgent listening for messages on {self.subscription_path}...")
            try:
                streaming_pull_future.result()
            except Exception as e:
                self.logger.log_struct({
                    "event": "pubsub_listener_error",
                    "error": str(e)
                }, severity="CRITICAL")
                streaming_pull_future.cancel()
                raise
            return {"status": "listening to Pub/Sub"}

    def _process_message(self, raw_data: dict):
        signal = Signal(
            source=raw_data.get("source"),
            type=raw_data.get("type"),
            message=raw_data.get("message"),
            timestamp=raw_data.get("timestamp"),
            resource=raw_data.get("resource"),
            labels=raw_data.get("labels"),
        )
        context = Context(
            incident_id=raw_data.get("incident_id"),
            severity=raw_data.get("severity"),
            environment=raw_data.get("environment"),
            detected_at=raw_data.get("timestamp"),
            additional_info=raw_data.get("additional_info"),
        )
        self._log_received_alert(signal, context)
        self.downstream_callback(signal, context)

    def _log_received_alert(self, signal: Signal, context: Context):
        log_entry = {
            "event": "received_alert",
            "cluster": signal.labels.get("cluster") if signal.labels else None,
            "namespace": signal.labels.get("namespace") if signal.labels else None,
            "metric": signal.type,
            "timestamp": signal.timestamp,
            "incident_id": context.incident_id,
            "severity": context.severity,
            "environment": context.environment,
        }
        self.logger.log_struct(log_entry, severity="INFO")

    @staticmethod
    def get_agent_card():
        return {
            "id": "watcher-agent",
            "name": "WatcherAgent",
            "endpoint": "<REPLACE_WITH_ENDPOINT>",
            "methods": ["ingest_alert", "get_agent_card"],
            "description": "Ingests and normalizes alerts from Pub/Sub and other sources.",
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

def serve_agent_card(agent, port=9000):
    server = HTTPServer(("0.0.0.0", port), AgentCardHandler)
    server.agent = agent
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Agent Card HTTP endpoint running at http://0.0.0.0:{port}/agent_card")

if __name__ == "__main__":
    # Example downstream_callback: replace with A2A client call in production
    def downstream_callback(signal, context):
        print(f"Downstream: {signal}, {context}")
    agent = WatcherAgent(subscription_name="your-subscription", project_id="your-project", downstream_callback=downstream_callback)
    serve_agent_card(agent, port=9000)  # Agent Card HTTP endpoint
    agent.run(host="0.0.0.0", port=8010)  # A2A JSON-RPC server
