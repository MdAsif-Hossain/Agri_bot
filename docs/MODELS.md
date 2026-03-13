# Model Specifications

AgriBot operates 100% locally and requires consumer hardware (minimum 8GB VRAM/16GB system RAM recommended).

## Primary LLM

- **Required Format**: GGUF (via `llama-cpp-python`)
- **Default Parameter Recommendation**: LLaMA-3 8B Instruct (Q4_K_M)
- **Path config**: `AGRIBOT_MODEL_PATH=models/llama-3-8b-instruct.Q4_K_M.gguf`

## Embeddings / Bi-Encoder

- **Framework**: `sentence-transformers`
- **Default Strategy Model**: `paraphrase-multilingual-MiniLM-L12-v2` (Chosen for effective EN/BN cross-linguistic alignment with low latency)

## Cross-Encoder / Reranking

- **Framework**: `sentence-transformers`
- **Default Strategy Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2`

## Translation

- **Default Framework**: `transformers` pipeline
- **Default Strategy Model**: Contextual fine-tuned models like BanglaT5.
