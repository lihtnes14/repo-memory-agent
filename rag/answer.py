from models.azure_client import generate_response


def generate_answer(question: str, context: str) -> str:

    prompt = f"""
You are a codebase analysis assistant.

Answer the user's question using ONLY the provided repository context.

If the answer cannot be determined from the context, say:
"I couldn't find enough information in the repository."

Always mention the relevant file paths when possible.

Repository context:
--------------------
{context}
--------------------

User question:
{question}

Answer:
"""

    return generate_response(prompt)