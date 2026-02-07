import json
import re
from abc import ABC, abstractmethod

SUMMARIZE_PROMPT = """
Act as a document indexer. Provide a 1-2 sentence summary of the text below, optimized for search.
You MUST include key technical terms, proper nouns, and numerical data. Return ONLY the summary text.
"""

RETRIEVER_PROMPT = """
Act as a precise document navigator. Your task is to identify the most relevant sections of a document to answer a user's question.

You will be provided with a Document Map in TOON format: (ref_id|title|summary).

Guidelines:
1. Analyze the user's query and find the sections that contain the direct answer or essential context.
2. Consider the hierarchy: if a parent section's summary is highly relevant, explore its children.
3. Return ONLY a JSON object with a list of 'ref_ids'.
4. Do not explain your reasoning.
4. Identify all relevant sections across any documents to answer the query.
5. Return ONLY a JSON object: {"ref_ids": ["ref_id1/ref_id_a", "ref_id2/ref_id_b"]}

Output Format:
{"ref_ids": ["ref_id1/5", "ref_id1/7"]}
"""


class LLMProvider(ABC):
    def __init__(
        self,
        summarise_prompt: str | None = None,
        retriever_prompt: str | None = None,
    ):
        self.summarise_prompt = summarise_prompt or SUMMARIZE_PROMPT
        self.retriever_prompt = retriever_prompt or RETRIEVER_PROMPT

    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        pass

    async def summarise(self, text: str) -> str:
        return await self.complete(self.summarise_prompt, text)

    async def retrieve(self, query: str, toon_map: str) -> list[str]:
        user_input = f"MAP:\n{toon_map}\n\nQUERY: {query}"
        raw = await self.complete(self.retriever_prompt, user_input)
        return self._extract_json_list(raw)

    def _extract_json_list(self, text: str) -> list[str]:
        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group()).get("ref_ids", [])
            return []
        except (json.JSONDecodeError, AttributeError):
            return []
