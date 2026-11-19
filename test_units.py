"""
In-Process Unit & Integration Tests for Upgraded Real Estate AI Advisor
Tests:
1. Image URL presence across all 23 properties
2. BM25 + Dense Semantic RRF Hybrid Search
3. Conversational Memory Query Expansion (Anaphora resolution)
4. Streaming Token Generator (SSE)
5. LangChain LCEL Pipeline Invocation
"""

import unittest
import json
from src.rag.search_engine import HybridRealEstateRAG
from src.llm.openrouter_client import OpenRouterRealEstateAdvisor
from src.langchain_pipeline import LangChainRealEstateRAGPipeline

class TestUpgradedRealEstateAdvisor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rag = HybridRealEstateRAG("data/properties.json")
        cls.advisor = OpenRouterRealEstateAdvisor()
        cls.langchain_pipe = LangChainRealEstateRAGPipeline()

    def test_1_properties_and_images(self):
        self.assertGreaterEqual(len(self.rag.properties), 20)
        # Verify all properties contain high-definition image_url
        for p in self.rag.properties:
            self.assertIn("image_url", p, f"Missing image_url in {p.get('id')}")
            self.assertTrue(p["image_url"].startswith("http"), f"Invalid image URL in {p.get('id')}")
        print(f"[TEST 1 PASS] Verified {len(self.rag.properties)} properties all contain valid image URLs.")

    def test_2_rrf_hybrid_search(self):
        # Conceptual query without exact keywords
        results = self.rag.search("secluded luxury villas overlooking the sea in Spain", top_k=2)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["source"], "DarGlobal")
        self.assertIn("Spain", results[0]["location"])
        print(f"[TEST 2 PASS] RRF Hybrid Search matched: {results[0]['title']}")

    def test_3_conversational_memory_expansion(self):
        mock_history = [
            {"role": "user", "content": "Tell me about Lamborghini villas"},
            {"role": "assistant", "content": "Tierra Viva by Automobili Lamborghini in Spain."}
        ]
        reformulated = self.rag.reformulate_query("What is its price and how many bedrooms?", mock_history)
        self.assertIn("Tierra Viva", reformulated)
        # Search using reformulated query
        hits = self.rag.search(reformulated, top_k=1)
        self.assertEqual(hits[0]["id"], "dg-tierra-viva")
        print(f"[TEST 3 PASS] Conversational memory resolved pronoun to: {hits[0]['title']}")

    def test_4_streaming_generator(self):
        props = self.rag.search("Tierra Viva", top_k=1)
        chunks = list(self.advisor.chat_stream("Hello", props))
        self.assertTrue(any(c.get("type") == "meta" for c in chunks), "Expected meta chunk with sources")
        self.assertTrue(any(c.get("type") == "token" for c in chunks), "Expected streaming tokens")
        self.assertTrue(any(c.get("type") == "done" for c in chunks), "Expected done chunk")
        print(f"[TEST 4 PASS] Streaming generator successfully yielded {len(chunks)} SSE chunks.")

    def test_5_langchain_lcel_pipeline(self):
        res = self.langchain_pipe.invoke("Tell me about Riyadh villas on Wasalt")
        self.assertTrue(len(res) > 20)
        print(f"[TEST 5 PASS] LangChain LCEL pipeline executed successfully ({len(res)} characters).")

if __name__ == "__main__":
    unittest.main()
