from backend.memory.database import initialize_database, add_memory
from backend.memory.persistent_memory import retrieve_memories
from backend.memory.vector_store import index_memory


USER_ID = "eval-user"
PROJECT_ID = "eval-project"


def setup_memories():

    initialize_database()

    memories = [
        (
            "User prefers concise explanations with short code examples.",
            "preference",
            0.9
        ),
        (
            "The project backend is implemented using Python.",
            "project_fact",
            0.8
        ),
        (
            "The application uses ChromaDB for vector storage.",
            "architecture",
            0.85
        ),
        (
            "The user prefers LangGraph for agent orchestration.",
            "preference",
            0.8
        ),
        (
            "The project uses Azure OpenAI for LLM inference.",
            "architecture",
            0.85
        ),
    ]

    # Clean previous evaluation data
    import sqlite3

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

    # Add memories to SQLite and Chroma
    for content, memory_type, importance in memories:

        memory_id = add_memory(
            user_id=USER_ID,
            project_id=PROJECT_ID,
            content=content,
            memory_type=memory_type,
            importance=importance
        )

        index_memory(
            memory_id=memory_id,
            content=content,
            user_id=USER_ID,
            project_id=PROJECT_ID,
        )


def run_evaluation():

    test_cases = [

        {
            "question": "How should I explain a Python concept to the user?",
            "expected": 0
        },

        {
            "question": "What programming language does the backend use?",
            "expected": 1
        },

        {
            "question": "Which database stores the vector embeddings?",
            "expected": 2
        },

        {
            "question": "What framework should be used to orchestrate the agents?",
            "expected": 3
        },

        {
            "question": "Which model provider is used for inference?",
            "expected": 4
        },
    ]

    correct = 0

    print("\n")
    print("=" * 70)
    print("MEMORY RETRIEVAL EVALUATION")
    print("=" * 70)

    for i, test in enumerate(test_cases, start=1):

        question = test["question"]
        expected_index = test["expected"]

        results = retrieve_memories(
            user_id=USER_ID,
            project_id=PROJECT_ID,
            question=question,
            max_memories=1
        )

        print("\n" + "-" * 70)
        print(f"TEST {i}")
        print("-" * 70)

        print("Question:")
        print(question)

        if not results:

            print("\nRetrieved: NONE")
            continue

        score, memory_id, content, memory_type, importance = results[0]

        print("\nRetrieved Memory:")
        print(content)

        print(f"Score: {score}")
        print(f"Memory ID: {memory_id}")

        expected_memory = [
            "User prefers concise explanations with short code examples.",
            "The project backend is implemented using Python.",
            "The application uses ChromaDB for vector storage.",
            "The user prefers LangGraph for agent orchestration.",
            "The project uses Azure OpenAI for LLM inference.",
        ][expected_index]

        if content == expected_memory:

            print("✓ CORRECT")
            correct += 1

        else:

            print("✗ INCORRECT")
            print(f"Expected: {expected_memory}")

    total = len(test_cases)

    accuracy = correct / total

    print("\n")
    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    print(f"Correct: {correct}/{total}")
    print(f"Accuracy: {accuracy:.2%}")

    print("=" * 70)


if __name__ == "__main__":

    setup_memories()
    run_evaluation()