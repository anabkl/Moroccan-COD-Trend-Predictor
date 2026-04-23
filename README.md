# 🛍️ SoukAI – AI Winning Product Analyzer for Moroccan COD E-commerce

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![USMS](https://img.shields.io/badge/University-USMS%20Beni%20Mellal-red)](https://www.usms.ac.ma)

> **SoukAI** is an AI-powered system that analyzes Moroccan COD (Cash-on-Delivery) e-commerce products, detects purchase intent from Darija/French/Arabic comments, and predicts winning products for the Moroccan market.

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Browser / Client                    │
│              React 18 + Tailwind CSS + Vite             │
│                     localhost:3000                      │
└───────────────────────┬─────────────────────────────────┘
                        │  HTTP / REST
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                       │
│              Python 3.11 · Uvicorn ASGI                 │
│                     localhost:8000                      │
│                                                         │
│   ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│   │ /products    │  │ /analysis    │  │ /dashboard  │  │
│   │ CRUD router  │  │ NLP + Score  │  │ Stats API   │  │
│   └──────────────┘  └──────────────┘  └─────────────┘  │
│                                                         │
│   ┌──────────────────────────────────────────────────┐  │
│   │              AI / ML Services                    │  │
│   │  NLP (Darija intent) · Scoring · Recommendation  │  │
│   └──────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
   ┌─────────────┐          ┌──────────────┐
   │  SQLite DB  │          │  data/*.csv  │
   │  soukai.db  │          │  Sample data │
   └─────────────┘          └──────────────┘
```

---

## ✨ Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | 🔍 **Product Scoring** | Composite AI score based on trend growth, competition level and profit margin |
| 2 | 💬 **Darija NLP** | Purchase-intent detection from Moroccan Darija, French and Arabic comments |
| 3 | 📈 **Trend Prediction** | Market trend analysis to identify winning COD products before saturation |
| 4 | 🏆 **Product Ranking** | Ranked leaderboard of the most profitable products for the Moroccan market |
| 5 | 📊 **Dashboard Analytics** | Visual KPIs: top categories, average margins, comment sentiment distribution |
| 6 | 🤖 **AI Explanations** | Human-readable justifications for every score and recommendation |
| 7 | 🌍 **Multilingual Support** | Full support for Darija · French · Arabic in comments and UI |
| 8 | 📦 **REST API** | Clean OpenAPI-documented REST endpoints for all features |

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | React + Vite | 18 / 5 |
| Styling | Tailwind CSS | 3 |
| Backend | FastAPI + Uvicorn | 0.110 |
| Language | Python | 3.11+ |
| Database | SQLite via SQLAlchemy | 2.x |
| NLP | Custom Darija tokenizer | — |
| Containerisation | Docker + Docker Compose | 24+ |
| Data | Pandas + CSV | — |
| Notebook | Jupyter | — |

---

## 🚀 Installation

### Prerequisites

- **Python** ≥ 3.11 – [python.org](https://python.org/downloads)
- **Node.js** ≥ 18 – [nodejs.org](https://nodejs.org)
- **Docker Desktop** (optional) – [docker.com](https://docker.com/products/docker-desktop)
- **Git**

---

### Option A – Local Development (macOS / Linux)

#### 1. Clone the repository

```bash
git clone https://github.com/anabkl/Moroccan-COD-Trend-Predictor.git
cd Moroccan-COD-Trend-Predictor
```

#### 2. Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start the API server
uvicorn app.main:app --reload --port 8000
```

> API available at **http://localhost:8000** · Swagger UI at **http://localhost:8000/docs**

#### 3. Frontend setup

```bash
# Open a new terminal from project root
cd frontend

# Copy environment file
cp ../.env.example .env.local
# Edit VITE_API_URL=http://localhost:8000 if needed

# Install dependencies and start dev server
npm install
npm run dev
```

> App available at **http://localhost:5173**

---

### Option B – Docker Compose (recommended for production)

```bash
# From project root
cp .env.example .env

docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |

To stop:

```bash
docker compose down
```

---

## 📡 API Documentation

All endpoints are documented interactively at **`/docs`** (Swagger UI) and **`/redoc`**.

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/products` | List all products with scores |
| `GET` | `/products/{id}` | Get a single product by ID |
| `POST` | `/products` | Create a new product |
| `PUT` | `/products/{id}` | Update a product |
| `DELETE` | `/products/{id}` | Delete a product |

### Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analysis/score/{id}` | Compute AI score for a product |
| `POST` | `/analysis/intent` | Detect purchase intent from a comment |
| `GET` | `/analysis/recommendations` | Get top-N recommended products |
| `GET` | `/analysis/explain/{id}` | Get human-readable AI explanation |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/dashboard/stats` | Global KPIs and statistics |
| `GET` | `/dashboard/top-categories` | Category-level aggregated scores |
| `GET` | `/dashboard/trending` | Currently trending products |

---

## 🖼️ Screenshots

| Dashboard | Product Analysis | Rankings |
|-----------|-----------------|----------|
| *(coming soon)* | *(coming soon)* | *(coming soon)* |

---

## 📂 Project Structure

```
Moroccan-COD-Trend-Predictor/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings & CORS
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models.py            # ORM models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routers/
│   │   │   ├── products.py
│   │   │   ├── analysis.py
│   │   │   └── dashboard.py
│   │   ├── services/
│   │   │   ├── nlp_service.py   # Darija NLP
│   │   │   ├── scoring_service.py
│   │   │   ├── recommendation_service.py
│   │   │   └── explanation_service.py
│   │   └── utils/
│   │       └── text_utils.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.js
├── data/
│   ├── products.csv             # 15 sample products
│   └── comments.csv             # 80+ Darija/French/Arabic comments
├── notebooks/
│   └── exploratory_analysis.ipynb
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 📊 Sample Data

The `data/` directory contains curated sample data reflecting the Moroccan COD market:

- **`products.csv`** – 15 products across 5 categories (health, gadgets, fashion, cosmetics, kitchen, home) with realistic trend scores, competition levels and profit margins for the Moroccan market.
- **`comments.csv`** – 80+ authentic-style customer comments written in **Darija** (Moroccan Arabic dialect), **French** and **Arabic**, covering purchase-intent signals like delivery questions, price enquiries and satisfaction feedback.

---

## 🔐 Ethical Data Policy

- All sample data is **synthetic and fictional** – no real personal data is collected or stored.
- The NLP purchase-intent detector is built to **assist** sellers, not to manipulate buyers.
- Comments are labelled by language to enable **multilingual fairness** in model evaluation.
- The system adheres to Moroccan data-privacy norms and does not scrape third-party platforms.

---

## 🗺️ Roadmap

- [ ] 🧠 Fine-tune a Darija BERT model for intent classification
- [ ] 📱 Progressive Web App (PWA) support
- [ ] 🔔 Trend alert notifications (email / WhatsApp)
- [ ] 🌐 Jumia MA / Avito scraper integration (with ToS compliance)
- [ ] 📦 Multi-database support (PostgreSQL)
- [ ] 🎯 Facebook Ads audience insights integration
- [ ] 📊 Export reports to PDF / Excel

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

Please follow the existing code style and add tests where applicable.

---

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Anas Lahraoui**
Student at **Université Sultan Moulay Slimane (USMS)**, Beni Mellal, Morocco.

- GitHub: [@anabkl](https://github.com/anabkl)
- University: [usms.ac.ma](https://www.usms.ac.ma)

---

<p align="center">Made with ❤️ for the Moroccan e-commerce ecosystem</p>

