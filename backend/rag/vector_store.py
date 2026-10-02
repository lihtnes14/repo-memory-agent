import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()


def create_vector_store(documents, project_id: str):

    # --------------------------------------------------
    # 1. Split repository files into chunks
    # --------------------------------------------------

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
    )

    chunks = splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks")
    print(f"Project ID: {project_id}")


    # --------------------------------------------------
    # 2. Azure AI Foundry Embeddings
    # --------------------------------------------------

    embeddings = OpenAIEmbeddings(
        model=os.getenv("AZURE_EMBEDDING_DEPLOYMENT"),
        api_key=os.getenv("AZURE_EMBEDDING_API_KEY"),
        base_url=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
    )


    # --------------------------------------------------
    # 3. Store embeddings in ChromaDB
    # --------------------------------------------------

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db",
        collection_name="repository_code",
    )

    print("ChromaDB created successfully")

    return vector_store