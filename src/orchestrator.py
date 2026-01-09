"""
GodAgent Orchestrator

Main orchestration engine that:
1. Receives tasks from users
2. Uses LLM Council to select the best agent
3. Executes the selected agent with original prompts
4. Manages inter-agent communication (full-mesh)
5. Logs decisions and collects feedback
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

try:
    from src.config import get_config, AgentConfig
except ImportError:
    from .config import get_config, AgentConfig


# =============================================================================
# ENUMS AND TYPES
# =============================================================================

class ApprovalMode(Enum):
    """Approval mode settings."""
    AUTO = "AUTO"
    APPROVE_ALL = "APPROVE_ALL"
    APPROVE_HIGH_RISK = "APPROVE_HIGH_RISK"


class TaskStatus(Enum):
    """Status of a task in the orchestration pipeline."""
    PENDING = "pending"
    COUNCIL_SELECTING = "council_selecting"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Task:
    """Represents a task submitted to GodAgent."""
    id: str
    system_prompt: str
    user_prompt: str
    working_directory: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: TaskStatus = TaskStatus.PENDING


@dataclass
class AgentSelection:
    """Result of the council agent selection."""
    selected_agent: str
    confidence: float
    reasoning: str
    votes: Dict[str, str] = field(default_factory=dict)
    rankings: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of agent execution."""
    task_id: str
    agent: str
    response: str
    success: bool
    duration_ms: int
    error: Optional[str] = None
    inter_agent_calls: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Decision:
    """A logged decision for audit trail."""
    id: str
    task_id: str
    decision_type: str
    title: str
    reasoning: str
    confidence: float
    alternatives: List[str] = field(default_factory=list)
    outcome: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


# =============================================================================
# ORCHESTRATOR
# =============================================================================

class Orchestrator:
    """
    Main GodAgent orchestrator.
    
    This is the central coordinator that:
    - Receives user tasks
    - Manages the council selection process
    - Handles approval workflows
    - Executes agents
    - Logs decisions
    
    Usage:
        orchestrator = Orchestrator()
        result = await orchestrator.process_task(
            system_prompt="You are a helpful assistant.",
            user_prompt="Write a Python script that...",
        )
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.config = get_config()
        self.logger = logging.getLogger("godagent.orchestrator")
        
        # Internal state
        self._tasks: Dict[str, Task] = {}
        self._decisions: List[Decision] = []
        
        # Will be initialized in Phase 2+
        self._council_selector = None  # CouncilSelector
        self._executor = None  # AgentExecutor
        self._decision_logger = None  # DecisionLogger
        
    async def process_task(
        self,
        system_prompt: str,
        user_prompt: str,
        working_directory: Optional[str] = None,
        approval_mode: Optional[ApprovalMode] = None,
    ) -> ExecutionResult:
        """
        Process a task through the full GodAgent pipeline.
        
        Args:
            system_prompt: System prompt for the task
            user_prompt: User prompt for the task
            working_directory: Optional working directory for CLI agents
            approval_mode: Override approval mode for this task
            
        Returns:
            ExecutionResult with the agent's response
        """
        import uuid
        
        # Create task
        task = Task(
            id=str(uuid.uuid4()),
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            working_directory=working_directory,
        )
        self._tasks[task.id] = task
        self.logger.info(f"Processing task {task.id}: {user_prompt[:50]}...")
        
        try:
            # Step 1: Select agent via council
            task.status = TaskStatus.COUNCIL_SELECTING
            selection = await self._select_agent(task)
            
            # Step 2: Check approval if needed
            mode = approval_mode or ApprovalMode(
                self.config.settings.approval.get("mode", "AUTO")
            )
            if mode != ApprovalMode.AUTO:
                task.status = TaskStatus.AWAITING_APPROVAL
                approved = await self._check_approval(task, selection, mode)
                if not approved:
                    task.status = TaskStatus.REJECTED
                    return ExecutionResult(
                        task_id=task.id,
                        agent=selection.selected_agent,
                        response="",
                        success=False,
                        duration_ms=0,
                        error="User rejected agent selection",
                    )
            
            # Step 3: Execute agent
            task.status = TaskStatus.EXECUTING
            result = await self._execute_agent(task, selection.selected_agent)
            
            # Step 4: Log decision
            await self._log_decision(task, selection, result)
            
            task.status = TaskStatus.COMPLETED
            return result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            self.logger.error(f"Task {task.id} failed: {e}")
            raise
            
    async def _select_agent(self, task: Task) -> AgentSelection:
        """
        Select the best agent for the task using LLM Council.
        
        Phase 2 will implement actual council voting.
        For now, returns a placeholder selection.
        """
        self.logger.info("Selecting agent via council...")
        
        # TODO: Phase 2 - Implement actual council selection
        # Will use llmCouncil.council.run_full_council()
        
        # Placeholder: default to Claude
        return AgentSelection(
            selected_agent="claude",
            confidence=0.9,
            reasoning="Default selection (council not yet implemented)",
            votes={},
            rankings={},
        )
        
    async def _check_approval(
        self,
        task: Task,
        selection: AgentSelection,
        mode: ApprovalMode,
    ) -> bool:
        """
        Check if user approves the agent selection.
        
        Phase 4 will implement actual approval UI.
        For now, auto-approves.
        """
        self.logger.info(f"Approval mode: {mode.value}")
        
        # TODO: Phase 4 - Implement approval workflow
        # Will integrate with seedGPT approval patterns
        
        # Placeholder: auto-approve
        return True
        
    async def _execute_agent(
        self,
        task: Task,
        agent_name: str,
    ) -> ExecutionResult:
        """
        Execute the selected agent with the original prompts.
        
        Phase 3 will implement direct agent execution.
        For now, returns a placeholder response.
        """
        import time
        start_time = time.time()
        
        self.logger.info(f"Executing agent: {agent_name}")
        
        # TODO: Phase 3 - Implement actual agent execution
        # Will use agentsParliament MCP servers
        
        # Placeholder response
        duration_ms = int((time.time() - start_time) * 1000)
        return ExecutionResult(
            task_id=task.id,
            agent=agent_name,
            response=f"[Placeholder] Agent '{agent_name}' would process: {task.user_prompt[:100]}...",
            success=True,
            duration_ms=duration_ms,
        )
        
    async def _log_decision(
        self,
        task: Task,
        selection: AgentSelection,
        result: ExecutionResult,
    ) -> None:
        """
        Log the decision for audit trail.
        
        Phase 4 will implement seedGPT decision logging.
        For now, logs locally.
        """
        import uuid
        
        decision = Decision(
            id=str(uuid.uuid4()),
            task_id=task.id,
            decision_type="AGENT_SELECTION",
            title=f"Selected {selection.selected_agent} for task",
            reasoning=selection.reasoning,
            confidence=selection.confidence,
            alternatives=list(self.config.agents.keys()),
            outcome="success" if result.success else "failure",
        )
        self._decisions.append(decision)
        
        self.logger.info(
            f"Decision logged: {decision.decision_type} -> {selection.selected_agent}"
        )
        
    def get_available_agents(self) -> List[str]:
        """Get list of available agent names."""
        return self.config.get_agent_names()
        
    def get_agent_info(self, name: str) -> AgentConfig:
        """Get detailed info about an agent."""
        return self.config.get_agent(name)
        
    def get_decisions(self, limit: int = 100) -> List[Decision]:
        """Get recent decisions for audit."""
        return self._decisions[-limit:]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_orchestrator: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    """Get the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
