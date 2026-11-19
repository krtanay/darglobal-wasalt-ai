"""
LangChain LCEL (LangChain Expression Language) Parallel Pipeline
Demonstrates idiomatic enterprise LangChain architecture for DarGlobal & Wasalt Real Estate RAG.
Can be executed standalone or imported into conversational chains.
"""

import os
import json
from typing import List, Dict, Any, Optional

# Load .env if present
try:
    from src.llm.openrouter_client import load_env
    load_env()
except Exception:
    pass

from src.rag.search_engine import HybridRealEstateRAG

class LangChainRealEstateRAGPipeline:
    """
    Idiomatic LangChain implementation using LCEL:
    Chain: {"context": retriever, "question": RunnablePassthrough()} | prompt | model | StrOutputParser()
    """

    def __init__(self, data_path: str = "data/properties.json", model_name: str = "nvidia/nemotron-3.5-lightning:free"):
        self.rag = HybridRealEstateRAG(data_path=data_path)
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.model_name = model_name
        self.chain = self._build_chain()

    def _format_docs(self, docs: List[Dict[str, Any]]) -> str:
        formatted = []
        for p in docs:
            formatted.append(
                f"- Property: {p.get('title')}\n"
                f"  Developer/Source: {p.get('source')}\n"
                f"  Location: {p.get('location', '')}\n"
                f"  Price: {p.get('price')}\n"
                f"  Type: {p.get('property_type')}\n"
                f"  Overview: {p.get('description')}\n"
                f"  URL: {p.get('url')}"
            )
        return "\n\n".join(formatted)

    def _build_chain(self):
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.runnables import RunnablePassthrough, RunnableLambda
            from langchain_core.output_parsers import StrOutputParser
            from langchain_openai import ChatOpenAI

            # 1. Prompt Template
            prompt = ChatPromptTemplate.from_messages([
                ("system", 
                 "You are an expert Real Estate Advisor representing DarGlobal (ultra-luxury international "
                 "branded properties) and Wasalt (Saudi Arabia's premier real estate marketplace).\n"
                 "Answer the inquiry based on the retrieved real estate context below. Always cite property "
                 "names, locations, exact prices, and URLs.\n\n"
                 "Real Estate Context:\n{context}"),
                ("human", "{question}")
            ])

            # 2. OpenRouter Chat Model via LangChain OpenAI adapter
            llm = ChatOpenAI(
                model=self.model_name,
                api_key=self.api_key or "sk-dummy-key",
                base_url="https://openrouter.ai/api/v1",
                temperature=0.35,
                default_headers={
                    "HTTP-Referer": "https://github.com/darglobal-wasalt-ai",
                    "X-Title": "DarGlobal Wasalt LangChain LCEL"
                }
            )

            # 3. Retriever Lambda
            retriever = RunnableLambda(lambda q: self._format_docs(self.rag.search(q, top_k=3)))

            # 4. Assembled LCEL Chain
            lcel_chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )
            return lcel_chain

        except ImportError:
            # Emulated LCEL Runner when langchain package is not installed
            return None

    def invoke(self, question: str) -> str:
        """Execute the RAG query through the LCEL chain or fallback orchestrator."""
        if self.chain:
            try:
                return self.chain.invoke(question)
            except Exception as e:
                print(f"[LangChain] Execution notice: {e}, using direct RAG engine.")

        # High-fidelity First-Principles Fallback
        retrieved = self.rag.search(question, top_k=3)
        from src.llm.openrouter_client import OpenRouterRealEstateAdvisor
        advisor = OpenRouterRealEstateAdvisor()
        answer, model, _ = advisor.chat(question, retrieved)
        return answer

if __name__ == "__main__":
    print("=================================================================")
    print("🏢 DarGlobal & Wasalt LangChain LCEL Pipeline Runner")
    print("=================================================================")
    pipeline = LangChainRealEstateRAGPipeline()
    sample_q = "What luxury branded villas are available in Spain by DarGlobal?"
    print(f"\n[Query]: {sample_q}\n")
    print("[Executing LCEL Chain...]")
    response = pipeline.invoke(sample_q)
    print("\n[AI Response]:\n", response)
