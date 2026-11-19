# 🏢 DarGlobal & Wasalt Real Estate AI Chatbot

An AI-powered real estate advisory application grounded with publicly available project and listing data scraped from:
* **[DarGlobal](https://darglobal.co.uk/)**: Premier international luxury developer (Dubai, London, Spain, Qatar, Oman).
* **[Wasalt](https://wasalt.com/)**: Saudi Arabia's premier PropTech marketplace licensed by the Real Estate General Authority (REGA).

This project was built to meet the requirements of a **Junior AI Engineer assessment**, featuring an end-to-end pipeline: **Web Scraping $\rightarrow$ RAG Hybrid Search $\rightarrow$ OpenRouter Free Tier LLMs $\rightarrow$ Full-Stack Chat UI $\rightarrow$ Docker Containerization $\rightarrow$ Cloud Deployment**.

---

## 🌟 Key Features

1. **Grounded Real Estate Data:**
   - Pre-scraped and verified catalog of **23 high-value properties** across Spain, Dubai, Ras Al Khaimah, Oman, Qatar, London, Riyadh, Jeddah, Dammam, and Al-Khobar.
   - Includes branded partnerships (Automobili Lamborghini, Pagani, Missoni, Aston Martin, Elie Saab, Trump Organization, Fendi Casa).

2. **RAG Hybrid Search Engine (`src/rag/search_engine.py`):**
   - Implements **BM25 + TF-IDF Vector Similarity** with intent-based metadata filtering.
   - Grounded context retrieval prevents hallucinations and ensures exact pricing, specs, and direct developer links are cited.

3. **OpenRouter Free Tier Integration (`src/llm/openrouter_client.py`):**
   - Integrates with OpenRouter (`https://openrouter.ai/api/v1`) using standard free models:
     - `meta-llama/llama-3.3-70b-instruct:free`
     - `google/gemini-2.0-flash-exp:free`
     - `deepseek/deepseek-r1:free`
     - `qwen/qwen-2.5-72b-instruct:free`
   - Features **automatic multi-model failover**: if one model experiences rate-limiting (429), it switches to the next free model.
   - Includes a **built-in grounded offline fallback mode** so the app is 100% interactive and testable immediately, even before an API key is provided.

4. **Modern Responsive Web Interface (`public/index.html`):**
   - Luxury Dark/Gold theme styled with Tailwind CSS.
   - One-click starter prompt chips.
   - Source filter pills (`All`, `DarGlobal Only`, `Wasalt Only`).
   - Clickable developer listing cards with live links.
   - Searchable Database Explorer sidebar.
   - Runtime OpenRouter API Key and Model configuration modal.

5. **Containerisation & Cloud Deployment Ready:**
   - Production multi-stage `Dockerfile` (Python 3.11-slim) with health checks.
   - `docker-compose.yml` for single-command orchestration.

---

## 📁 Project Structure

```text
darrproject/
│
├── data/
│   ├── properties.json           # Scraped unified real estate dataset
│   └── properties.jsonl          # Line-delimited JSON for RAG streaming
│
├── src/
│   ├── scrapers/
│   │   ├── darglobal_scraper.py  # DarGlobal luxury projects scraper
│   │   ├── wasalt_scraper.py     # Wasalt Saudi Arabia properties scraper
│   │   └── run_all_scrapers.py   # Aggregation pipeline
│   │
│   ├── rag/
│   │   └── search_engine.py      # BM25 + TF-IDF hybrid retrieval engine
│   │
│   ├── llm/
│   │   └── openrouter_client.py  # OpenRouter free model client with failover
│   │
│   └── server.py                 # REST API server & static file host
│
├── public/
│   └── index.html                # Luxury real estate chat UI (Tailwind + Lucide)
│
├── Dockerfile                    # Production container specification
├── docker-compose.yml            # Docker Compose service definition
├── .dockerignore                 # Excluded container build paths
├── requirements.txt              # Python dependencies
├── start.py                      # Quick start entrypoint
└── README.md                     # Documentation & usage guide
```

---

## 🚀 How to Run Locally

### 1. Direct Python Execution (Zero Extra Dependencies)
This project uses standard Python libraries for maximum portability:

```bash
# Clone or navigate to the repository
cd darrproject

# Start the server (default port 8080)
python start.py
```
Open **[http://localhost:8080](http://localhost:8080)** in your browser.

### 2. Running with Docker

```bash
# Build the Docker image
docker build -t darglobal-wasalt-ai .

# Run the container
docker run -p 8080:8080 -e OPENROUTER_API_KEY="your-openrouter-key" darglobal-wasalt-ai
```
Or via Docker Compose:
```bash
docker-compose up --build
```

---

## 🌐 Deploying to the Cloud for a Free Working URL

You can host this Dockerized app on any of the following platforms for free:

### Option 1: Render.com (Recommended)
1. Push this project to GitHub.
2. Log into [Render.com](https://render.com) $\rightarrow$ **New Web Service**.
3. Connect your repository and select **Docker**.
4. Set Environment Variable:
   - `OPENROUTER_API_KEY` = `your-key` (optional, can also be entered directly in the UI).
5. Click **Deploy**. Render builds the Dockerfile and assigns a live HTTPS URL (e.g., `https://darglobal-wasalt-ai.onrender.com`).

### Option 2: Hugging Face Spaces
1. Create a new Space on [Hugging Face Spaces](https://huggingface.co/spaces).
2. Choose **Docker** as the SDK.
3. Push the repository to the space.
4. Access your instant live URL: `https://huggingface.co/spaces/<your-username>/real-estate-ai`.

---

## 🧪 Sample Evaluation Queries

Try these sample queries directly in the chatbot:
* *"What luxury branded residences does DarGlobal have in Dubai?"*
* *"Find 4-bedroom villas in Riyadh under 4M SAR on Wasalt."*
* *"Tell me about the Tierra Viva Lamborghini villas in Spain."*
* *"Compare DarGlobal's international projects with Wasalt's Saudi master developments."*
* *"Does DarGlobal have any developments in Oman or Qatar?"*
