"""Agent core module."""

from nano_hermes.agent.context import ContextBuilder
from nano_hermes.agent.hook import AgentHook, AgentHookContext, CompositeHook
from nano_hermes.agent.loop import AgentLoop
from nano_hermes.agent.memory import Dream, MemoryStore
from nano_hermes.agent.skills import SkillsLoader
from nano_hermes.agent.subagent import SubagentManager

__all__ = [
    "AgentHook",
    "AgentHookContext",
    "AgentLoop",
    "CompositeHook",
    "ContextBuilder",
    "Dream",
    "MemoryStore",
    "SkillsLoader",
    "SubagentManager",
]
