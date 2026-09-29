import json

from models.azure_client import generate_response


def check_memory(
    content: str,
    memory_type: str,
    importance: float
):
    """
    Validate a candidate memory before it is stored permanently.
    """

    prompt = f"""
You are a memory security guardrail for a GitHub codebase assistant.

Decide whether the candidate memory is safe and useful to store
as persistent memory.

ALLOW memories that contain:

- Stable repository facts
- Important architecture decisions
- Persistent project decisions
- Useful development preferences
- Information that can improve future conversations

BLOCK memories that contain:

- API keys
- Passwords
- Authentication tokens
- Access credentials
- Secrets
- Sensitive personal information
- Temporary information
- One-time requests
- Greetings or casual conversation
- Irrelevant information
- Information that should not be stored permanently

Return ONLY valid JSON.

For a safe memory:

{{
    "allowed": true,
    "reason": "Stable project information",
    "sanitized_content": "original or safely rewritten memory"
}}

For an unsafe memory:

{{
    "allowed": false,
    "reason": "Contains sensitive information",
    "sanitized_content": ""
}}

Candidate memory:
--------------------
Content: {content}
Memory type: {memory_type}
Importance: {importance}
--------------------
"""

    try:
        response = generate_response(prompt)

    except Exception:
        return {
            "allowed": False,
            "reason": "Memory guardrail classification failed",
            "sanitized_content": ""
        }

    try:
        result = json.loads(response)

    except json.JSONDecodeError:
        return {
            "allowed": False,
            "reason": "Invalid guardrail response",
            "sanitized_content": ""
        }

    return {
        "allowed": bool(
            result.get("allowed", False)
        ),
        "reason": result.get(
            "reason",
            "No reason provided"
        ),
        "sanitized_content": result.get(
            "sanitized_content",
            ""
        )
    }