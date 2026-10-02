from backend.ingestion.github_loader import load_github_repository
from backend.rag.vector_store import create_vector_store


def ingest_repository(
    repo_url: str,
    project_id: str,
):
    print("=" * 70)
    print("REPOSITORY INGESTION")
    print("=" * 70)

    print(f"Repository: {repo_url}")
    print(f"Project ID: {project_id}")

    documents = load_github_repository(
        repo_url=repo_url,
        project_id=project_id,
    )

    if not documents:
        raise ValueError(
            "No supported files were found in the repository."
        )

    vector_store = create_vector_store(
        documents=documents,
        project_id=project_id,
    )

    print("=" * 70)
    print("REPOSITORY INGESTION COMPLETE")
    print("=" * 70)

    return vector_store