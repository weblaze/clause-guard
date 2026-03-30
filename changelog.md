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
- **Firebase Cloud Transition (Phase 4 Started)**:
  - Initialized `firebase.ts` with the configuration for project `clause-guard-cf894`.
  - Configured `firebase.json` for Next.js Web App deployment.
  - Implemented `firestore.rules` and `storage.rules` for cloud-native security.
  - Targeted Firebase project `clause-guard-cf894` for Cloud native deployment.
  - Successfully committed all previous development progress for Phase 1/2 to the `arunav` branch.
  - Initialized backend Dockerization for Google Cloud Run (Linked to Firebase).
- **Version Control (Persistent Execution)**:
  - Implemented automatic Phase-based Git staging and committing as instructed.
  - Updated `.gitignore` for standard cloud/Next.js efficiency.

### Things To Do next session
- Complete frontend framework initialization.
- Implement the "Rich Aesthetic" Design System in CSS.
- Integrate the Backend RAG pipeline with actual Ollama inference.
- Develop the "Results Dashboard" UI component.
