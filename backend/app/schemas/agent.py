from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class AgentToolCallLog(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result_summary: str
    execution_status: str = "success"


class AgentQueryRequest(BaseModel):
    query: str


class AgentQueryResponse(BaseModel):
    query: str
    answer: str
    tool_calls: List[AgentToolCallLog]
    guardrails_enforced: List[str]
    disclaimer: str
