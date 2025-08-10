import os
import shutil
import tempfile
import subprocess
import asyncio
from typing import Any, Dict, List
from datetime import datetime, timezone
import time

from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from logger import backend_logger
from utils.weaviate_manager import WeaviateManager


class GithubManager:
    def __init__(
        self,
        mongo_db,
        mongo_collection: str = "repos"
    ):
        self.vector_store_manager = WeaviateManager()
        self.mongo = mongo_db[mongo_collection]

    def _get_branches(self, repo_url: str) -> List[str]:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", repo_url],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.strip().split("\n")
        return [line.split("refs/heads/")[1] for line in lines if "refs/heads/" in line]
    
    def _get_default_branch(self, repo_url: str) -> str:
        result = subprocess.run(
            ["git", "ls-remote", "--symref", repo_url, "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.strip().split("\n"):
            if line.startswith("ref:"):
                return line.split("refs/heads/")[1].strip()
        raise RuntimeError("Could not determine default branch.")


    def _clone_repo(self, repo_url: str, branch: str, dest: str):
        subprocess.run(
            ["git", "clone", "--branch", branch, "--single-branch", repo_url, dest],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        shutil.rmtree(os.path.join(dest, ".git"), ignore_errors=True)

    def _load_documents(self, repo_path: str):
        unstructured_loader = DirectoryLoader(
            path=repo_path,
            exclude=["**/*.pptx", "**/*.docx", "**/*.doc", "**/*.pdf", "**/*.png", "**/*.jpg", "**/*.jpeg"],
            glob=["**/*.md", "**/*.rst"],
            silent_errors=True,
            show_progress=True,
            use_multithreading=True,
            recursive=True,
        )
        text_loader = DirectoryLoader(
            path=repo_path,
            exclude=["**/*.md", "**/*.rst", "**/*.pptx", "**/*.doc", "**/*.docx", "**/*.pdf", "**/*.png", "**/*.jpg", "**/*.jpeg"],
            glob=["**/*.*"],
            silent_errors=True,
            show_progress=True,
            use_multithreading=True,
            recursive=True,
        )
        return unstructured_loader.load() + text_loader.load()

    def _chunk_documents(self, docs):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, add_start_index=True
        )
        return splitter.split_documents(docs)

    async def _process_branch(self, repo_url: str, owner: str, repo_name: str, branch: str, embeddings: Any) -> Dict:
        vs_collection_name = f"{owner}_{repo_name}_{branch}".replace("-", "_").lower()
        temp_dir = tempfile.mkdtemp()

        try:
            backend_logger.info(f"Cloning {repo_url} [branch: {branch}]...")
            await asyncio.to_thread(self._clone_repo, repo_url, branch, temp_dir)

            backend_logger.info(f"Loading documents from branch '{branch}'...")
            docs = await asyncio.to_thread(self._load_documents, temp_dir)
            splits = self._chunk_documents(docs)

            backend_logger.info(f"Initializing collection: {vs_collection_name}")
            await self.vector_store_manager.initialize_collection(vs_collection_name)

            backend_logger.info("Pushing to vector store...")
            vs = await self.vector_store_manager.get_vector_store(vs_collection_name, embeddings)
            await asyncio.to_thread(vs.add_documents, splits)

            return {
                "branch": branch,
                "vs_collection": vs_collection_name,
                "chunks": len(splits)
            }

        except Exception as e:
            backend_logger.error(f"[{branch}] Failed: {e}")
            return {
                "branch": branch,
                "vs_collection": None,
                "chunks": 0,
                "error": str(e)
            }

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    async def ingest_repo(self, repo_url: str, embeddings: Any) -> dict:
        repo_name = repo_url.rstrip("/").split("/")[-1].lower()
        owner = repo_url.rstrip("/").split("/")[-2].lower()
        branches = self._get_branches(repo_url)

        backend_logger.info(f"Found branches for {repo_url}: {branches}")

        if len(branches) > 10:
            default_branch = self._get_default_branch(repo_url)
            backend_logger.info(f"More than 10 branches detected. Only processing default branch: {default_branch}")
            branches = [default_branch]

        tasks = [
            self._process_branch(repo_url, owner, repo_name, branch, embeddings)
            for branch in branches
        ]
        results = await asyncio.gather(*tasks)

        successful_branches = [r for r in results if r.get("vs_collection")]
        failed_branches = [r for r in results if not r.get("vs_collection")]

        if not successful_branches:
            backend_logger.error("All branches failed to process. Aborting MongoDB insert.")
            raise RuntimeError("Failed to ingest any branches from the repository.")

        repo_meta = {
            "repo_url": repo_url,
            "repo_name": repo_name,
            "owner": owner,
            "branches": results,
            "created_at": int(time.time()),
        }

        backend_logger.info("Saving metadata to MongoDB...")
        self.mongo.insert_one(repo_meta)
        return repo_meta

