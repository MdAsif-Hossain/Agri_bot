# AgriBot: A Production-Grade Offline Multimodal Agentic RAG System with Dialect Knowledge Graph for Bilingual (Bengali–English) Agricultural Decision Support

<p align="center">
  <img src="./frontend/public/logo.png" alt="AgriBot Logo" width="150"/>
</p>

## 1. Executive Summary
Farmers and extension officers in rural Bangladesh often lack timely access to reliable, evidence-based agricultural guidance due to unstable internet connectivity, limited expert availability, and a language gap between scientific manuals and colloquial/dialectal Bengali. Meanwhile, crucial knowledge exists in trusted resources (e.g., FAO/IRRI manuals and local extension documents), but these are typically PDF-heavy, difficult to search, and frequently contain complex layouts: tables, figures, scanned pages, and images carrying essential instructions.

This project proposes **AgriBot**, a **production-grade, offline-first** decision-support system that accepts **multimodal inputs**—**voice, text, and images**—and produces **bilingual outputs (Bengali + English)** with **traceable citations** (source + page). AgriBot uses **Retrieval-Augmented Generation (RAG)**, strengthened by three mandatory reliability pillars:

1. **Multimodal Document Understanding for PDFs**  
   Instead of brittle hand-written heuristics, AgriBot uses **Marker** (a layout-aware document extraction tool) to recover reading order, headings, tables, and figure structure. A lightweight post-processing layer removes repeated headers/footers, downweights TOC/index/reference sections, and produces high-quality, provenance-rich chunks.

2. **Dialect Knowledge Graph (KG) beyond a Lexicon**  
   AgriBot maintains a versioned, offline **knowledge graph** (stored in **SQLite graph tables** for portability) mapping dialect terms to canonical Bengali/English/scientific entities, and representing relations such as symptom→disease and disease→treatment. The KG is used for entity linking, query expansion, and disambiguation.

3. **Agentic Self-Correction using LangGraph**  
   AgriBot implements a bounded self-correct loop: **Retrieve → Grade → Rewrite/Expand → Retrieve → Generate → Verify**, ensuring that weak evidence triggers retrieval retry and that unsafe or ungrounded outputs are refused or converted into follow-up questions.

AgriBot is designed for real deployment: a laptop/desktop (consumer GPU e.g., RTX 3050 4GB) runs the offline models and indexes in “kiosk mode,” while a **mobile thin client** connects over local Wi‑Fi/LAN—delivering usability without forcing on-device LLM inference.

---

## 2. Problem Statement
AgriBot targets the following field-real constraints:

1. **Connectivity constraint:** Cloud AI is unreliable in rural environments; the system must function offline.
2. **Language + dialect constraint:** Farmers use colloquial/dialect Bengali; manuals use scientific terminology. Direct translation is insufficient.
3. **Visual-first diagnosis:** Crop issues are often best expressed via images (lesions, pest damage) and voice descriptions.
4. **PDF complexity and noise:** Manuals contain indexes/TOCs/references, repeated headers/footers, tables, diagrams, and scanned content.
5. **Safety and trust:** Agricultural recommendations can be harmful if incorrect; outputs must be evidence-based, cited, and conservative under uncertainty.
6. **Edge hardware constraint:** Deployment must be feasible on consumer hardware used by NGOs/local offices.

---

## 3. Goals and Success Criteria
### 3.1 Primary Goals (Must Deliver)
1. **Offline-first operation** after initial setup (models/indexes local).
2. **Multimodal input support**:
   - Voice (Bengali) via offline ASR (`faster-whisper`),
   - Text (BN/EN),
   - Image (farmer crop photo).
3. **Bilingual outputs (BN + EN)** with aligned terms.
4. **Multimodal PDF ingestion**:
   - robust extraction of text, tables, and figures natively with Marker,
   - OCR for scanned content,
   - filtering/downweighting of irrelevant PDF sections.
5. **Hybrid retrieval** (BM25 + FAISS dense vectors) with Cross-Encoder reranking.
6. **Dialect Knowledge Graph** for entity linking and query expansion.
7. **LangGraph agentic self-correction loop** (bounded retries) + verification.
8. **Citations + evidence panel**: every answer includes source/page references.
9. **Voice output (offline TTS)** in Bengali.
10. **Production readiness**:
    - stable API contracts,
    - logging and metrics,
    - automated tests,
    - reproducible build artifacts.
11. **Deployment**:
    - React kiosk web UI for desktop/laptop,
    - mobile thin client app over LAN/Wi‑Fi,
    - exportable case reports.

### 3.2 Success Criteria (Measurable)
- **Groundedness:** ≥X% responses contain valid citations supporting key claims.
- **Refusal correctness:** system refuses when evidence is insufficient rather than hallucinating.
- **Retrieval quality:** improved Recall@k/MRR with KG expansion vs without.
- **Edge feasibility:** stable operation within consumer hardware limits; bounded latency per query.
- **Usability:** a non-technical user can run it via documented setup and UI.

---

## 4. Target Users and Use Cases
### 4.1 Users
- **Extension officers / NGO field staff** (primary operators)
- **Farmers** (via assisted kiosk or mobile client interaction)

### 4.2 Typical Scenarios
1. **Voice-based query:** A farmer speaks Bengali symptoms; the system asks follow-up questions; returns cited recommendations and speaks Bengali output.
2. **Image-based query:** A farmer uploads a leaf image; the VLM extracts symptoms and retrieves relevant evidence from manuals.
3. **Dosage query:** User asks dosage; the system only provides dosage if found and cited; otherwise refuses and references manual sections.

---

## 5. System Overview
AgriBot combines:
- **Offline ASR/TTS** (faster-whisper) for voice interaction,
- **Multimodal PDF understanding** (Marker + OCR + post-processing),
- **Hybrid retrieval** (FAISS dense + BM25 sparse + ms-marco reranker),
- **Dialect Knowledge Graph** (SQLite/NetworkX graph) for term alignment,
- **LangGraph bounded self-correct loop** with evidence grading and verification,
- **Offline local LLM** (Qwen 2.5 1.5B) running quantized on consumer GPU/CPU via `llama-cpp-python`,
- **Kiosk React web UI + mobile thin client**.

---

## 6. Architecture (Production View)
### 6.1 Core Modules / Services
1. **Ingestion Pipeline** (`/agribot/ingestion`): Curates PDF sets into a chunk store, FAISS/BM25 indexes, and Knowledge Graph snapshots (versioned).
2. **Orchestrator API** (`api.py`): FastAPI exposing `/v1/chat` endpoint executing the full LangGraph workflow.
3. **Retrieval Service** (`/agribot/retrieval`): Hybrid retrieval and reranking; returns structured evidence.
4. **Knowledge Graph Service** (`/agribot/knowledge`): Entity linking, alias expansion, and neighborhood query expansion.
5. **ASR/TTS Service** (`/agribot/voice`): Voice processing with strict language enforcement and anti-hallucination settings.
6. **LLM Engine** (`/agribot/llm`): Local quantized LLM integration with rigorous JSON output formatting.

### 6.2 Client Applications
- **React Web UI** (`/frontend`): A glassmorphism kiosk app for desktops with an integrated Research Evaluation Diagnostics drawer.
- **Mobile Thin Client**: Responsive UI accessible over LAN.

---

## 7. Technology-to-Task Mapping (What is used where, and in which mode)

| Task | Technology | Mode | Output |
|---|---|---|---|
| Voice → text (Bengali ASR) | **faster-whisper** (CTranslate2) | Offline runtime | BN transcript + confidence |
| Image → description | **Offline VLM captioning** / LLM reasoning | Offline runtime | Symptom extraction + query logic |
| PDF Extraction | **Marker** | Offline build | Structured markdown + tables |
| OCR Fallback | **pypdf / Tesseract** | Offline build | OCR chunks |
| KG Storage | **SQLite graph tables** | Offline runtime | Versioned KG snapshot |
| Dense Retrieval | **FAISS** (`all-MiniLM-L6-v2`) | Offline runtime | Semantic evidence candidates |
| Sparse Retrieval | **BM25** | Offline runtime | Lexical evidence candidates |
| Reranking | **CrossEncoder** (`ms-marco-MiniLM-L-6-v2`) | Offline runtime | Precision-ranked evidence |
| Local LLM Generation | **llama-cpp-python** (Qwen2.5 1.5B GGUF) | Offline runtime | Structured BN+EN JSON answers |
| Desktop UI | **React + Vite + Tailwind** | Offline runtime | Client app w/ metrics drawer |

---

## 8. Multimodal PDF Filtering and Evidence Quality
AgriBot prevents retrieval pollution by:
- Using **Marker** to extract layout-aware content, capturing reading order natively.
- Removing repeated header/footer noise mathematically.
- Downweighting TOC/index/reference pages during ingestion.
- Treating tables as first-class Markdown evidence chunks to preserve structured relationships.

All evidence returned is provenance-rich and citation-ready.

---

## 9. Dialect Knowledge Graph (Beyond Lexicon)
AgriBot’s Information Extraction KG includes:
- Aliasing and canonical mapping (colloquial dialect → canonical scientific terminology).
- Graph relations connecting symptoms, diseases, pests, and treatments.
- Provenance to support trust and maintainability.

The KG materially improves retrieval recall for colloquial queries and provides strong disambiguation during agentic correction.

---

## 10. LangGraph Agentic Self-Correction and Safety
### 10.1 Bounded Self-Correct Loop
**Normalize → KG Link → Expand → Retrieve → Rerank → Grade → (Rewrite + Retry) → Generate → Verify → Respond**

### 10.2 Safety Rules Supported
- No chemical dosages provided without an evidence chunk explicitly supporting it.
- Ask follow-ups if context is incomplete (e.g., missing crop stage, location, severity).
- Strict refusal generation when evidence is missing or contradictory in the vector space.

---

## 11. Production Readiness and Maintainability
AgriBot is engineered for:
- **Reproducible builds** (versioned `.db` and `faiss` artifacts).
- **Automated Logging** of trace IDs, node latencies, and generation outputs for debugging.
- **Diagnostic UX** transparently rendering LLM verification reasoning to researchers in the UI.

---

## 12. Planned Research Publications (Paper Title Portfolio)
These titles maximize competitiveness by emphasizing generalizable CS contributions (trustworthy offline agentic RAG, multimodal document intelligence, KG-augmented low-resource retrieval, and speech-first interaction).

**A. Flagship (Edge Systems + Trustworthy AI)**
1. “Evidence-Graded Agentic RAG on Consumer GPUs: Offline, Citation-Enforced Bilingual Decision Support for Low-Connectivity Regions”
2. “Trustworthy Offline Decision Support with Verified RAG: Transparent Evidence, Safety Policies, and Bounded Self-Correction”

**B. Multimodal Document Intelligence for RAG**
3. “RAG from Real-World PDFs at Scale: Layout-Aware Extraction, Table/OCR Recovery, and Figure-Grounded Answering”
4. “From Figures and Tables to Grounded Answers: Multimodal Manual Ingestion for Evidence-Based Advisory under Offline Constraints”

**C. Low-Resource Language + Knowledge Graph Augmentation**
5. “Dialect-to-Science Alignment via Knowledge Graph-Augmented Retrieval: Robust Evidence Search for Colloquial Bengali Queries”
6. “Graph-Guided Query Expansion for Low-Resource Bilingual RAG: Entity Linking and Provenance-Aware Evidence Selection”

**D. Agentic Self-Correction + Verification (Method-Focused)**
7. “Self-Correcting RAG with Bounded Retrieval Loops: Evidence Grading, Query Rewriting, and Conservative Refusal Offline”
8. “Verification-First RAG for Safety-Critical Advisory: Citation Coverage and Claim Support Checks in Offline Agents”

**E. Speech-First Grounded Advisory (ASR→RAG→TTS)**
9. “Speech-to-Evidence Advisory Systems: Offline Whisper, Graph Expansion, and Citation-Grounded Responses in Bengali”
10. “Bilingual Voice Interfaces for Verified RAG: Measuring ASR Error Propagation and Evidence Robustness in Low-Resource Settings”
