import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

load_dotenv()


PERSIST_DIRECTORY = "memory_chroma"


embeddings = OpenAIEmbeddings(
    model=os.getenv("AZURE_EMBEDDING_DEPLOYMENT"),
    base_url=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
    api_key=os.getenv("AZURE_EMBEDDING_API_KEY"),
)


vector_store = Chroma(
    collection_name="persistent_memories",
    embedding_function=embeddings,
    persist_directory=PERSIST_DIRECTORY,
)


def index_memory(
    memory_id: int,
    content: str,
    user_id: str,
    project_id: str,
):
    vector_store.add_texts(
        texts=[content],
        metadatas=[
            {
                "memory_id": memory_id,
                "user_id": user_id,
                "project_id": project_id,
            }
        ],
        ids=[f"memory-{memory_id}"],
    )


def update_memory_vector(
    memory_id: int,
    content: str,
    user_id: str,
    project_id: str,
):
    vector_store.update_documents(
        ids=[f"memory-{memory_id}"],
        documents=[
            Document(
                page_content=content,
                metadata={
                    "memory_id": memory_id,
                    "user_id": user_id,
                    "project_id": project_id,
                },
            )
        ],
    )

def delete_memory_vector(memory_id: int):
    vector_store.delete(
        ids=[f"memory-{memory_id}"]
    )