
import json

from models.azure_client import generate_response

from memory.database import get_memories


# ==================================================
# MEMORY EXTRACTION
# ==================================================

def extract_memory(
    user_id: str,
    project_id: str,
    conversation: str,
):
    """
    Extract and optimize a persistent memory.

    IMPORTANT:
    This function does NOT modify the database.

    It only:
    1. Extracts a candidate memory.
    2. Retrieves existing memories.
    3. Determines NEW / DUPLICATE / MERGE.
    4. Returns the decision.

    Database writes are handled later by workflow.py
    after the memory security guardrail passes.
    """

    # ==================================================
    # STEP 1 — EXTRACT CANDIDATE MEMORY
    # ==================================================

    extraction_prompt = f"""
You are a memory extraction agent for a GitHub codebase assistant.

Your job is to identify information from the conversation
that is useful to remember across future conversations.

Only consider information such as:

- Persistent user preferences
- Important project decisions
- Architectural decisions
- Stable repository facts
- Recurring development preferences

Do NOT remember:

- Greetings
- Temporary questions
- One-time requests
- Secrets
- API keys
- Passwords
- Authentication tokens
- Access credentials
- Sensitive personal information
- Temporary debugging information
- Information that is obvious from the repository

Create a short, canonical memory.

Return ONLY valid JSON.

If something should be remembered:

{{
    "should_remember": true,
    "content": "short canonical memory",
    "memory_type": "fact",
    "importance": 0.8
}}

If nothing should be remembered:

{{
    "should_remember": false,
    "content": "",
    "memory_type": "",
    "importance": 0
}}

Conversation:
--------------------
{conversation}
--------------------
"""

    # ==================================================
    # CALL LLM
    # ==================================================

    try:
        response = generate_response(
            extraction_prompt
        )

        data = json.loads(response)

    except Exception:
        return None

    # ==================================================
    # CHECK WHETHER MEMORY SHOULD EXIST
    # ==================================================

    if not data.get("should_remember"):
        return None

    content = data.get(
        "content",
        ""
    ).strip()

    if not content:
        return None

    memory_type = data.get(
        "memory_type",
        "fact"
    )

    try:
        importance = float(
            data.get(
                "importance",
                0.5
            )
        )
    except (TypeError, ValueError):
        importance = 0.5

    # Keep importance within valid range
    importance = max(
        0.0,
        min(1.0, importance)
    )

    # ==================================================
    # STEP 2 — RETRIEVE EXISTING MEMORIES
    # ==================================================

    existing_memories = get_memories(
        user_id=user_id,
        project_id=project_id,
    )

    # ==================================================
    # NO EXISTING MEMORIES
    # ==================================================

    if not existing_memories:

        return {
            "action": "new",
            "id": None,
            "content": content,
            "memory_type": memory_type,
            "importance": importance,
        }

    # ==================================================
    # STEP 3 — PREPARE EXISTING MEMORIES
    # ==================================================

    existing_text = "\n".join(
        f"""
ID: {memory[0]}
Type: {memory[2]}
Importance: {memory[3]}
Content: {memory[1]}
"""
        for memory in existing_memories
    )

    # ==================================================
    # STEP 4 — MEMORY DEDUPLICATION / MERGING
    # ==================================================

    dedup_prompt = f"""
You are a memory optimization agent.

A new candidate memory has been extracted from a conversation.

Compare it with the existing persistent memories.

You must classify the candidate as exactly one of:

1. NEW

The candidate contains information that is not already
represented by an existing memory.

2. DUPLICATE

An existing memory already expresses essentially the same
information.

Do not create another memory.

3. MERGE

An existing memory contains related information, but the
candidate adds useful information.

Create ONE improved canonical memory that combines
the useful information.

Candidate memory:
--------------------
Content: {content}
Type: {memory_type}
Importance: {importance}

Existing memories:
--------------------
{existing_text}

Return ONLY valid JSON.

For NEW:

{{
    "action": "new",
    "memory_id": null,
    "content": "canonical memory",
    "importance": 0.8
}}

For DUPLICATE:

{{
    "action": "duplicate",
    "memory_id": 123,
    "content": "",
    "importance": 0
}}

For MERGE:

{{
    "action": "merge",
    "memory_id": 123,
    "content": "improved canonical memory",
    "importance": 0.9
}}
"""

    # ==================================================
    # CALL DEDUPLICATION LLM
    # ==================================================

    try:
        dedup_response = generate_response(
            dedup_prompt
        )

        decision = json.loads(
            dedup_response
        )

    except Exception:
        return None

    action = decision.get(
        "action"
    )

    # ==================================================
    # STEP 5 — DUPLICATE
    # ==================================================

    if action == "duplicate":

        memory_id = decision.get(
            "memory_id"
        )

        return {
            "action": "duplicate",
            "id": memory_id,
            "content": "",
        }

    # ==================================================
    # STEP 6 — NEW MEMORY
    # ==================================================

    if action == "new":

        new_content = decision.get(
            "content",
            content
        ).strip()

        if not new_content:
            return None

        try:
            new_importance = float(
                decision.get(
                    "importance",
                    importance
                )
            )
        except (TypeError, ValueError):
            new_importance = importance

        new_importance = max(
            0.0,
            min(1.0, new_importance)
        )

        return {
            "action": "new",
            "id": None,
            "content": new_content,
            "memory_type": memory_type,
            "importance": new_importance,
        }

    # ==================================================
    # STEP 7 — MERGE
    # ==================================================

    if action == "merge":

        memory_id = decision.get(
            "memory_id"
        )

        merged_content = decision.get(
            "content",
            ""
        ).strip()

        if not memory_id:
            return None

        if not merged_content:
            return None

        try:
            merged_importance = float(
                decision.get(
                    "importance",
                    importance
                )
            )
        except (TypeError, ValueError):
            merged_importance = importance

        merged_importance = max(
            0.0,
            min(1.0, merged_importance)
        )

        return {
            "action": "merge",
            "id": memory_id,
            "content": merged_content,
            "memory_type": memory_type,
            "importance": merged_importance,
        }

    # ==================================================
    # UNKNOWN ACTION
    # ==================================================

    return None

