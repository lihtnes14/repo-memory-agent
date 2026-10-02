import sqlite3

from backend.memory.database import (
    initialize_database,
    add_memory,
    get_memories,
    update_memory,
)

from backend.memory.vector_store import (
    index_memory,
    update_memory_vector,
)

from backend.memory.persistent_memory import retrieve_memories


USER_ID = "sync-test-user"
PROJECT_ID = "sync-test-project"


def clean_database():

    conn = sqlite3.connect("memory.sqlite")

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


def test_memory_sync():

    initialize_database()
    clean_database()

    print("\n")
    print("=" * 70)
    print("MEMORY SQLITE ↔ CHROMA SYNCHRONIZATION TEST")
    print("=" * 70)

    # --------------------------------------------------
    # STEP 1 — NEW
    # --------------------------------------------------

    print("\n")
    print("=" * 70)
    print("STEP 1 — CREATE MEMORY")
    print("=" * 70)

    content = "User prefers concise explanations."

    memory_id = add_memory(
        user_id=USER_ID,
        project_id=PROJECT_ID,
        content=content,
        memory_type="preference",
        importance=0.9,
    )

    index_memory(
        memory_id=memory_id,
        content=content,
        user_id=USER_ID,
        project_id=PROJECT_ID,
    )

    print(f"SQLite Memory ID: {memory_id}")
    print(f"Content: {content}")

    results = retrieve_memories(
        user_id=USER_ID,
        project_id=PROJECT_ID,
        question="How should explanations be written?",
        max_memories=1,
    )

    print("\nChroma Retrieval:")

    if results:
        print(results[0][2])
        print("✓ NEW MEMORY SYNCHRONIZED")

    else:
        print("✗ MEMORY NOT FOUND")


    # --------------------------------------------------
    # STEP 2 — MERGE / UPDATE
    # --------------------------------------------------

    print("\n")
    print("=" * 70)
    print("STEP 2 — MERGE MEMORY")
    print("=" * 70)

    updated_content = (
        "User prefers concise explanations "
        "with short code examples."
    )

    update_memory(
        memory_id=memory_id,
        content=updated_content,
        importance=0.95,
    )

    update_memory_vector(
        memory_id=memory_id,
        content=updated_content,
        user_id=USER_ID,
        project_id=PROJECT_ID,
    )

    print(f"Updated SQLite Memory ID: {memory_id}")
    print(f"New Content: {updated_content}")

    # --------------------------------------------------
    # STEP 3 — RETRIEVE UPDATED MEMORY
    # --------------------------------------------------

    print("\n")
    print("=" * 70)
    print("STEP 3 — RETRIEVE AFTER MERGE")
    print("=" * 70)

    results = retrieve_memories(
        user_id=USER_ID,
        project_id=PROJECT_ID,
        question="How should I explain Python concepts?",
        max_memories=1,
    )

    if not results:

        print("✗ NO MEMORY RETRIEVED")
        return

    retrieved_content = results[0][2]

    print("\nRetrieved Memory:")
    print(retrieved_content)

    if retrieved_content == updated_content:

        print("\n✓ SQLITE AND CHROMA ARE SYNCHRONIZED")

    else:

        print("\n✗ STALE VECTOR DETECTED")
        print(f"Expected: {updated_content}")
        print(f"Retrieved: {retrieved_content}")


if __name__ == "__main__":

    test_memory_sync()