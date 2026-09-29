from rag.retriever import get_retriever
from rag.answer import generate_answer


question = "How are images and tables extracted from PDF documents?"


# Retrieve relevant repository code
retriever = get_retriever()

documents = retriever.invoke(question)


# Build context for GPT
context = "\n\n".join(
    f"FILE: {doc.metadata.get('source')}\n"
    f"{doc.page_content}"
    for doc in documents
)


# Generate grounded answer
answer = generate_answer(
    question,
    context
)


print("\n" + "=" * 60)
print("QUESTION")
print("=" * 60)
print(question)

print("\n" + "=" * 60)
print("ANSWER")
print("=" * 60)
print(answer)