
import sqlite3

from langchain_core.messages import AIMessage

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END

from graph.state import AgentState

from rag.retriever import get_retriever
from rag.answer import generate_answer

from memory.persistent_memory import retrieve_memories
from memory.memory_manager import extract_memory
from memory.database import (
    add_memory,
    update_memory,
)

from guardrails.input_guard import check_input
from guardrails.memory_guard import check_memory
from guardrails.repository_guard import check_repository_content
from guardrails.output_guard import check_output


# ==================================================
# RETRIEVER
# ==================================================

retriever = get_retriever()


# ==================================================
# MEMORY RETRIEVAL
# ==================================================

def retrieve_memory(state: AgentState):

    memories = retrieve_memories(
        user_id=state["user_id"],
        project_id=state["project_id"],
        question=state["question"],
    )

    if not memories:
        return {
            "memories": "No relevant persistent memories found."
        }

    memory_text = "\n".join(
        f"- {memory[2]} "
        f"(type={memory[3]}, importance={memory[4]})"
        for memory in memories
    )

    return {
        "memories": memory_text
    }


# ==================================================
# CODE RETRIEVAL
# ==================================================

def retrieve(state: AgentState):

    question = state["question"]

    documents = retriever.invoke(question)

    context = "\n\n".join(
        f"FILE: {doc.metadata.get('source')}\n"
        f"{doc.page_content}"
        for doc in documents
    )

    return {
        "context": context
    }


# ==================================================
# GENERATE ANSWER
# ==================================================

def generate(state: AgentState):

    question = state["question"]

    context = state["context"]

    memories = state["memories"]

    conversation = state["conversation"]

    # --------------------------------------------------
    # Convert conversation to text
    # --------------------------------------------------

    conversation_text = "\n".join(
        f"{message.type}: {message.content}"
        for message in conversation
    )

    # --------------------------------------------------
    # Combine memory + conversation + repository
    # --------------------------------------------------

    combined_context = f"""
Persistent memory:
--------------------
{memories}

Previous conversation:
--------------------
{conversation_text}

Repository context:
--------------------
{context}
"""

    # --------------------------------------------------
    # Generate grounded answer
    # --------------------------------------------------

    answer = generate_answer(
        question=question,
        context=combined_context,
    )

    return {
        "answer": answer,
        "conversation": [
            AIMessage(content=answer)
        ]
    }


# ==================================================
# MEMORY EXTRACTION + GUARDRAIL
# ==================================================

def save_memory(state: AgentState):

    conversation = state["conversation"]

    conversation_text = "\n".join(
        f"{message.type}: {message.content}"
        for message in conversation
    )

    # --------------------------------------------------
    # Extract memory decision
    # --------------------------------------------------

    memory = extract_memory(
        user_id=state["user_id"],
        project_id=state["project_id"],
        conversation=conversation_text,
    )

    if not memory:

        print("\nNo persistent memory extracted.")

        return {}

    action = memory.get("action")

    # --------------------------------------------------
    # DUPLICATE
    # --------------------------------------------------

    if action == "duplicate":

        print("\n" + "=" * 70)
        print("DUPLICATE MEMORY")
        print("=" * 70)

        print("Existing Memory ID:", memory.get("id"))

        return {}

    # --------------------------------------------------
    # NEW / MERGE
    # --------------------------------------------------

    if action not in ("new", "merge"):

        print("\nUnknown memory action.")

        return {}

    content = memory.get("content", "").strip()

    if not content:

        print("\nMemory content is empty.")

        return {}

    memory_type = memory.get(
        "memory_type",
        "fact"
    )

    importance = float(
        memory.get(
            "importance",
            0.5
        )
    )

    # --------------------------------------------------
    # MEMORY SECURITY GUARDRAIL
    # --------------------------------------------------

    guard_result = check_memory(
        content=content,
        memory_type=memory_type,
        importance=importance,
    )

    if not guard_result["allowed"]:

        print("\n" + "=" * 70)
        print("MEMORY BLOCKED BY GUARDRAIL")
        print("=" * 70)

        print(
            "Reason:",
            guard_result["reason"]
        )

        return {}

    # --------------------------------------------------
    # Use sanitized memory
    # --------------------------------------------------

    sanitized_content = (
        guard_result["sanitized_content"]
    )

    if not sanitized_content:

        print("\nMemory blocked: sanitized content is empty.")

        return {}

    # --------------------------------------------------
    # NEW MEMORY
    # --------------------------------------------------

    if action == "new":

        memory_id = add_memory(
            user_id=state["user_id"],
            project_id=state["project_id"],
            content=sanitized_content,
            memory_type=memory_type,
            importance=importance,
        )

        print("\n" + "=" * 70)
        print("NEW MEMORY SAVED")
        print("=" * 70)

        print("Memory ID:", memory_id)
        print("Type:", memory_type)
        print("Importance:", importance)
        print("Content:", sanitized_content)

        return {}

    # --------------------------------------------------
    # MERGE MEMORY
    # --------------------------------------------------

    if action == "merge":

        memory_id = memory.get("id")

        if not memory_id:

            print("\nMerge failed: memory ID missing.")

            return {}

        update_memory(
            memory_id=memory_id,
            content=sanitized_content,
            importance=importance,
        )

        print("\n" + "=" * 70)
        print("MEMORY MERGED")
        print("=" * 70)

        print("Memory ID:", memory_id)
        print("Importance:", importance)
        print("Content:", sanitized_content)

        return {}

    return {}


# ==================================================
# INPUT GUARDRAIL
# ==================================================

def input_guard(state: AgentState):

    result = check_input(
        state["question"]
    )

    if not result["allowed"]:

        return {
            "input_allowed": False,
            "guardrail_reason": result["reason"],
            "answer": (
                "Request blocked by "
                "input security guardrail."
            )
        }

    return {
        "input_allowed": True,
        "guardrail_reason": ""
    }


def route_after_input_guard(state: AgentState):

    if not state["input_allowed"]:
        return "blocked"

    return "continue"


# ==================================================
# REPOSITORY GUARDRAIL
# ==================================================

def repository_guard(state: AgentState):

    result = check_repository_content(
        state["context"]
    )

    if not result["allowed"]:

        return {
            "repository_allowed": False,
            "guardrail_reason": result["reason"]
        }

    return {
        "repository_allowed": True,
        "guardrail_reason": ""
    }


def route_after_repository_guard(state: AgentState):

    if not state["repository_allowed"]:
        return "blocked"

    return "continue"


# ==================================================
# OUTPUT GUARDRAIL
# ==================================================

def output_guard(state: AgentState):

    result = check_output(
        answer=state["answer"],
        context=state["context"],
    )

    if not result["allowed"]:

        return {
            "output_allowed": False,
            "guardrail_reason": result["reason"],
            "answer": (
                "Response blocked by "
                "output security guardrail."
            )
        }

    return {
        "output_allowed": True,
        "guardrail_reason": "",
        "answer": result["sanitized_answer"]
    }


def route_after_output_guard(state: AgentState):

    if not state["output_allowed"]:
        return "blocked"

    return "continue"


# ==================================================
# BUILD GRAPH
# ==================================================

builder = StateGraph(AgentState)


# ==================================================
# NODES
# ==================================================

builder.add_node(
    "input_guard",
    input_guard
)

builder.add_node(
    "retrieve_memory",
    retrieve_memory
)

builder.add_node(
    "retrieve",
    retrieve
)

builder.add_node(
    "repository_guard",
    repository_guard
)

builder.add_node(
    "generate",
    generate
)

builder.add_node(
    "output_guard",
    output_guard
)

builder.add_node(
    "save_memory",
    save_memory
)


# ==================================================
# EDGES
# ==================================================

builder.add_edge(
    START,
    "input_guard"
)

builder.add_conditional_edges(
    "input_guard",
    route_after_input_guard,
    {
        "continue": "retrieve_memory",
        "blocked": END,
    }
)

builder.add_edge(
    "retrieve_memory",
    "retrieve"
)

builder.add_edge(
    "retrieve",
    "repository_guard"
)

builder.add_conditional_edges(
    "repository_guard",
    route_after_repository_guard,
    {
        "continue": "generate",
        "blocked": END,
    }
)

builder.add_edge(
    "generate",
    "output_guard"
)

builder.add_conditional_edges(
    "output_guard",
    route_after_output_guard,
    {
        "continue": "save_memory",
        "blocked": END,
    }
)

builder.add_edge(
    "save_memory",
    END
)


# ==================================================
# SQLITE CHECKPOINT
# ==================================================

conn = sqlite3.connect(
    "checkpoints.sqlite",
    check_same_thread=False
)

memory = SqliteSaver(
    conn
)


# ==================================================
# COMPILE GRAPH
# ==================================================

graph = builder.compile(
    checkpointer=memory
)

