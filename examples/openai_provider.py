import asyncio

from openai import AsyncOpenAI

from rektrag import LLMProvider, RektEngine


class OpenAIProvider(LLMProvider):
    """
    Concrete implementation of LLMProvider using OpenAI's API.
    Decouples the core engine from the specific LLM client.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__()
        self.client = AsyncOpenAI()
        self.model = model

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        """
        Sends a request to OpenAI's ChatCompletion API.
        This is the bridge between rektrag's logic and the actual LLM.
        """
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )
        return resp.choices[0].message.content.strip()


async def main():
    # 1. Initialize the Provider and the Orchestration Engine
    llm = OpenAIProvider()
    engine = RektEngine(llm)

    # 2. Define source documents (URLs or local file paths)
    test_files = [
        "https://arxiv.org/pdf/2408.09869",
        "https://arxiv.org/pdf/2005.11401",
    ]

    # 3. Ingest documents: This performs Parsing -> Tree Building -> Summarization
    await engine.ingest(test_files)

    # 4. State Management: Save the processed TOON maps and indexes to disk
    ## This allows skipping the expensive ingestion process in the future
    engine.save_state()

    ## Reload the state to demonstrate persistence capability
    engine.load_state()

    # 5. Retrieval Test: Query across all ingested documents
    queries = [
        "What are the core technologies supported by Docling?",
        "What are the two main components of a RAG model?",
    ]

    for q in queries:
        print(f"\nQuery: {q}")
        contents = await engine.retrieve(q)
        if contents:
            print(f"Retrieval Success ({len(contents)} sections found):")
            for i, text in enumerate(contents):
                print(f"  [{i + 1}] {text[:150].replace('\n', ' ')}...")
        else:
            print("No relevant content found.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
