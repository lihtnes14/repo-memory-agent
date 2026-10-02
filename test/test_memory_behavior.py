import sqlite3
import uuid

from graph.workflow import graph
from backend.memory.database import initialize_database, get_connection, get_memories


# ============================================================
# TEST CONFIGURATION
# ============================================================

USER_ID = "behavior-test-user"
PROJECT_ID = "behavior-test-project"

THREAD_1 = f"memory-learning-{uuid.uuid4()}"
THREAD_2 = f"memory-recall-{uuid.uuid4()}"


# ============================================================
# CLEAN TEST DATA
# ============================================================

def clean_test_memories():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM memories
        WHERE user_id = ?
        AND project_id = ?
        """,
        (USER_ID, PROJECT_ID)
    )

    conn.commit()
    conn.close()


# ============================================================
# RUN GRAPH
# ============================================================

def run_agent(question: str, thread_id: str):

    state = {
        "question": question,
        "context": "",
        "memories": "",
        "answer": "",
        "user_id": USER_ID,
        "project_id": PROJECT_ID,

        "input_allowed": True,
        "repository_allowed": True,
        "output_allowed": True,

        "guardrail_reason": "",

        "conversation": [],
    }

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    return graph.invoke(
        state,
        config=config
    )


# ============================================================
# MAIN TEST
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("MEMORY BEHAVIOR TEST")
    print("=" * 70)

    initialize_database()
    clean_test_memories()

    # --------------------------------------------------------
    # STEP 1 — TEACH THE AGENT
    # --------------------------------------------------------

    print("\nSTEP 1 — TEACH AGENT")
    print("-" * 70)

    teaching_question = (
        "Remember that I prefer concise explanations "
        "with short code examples."
    )

    result_1 = run_agent(
        teaching_question,
        THREAD_1
    )

    print("\nUser:")
    print(teaching_question)

    print("\nAssistant:")
    print(result_1.get("answer", ""))

    # --------------------------------------------------------
    # VERIFY MEMORY WAS SAVED
    # --------------------------------------------------------

    memories = get_memories(
        user_id=USER_ID,
        project_id=PROJECT_ID
    )

    if not memories:

        print("\n❌ TEST FAILED")
        print("No persistent memory was created.")

        return

    print("\n✓ Persistent memory created")

    for memory in memories:

        print("\nMemory ID:", memory[0])
        print("Content:", memory[1])
        print("Type:", memory[2])
        print("Importance:", memory[3])

    # --------------------------------------------------------
    # STEP 2 — NEW CONVERSATION
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("STEP 2 — NEW CONVERSATION")
    print("=" * 70)

    question = "Explain recursion."

    result_2 = run_agent(
        question,
        THREAD_2
    )

    print("\nUser:")
    print(question)

    # --------------------------------------------------------
    # CHECK RETRIEVED MEMORY
    # --------------------------------------------------------

    retrieved_memories = result_2.get(
        "memories",
        ""
    )

    print("\nRetrieved persistent memory:")
    print(retrieved_memories)

    if "concise" not in retrieved_memories.lower():

        print("\n❌ TEST FAILED")
        print("Persistent memory was not retrieved.")

        return

    print("\n✓ Persistent memory retrieved")

    # --------------------------------------------------------
    # CHECK RESPONSE
    # --------------------------------------------------------

    answer = result_2.get(
        "answer",
        ""
    )

    print("\nAssistant:")
    print(answer)

    # --------------------------------------------------------
    # VERIFY MEMORY INFLUENCED RESPONSE
    # --------------------------------------------------------

    answer_lower = answer.lower()

    concise_indicators = [
        "concise",
        "brief",
        "short",
    ]

    code_indicators = [
        "```",
        "def ",
        "function",
    ]

    has_concise_signal = any(
        word in answer_lower
        for word in concise_indicators
    )

    has_code_signal = any(
        word in answer_lower
        for word in code_indicators
    )

    print("\n")
    print("=" * 70)
    print("MEMORY BEHAVIOR VERIFICATION")
    print("=" * 70)

    memory_text = retrieved_memories.lower()

    memory_retrieved = (
    "concise" in memory_text
    and "short code examples" in memory_text
)

    has_code_example = "```" in answer

    if memory_retrieved:
        print("✓ Persistent preference retrieved in new conversation")
    else:
        print("❌ Persistent preference was not retrieved")

    if has_code_example:
        print("✓ Response contains a code example")
    else:
        print("⚠ Response does not contain a code example")

    if memory_retrieved and has_code_example:
        print("\n")
        print("=" * 70)
        print("✓ MEMORY BEHAVIOR TEST PASSED")
        print("=" * 70)
    else:
        print("\n")
        print("=" * 70)
        print("❌ MEMORY BEHAVIOR TEST FAILED")
        print("=" * 70)

if __name__ == "__main__":
    main()