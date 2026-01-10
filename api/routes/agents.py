"""
Agents Endpoint

List and get information about available agents.
AGENTS ARE NOT LLMs - they have CLI/SDK with agentic capabilities.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import get_config


router = APIRouter()


# =============================================================================
# MODELS
# =============================================================================

class AgentInfo(BaseModel):
    """Information about an agent (CLI-based, not LLM)."""
    name: str
    display_name: str
    type: str  # Always "cli" for agents
    command: Optional[str]  # CLI command (e.g., "claude", "aider")
    capabilities: List[str]
    strengths: List[str]
    mcp_server: Optional[str]
    requires_working_directory: bool


class AgentsListResponse(BaseModel):
    """Response for listing agents."""
    agents: List[AgentInfo]
    count: int


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/agents", response_model=AgentsListResponse)
async def list_agents():
    """
    List all available agents.
    
    Returns information about each agent including capabilities and strengths.
    All agents are CLI-based (not LLM APIs).
    """
    config = get_config()
    agents = []
    
    for name in config.get_agent_names():
        agent = config.get_agent(name)
        agents.append(AgentInfo(
            name=name,
            display_name=agent.display_name,
            type=agent.type,
            command=agent.command,
            capabilities=agent.capabilities,
            strengths=agent.strengths,
            mcp_server=agent.mcp_server,
            requires_working_directory=agent.requires_working_directory,
        ))
        
    return AgentsListResponse(agents=agents, count=len(agents))


@router.get("/agents/{agent_name}", response_model=AgentInfo)
async def get_agent(agent_name: str):
    """
    Get information about a specific agent.
    
    Args:
        agent_name: Name of the agent (e.g., "claude", "aider")
    """
    config = get_config()
    
    try:
        agent = config.get_agent(agent_name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_name}")
        
    return AgentInfo(
        name=agent_name,
        display_name=agent.display_name,
        type=agent.type,
        command=agent.command,
        capabilities=agent.capabilities,
        strengths=agent.strengths,
        mcp_server=agent.mcp_server,
        requires_working_directory=agent.requires_working_directory,
    )


@router.get("/agents/by-capability/{capability}")
async def get_agents_by_capability(capability: str):
    """
    Get agents that have a specific capability.
    
    Args:
        capability: Capability name (e.g., "coding", "research")
    """
    config = get_config()
    agents = config.get_agents_by_capability(capability)
    
    return {
        "capability": capability,
        "agents": agents,
        "count": len(agents),
    }
