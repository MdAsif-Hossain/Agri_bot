# AgriBot Architecture

## Overview

AgriBot is designed as an agentic Retrieval-Augmented Generation (RAG) system with a strong focus on offline capability, robustness, and safe information delivery for agricultural contexts.

```mermaid
graph TD
  A[React UI] <-->|HTTP JSON/Multipart| B(FastAPI Backend)
  B --> C{LangGraph Agent}
  
  C --> D[Normalize & Translate]
  C --> E[Hybrid Retrieval]
  C --> F[Reranking]
  C --> G[Grade Evidence]
  C --> H[Generate Answer]
  C --> I[Verify & Enforce Policy]
  
  E --> J[(FAISS + BM25)]
  E --> K[(Knowledge Graph)]
  
  subplace H
    H --> L[Llama.cpp (Local LLM)]
  end
```

## Core Components

### 1. Agent Workflow (`agribot/agent/`)
Uses **LangGraph** to model the RAG pipeline as a state machine. This allows for conditional routing (e.g., query rewriting if evidence grading fails) and clear boundaries for instrumentation.

### 2. Retrieval Layer (`agribot/retrieval/`)
A **Hybrid Retriever** combining:
- Dense Vector Search (Sentence Transformers + FAISS)
- Sparse Keyword Search (BM25)
- Domain Knowledge Graph link expansion

Results are passed through a **Cross-Encoder Reranker** for semantic relevance filtration.

### 3. Generation Engine (`agribot/llm/`)
Provides a unified abstraction over local Llama models via `llama-cpp-python` with `outlines`-based JSON constrained decoding for evaluation and metadata extraction tasks.

### 4. Grounding & Safety (`agribot/agent/grounding_policy.py`)
Provides strict/lenient policy enforcement based on context verification. Risk-flagged queries (e.g., chemical dosages) trigger default refusals if the LLM output deviates from retrieved facts.
