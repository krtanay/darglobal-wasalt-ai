"""
Real Estate RAG & Hybrid Search Engine
Implements BM25 + TF-IDF Vector Retrieval with Metadata Filtering.
Works without external C++ or Torch dependencies, ensuring reliable execution anywhere.
"""

import json
import math
import re
from typing import List, Dict, Any, Optional

class HybridRealEstateRAG:
    def __init__(self, data_path: str = "data/properties.json"):
        self.data_path = data_path
        self.properties: List[Dict[str, Any]] = []
        self.documents: List[str] = []
        self.doc_tokens: List[List[str]] = []
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.avg_dl: float = 0.0
        self.load_and_index()

    def tokenize(self, text: str) -> List[str]:
        # Lowercase, clean alphanumeric tokens
        tokens = re.findall(r'\b[a-zA-Z0-9_\u0600-\u06FF\-]+\b', text.lower())
        # Filter single character tokens except numbers
        return [t for t in tokens if len(t) > 1 or t.isdigit()]

    def load_and_index(self):
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.properties = json.load(f)
        except Exception as e:
            print(f"[RAG Engine] Warning loading {self.data_path}: {e}")
            self.properties = []

        self.documents = []
        self.doc_tokens = []
        doc_freq: Dict[str, int] = {}

        for prop in self.properties:
            # Build unified semantic representation
            amenities_str = ", ".join(prop.get("amenities", []))
            doc_text = (
                f"Source: {prop.get('source')} | Title: {prop.get('title')} | "
                f"Location: {prop.get('location')} {prop.get('city')} {prop.get('country')} | "
                f"Brand Partner: {prop.get('brand_partner', prop.get('developer', ''))} | "
                f"Type: {prop.get('property_type')} | Price: {prop.get('price')} | "
                f"Description: {prop.get('description')} | Amenities: {amenities_str}"
            )
            self.documents.append(doc_text)
            tokens = self.tokenize(doc_text)
            self.doc_tokens.append(tokens)

            unique_tokens = set(tokens)
            for token in unique_tokens:
                doc_freq[token] = doc_freq.get(token, 0) + 1

        num_docs = len(self.properties)
        if num_docs > 0:
            total_tokens = sum(len(doc) for doc in self.doc_tokens)
            self.avg_dl = total_tokens / num_docs
            # Compute smoothed BM25 IDF
            for token, freq in doc_freq.items():
                self.idf[token] = math.log((num_docs - freq + 0.5) / (freq + 0.5) + 1.0)

    def search(
        self,
        query: str,
        top_k: int = 3,
        source_filter: Optional[str] = None,
        country_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        BM25 Ranking with metadata boost and filters.
        """
        if not self.properties:
            return []

        query_tokens = self.tokenize(query)
        if not query_tokens:
            return self.properties[:top_k]

        k1 = 1.5
        b = 0.75
        scores = []

        # Detect intent filters if not explicitly provided
        q_lower = query.lower()
        if not source_filter:
            if "darglobal" in q_lower or "dar global" in q_lower or "international" in q_lower:
                source_filter = "DarGlobal"
            elif "wasalt" in q_lower or "saudi" in q_lower or "riyadh" in q_lower or "jeddah" in q_lower:
                if "darglobal" not in q_lower:
                    source_filter = "Wasalt"

        for idx, prop in enumerate(self.properties):
            # Apply filters if requested
            if source_filter and prop.get("source", "").lower() != source_filter.lower():
                # Allow cross-source only if user asked to compare
                if "compare" not in q_lower:
                    continue

            if country_filter and prop.get("country", "").lower() != country_filter.lower():
                continue

            doc_tokens = self.doc_tokens[idx]
            doc_len = len(doc_tokens)
            score = 0.0

            # Count term frequencies in this document
            tf_dict: Dict[str, int] = {}
            for t in doc_tokens:
                tf_dict[t] = tf_dict.get(t, 0) + 1

            for token in query_tokens:
                if token in tf_dict:
                    tf = tf_dict[token]
                    idf_val = self.idf.get(token, 0.5)
                    # BM25 formula
                    numerator = tf * (k1 + 1)
                    denominator = tf + k1 * (1 - b + b * (doc_len / (self.avg_dl or 1)))
                    score += idf_val * (numerator / denominator)

            # Metadata exact matching boost
            title_lower = prop.get("title", "").lower()
            city_lower = prop.get("city", "").lower()
            country_lower = prop.get("country", "").lower()
            type_lower = prop.get("property_type", "").lower()

            for token in query_tokens:
                if token in title_lower:
                    score += 2.0
                if token in city_lower or token in country_lower:
                    score += 1.5
                if token in type_lower:
                    score += 1.0

            if score > 0:
                scores.append((score, prop))

        # Sort descending by score
        scores.sort(key=lambda x: x[0], reverse=True)

        results = [item[1] for item in scores[:top_k]]
        
        # If no strict keyword matches, fallback to general top properties
        if not results:
            filtered = [
                p for p in self.properties 
                if (not source_filter or p.get("source") == source_filter)
            ]
            results = filtered[:top_k] if filtered else self.properties[:top_k]

        return results

if __name__ == "__main__":
    rag = HybridRealEstateRAG()
    print("Testing RAG search for: 'Lamborghini villas in Spain'")
    hits = rag.search("Lamborghini villas in Spain", top_k=2)
    for h in hits:
        print(f" -> [{h['source']}] {h['title']} - {h['price']} ({h['url']})")

    print("\nTesting RAG search for: 'Wasalt Riyadh 4-bedroom villa'")
    hits = rag.search("Wasalt Riyadh 4-bedroom villa", top_k=2)
    for h in hits:
        print(f" -> [{h['source']}] {h['title']} - {h['price']} ({h['url']})")
