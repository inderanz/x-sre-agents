from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from datetime import datetime
import json

app = FastAPI(
    title="x-sre-agents",
    description="Enterprise-grade SRE automation platform with agentic architecture",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with platform information"""
    return {
        "message": "x-sre-agents platform",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "description": "Enterprise-grade SRE automation platform with agentic architecture"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "x-sre-agents"
    }

@app.get("/agents")
async def list_agents():
    """List all available agents"""
    agents = [
        {
            "name": "Watcher",
            "description": "Monitors infrastructure and detects anomalies",
            "status": "active"
        },
        {
            "name": "Classifier", 
            "description": "Categorizes incidents and issues",
            "status": "active"
        },
        {
            "name": "Grounding",
            "description": "Validates and grounds LLM outputs",
            "status": "active"
        },
        {
            "name": "Personalization",
            "description": "Customizes responses based on context",
            "status": "active"
        },
        {
            "name": "Orchestrator",
            "description": "Coordinates agent interactions",
            "status": "active"
        },
        {
            "name": "Reasoning",
            "description": "Performs logical analysis and decision making",
            "status": "active"
        },
        {
            "name": "Policy",
            "description": "Enforces security and compliance policies",
            "status": "active"
        },
        {
            "name": "Executor",
            "description": "Executes remediation actions",
            "status": "active"
        },
        {
            "name": "Notification",
            "description": "Manages alerting and notifications",
            "status": "active"
        },
        {
            "name": "Validator",
            "description": "Validates actions before execution",
            "status": "active"
        },
        {
            "name": "LLMJudge",
            "description": "Evaluates LLM outputs and decisions",
            "status": "active"
        }
    ]
    return {"agents": agents}

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "v1",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "workload_identity_federation": "enabled",
        "platform": "google-cloud-run"
    }

@app.post("/api/v1/incident")
async def create_incident(incident_data: dict):
    """Create a new incident (placeholder)"""
    return {
        "message": "Incident created successfully",
        "incident_id": "INC-001",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
