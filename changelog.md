# Changelog - Clause-Guard

All notable changes to the **Clause-Guard** project will be documented in this file.

## [Session 1] - 2026-03-30
*Project Initialization and Foundation Setup*

### Completed
- **Git Initialization**:
  - Initialized repository with standard structure.
  - Created branches: `master`, `arunav`, `srishti`.
  - Switched to `arunav` for primary development.
- **Project Structure**:
  - Created `/backend` and `/frontend` directories.
  - Refined `.gitignore` for efficient GitHub experience (covers Python, Node, and Vector DB).
- **Backend Foundation**:
  - Created `requirements.txt` with essential dependencies (FastAPI, ChromaDB, Ollama, Tesseract).
  - Implemented `main.py` entry point with FastAPI and CORS.
  - Implemented `ocr_service.py` for Tesseract-based PDF text extraction.
  - Implemented `rag_service.py` for ChromaDB and Ollama-based clause analysis.
  - Implemented `clause_segmenter.py` for heuristic legal text splitting.
  - Implemented `risk_calculator.py` for weighted risk score calculation.
  - Implemented `models.py` for Pydantic schema consistency.
  - Initialized `knowledge_base.json` with Indian Model Tenancy Act 2021 clauses.
- **Frontend Foundation (Phase 3 Started)**:
  - Initialized Next.js framework in `/frontend`.
  - Implemented a premium **Design System** in `globals.css` (Glassmorphism, Dark Mode, Emerald/Gold palette).
  - Developed the **High-Fidelity Home Page** with a cursor-reveal style hero and Indian legal context highlights.
  - Implemented the **Analysis Dashboard (`/analyze`)** with an interactive uploader and glassmorphic results view.
  - Configured global typography (Playfair Display & Inter) and metadata.
- **Environment Setup** (Complete):
  - Initialized Python `venv` and installed all AI dependencies.
  - Successfully scaffolded the Next.js application with TypeScript and Lucide-React.

### Things To Do next session
- Complete frontend framework initialization.
- Implement the "Rich Aesthetic" Design System in CSS.
- Integrate the Backend RAG pipeline with actual Ollama inference.
- Develop the "Results Dashboard" UI component.
