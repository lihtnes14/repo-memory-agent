from backend.agents.router_agent import route_question


questions = [
    "Where is PGVectorStore implemented?",
    "What coding preferences do I have?",
    "Explain the vector store implementation using my preferred explanation style.",
    "What is Python?",
]


for question in questions:

    route = route_question(question)

    print("=" * 60)
    print("Question:", question)
    print("Route:", route)