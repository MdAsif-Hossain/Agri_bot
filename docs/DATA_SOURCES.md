# Customizing Data Sources

AgriBot allows complete customization of the offline internal corpus.

## Ingestion Pipeline

1. **Place raw text documents** in `data/raw_manuals/`.
2. **Execute build script**: `make ingest`.
3. The system parses, splits via character bounds, generates embeddings, pushes to FAISS/BM25, and issues an offline `manifest.json`.

*Note: Ensure `MODEL_PATH` and `EMBEDDING_MODEL` configurations are set appropriately before running ingestion to guarantee vector alignment during runtime.*

## Adding Knowledge Graph Relations

The localized Knowledge Graph helps bridge the mapping between Bangla vernacular/dialect terms and formal English agricultural ontology.

Modifications to baseline seeds can be managed within `agribot/knowledge_graph/seed_data.py` or imported dynamically via external RDF/Turtle definitions.
