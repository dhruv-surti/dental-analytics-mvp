# Multi-Clinic Dental Group Analytics & Revenue Platform (GCP)

An end-to-end cloud analytics and data engineering platform built to simulate the multi-state operational and financial data challenges faced by Dental Boutique. This serverless, idempotent pipeline ingests messy operational, billing, and payment collection data into Google Cloud, models it for business intelligence, and enforces strict automated testing to guarantee financial reconciliation and prevent report leakage.

**Live BI Dashboard Link:** [(https://datastudio.google.com/s/tf1qJ4EBEkY)]

---

## 📸 The Platform in Action

### 1. Modern Analytics Executive Dashboard (Looker Studio)
![BI Dashboard Screenshot]([screenshots/dashboard.png])

### 2. Directed Acyclic Graph (Dataform Workflow DAG)
![Dataform DAG Graph]([screenshots/compiled-graph.png])

### 3. Serverless Execution Running on Schedule
![Cloud Run Job Log]([screenshots/dental-ingest-job.png])

---

## 🛠️ The Cloud Stack & Tools
* **Ingestion:** `Python` (using `dlt` for secure, schema-tolerant extraction)
* **Packaging & Containerization:** `Docker`
* **Workflow & Orchestration:** `Google Cloud Build` & `Google Cloud Run Jobs`
* **Data Warehouse:** `Google BigQuery`
* **Data Transformation & Quality Testing:** `Google Cloud Dataform` (SQLX pipeline)
* **Visualization:** `Google Looker Studio`
* **Version Control:** `GitHub` (with a dedicated git branching workflow)

---

## 📂 Repository Structure
```text
dental-analytics-mvp/
├── .dlt/
│   └── config.toml          # Lock configurations to Sydney (australia-southeast1)
├── src/
│   ├── generate_data.py     # Generates 6-month synthetic clinic operations and payment data (with injected bugs)
│   └── ingest_to_bq.py      # python/dlt script to land raw tables into BigQuery
├── definitions/             # Dataform transformation & quality scripts
│   ├── sources/             # Raw dataset declarations
│   ├── staging/             # Cleaning, casting, & deduplication layers (dedups APT-IDs, fixes clinic typos)
│   ├── marts/               # Joins for Clinic performance & Smile Discovery Conversions
│   └── assertions/          # Assertions (Custom tests catching Cancelled apps with billed status)
├── Dockerfile               # Container build configuration
├── requirements.txt         # Container dependencies (dlt[bigquery])
├── .dockerignore            # Excludes local venv and credentials from being built
├── .gitignore               # Excludes secrets (gcp-key.json)
└── README.md
