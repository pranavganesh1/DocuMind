# DAILY TASK

## 🧑‍🤝‍🧑 Team Setup Overview

| Member | Role | Focus Area |
| --- | --- | --- |
| Member 1 | **Backend & API Lead** | FastAPI, Notion/Google Docs integration |
| Member 2 | **AI/ML Lead** | Embeddings, FAISS, NLP |
| Member 3 | **Frontend Lead** | Streamlit or React UI |
| Member 4 | **DevOps & Security Lead** | Packaging, encryption, testing, CI/CD |

---

## 🗓️ 7-Day Action Plan & Guide

---

### 🔰 **Day 0: Preparation & Planning**

**All Members:**

- Create a **GitHub Repo** & assign branches (API, AI, UI, Packaging)
- Set up **communication channels** (WhatsApp/Slack + Google Meet)
- Finalize tech stack (Streamlit or React.js, Notion/Docs Export method)
- Import 10–15 Notion/Google Docs files as **sample data**

✅ **Checkpoint:** Kickoff call to confirm roles, tools, and deliverables.

---

### 📅 **Day 1: Architecture & Initial Setup**

### Member 1 – Backend/API

- Set up FastAPI boilerplate
- Define core endpoints: `/upload`, `/search`, `/health`
- Start parsing Google Docs/Notion Markdown exports

### Member 2 – AI/ML

- Install `sentence-transformers`, `FAISS`, and `spaCy`
- Test `all-MiniLM-L6-v2` on sample text
- Build a test embedding + similarity search script

### Member 3 – Frontend

- Set up Streamlit layout or React skeleton
- Design basic UI: input query box + result display section

### Member 4 – DevOps & Security

- Initialize Dockerfile + .gitignore + requirements.txt
- Set up folder structure: `api/`, `ml/`, `frontend/`, `utils/`
- Configure GitHub Actions (optional)

✅ **Checkpoint:** Validate that all tools run locally, initial skeletons ready

---

### 📅 **Day 2: Parsing & Embedding Pipeline**

### Member 1

- Complete Notion/Docs parser (Markdown or `.docx` → plain text)
- Extract metadata: title, author, last modified, tags

### Member 2

- Embed parsed text and store embeddings in FAISS index
- Build metadata JSON and store in SQLite

### Member 3

- UI: Display filters (author, date), and search result cards
- Add loading spinners and placeholder docs

### Member 4

- Implement AES encryption for local FAISS and metadata files
- Test mounting volumes in Docker

✅ **Checkpoint:** One full document successfully parsed and embedded

---

### 📅 **Day 3: Core Search Functionality**

### Member 1

- Build `/search` API: input query → return Top 5 similar docs
- Integrate SQLite to fetch metadata by ID

### Member 2

- Tune hybrid ranking (semantic score + keyword frequency)
- Add NER with spaCy for entity-aware queries (e.g., people, dates)

### Member 3

- Connect UI to `/search` endpoint
- Display matching score, title, author, snippet

### Member 4

- Encrypt and test read/write operations for FAISS and SQLite
- Document encryption/decryption commands

✅ **Checkpoint:** End-to-end query → result display demo (basic version)

---

### 📅 **Day 4: Filter & UI Completion**

### Member 1

- Add filtering options: document type, author, date range
- Cache recent search queries

### Member 2

- Test on larger dataset (≥50 docs)
- Add a fallback logic for low-confidence search

### Member 3

- Finalize UI: dark mode, search bar, filters, result layout
- Handle errors: “No results”, “Invalid input”, etc.

### Member 4

- Setup PyInstaller or Docker to bundle full app
- Begin internal testing checklist

✅ **Checkpoint:** MVP completed. Team reviews UI + features together.

---

### 📅 **Day 5: Full Integration & Bug Fixes**

### Member 1

- Complete all endpoint wiring
- Test with incorrect/malformed inputs

### Member 2

- Conduct edge-case testing for semantic queries
- Create test queries list for QA

### Member 3

- Add UI feedback: “Searching...”, “Results found”, etc.
- Ensure responsiveness on mobile and desktop

### Member 4

- Fix packaging issues (fonts, drivers, model sizes)
- Build standalone `.exe` or `.app` using PyInstaller

✅ **Checkpoint:** Run full app demo offline with sample data

---

### 📅 **Day 6: Final Testing & Documentation**

### Member 1

- Write API documentation (Swagger or Markdown)
- Validate all inputs/outputs

### Member 2

- Evaluate KPIs: precision, response time, indexing speed
- Prepare model tuning notes

### Member 3

- Polish UI, finalize all icons, colors, fonts
- Add logo or name to the app

### Member 4

- Write README + installation instructions
- Prepare demo script or recording

✅ **Checkpoint:** Share build with external tester for final feedback

---

### 📅 **Day 7: Final QA & Submission**

**All Members:**

- Final call to walkthrough full app
- Review all code, comments, and docs
- Submit final report (or record a demo)
- Push to GitHub with clear folder structure

✅ **Final Deliverables:**

- Working offline desktop app
- Source code repo
- README + User Manual
- (Optional) Demo video

---

## 🧾 Summary Table of Milestones

| Milestone | Description | Owner(s) | Deadline |
| --- | --- | --- | --- |
| Setup & Planning | Tools, repo, data | All | Day 1 |
| Data Parser + Embedding | Docs → embeddings | M1, M2 | Day 2 |
| Core Search & Ranking | Semantic + filters | M1, M2 | Day 3 |
| Frontend UI | Input, display, filters | M3 | Day 4 |
| Integration | Frontend + backend | All | Day 5 |
| Packaging + Testing | Offline build | M4 | Day 6 |
| Final Delivery | Docs + app | All | Day 7 |

---