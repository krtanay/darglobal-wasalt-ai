"""
Real Estate RAG & Hybrid Search Engine with Reciprocal Rank Fusion (RRF)
Combines BM25 Lexical Retrieval + Dense Semantic Subword Cosine Similarity + Metadata Filtering.
Includes Conversational Query Expansion for Multi-Turn Dialogue.
"""

import json
import math
import re
from typing import List, Dict, Any, Optional

ENGLISH_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "cannot", "could", "did", "do", "does", "doing", "down", "during", "each",
    "few", "for", "from", "further", "had", "has", "have", "having", "he", "her", "here",
    "him", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself",
    "me", "more", "most", "my", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "our", "ours", "out", "over", "own", "same", "she", "should", "so",
    "some", "such", "than", "that", "the", "their", "theirs", "them", "then", "there",
    "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "with",
    "would", "you", "your", "yours", "need", "built", "using", "use", "uses", "mean", "tell",
    "give", "want", "like", "know", "model", "models", "ai", "bot", "assistant",
    "test", "testing", "sample", "check", "hello", "hi", "hey"
}

class HybridRealEstateRAG:
    def __init__(self, data_path: str = "data/properties.json"):
        self.data_path = data_path
        self.properties: List[Dict[str, Any]] = []
        self.documents: List[str] = []
        self.doc_tokens: List[List[str]] = []
        self.doc_ngrams: List[Dict[str, float]] = []  # Dense semantic vectors
        self.idf: Dict[str, float] = {}
        self.ngram_idf: Dict[str, float] = {}
        self.avg_dl: float = 0.0
        self.load_and_index()

    def tokenize(self, text: str, remove_stopwords: bool = True) -> List[str]:
        tokens = re.findall(r'\b[a-zA-Z0-9_\u0600-\u06FF\-]+\b', text.lower())
        valid = [t for t in tokens if len(t) > 1 or t.isdigit()]
        if remove_stopwords:
            return [t for t in valid if t not in ENGLISH_STOPWORDS]
        return valid

    def extract_ngrams(self, text: str, n_range=(3, 5)) -> List[str]:
        """Character n-grams for dense subword semantic representation."""
        clean = re.sub(r'\s+', ' ', text.lower().strip())
        ngrams = []
        words = clean.split(' ')
        for w in words:
            if len(w) < 3:
                ngrams.append(w)
                continue
            for n in range(n_range[0], min(len(w) + 1, n_range[1] + 1)):
                for i in range(len(w) - n + 1):
                    ngrams.append(w[i:i+n])
        return ngrams

    def load_and_index(self):
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.properties = json.load(f)
        except Exception as e:
            print(f"[RAG Engine] Warning loading {self.data_path}: {e}")
            self.properties = []

        self.documents = []
        self.doc_tokens = []
        self.doc_ngrams = []
        doc_freq: Dict[str, int] = {}
        ngram_freq: Dict[str, int] = {}

        for prop in self.properties:
            amenities_str = ", ".join(prop.get("amenities", []))
            doc_text = (
                f"Source: {prop.get('source')} | Title: {prop.get('title')} | "
                f"Location: {prop.get('location')} {prop.get('city')} {prop.get('country')} | "
                f"Brand Partner: {prop.get('brand_partner', prop.get('developer', ''))} | "
                f"Type: {prop.get('property_type')} | Price: {prop.get('price')} | "
                f"Description: {prop.get('description')} | Amenities: {amenities_str}"
            )
            self.documents.append(doc_text)
            
            # 1. Lexical Tokens
            tokens = self.tokenize(doc_text)
            self.doc_tokens.append(tokens)
            for token in set(tokens):
                doc_freq[token] = doc_freq.get(token, 0) + 1

            # 2. Semantic N-grams
            ngrams = self.extract_ngrams(doc_text)
            ngram_counts: Dict[str, float] = {}
            for ng in ngrams:
                ngram_counts[ng] = ngram_counts.get(ng, 0.0) + 1.0
            
            # Norm vector
            mag = math.sqrt(sum(v*v for v in ngram_counts.values())) or 1.0
            norm_vector = {k: v / mag for k, v in ngram_counts.items()}
            self.doc_ngrams.append(norm_vector)

            for ng in set(ngrams):
                ngram_freq[ng] = ngram_freq.get(ng, 0) + 1

        num_docs = len(self.properties)
        if num_docs > 0:
            total_tokens = sum(len(doc) for doc in self.doc_tokens)
            self.avg_dl = total_tokens / num_docs
            for token, freq in doc_freq.items():
                self.idf[token] = math.log((num_docs - freq + 0.5) / (freq + 0.5) + 1.0)
            for ng, freq in ngram_freq.items():
                self.ngram_idf[ng] = math.log((num_docs + 1) / (freq + 1)) + 1.0

    def reformulate_query(self, query: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Context-aware query reformulation for multi-turn conversational follow-ups.
        Resolves pronouns ('it', 'this villa', 'its price', 'how many beds does that have').
        """
        if not history or len(history) < 2:
            return query

        q_lower = query.lower()
        pronoun_triggers = ["it", "its", "this", "that", "the villa", "the apartment", "they", "there", "them", "cost", "price", "amenities", "elevator", "pool"]
        is_followup = any(re.search(r'\b' + re.escape(p) + r'\b', q_lower) for p in pronoun_triggers) or len(query.split()) <= 4

        if is_followup:
            # Extract property title or brand from previous assistant message
            for msg in reversed(history):
                if msg.get("role") == "assistant":
                    content = msg.get("content", "")
                    # Match known property titles
                    for p in self.properties:
                        title = p.get("title", "")
                        brand = p.get("brand_partner", "")
                        if title.lower() in content.lower():
                            return f"{query} {title}"
                        elif brand and brand.lower() in content.lower():
                            return f"{query} {brand}"
                    break
        return query

    def search(
        self,
        query: str,
        top_k: int = 3,
        source_filter: Optional[str] = None,
        country_filter: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid Search combining BM25 and Dense Semantic Cosine Similarity via Reciprocal Rank Fusion (RRF).
        """
        if not self.properties:
            return []

        # Step 1: Conversational query expansion
        enriched_query = self.reformulate_query(query, history)
        query_tokens = self.tokenize(enriched_query)
        q_lower = enriched_query.lower()

        broad_triggers = ["all", "browse", "list", "properties", "catalog", "portfolio", "recommend", "show me", "available", "explore"]
        is_broad_query = any(bt in q_lower for bt in broad_triggers)

        if not query_tokens:
            if is_broad_query:
                return self.properties[:top_k]
            # Queries with no real estate tokens (e.g. meta or off-topic questions)
            return []
        if not source_filter:
            if "darglobal" in q_lower or "dar global" in q_lower or "international" in q_lower:
                source_filter = "DarGlobal"
            elif "wasalt" in q_lower or "saudi" in q_lower or "riyadh" in q_lower or "jeddah" in q_lower:
                if "darglobal" not in q_lower:
                    source_filter = "Wasalt"

        # --- A. BM25 Lexical Ranking ---
        bm25_scores = []
        k1, b = 1.5, 0.75
        for idx, prop in enumerate(self.properties):
            if source_filter and prop.get("source", "").lower() != source_filter.lower():
                if "compare" not in q_lower:
                    continue
            if country_filter and prop.get("country", "").lower() != country_filter.lower():
                continue

            doc_tokens = self.doc_tokens[idx]
            doc_len = len(doc_tokens)
            score = 0.0

            tf_dict: Dict[str, int] = {}
            for t in doc_tokens:
                tf_dict[t] = tf_dict.get(t, 0) + 1

            for token in query_tokens:
                if token in tf_dict:
                    tf = tf_dict[token]
                    idf_val = self.idf.get(token, 0.5)
                    num = tf * (k1 + 1)
                    denom = tf + k1 * (1 - b + b * (doc_len / (self.avg_dl or 1)))
                    score += idf_val * (num / denom)

            # Metadata exact word token match boost (avoid substring false positives like 'ai' in 'spain')
            title_words = set(self.tokenize(prop.get("title", ""), remove_stopwords=False))
            city_words = set(self.tokenize(prop.get("city", ""), remove_stopwords=False))
            country_words = set(self.tokenize(prop.get("country", ""), remove_stopwords=False))
            brand_words = set(self.tokenize(prop.get("brand_partner", "") or "", remove_stopwords=False))
            for token in query_tokens:
                if token in title_words:
                    score += 2.5
                if token in city_words or token in country_words:
                    score += 1.5
                if token in brand_words:
                    score += 2.0

            bm25_scores.append((idx, score))

        bm25_scores.sort(key=lambda x: x[1], reverse=True)
        bm25_ranks = {item[0]: rank + 1 for rank, item in enumerate(bm25_scores)}

        # --- B. Dense Semantic Vector Similarity ---
        query_ngrams = self.extract_ngrams(enriched_query)
        q_vec: Dict[str, float] = {}
        for ng in query_ngrams:
            idf_weight = self.ngram_idf.get(ng, 1.0)
            q_vec[ng] = q_vec.get(ng, 0.0) + idf_weight
        q_mag = math.sqrt(sum(v*v for v in q_vec.values())) or 1.0
        q_norm = {k: v / q_mag for k, v in q_vec.items()}

        semantic_scores = []
        for idx, prop in enumerate(self.properties):
            if idx not in bm25_ranks:
                continue
            doc_vec = self.doc_ngrams[idx]
            # Cosine similarity
            cos_sim = sum(val * doc_vec.get(ng, 0.0) for ng, val in q_norm.items())
            semantic_scores.append((idx, cos_sim))

        semantic_scores.sort(key=lambda x: x[1], reverse=True)
        semantic_ranks = {item[0]: rank + 1 for rank, item in enumerate(semantic_scores)}

        # Check relevance: if neither BM25 nor semantic match detected anything, it's out-of-domain
        max_bm25 = max((s[1] for s in bm25_scores), default=0.0)
        max_semantic = max((s[1] for s in semantic_scores), default=0.0)

        # Broad browse keywords that should return properties even without specific filters
        broad_triggers = ["all", "browse", "list", "properties", "catalog", "portfolio", "recommend", "show me", "available"]
        is_broad_query = any(bt in q_lower for bt in broad_triggers)

        if max_bm25 <= 0.0 and max_semantic < 0.18 and not is_broad_query:
            # Query is completely unrelated to real estate (e.g. greetings, testing, meta, off-topic)
            return []

        # Reciprocal Rank Fusion (RRF)
        rrf_constant = 60.0
        fused_scores = []
        for idx in bm25_ranks:
            r_bm25 = bm25_ranks[idx]
            r_dense = semantic_ranks.get(idx, len(self.properties))
            rrf_score = (1.0 / (rrf_constant + r_bm25)) + (1.0 / (rrf_constant + r_dense))
            fused_scores.append((rrf_score, self.properties[idx]))

        fused_scores.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in fused_scores[:top_k]]
        return results

if __name__ == "__main__":
    rag = HybridRealEstateRAG()
    print("Testing Multi-Turn Follow-Up Query:")
    mock_history = [
        {"role": "user", "content": "Tell me about Lamborghini villas"},
        {"role": "assistant", "content": "Tierra Viva by Automobili Lamborghini in Benahavis Spain is an ultra-luxury development."}
    ]
    expanded = rag.reformulate_query("How much does it cost and how many bedrooms?", mock_history)
    print(f" -> Reformulated Query: '{expanded}'")
    hits = rag.search(expanded, top_k=1)
    print(f" -> Result: [{hits[0]['source']}] {hits[0]['title']} ({hits[0]['price']})")
