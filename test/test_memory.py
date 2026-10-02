from backend.memory.database import (
    get_connection,
    initialize_database,
    add_memory,
    get_memories,
    update_memory,
)

from backend.memory.memory_manager import extract_memory


# ============================================================
# TEST CONFIGURATION
# ============================================================

USER_ID = "memory-test-user"
PROJECT_ID = "memory-lifecycle-test"


# ============================================================
# CLEAN TEST DATABASE
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
        (
            USER_ID,
            PROJECT_ID,
        )
    )

    conn.commit()
    conn.close()


# ============================================================
# PRINT DATABASE
# ============================================================

def print_memories():

    memories = get_memories(
        user_id=USER_ID,
        project_id=PROJECT_ID,
    )

    print("\n" + "=" * 70)
    print("CURRENT DATABASE")
    print("=" * 70)

    if not memories:
        print("No memories stored.")
        return

    for memory in memories:

        memory_id = memory[0]
        content = memory[1]
        memory_type = memory[2]
        importance = memory[3]

        print(f"\nMemory ID: {memory_id}")
        print(f"Type: {memory_type}")
        print(f"Importance: {importance}")
        print(f"Content: {content}")


# ============================================================
# APPLY MEMORY DECISION
# ============================================================

def apply_memory_decision(decision):

    if not decision:
        print("\nNo memory decision returned.")
        return

    action = decision["action"]

    # --------------------------------------------------------
    # NEW
    # --------------------------------------------------------

    if action == "new":

        memory_id = add_memory(
            user_id=USER_ID,
            project_id=PROJECT_ID,
            content=decision["content"],
            memory_type=decision["memory_type"],
            importance=decision["importance"],
        )

        print("\n✓ NEW MEMORY SAVED")
        print(f"Memory ID: {memory_id}")
        print(f"Content: {decision['content']}")

    # --------------------------------------------------------
    # DUPLICATE
    # --------------------------------------------------------

    elif action == "duplicate":

        print("\n✓ DUPLICATE DETECTED")
        print(f"Existing Memory ID: {decision['id']}")
        print("No new memory was created.")

    # --------------------------------------------------------
    # MERGE
    # --------------------------------------------------------

    elif action == "merge":

        update_memory(
            memory_id=decision["id"],
            content=decision["content"],
            importance=decision["importance"],
        )

        print("\n✓ MEMORY MERGED")
        print(f"Updated Memory ID: {decision['id']}")
        print(f"New Content: {decision['content']}")

    else:

        print("\n✗ UNKNOWN MEMORY ACTION")
        print(decision)


# ============================================================
# RUN MEMORY EXTRACTION
# ============================================================

def run_memory_test(label, conversation):

    print("\n" + "=" * 70)
    print(label)
    print("=" * 70)

    print("\nConversation:")
    print(conversation)

    decision = extract_memory(
        user_id=USER_ID,
        project_id=PROJECT_ID,
        conversation=conversation,
    )

    print("\nMemory Manager Decision:")

    if decision:
        print(f"Action: {decision['action']}")

        if decision.get("id"):
            print(f"Memory ID: {decision['id']}")

        if decision.get("content"):
            print(f"Content: {decision['content']}")

        if decision.get("importance") is not None:
            print(f"Importance: {decision.get('importance')}")

    else:
        print("No memory extracted.")

    apply_memory_decision(decision)

    print_memories()


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "#" * 70)
    print("# MEMORY LIFECYCLE TEST")
    print("# NEW → DUPLICATE → MERGE")
    print("#" * 70)

    # --------------------------------------------------------
    # DATABASE SETUP
    # --------------------------------------------------------

    initialize_database()
    clean_test_memories()

    print("\n✓ Test database initialized")
    print(f"User ID: {USER_ID}")
    print(f"Project ID: {PROJECT_ID}")

    # --------------------------------------------------------
    # TEST 1 — NEW
    # --------------------------------------------------------

    run_memory_test(
        "TEST 1 — NEW MEMORY",
        """
Remember that I prefer concise explanations.
""",
    )

    # --------------------------------------------------------
    # TEST 2 — DUPLICATE
    # --------------------------------------------------------

    run_memory_test(
        "TEST 2 — DUPLICATE MEMORY",
        """
Remember that I prefer concise explanations.
""",
    )

    # --------------------------------------------------------
    # TEST 3 — MERGE
    # --------------------------------------------------------

    run_memory_test(
        "TEST 3 — MERGE MEMORY",
        """
Remember that I prefer concise explanations with short code examples.
""",
    )

    # --------------------------------------------------------
    # FINAL DATABASE
    # --------------------------------------------------------

    print("\n" + "#" * 70)
    print("# FINAL MEMORY DATABASE")
    print("#" * 70)

    memories = get_memories(
        user_id=USER_ID,
        project_id=PROJECT_ID,
    )

    print(f"\nTotal memories: {len(memories)}")

    for memory in memories:

        print("\n----------------------------------------")
        print(f"ID: {memory[0]}")
        print(f"Content: {memory[1]}")
        print(f"Type: {memory[2]}")
        print(f"Importance: {memory[3]}")

    print("\n" + "#" * 70)
    print("# MEMORY TEST COMPLETE")
    print("#" * 70)