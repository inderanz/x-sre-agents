from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Signal(BaseModel):
    source: str
    type: str
    message: str
    timestamp: str
    resource: Optional[str] = None
    labels: Optional[Dict[str, Any]] = None

class Context(BaseModel):
    incident_id: str
    severity: str
    environment: str
    detected_at: str
    additional_info: Optional[Dict[str, Any]] = None

class MCPEnvelope(BaseModel):
    envelope_id: str
    created_at: str
    agent: str
    payload: Dict[str, Any]
    signature: Optional[str] = None

class ActionProposal(BaseModel):
    action: str
    reason: str
    confidence: int = Field(..., ge=0, le=100)
    metadata: Optional[Dict[str, Any]] = None
