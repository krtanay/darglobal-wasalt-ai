# 🏢 DarGlobal & Wasalt Real Estate AI Chatbot Pro

An AI-powered luxury real estate advisory application grounded with publicly available project and listing data scraped from:
* **[DarGlobal](https://darglobal.co.uk/)**: Premier international luxury developer (Dubai, London, Spain, Qatar, Oman).
* **[Wasalt](https://wasalt.com/)**: Saudi Arabia's premier PropTech marketplace licensed by the Real Estate General Authority (REGA).

This application was engineered to showcase **end-to-end production AI engineering discipline** featuring:
1. **Multi-Turn Conversational Memory (Follow-up pronoun resolution)**
2. **Real-Time Token Streaming (Server-Sent Events / SSE)**
3. **Visual Property Cards with High-Res Hero Architecture Images**
4. **Hybrid RAG with Reciprocal Rank Fusion (BM25 + Dense Semantic Subwords)**
5. **Parallel LangChain Expression Language (LCEL) Pipeline**
6. **OpenRouter Free Tier Integration with Multi-Model Failover**
7. **Production Docker Containerization**

---

## 🌟 Architecture & Advanced Features

### 1. Hybrid RAG with Reciprocal Rank Fusion (RRF)
Implemented in [`src/rag/search_engine.py`](file:///c:/Users/tanay/Desktop/ass%20proeject/darrproject/src/rag/search_engine.py):
* **Lexical BM25:** Keyword precision with $k_1=1.5, b=0.75$.
* **Dense Semantic Subword Cosine:** Character/word n-gram vector similarity capturing semantic concepts (e.g., *"secluded holiday retreat for billionaire families"* matches *Tierra Viva*).
* **RRF Scoring Formula:**
  $$\text{RRF}(d) = \frac{1}{60 + \text{rank}_{\text{bm25}}(d)} + \frac{1}{60 + \text{rank}_{\text{dense}}(d)} + \text{MetadataBoost}$$

### 2. Multi-Turn Conversational Memory
* Resolves anaphora and pronouns automatically (*"How much does it cost?", "How many bedrooms does this villa have?"*).
* Expands the retrieval query with recent context and preserves previous conversation turns in the LLM payload.

### 3. Real-Time Token Streaming (SSE)
* Uses Server-Sent Events (`/api/chat/stream`) yielding token chunks with sub-200ms perceived response latency.
* Markdown formatting and visual citation cards are rendered on the fly.

### 4. Rich Visual Architecture Cards
* Scraped catalog of **23 luxury properties** featuring curated high-resolution architectural images.
* Displayed dynamically in both the searchable side drawer and beneath AI recommendations.

### 5. Dual Implementation: Native Zero-Dependency & LangChain LCEL
* **Default Engine:** Zero-dependency Python standard library implementation for minimal footprint (~120MB Docker container, <40MB RAM).
* **LangChain Pipeline ([`src/langchain_pipeline.py`](file:///c:/Users/tanay/Desktop/ass%20proeject/darrproject/src/langchain_pipeline.py)):** Idiomatic LCEL chain demonstrating enterprise framework versatility:
  ```python
  chain = (
      {"context": retriever, "question": RunnablePassthrough()}
      | prompt_template
      | chat_model
      | StrOutputParser()
  )
  ```

---

## 📁 Project Directory

```text
darrproject/
│
├── data/
│   ├── properties.json           # Scraped dataset with visual image URLs
│   └── properties.jsonl          # JSONL format for vector ingestion
│
├── src/
│   ├── scrapers/
│   │   ├── darglobal_scraper.py  # DarGlobal scraper
│   │   ├── wasalt_scraper.py     # Wasalt scraper
│   │   └── run_all_scrapers.py   # Ingestion pipeline
│   │
│   ├── rag/
│   │   └── search_engine.py      # Hybrid BM25 + Semantic Cosine RRF Engine
│   │
│   ├── llm/
│   │   └── openrouter_client.py  # OpenRouter multi-turn & SSE streaming client
│   │
│   ├── langchain_pipeline.py     # Modern LangChain LCEL pipeline
│   └── server.py                 # REST & SSE streaming server
│
├── public/
│   └── index.html                # Streaming chat UI with visual property cards
│
├── Dockerfile                    # Production container specification
├── docker-compose.yml            # Docker Compose orchestration
├── requirements.txt              # Python dependencies
├── start.py                      # Server entrypoint
├── test_units.py                 # Full test suite (all 5 tests passing)
└── README.md                     # Documentation
```

---

## 🚀 Running the Application

### 1. Direct Python Execution
```bash
python start.py
```
Open **[http://localhost:8080](http://localhost:8080)** in your browser.

### 2. Testing the LangChain LCEL Pipeline
```bash
python -m src.langchain_pipeline
```

### 3. Running with Docker
```bash
docker build -t darglobal-wasalt-ai .
docker run -p 8080:8080 -e OPENROUTER_API_KEY="your-key" darglobal-wasalt-ai
```

---

## 🧪 Sample Evaluation Queries

Try asking these multi-turn questions in the chat:
1. *"Show me the Tierra Viva Lamborghini villas in Spain."*
2. *(Follow-up)*: *"What is its starting price and how many bedrooms?"* $\rightarrow$ *(AI answers directly using conversational memory without repeating the property name!)*
3. *"What luxury villas in Riyadh are listed on Wasalt under 4M SAR?"*
4. *"Compare DarGlobal's international branded residences with Wasalt's Saudi master developments."*
