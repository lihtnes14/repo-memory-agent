from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

import os
from dotenv import load_dotenv


load_dotenv()


# --------------------------------------------------
# 1. Connect to Azure Embeddings
# --------------------------------------------------

embeddings = OpenAIEmbeddings(
    model=os.getenv("AZURE_EMBEDDING_DEPLOYMENT"),
    api_key=os.getenv("AZURE_EMBEDDING_API_KEY"),
    base_url=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
)


# --------------------------------------------------
# 2. Load existing ChromaDB
# --------------------------------------------------

vector_store = Chroma(
    persist_directory="./chroma_db",
    collection_name="repository_code",
    embedding_function=embeddings,
)


# --------------------------------------------------
# 3. Ask a question
# --------------------------------------------------

query = "Where is authentication implemented?"


# --------------------------------------------------
# 4. Retrieve relevant code
# --------------------------------------------------

results = vector_store.similarity_search(
    query,
    k=5,
)


# --------------------------------------------------
# 5. Display results
# --------------------------------------------------

for i, doc in enumerate(results):

    print("\n" + "=" * 60)
    print(f"RESULT {i + 1}")
    print("=" * 60)

    print("FILE:", doc.metadata.get("source"))
    print("TYPE:", doc.metadata.get("file_type"))

    print("\nCODE:")
    print(doc.page_content[:1000])