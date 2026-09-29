from ingestion.github_loader import load_github_repository
from rag.vector_store import create_vector_store


REPO_URL = "https://github.com/lihtnes14/paperpilot"


documents = load_github_repository(REPO_URL)

vector_store = create_vector_store(documents)

print("\nPhase 1 completed successfully!")