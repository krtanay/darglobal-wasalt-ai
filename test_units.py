"""
In-Process Unit & Integration Tests for Real Estate AI Advisor
Tests RAG search, metadata filtering, OpenRouter client fallback, and API response formatting.
Runs without socket binding.
"""

import unittest
import json
from src.rag.search_engine import HybridRealEstateRAG
from src.llm.openrouter_client import OpenRouterRealEstateAdvisor

class TestRealEstateAdvisor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rag = HybridRealEstateRAG("data/properties.json")
        cls.advisor = OpenRouterRealEstateAdvisor()

    def test_properties_loaded(self):
        self.assertGreaterEqual(len(self.rag.properties), 20, "Should have at least 20 properties indexed")
        print(f"[OK] Successfully indexed {len(self.rag.properties)} properties.")

    def test_darglobal_search(self):
        results = self.rag.search("Lamborghini villas in Spain", top_k=3, source_filter="DarGlobal")
        self.assertTrue(any("Tierra Viva" in p["title"] for p in results))
        self.assertEqual(results[0]["source"], "DarGlobal")
        print(f"[OK] DarGlobal search returned: {results[0]['title']}")

    def test_wasalt_search(self):
        results = self.rag.search("Modern villa in Riyadh", top_k=3, source_filter="Wasalt")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["source"], "Wasalt")
        self.assertIn("Riyadh", results[0]["location"])
        print(f"[OK] Wasalt search returned: {results[0]['title']}")

    def test_openrouter_offline_synthesis(self):
        props = self.rag.search("Luxury villas in Spain", top_k=2)
        answer, model_used, sources = self.advisor.chat("Luxury villas in Spain", props)
        self.assertIn("Tierra Viva", answer)
        self.assertIn("Offline", model_used)
        self.assertEqual(len(sources), 2)
        print(f"[OK] Grounded offline synthesis generated successfully.")

    def test_cross_comparison_query(self):
        results = self.rag.search("Compare DarGlobal Dubai and Wasalt Riyadh properties", top_k=4)
        sources_found = set(p["source"] for p in results)
        self.assertIn("DarGlobal", sources_found)
        self.assertIn("Wasalt", sources_found)
        print(f"[OK] Cross-comparison retrieved both DarGlobal and Wasalt items: {sources_found}")

if __name__ == "__main__":
    unittest.main()
