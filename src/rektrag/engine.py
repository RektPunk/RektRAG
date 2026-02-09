import asyncio
import hashlib
import json
import os

from toon_format import encode

from rektrag.logger import logger
from rektrag.models import LLMProvider
from rektrag.parser import build_map
from rektrag.schema import DocNode


async def summarize_node(
    node: DocNode, semaphore: asyncio.Semaphore, llm: LLMProvider
) -> None:
    if len(node.content) < 200:
        node.summary = node.content[:50] or node.title
        return

    async with semaphore:
        try:
            node.summary = await llm.summarise(
                text=f"Title: {node.title}\nContent: {node.content}",
            )
        except Exception as e:
            logger.error(f"Error summarizing {node.ref_id}: {e}")
            node.summary = node.title


async def run_summarization(
    node: DocNode, llm: LLMProvider, max_concurrency: int = 5
) -> None:
    semaphore = asyncio.Semaphore(max_concurrency)
    tasks = []

    def collect_tasks(node: DocNode):
        if node.content.strip():
            tasks.append(summarize_node(node=node, semaphore=semaphore, llm=llm))
        for child in node.children:
            collect_tasks(child)

    collect_tasks(node)
    if tasks:
        await asyncio.gather(*tasks)


class RektEngine:
    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self.documents: dict[str, str] = {}
        self.indexes: dict[str, dict[str, str | int]] = {}

    async def ingest(self, file_paths: str | list[str]) -> None:
        if isinstance(file_paths, str):
            file_paths = [file_paths]

        for file_path in file_paths:
            doc_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
            logger.info(f"Starting document conversion: {file_path}({doc_hash})")
            node = build_map(path=file_path, doc_hash=doc_hash)
            logger.info("Starting concurrent summarization...")
            await run_summarization(node=node, llm=self.llm)
            logger.info(f"Successfully built rekt_map for: {file_path}({doc_hash})")
            self.documents[doc_hash] = encode(node.get_slim_tree())
            self.indexes.update(node.get_index_map())

    def save_state(self, file_path: str = "rektrag_state.json") -> None:
        temp_file = f"{file_path}.tmp"
        try:
            state = {"documents": self.documents, "indexes": self.indexes}
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_file, file_path)
            logger.info(f"Successfully saved state to '{file_path}'")
        except Exception as e:
            logger.error(f"Failed to save state to '{file_path}': {str(e)}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise e

    def load_state(self, file_path: str = "rektrag_state.json") -> None:
        if not os.path.exists(file_path):
            msg = f"State file not found: '{file_path}'. Loading aborted."
            logger.error(msg)
            raise FileNotFoundError(msg)

        with open(file_path, "r", encoding="utf-8") as f:
            try:
                state = json.load(f)
                self.documents = state.get("documents", {})
                self.indexes = state.get("indexes", {})
                logger.info(
                    f"Successfully loaded state from '{file_path}' ({len(self.documents)} documents, {len(self.indexes)} indexes)"
                )
            except json.JSONDecodeError as e:
                msg = f"Invalid JSON format in '{file_path}': {str(e)}"
                logger.error(msg)
                raise e
            except Exception as e:
                msg = f"Unexpected error while loading state: {str(e)}"
                logger.error(msg)
                raise e

    async def retrieve(self, query: str) -> list[str]:
        if not self.documents:
            logger.info("No documents ingested yet.")
            return []

        toon_map = ""
        for doc_id, toon in self.documents.items():
            toon_map += f"\n=== DOCUMENT ID: {doc_id} ===\n{toon}"

        selected_ids = await self.llm.retrieve(toon_map=toon_map, query=query)
        results = []
        for ref_id in selected_ids:
            if ref_id in self.indexes:
                content = self.indexes[ref_id].get("content", "")
                if content:
                    results.append(content)
            else:
                logger.warning(f"Warning: ID {ref_id} not found in index.")

        return results
