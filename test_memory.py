from memory.database import initialize_database
from memory.database import add_memory
from memory.persistent_memory import retrieve_memories


# ==================================================
# INITIALIZE
# ==================================================

initialize_database()


# ==================================================
# ADD TEST MEMORY
# ==================================================

add_memory(
    user_id="senthil",
    project_id="paperpilot",
    content="The project uses Azure OpenAI for LLM inference.",
    memory_type="architecture",
    importance=0.9,
)


add_memory(
    user_id="senthil",
    project_id="paperpilot",
    content="Tables are transformed into summaries before embedding.",
    memory_type="fact",
    importance=0.8,
)


# ==================================================
# RETRIEVE
# ==================================================

memories = retrieve_memories(
    user_id="senthil",
    project_id="paperpilot",
    question="How are tables processed?"
)


# ==================================================
# DISPLAY
# ==================================================

print("\n" + "=" * 70)
print("RETRIEVED MEMORIES")
print("=" * 70)


for memory in memories:

    score = memory[0]
    memory_id = memory[1]
    content = memory[2]
    memory_type = memory[3]
    importance = memory[4]

    print("\nMemory ID:", memory_id)
    print("Score:", score)
    print("Type:", memory_type)
    print("Importance:", importance)
    print("Content:", content)
