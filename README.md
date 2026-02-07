<div style="text-align: center;">
  <img src="https://capsule-render.vercel.app/api?type=transparent&fontColor=0047AB&text=RektRAG&height=120&fontSize=90">
</div>
<p align="center">
  <a href="https://github.com/RektPunk/RektRAG/releases/latest">
    <img alt="release" src="https://img.shields.io/github/v/release/RektPunk/RektRAG.svg">
  </a>
  <a href="https://pypi.org/project/RektRAG">
    <img alt="Pythonv" src="https://img.shields.io/pypi/pyversions/RektRAG.svg?logo=python&logoColor=white">
  </a>
  <a href="https://github.com/RektPunk/RektRAG/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/RektPunk/RektRAG.svg">
  </a>
</p>


RektRAG introduces a lightweight, tree-based RAG designed for high-precision retrieval with minimal token overhead. RektRAG utilizes [Docling](https://github.com/docling-project/docling) for structured parsing and introduces the [TOON](https://github.com/toon-format/toon) format to optimize context window usage.

By decoupling the core logic from specific LLM providers, RektRAG allows integration with any model. It leverages asynchronous processing and hierarchical summarization to provide a "No-brainer" experience for complex document retrieval.

# Installation
Install using pip:
```bash
pip install rektrag
```

# Usage
- **RektEngine**: Orchestrates document ingestion, state management, and multi-document retrieval.
- **LLMProvider**: Easily plug in OpenAI, Anthropic, or local LLMs by implementing the interface.

# Example
Please refer to the [**Examples**](https://github.com/RektPunk/RektRAG/tree/main/examples) provided for further clarification.
