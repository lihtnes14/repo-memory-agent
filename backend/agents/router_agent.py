import json

from backend.models.azure_client import client, MODEL


ROUTER_PROMPT = """
You are a routing agent for a repository-aware coding assistant.

Your job is to decide what information is required to answer the user's question.

Available information sources:

1. repository
   Use when the question requires information from the GitHub repository,
   such as source code, architecture, files, classes, functions, dependencies,
   implementation details, or repository-specific behavior.

2. memory
   Use when the question requires persistent information about the user's
   preferences, previous decisions, project context, or previously remembered facts.

3. both
   Use when answering the question requires both repository information and
   persistent user/project memory.

4. direct
   Use when the question can be answered without repository information
   and without persistent memory.

Return ONLY valid JSON.

Format:

{{
    "route": "repository"
}}

or

{{
    "route": "memory"
}}

or

{{
    "route": "both"
}}

or

{{
    "route": "direct"
}}

User question:

{question}
"""


VALID_ROUTES = {
    "repository",
    "memory",
    "both",
    "direct",
}


def route_question(question: str) -> str:

    prompt = ROUTER_PROMPT.format(
        question=question
    )

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )

    raw_output = response.output_text.strip()

    try:
        result = json.loads(raw_output)

        route = result.get("route")

        if route not in VALID_ROUTES:
            return "direct"

        return route

    except (json.JSONDecodeError, AttributeError, TypeError):
        return "direct"