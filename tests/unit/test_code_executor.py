# Unit tests for AgentEngineSandboxCodeExecutor configuration

from app.agent import (
    AGENT_ENGINE_RESOURCE_NAME,
    SANDBOX_RESOURCE_NAME,
    root_agent,
)
from google.adk.code_executors.agent_engine_sandbox_code_executor import (
    AgentEngineSandboxCodeExecutor,
)


def test_agent_has_code_executor():
    assert root_agent.code_executor is not None
    assert isinstance(root_agent.code_executor, AgentEngineSandboxCodeExecutor)
    assert root_agent.code_executor.sandbox_resource_name == SANDBOX_RESOURCE_NAME
    assert SANDBOX_RESOURCE_NAME.startswith(AGENT_ENGINE_RESOURCE_NAME)
    assert "sandboxEnvironments" in SANDBOX_RESOURCE_NAME
