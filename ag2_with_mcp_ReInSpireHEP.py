from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client

from autogen import LLMConfig
from autogen.agentchat import AssistantAgent
from autogen.mcp import create_toolkit
import json
import anyio
import asyncio

# Only needed for Jupyter notebooks
import nest_asyncio
nest_asyncio.apply()

from autogen.agentchat.group import (
    AgentNameTarget,
    AgentTarget,
    AskUserTarget,
    ContextExpression,
    ContextStr,
    ContextStrLLMCondition,
    ContextVariables,
    ExpressionAvailableCondition,
    ExpressionContextCondition,
    GroupChatConfig,
    GroupChatTarget,
    Handoffs,
    NestedChatTarget,
    OnCondition,
    OnContextCondition,
    ReplyResult,
    RevertToUserTarget,
    SpeakerSelectionResult,
    StayTarget,
    StringAvailableCondition,
    StringContextCondition,
    StringLLMCondition,
    TerminateTarget,
)

from autogen.agentchat.group.patterns import (
    DefaultPattern,
    ManualPattern,
    AutoPattern,
    RandomPattern,
    RoundRobinPattern,
)


from autogen import ConversableAgent, UpdateSystemMessage
from autogen.agents.experimental import DocAgent
import os
import copy
from typing import Any, Dict, List
from pydantic import BaseModel, Field


from autogen.agentchat import initiate_group_chat, a_initiate_group_chat



#%%
# Path to the arxiv MCP server
mcp_server_path = Path("mcp_reinspire.py")

#%%
