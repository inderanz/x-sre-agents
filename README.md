# x-sre-agents

## Overview

x-sre-agents is an enterprise-grade, production-ready SRE automation platform built on a modular, agentic architecture. Each agent is implemented as an [A2A protocol](https://github.com/a2aproject/A2A) endpoint, enabling secure, interoperable, and auditable workflows across clouds, organizations, and technology stacks.

- **Platform-agnostic:** Ingests and remediates alerts from any Google Cloud or custom source.
- **A2A-enabled:** All agents expose their core methods as JSON-RPC endpoints using the [a2a-sdk](https://github.com/a2aproject/A2A).
- **LLM-powered:** Uses Gemini CLI for reasoning and CI/CD evaluation.
- **MCP-compliant:** All actions are signed and auditable via Managed Control Plane envelopes.
- **Extensible:** Plug-and-play new agents, tools, or integrations with zero code changes.

## End-to-End Architecture & Workflow

### Complete System Design

```mermaid
flowchart TD
    subgraph "1. Alert Ingestion & Normalization"
        A["Google Cloud Monitoring<br/>(GKE, Spanner, Kafka, IAM, etc.)"] --> B["Pub/Sub Topic<br/>(Alert Stream)"]
        B --> C["WatcherAgent (A2A)<br/>Port: 8010 + 9000/agent_card<br/>• Ingests alerts from Pub/Sub<br/>• Normalizes to standard format<br/>• Creates initial MCP envelope<br/>• Logs to Cloud Logging"]
        C --> C1["Signal: {message, severity, timestamp}<br/>Context: {org, environment, metadata}"]
    end
    
    subgraph "2. Classification & Enrichment"
        C1 --> D["ClassifierAgent (A2A)<br/>Port: 8001 + 9001/agent_card<br/>• Rules engine classification<br/>• Gemini CLI fallback<br/>• Returns: action_type, confidence"]
        D --> E["GroundingAgent (A2A)<br/>Port: 8002 + 9002/agent_card<br/>• Vector search for context<br/>• Retrieves relevant docs/runbooks<br/>• Returns: grounding_snippets"]
        E --> F["PersonalizationAgent (A2A)<br/>Port: 8003 + 9003/agent_card<br/>• Org-specific prompt injection<br/>• Custom policies & procedures<br/>• Returns: personalized_examples"]
    end
    
    subgraph "3. Orchestration & MCP Management"
        F --> G["OrchestratorAgent (A2A)<br/>Port: 8004 + 9004/agent_card<br/>• Creates MCP envelope<br/>• Signs with digital signature<br/>• Routes to next agent<br/>• Persists to BigQuery"]
        G --> G1["MCP Envelope:<br/>{envelope_id, created_at,<br/>agent, payload, signature}"]
    end
    
    subgraph "4. LLM Reasoning & Planning"
        G1 --> H["ReasoningAgent (A2A)<br/>Port: 8005 + 9005/agent_card<br/>• Gemini CLI integration<br/>• Root cause analysis<br/>• Remediation planning<br/>• Returns: ActionProposal"]
        H --> H1["ActionProposal:<br/>{action, reason, confidence,<br/>resource_id, parameters}"]
    end
    
    subgraph "5. Policy Validation"
        H1 --> I["PolicyAgent (A2A)<br/>Port: 8006 + 9006/agent_card<br/>• OPA Gatekeeper integration<br/>• Policy compliance check<br/>• Security validation<br/>• Returns: {admit, reason, confidence}"]
        I --> I1{Policy Decision}
    end
    
    subgraph "6. Execution & Validation"
        I1 -->|"Admitted"| J["ExecutorAgent (A2A)<br/>Port: 8007 + 9007/agent_card<br/>• GKE operations (scale, restart)<br/>• Cloud Run deployments<br/>• Spanner admin actions<br/>• Kafka management<br/>• Returns: execution_result"]
        I1 -->|"Denied/Low Confidence"| K["NotificationAgent (A2A)<br/>Port: 8008 + 9008/agent_card<br/>• Slack escalation<br/>• Email notifications<br/>• PagerDuty integration<br/>• Returns: notification_status"]
        J --> L["ValidatorAgent (A2A)<br/>Port: 8009 + 9009/agent_card<br/>• Post-execution validation<br/>• BigQuery health checks<br/>• Kubernetes state verification<br/>• Returns: validation_result"]
    end
    
    subgraph "7. Quality Assurance"
        G & H & I & J & K & L --> M["LLMJudgeAgent (A2A)<br/>Port: 8011 + 9011/agent_card<br/>• CI/CD evaluation<br/>• Workflow quality scoring<br/>• Improvement suggestions<br/>• Returns: {score, comments}"]
    end
    
    subgraph "8. Discovery & Interoperability"
        N["Agent Registry<br/>• Collects Agent Cards<br/>• Service discovery<br/>• Health monitoring<br/>• Load balancing"]
        O["A2A Protocol<br/>• JSON-RPC 2.0<br/>• Agent Cards<br/>• Secure communication<br/>• Standards compliance"]
    end
    
    C -.->|Agent Card| N
    D -.->|Agent Card| N
    E -.->|Agent Card| N
    F -.->|Agent Card| N
    G -.->|Agent Card| N
    H -.->|Agent Card| N
    I -.->|Agent Card| N
    J -.->|Agent Card| N
    K -.->|Agent Card| N
    L -.->|Agent Card| N
    M -.->|Agent Card| N
    
    style C fill:#e1f5fe
    style D fill:#f3e5f5
    style E fill:#e8f5e8
    style F fill:#fff3e0
    style G fill:#fce4ec
    style H fill:#e0f2f1
    style I fill:#f1f8e9
    style J fill:#fff8e1
    style K fill:#fce4ec
    style L fill:#e8f5e8
    style M fill:#e3f2fd
```

### Detailed Workflow Steps

#### **Step 1: Alert Ingestion & Normalization**
1. **Source**: Google Cloud Monitoring detects issues (high CPU, pod failures, etc.)
2. **Pub/Sub**: Alerts are published to a Pub/Sub topic
3. **WatcherAgent**: 
   - Listens to Pub/Sub subscription
   - Normalizes alerts to standard `Signal` format
   - Creates initial MCP envelope with audit trail
   - Logs to Cloud Logging with structured data

#### **Step 2: Classification & Enrichment**
4. **ClassifierAgent**:
   - Uses rules engine for fast classification
   - Falls back to Gemini CLI for complex cases
   - Returns action type (scale, restart, investigate)
5. **GroundingAgent**:
   - Performs vector search on documentation
   - Retrieves relevant runbooks and KB articles
   - Provides context for reasoning
6. **PersonalizationAgent**:
   - Injects organization-specific prompts
   - Applies custom policies and procedures
   - Ensures compliance with org standards

#### **Step 3: Orchestration & MCP Management**
7. **OrchestratorAgent**:
   - Creates MCP envelope with full context
   - Signs envelope for audit trail
   - Routes to next agent in workflow
   - Persists envelope to BigQuery for audit

#### **Step 4: LLM Reasoning & Planning**
8. **ReasoningAgent**:
   - Uses Gemini CLI for natural language reasoning
   - Analyzes root cause of the incident
   - Proposes specific remediation actions
   - Returns structured ActionProposal

#### **Step 5: Policy Validation**
9. **PolicyAgent**:
   - Integrates with OPA Gatekeeper
   - Validates proposed actions against policies
   - Ensures security and compliance
   - Returns admit/deny decision with confidence

#### **Step 6: Execution & Validation**
10. **ExecutorAgent** (if admitted):
    - Executes approved actions on GCP resources
    - Uses Google Cloud SDKs and CLI tools
    - Logs all actions for audit
    - Returns execution results
11. **NotificationAgent** (if denied):
    - Sends escalations to Slack/email
    - Notifies on-call engineers
    - Creates incident tickets
12. **ValidatorAgent**:
    - Verifies post-execution system health
    - Queries BigQuery for metrics
    - Checks Kubernetes cluster state
    - Confirms incident resolution

#### **Step 7: Quality Assurance**
13. **LLMJudgeAgent**:
    - Evaluates entire workflow quality
    - Scores effectiveness of remediation
    - Provides improvement suggestions
    - Used for CI/CD pipeline validation

### Agent Discovery & Interoperability

```mermaid
sequenceDiagram
    participant Registry as Agent Registry
    participant Orchestrator as OrchestratorAgent
    participant Agent as Any Agent
    participant A2A as A2A Protocol

    Agent->>Registry: Register Agent Card
    Registry->>Registry: Store agent metadata
    Orchestrator->>Registry: Query available agents
    Registry->>Orchestrator: Return Agent Cards
    Orchestrator->>Agent: JSON-RPC call
    Agent->>Orchestrator: Return result
    Orchestrator->>A2A: Log interaction
```

### Data Flow & MCP Envelope Structure

```mermaid
flowchart LR
    subgraph "MCP Envelope Evolution"
        A["Initial Envelope<br/>{envelope_id, created_at,<br/>agent: 'watcher', payload: signal}"]
        B["Enriched Envelope<br/>{...agent: 'classifier',<br/>payload: {signal, classification}}"]
        C["Final Envelope<br/>{...agent: 'executor',<br/>payload: {signal, classification,<br/>reasoning, policy_result,<br/>execution_result}}"]
    end
    
    A --> B --> C
```

## Running Agents as A2A Services

Each agent is a standalone A2A service with dual discovery methods:

### **JSON-RPC Endpoints (A2A Protocol)**
```sh
python src/agents/classifier_agent.py      # Runs ClassifierAgent on port 8001
python src/agents/grounding_agent.py       # Runs GroundingAgent on port 8002
python src/agents/personalization_agent.py # Runs PersonalizationAgent on port 8003
python src/agents/orchestrator_agent.py    # Runs OrchestratorAgent on port 8004
python src/agents/reasoning_agent.py       # Runs ReasoningAgent on port 8005
python src/agents/policy_agent.py          # Runs PolicyAgent on port 8006
python src/agents/executor_agent.py        # Runs ExecutorAgent on port 8007
python src/agents/notification_agent.py    # Runs NotificationAgent on port 8008
python src/agents/validator_agent.py       # Runs ValidatorAgent on port 8009
python src/agents/watcher_agent.py         # Runs WatcherAgent on port 8010
python src/agents/llmjudge_agent.py        # Runs LLMJudgeAgent on port 8011
```

### **HTTP REST Endpoints (Agent Card Discovery)**
Each agent also serves its Agent Card at:
- `http://localhost:9000/agent_card` (WatcherAgent)
- `http://localhost:9001/agent_card` (ClassifierAgent)
- `http://localhost:9002/agent_card` (GroundingAgent)
- And so on...

## Orchestrating the Workflow via A2A

### **Using A2A SDK Client**
```python
from a2a_sdk import A2AClient

# Initialize clients for each agent
classifier = A2AClient('http://localhost:8001')
grounder = A2AClient('http://localhost:8002')
personalizer = A2AClient('http://localhost:8003')
orchestrator = A2AClient('http://localhost:8004')
reasoner = A2AClient('http://localhost:8005')
policy = A2AClient('http://localhost:8006')
executor = A2AClient('http://localhost:8007')
validator = A2AClient('http://localhost:8009')

# Execute workflow
signal = {"message": "High CPU usage detected", "severity": "critical"}
context = {"org": "prod", "environment": "gke-cluster-1"}

# Step 1: Classify
classification, method = classifier.classify(signal, context)

# Step 2: Ground
grounding = grounder.ground(signal, classification)

# Step 3: Personalize
examples = personalizer.personalize(context, grounding)

# Step 4: Orchestrate
mcp_envelope = orchestrator.orchestrate({
    "envelope_id": "env-123",
    "agent": "orchestrator",
    "payload": {"signal": signal, "classification": classification}
})

# Step 5: Reason
action_proposal = reasoner.reason(mcp_envelope, grounding, examples)

# Step 6: Policy Check
policy_result = policy.policy_check(action_proposal)

# Step 7: Execute (if admitted)
if policy_result["admit"]:
    execution_result = executor.execute(action_proposal)
    validation_result = validator.validate(execution_result)
```

### **Using HTTP REST (Agent Card Discovery)**
```bash
# Discover agent capabilities
curl http://localhost:9000/agent_card
curl http://localhost:9001/agent_card
# ... etc

# Example response:
{
  "id": "watcher-agent",
  "name": "WatcherAgent", 
  "endpoint": "http://localhost:8010/jsonrpc",
  "methods": ["ingest_alert", "get_agent_card"],
  "description": "Ingests and normalizes alerts from Pub/Sub and other sources.",
  "version": "1.0.0",
  "owner": "SRE Automation Team"
}
```

## Key Features

### **A2A Protocol Compliance**
- All agents expose JSON-RPC 2.0 endpoints
- Agent Cards for discovery and capability negotiation
- Secure, standards-based communication
- Interoperable across different implementations

### **MCP (Model Context Protocol) Integration**
- All actions wrapped in signed MCP envelopes
- Full audit trail from ingestion to execution
- BigQuery persistence for compliance
- Digital signatures for integrity

### **LLM Integration (Gemini CLI)**
- **ClassifierAgent**: Fallback classification when rules are insufficient
- **ReasoningAgent**: Root cause analysis and remediation planning
- **PersonalizationAgent**: Org-specific prompt injection
- **LLMJudgeAgent**: CI/CD evaluation and quality scoring

### **Security & Compliance**
- **PolicyAgent**: OPA Gatekeeper integration for policy enforcement
- **ExecutorAgent**: Isolated execution with least privilege
- **ValidatorAgent**: Post-execution validation and health checks
- **NotificationAgent**: Escalation and incident management

### **Enterprise Features**
- Structured logging to Cloud Logging
- BigQuery persistence for analytics
- Agent discovery and health monitoring
- Extensible architecture for new agents/tools

## Interoperability Notes

- Agents can be distributed across clouds, orgs, or languages
- Each agent publishes an Agent Card for discovery
- All agent-to-agent calls are secure, auditable, and standards-based
- MCP envelopes ensure full traceability and compliance

## References
- [A2A Project on GitHub](https://github.com/a2aproject/A2A)
- [A2A Protocol Documentation](https://a2aproject.github.io/A2A/)
- [Google Cloud Monitoring](https://cloud.google.com/monitoring)
- [OPA Gatekeeper](https://open-policy-agent.github.io/gatekeeper/)
