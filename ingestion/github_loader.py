import os
import shutil
import tempfile

from git import Repo
from langchain_core.documents import Document


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".go",
    ".rs",
    ".md",
    ".json",
    ".yaml",
    ".yml",
}


IGNORED_DIRS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
}


def load_github_repository(repo_url: str):
    temp_dir = tempfile.mkdtemp()

    try:
        print(f"Cloning repository: {repo_url}")

        Repo.clone_from(repo_url, temp_dir)

        documents = []

        for root, dirs, files in os.walk(temp_dir):

            # Don't enter ignored directories
            dirs[:] = [
                d for d in dirs
                if d not in IGNORED_DIRS
            ]

            for file in files:

                extension = os.path.splitext(file)[1].lower()

                if extension not in SUPPORTED_EXTENSIONS:
                    continue

                file_path = os.path.join(root, file)

                try:
                    with open(
                        file_path,
                        "r",
                        encoding="utf-8",
                        errors="ignore"
                    ) as f:
                        content = f.read()

                    relative_path = os.path.relpath(
                        file_path,
                        temp_dir
                    )

                    documents.append(
                        Document(
                            page_content=content,
                            metadata={
                                "source": relative_path,
                                "file_type": extension,
                            }
                        )
                    )

                except Exception as e:
                    print(
                        f"Skipping {file_path}: {e}"
                    )

        print(f"Loaded {len(documents)} files")

        return documents

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)