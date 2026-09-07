# AI-Powered Land Record Digitization and Validation System

A production-grade web application built with **FastAPI**, **React + TypeScript**, **PaddleOCR**, **Indic-TrOCR**, and **OpenCV** to preprocess, extract, validate, human-verify, and export Indian land records (Record of Rights, 7/12 Extract, Khasra, Khata, Patta) into **UTF-8 BOM CSV files**.

---

## 1. System Architecture

```
                               ┌────────────────────────────────┐
                               │   React + TypeScript Frontend  │
                               │   (Drag & Drop, Verification)  │
                               └───────────────┬────────────────┘
                                               │ REST API / JSON
                               ┌───────────────▼────────────────┐
                               │     FastAPI Backend Server     │
                               └───────────────┬────────────────┘
                                               │
   ┌───────────────────────────────────────────┴───────────────────────────────────────────┐
   │                                                                                       │
   ▼                                           ▼                                           ▼
┌────────────────────────┐         ┌────────────────────────┐         ┌────────────────────────┐
│  Preprocessing Engine  │         │   Modular OCR Engine   │         │ Validation & Scoring   │
│  - Deskew & Normalize  │ ──────► │  - PaddleOCR (Printed) │ ──────► │ - Format & Logical     │
│  - CLAHE & Contrast    │         │  - Indic-TrOCR (Hand)  │         │ - Duplicate Check      │
│  - Adaptive Threshold  │         │  - Layout Parser       │         │ - Multi-Signal Score   │
└────────────────────────┘         └────────────────────────┘         └────────────────────────┘
                                                                                   │
                                                                                   ▼
                                                                      ┌────────────────────────┐
                                                                      │   UTF-8 BOM CSV Engine │
                                                                      │   (utf-8-sig Excel)    │
                                                                      └────────────────────────┘
```

---

## 2. Supported Indian Languages

The system includes native multi-lingual support across 12 Indian languages:

| Language | Code | Primary OCR Engine | Layout Bounding Boxes |
| :--- | :--- | :--- | :--- |
| **English** | `en` | PaddleOCR | Supported |
| **Hindi (हिन्दी)** | `hi` | PaddleOCR | Supported |
| **Tamil (தமிழ்)** | `ta` | PaddleOCR | Supported |
| **Telugu (తెలుగు)** | `te` | PaddleOCR | Supported |
| **Kannada (கன்னட)** | `kn` | PaddleOCR | Supported |
| **Malayalam (മലയാളം)** | `ml` | PaddleOCR | Supported |
| **Marathi (मराठी)** | `mr` | PaddleOCR | Supported |
| **Bengali (বাংলা)** | `bn` | PaddleOCR | Supported |
| **Gujarati (ગુજરાતી)** | `gu` | PaddleOCR | Supported |
| **Punjabi (ਪੰਜਾਬੀ)** | `pa` | PaddleOCR | Supported |
| **Odia (ଓଡ଼ିଆ)** | `or` | PaddleOCR | Supported |
| **Assamese (অসমীয়া)** | `as` | PaddleOCR | Supported |

---

## 3. Quick Start (Local Setup)

### Step 1: Install Backend Dependencies & Run FastAPI

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
Backend API will run at: `http://localhost:8000`  
Swagger API Documentation: `http://localhost:8000/api/v1/docs`

### Step 2: Run Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```
Frontend Web UI will run at: `http://localhost:5173`

---

## 4. Running with Docker

Run the full stack (FastAPI backend, React frontend, PostgreSQL + PostGIS, Redis, Celery worker) with a single command:

```bash
docker compose up --build
```
Access the application at: `http://localhost:3000`

---

## 5. Synthetic Document Generator & Test Suite

Generate sample bilingual land records (RoR / Khasra-Khata) for testing:

```bash
python scripts/generate_sample_docs.py
```

Run automated pytest backend suite:

```bash
cmd /c "set PYTHONPATH=backend && python -m pytest backend/tests"
```

---

## 6. CSV Format Specifications

All CSV downloads are generated using `utf-8-sig` (UTF-8 with Byte Order Mark). This guarantees native rendering of Indian scripts in Microsoft Excel, Apple Numbers, and Google Sheets without encoding corruptions.

### Standard CSV Column Structure

`record_id`, `document_id`, `document_name`, `document_type`, `state`, `district`, `tehsil`, `taluk`, `village`, `ward`, `owner_name`, `co_owner_names`, `parent_name`, `ownership_type`, `ownership_share`, `survey_number`, `sub_survey_number`, `khasra_number`, `khata_number`, `plot_number`, `patta_number`, `parcel_id`, `area`, `area_unit`, `land_classification`, `land_type`, `irrigation_status`, `land_use`, `mutation_number`, `mutation_date`, `mutation_type`, `previous_owner`, `new_owner`, `registration_number`, `registration_date`, `deed_number`, `transaction_type`, `record_date`, `source_department`, `language`, `ocr_engine`, `ocr_confidence`, `extraction_confidence`, `validation_status`, `verification_status`, `remarks`

---

## 7. Model Licensing Information

| Library / Model | License | Notes |
| :--- | :--- | :--- |
| **PaddleOCR** | Apache 2.0 | Open-source multi-lingual printed text OCR engine |
| **PyTorch / Transformers** | Apache 2.0 | Transformer architecture for handwriting recognition |
| **FastAPI** | MIT | High-performance Python backend framework |
| **PyMuPDF (fitz)** | AGPL-3.0 / Commercial | High-resolution PDF page rendering & text extraction |
| **OpenCV** | Apache 2.0 | Image preprocessing, deskewing, and contrast adjustment |
