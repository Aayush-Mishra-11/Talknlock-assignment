# Talknlock AI-Powered Marketing Intelligence System

This repository contains the source code, analysis scripts, dashboard prototype, and technical documentation for the Talknlock AI/ML Intern Assignment.

The system combines a **Content Performance Predictive Model** (using a Scikit-Learn Decision Tree Regressor) and a **Content Recommender Engine** (using candidate parameter search and local SHAP explains) with a **Generative LLM Reasoning Layer** (integrating local Ollama or Cloud APIs) to help a digital marketing agency optimize content before publishing.

---

## 📂 Repository Structure

```
talknlock-ai-assignment/
│
├── Dataset/
│   └── synthetic_marketing_data.csv    # Generated 1,500 record dataset
│
├── src/
│   ├── __init__.py
│   ├── data_generator.py               # Data generation script (1,500 rows)
│   ├── eda.py                          # Exploratory Data Analysis & visualisations
│   ├── model.py                        # ML model training and metrics comparison
│   ├── recommender.py                  # Recommendation engine using model grid scoring
│   └── llm_layer.py                    # LLM handler (Ollama, Cloud APIs, mock fallback)
│
├── app/
│   ├── main.py                         # FastAPI web server
│   ├── templates/
│   │   └── index.html                  # Glassmorphic dashboard UI
│   └── static/
│       ├── css/
│       │   └── style.css               # Dashboard theme styling
│       └── js/
│           └── app.js                  # Frontend logic & API handlers
│
├── reports/
│   ├── technical_report.md             # 15-page comprehensive technical report
│   └── architecture.mermaid            # Standalone production architecture diagram
│
├── requirements.txt                    # Project dependencies
└── README.md                           # Quickstart guide (this file)
```

---

## ⚡ Quickstart Guide

### 1. Install Dependencies
Ensure you have Python 3.9+ installed. Run:
```bash
pip install -r requirements.txt
```

### 2. Generate the Dataset
Create the synthetic dataset of 1,500 records inside `Dataset/`:
```bash
python src/data_generator.py
```

### 3. Run Exploratory Data Analysis
Execute the statistical test (ANOVA) and save the visualization plots under `reports/static/`:
```bash
python src/eda.py
```

### 4. Train the ML Models & Setup SHAP
Train the baseline vs. champion models, evaluate test set performance, and save the explainer parameters:
```bash
python src/model.py
```

### 5. Launch the Dashboard
Start the FastAPI server:
```bash
python app/main.py
```
Open your browser and navigate to: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🤖 LLM & Ollama Configuration

The AI Reasoning Layer is built to support local **Ollama** by default, but it degrades gracefully or scales up depending on your environment.

To configure LLM providers, set the appropriate environment variables before running `app/main.py`:

*   **Option A: Local Ollama (Default)**
    *   Ensure Ollama is running on your machine.
    *   Variables (defaults are used if unset):
        ```bash
        set OLLAMA_URL=http://127.0.0.1:11434
        set OLLAMA_MODEL=mistral
        ```
*   **Option B: Google Gemini API (Recommended for Cloud Deployment)**
    *   Set the Gemini key:
        ```bash
        set GEMINI_API_KEY=your_gemini_api_key_here
        ```
*   **Option C: OpenAI API**
    *   Set the OpenAI key:
        ```bash
        set OPENAI_API_KEY=your_openai_api_key_here
        ```
*   **Option D: Offline Mock Fallback**
    *   If no cloud API key is set and Ollama is unreachable/offline, the system will **automatically fall back to a high-quality rule-based local writer**. This guarantees that the dashboard never crashes and works flawlessly in any evaluation environment.

---

## 📈 ML Performance Highlights

Our training pipeline splits the data (80% train, 20% test) and compares Decision Tree vs. Random Forest models:
*   **Baseline (Decision Tree, depth=6):** MAE = `4.872` | RMSE = `7.355` | $R^2$ = `0.728`
*   **Champion (Random Forest, depth=12):** MAE = `4.375` | RMSE = `7.530` | $R^2$ = `0.715`
*   **Decision Tree Selected:** While Random Forest had lower training error, the Decision Tree Regressor scored a higher test set $R^2$ (0.728 vs 0.715), making it more generalized and robust for predicting our hierarchical platform-topic relationships without overfitting.
