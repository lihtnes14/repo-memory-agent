from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

import os
from dotenv import load_dotenv


load_dotenv()


def get_retriever():

    embeddings = OpenAIEmbeddings(
        model=os.getenv("AZURE_EMBEDDING_DEPLOYMENT"),
        api_key=os.getenv("AZURE_EMBEDDING_API_KEY"),
        base_url=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
    )

    vector_store = Chroma(
        persist_directory="./chroma_db",
        collection_name="repository_code",
        embedding_function=embeddings,
    )

    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": 5
        }
    )

    return retriever