from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):

    question: str
    context: str
    memories: str
    answer: str

    user_id: str
    project_id: str

    input_allowed: bool
    repository_allowed: bool
    output_allowed: bool

    guardrail_reason: str

    conversation: Annotated[
        list[BaseMessage],
        add_messages
    ]