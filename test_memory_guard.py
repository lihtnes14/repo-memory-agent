from guardrails.memory_guard import check_memory


memories = [
    {
        "content": "The project uses Azure OpenAI for LLM inference.",
        "memory_type": "architecture",
        "importance": 0.9,
    },
    {
        "content": "The user prefers Python for backend development.",
        "memory_type": "preference",
        "importance": 0.8,
    },
    {
        "content": "The API key is sk-123456789.",
        "memory_type": "secret",
        "importance": 1.0,
    },
    {
        "content": "The user asked how tables are extracted from PDFs.",
        "memory_type": "temporary",
        "importance": 0.3,
    },
    {
        "content": "Hello, how are you?",
        "memory_type": "conversation",
        "importance": 0.1,
    },
]


for memory in memories:

    result = check_memory(
        content=memory["content"],
        memory_type=memory["memory_type"],
        importance=memory["importance"],
    )

    print("\n" + "=" * 70)
    print("MEMORY")
    print(memory["content"])

    print("\nRESULT")
    print(result)