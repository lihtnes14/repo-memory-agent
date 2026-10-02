from backend.memory.database import get_memories
from backend.memory.vector_store import vector_store


def retrieve_memories(
    user_id: str,
    project_id: str,
    question: str,
    max_memories: int = 5
):
    memories = get_memories(
        user_id=user_id,
        project_id=project_id,
    )

    if not memories:
        return []

    # Create lookup from memory ID → database record
    memory_lookup = {
        int(memory[0]): memory
        for memory in memories
    }

    # Search only memories belonging to this user/project
    results = vector_store.similarity_search_with_score(
        question,
        k=max_memories,
        filter={
            "$and": [
                {"user_id": user_id},
                {"project_id": project_id},
            ]
        }
    )

    scored_memories = []

    for document, distance in results:

        memory_id = document.metadata.get("memory_id")

        if memory_id is None:
            continue

        memory_id = int(memory_id)

        if memory_id not in memory_lookup:
            continue

        memory = memory_lookup[memory_id]

        content = memory[1]
        memory_type = memory[2]
        importance = memory[3]

        # Chroma distance: lower is better.
        # Convert it into a similarity-like score.
        semantic_score = 1 / (1 + distance)

        final_score = (
            semantic_score * 0.8
            + importance * 0.2
        )

        scored_memories.append(
            (
                final_score,
                memory_id,
                content,
                memory_type,
                importance,
            )
        )

    scored_memories.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return scored_memories[:max_memories]