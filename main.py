from backend.ingestion.github_loader import load_github_repository
from backend.rag.vector_store import create_vector_store


REPO_URL = "https://github.com/lihtnes14/paperpilot"
PROJECT_ID = "paperpilot"


documents = load_github_repository(
    repo_url=REPO_URL,
    project_id=PROJECT_ID,
)

vector_store = create_vector_store(
    documents=documents,
    project_id=PROJECT_ID,
)

print("\nPhase 1 completed successfully!")