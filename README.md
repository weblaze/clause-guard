# Clause-Guard: Automated Lease & Rental Agreement Analyzer

**Clause-Guard** is an AI-powered legal technology platform designed to bridge the information gap between landlords and tenants. By leveraging Natural Language Processing (NLP) and Retrieval-Augmented Generation (RAG), the system analyzes rental agreements, identifies predatory or illegal clauses, and translates complex legal jargon into plain, understandable English.

---

## 🚀 Overview

Tenants frequently sign exploitative lease agreements due to a lack of legal knowledge or access to counsel. Clause-Guard addresses this information asymmetry by providing:
- **Instant Analysis**: Upload a PDF and get a risk report in seconds.
- **Jurisdiction Awareness**: Analysis based on specific Indian Tenancy Laws (e.g., Model Tenancy Act 2021).
- **Risk Scoring**: A clear 0–100 score (Low, Medium, High) for quick decision-making.
- **Plain English Explanations**: Side-by-side comparison of original legalese vs. simplified meanings.

## ✨ Key Features

- **Document Parsing**: Robust PDF text extraction with **Tesseract OCR** fallback for scanned documents.
- **RAG-Powered Analysis**: semantic clause analysis using **ChromaDB** vector storage and **Ollama** (Local LLMs).
- **Clause Classification**: Automatic tagging of clauses as **Fair**, **Unfair**, or **Illegal**.
- **Interactive Dashboard**: High-fidelity UI for viewing flagged clauses and jurisdictional citations.
- **No Account Required**: Documents are analyzed on the fly and nothing is persisted server-side — no login, no stored history.

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**: LangChain, Ollama (Gemma 3), FastEmbed
- **Vector Database**: ChromaDB
- **OCR**: Tesseract OCR
- **PDF Processing**: pdfplumber

### Frontend
- **Framework**: Next.js (App Router)
- **Styling**: Vanilla CSS (Modern, Premium Aesthetics)
- **Icons**: Lucide-React

### Data Persistence
- **None** — this prototype is stateless. Uploaded PDFs are processed in-memory/on-disk for the duration of a single request and the analysis result is returned directly to the client; nothing is written to a database.

---

## 📂 Project Structure

```text
clause-guard/
├── backend/            # FastAPI application
│   ├── venv/           # Python Virtual Environment
│   ├── main.py         # Entry point
│   ├── services/       # OCR, RAG, and Segmenter logic
│   └── knowledge_base/ # Indian legal statutes (JSON/Chroma)
├── frontend/           # Next.js application
│   ├── src/            # App components and pages
│   └── public/         # Static assets
├── session_logs/       # Progressive project tracking
└── README.md           # Documentation
```

## 🌿 Branching Strategy

- `master`: Stable production-ready code (Tracked by Vercel and Render for deployments).
- `arunav`: Main development branch for Arunav.
- `srishti`: Collaboration branch for Srishti.

---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 24+
- Tesseract OCR (Installed and added to PATH)
- Ollama (Running locally)

No third-party account (Supabase, Google OAuth, etc.) is required — the app runs standalone out of the box.

### Backend Setup
1. Navigate to `/backend`.
2. Create and activate a virtual environment: `python -m venv venv`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Start the server: `python main.py`.

### Frontend Setup
1. Navigate to `/frontend`.
2. Install dependencies: `npm install`.
3. Start the development server: `npm run dev`.

---

## ⚖️ Legal Disclaimer

*Note: Clause-Guard is an educational tool designed to assist in understanding rental agreements. It does not constitute formal legal advice. Always consult with a qualified legal professional for critical legal decisions.*

---

*Based on the "Clause-Guard Final Report" (March 2026).*
