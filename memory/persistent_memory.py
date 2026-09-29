from memory.database import get_memories


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


    question_words = set(
        question.lower().split()
    )


    scored_memories = []


    for memory in memories:

        memory_id = memory[0]
        content = memory[1]
        memory_type = memory[2]
        importance = memory[3]

        memory_words = set(
            content.lower().split()
        )

        overlap = len(
            question_words.intersection(
                memory_words
            )
        )

        score = overlap + importance

        scored_memories.append(
            (
                score,
                memory_id,
                content,
                memory_type,
                importance,
            )
        )


    scored_memories.sort(
        reverse=True
    )


    return scored_memories[:max_memories]

