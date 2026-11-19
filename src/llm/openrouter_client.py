"""
OpenRouter Client for Free LLM Models with Multi-Turn Memory & Real-Time Streaming
Handles SSE streaming, conversation history, model failovers, and grounded offline synthesis.
"""

import os
import json
import time
import urllib.request
import urllib.error
from typing import List, Dict, Any, Tuple, Optional, Generator

def load_env(filepath: str = ".env"):
    """Lightweight zero-dependency .env loader."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

load_env()

# Curated list of verified active free models on OpenRouter, prioritized by lowest latency
OPENROUTER_FREE_MODELS = [
    "nvidia/nemotron-3.5-lightning:free",
    "inclusionai/ling-3.2-flash:free",
    "liquid/lfm-3-1.7b:free",
    "google/gemma-4-26b-a4b-it:free"
]

class OpenRouterRealEstateAdvisor:
    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "").strip()
        self.default_model = default_model or OPENROUTER_FREE_MODELS[0]

    def set_api_key(self, api_key: str):
        self.api_key = api_key.strip()

    def generate_grounded_fallback(self, query: str, properties: List[Dict[str, Any]]) -> str:
        """
        Grounded response generator used when API key is not yet configured.
        """
        if not properties:
            return (
                "### 🔍 No Specific Match Found\n\n"
                "I searched the DarGlobal and Wasalt portfolios, but didn't find properties matching those specific criteria.\n"
                "You can explore:\n"
                "- **DarGlobal International Luxury:** Branded villas and apartments in Dubai, Spain, Oman, and Qatar.\n"
                "- **Wasalt Saudi Properties:** Residential villas, apartments, and masterplans across Riyadh, Jeddah, and Al-Khobar."
            )

        lines = [
            "### 🏢 Curated Real Estate Recommendations\n",
            f"Based on your inquiry *\"{query}\"*, here are the top matching opportunities from the **DarGlobal** and **Wasalt** portfolios:\n"
        ]

        for idx, p in enumerate(properties, 1):
            source_badge = "🌟 **DarGlobal Luxury**" if p.get("source") == "DarGlobal" else "🇸🇦 **Wasalt Verified**"
            brand = f" (Brand Partner: *{p.get('brand_partner')}*)" if p.get('brand_partner') else ""
            lines.append(f"#### {idx}. [{p.get('title')}]({p.get('url')}) {brand}")
            lines.append(f"- **Developer / Source:** {source_badge}")
            lines.append(f"- **Location:** {p.get('location', p.get('city', ''))}")
            lines.append(f"- **Property Type:** {p.get('property_type')} | **Price:** `{p.get('price')}`")
            if p.get("specs"):
                specs_desc = ", ".join(f"{k.replace('_', ' ').title()}: {v}" for k, v in p["specs"].items())
                lines.append(f"- **Key Specs:** {specs_desc}")
            lines.append(f"- **Overview:** {p.get('description')}")
            if p.get("amenities"):
                lines.append(f"- **Highlights:** {', '.join(p['amenities'][:4])}")
            lines.append(f"- 🔗 **Official Listing:** [Explore Project Page]({p.get('url')})\n")

        lines.append(
            "\n> 💡 *Tip: Connect your free OpenRouter API key in the top bar to enable live generative inference with Nemotron / Gemma.*"
        )
        return "\n".join(lines)

    def _build_context_and_messages(
        self,
        query: str,
        retrieved_properties: List[Dict[str, Any]],
        history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, List[Dict[str, str]]]:
        context_blocks = []
        for p in retrieved_properties:
            amenities = ", ".join(p.get("amenities", []))
            block = (
                f"- Property: {p.get('title')}\n"
                f"  Source: {p.get('source')}\n"
                f"  Location: {p.get('location', '')}\n"
                f"  Type: {p.get('property_type')}\n"
                f"  Price: {p.get('price')}\n"
                f"  Brand / Developer: {p.get('brand_partner', p.get('developer', 'N/A'))}\n"
                f"  Description: {p.get('description')}\n"
                f"  Amenities: {amenities}\n"
                f"  URL: {p.get('url')}"
            )
            context_blocks.append(block)

        context_text = "\n\n".join(context_blocks)
        system_prompt = (
            "You are a dedicated AI Real Estate Consultant exclusively representing DarGlobal (international luxury "
            "branded residences in Dubai, Spain, Oman, Qatar, London) and Wasalt (Saudi Arabia's licensed real estate marketplace).\n\n"
            "STRICT DOMAIN GUARDRAILS:\n"
            "1. You ONLY answer inquiries regarding real estate, properties, villas, apartments, developers, pricing, locations, and architectural amenities.\n"
            "2. If the user asks about ANY unrelated topic (e.g. machine learning, research papers, coding, science, homework, general knowledge), "
            "you MUST POLITELY REFUSE and clarify that your expertise is strictly restricted to DarGlobal and Wasalt real estate inquiries.\n"
            "3. Be direct, crisp, and concise (under 150 words). Use bullet points for key property features.\n"
            "4. Always cite property names, exact prices, locations, and clickable markdown URLs.\n"
            "5. If the user asks follow-up questions, use the conversation context."
        )

        messages = [{"role": "system", "content": system_prompt}]

        # Inject conversation history for multi-turn conversational memory
        if history:
            for turn in history[-6:]:
                role = turn.get("role")
                content = turn.get("content", "")
                if role in ("user", "assistant") and content and content != query:
                    messages.append({"role": role, "content": content})

        user_content = f"Real Estate Context:\n{context_text}\n\nClient Inquiry: {query}"
        messages.append({"role": "user", "content": user_content})

        return system_prompt, messages

    def chat(
        self,
        query: str,
        retrieved_properties: List[Dict[str, Any]],
        model_override: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Generates response using OpenRouter free models with failover and conversation memory.
        """
        if not self.api_key:
            answer = self.generate_grounded_fallback(query, retrieved_properties)
            return answer, "RAG Knowledge Synthesizer (Offline Mode)", retrieved_properties

        _, messages = self._build_context_and_messages(query, retrieved_properties, history)

        models_to_try = [model_override] if model_override else []
        for m in OPENROUTER_FREE_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)

        last_error = None
        for model in models_to_try:
            try:
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 300,
                    "reasoning": {"max_tokens": 0}
                }

                req = urllib.request.Request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/darglobal-wasalt-ai",
                        "X-Title": "DarGlobal & Wasalt Real Estate AI"
                    }
                )

                with urllib.request.urlopen(req, timeout=20) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    msg_obj = res_data["choices"][0]["message"]
                    text = msg_obj.get("content") or msg_obj.get("reasoning") or ""
                    if text:
                        return text, model, retrieved_properties

            except urllib.error.HTTPError as e:
                err_msg = e.read().decode("utf-8", errors="ignore")
                last_error = f"HTTP {e.code}: {err_msg}"
                if e.code in (429, 502, 503, 504, 404):
                    continue
                else:
                    break
            except Exception as e:
                last_error = str(e)
                continue

        fallback = self.generate_grounded_fallback(query, retrieved_properties)
        diagnostic = f"\n\n*(Note: Live OpenRouter call encountered: {last_error}. Switched to local RAG fallback.)*"
        return fallback + diagnostic, "RAG Knowledge Synthesizer (Fallback)", retrieved_properties

    def chat_stream(
        self,
        query: str,
        retrieved_properties: List[Dict[str, Any]],
        model_override: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Server-Sent Events (SSE) streaming generator.
        Yields chunk dictionaries: {'token': '...', 'model': '...', 'done': bool, 'sources': [...]}
        """
        # Yield metadata first (sources)
        yield {
            "type": "meta",
            "sources": retrieved_properties,
            "model": model_override or self.default_model
        }

        if not self.api_key:
            # Yield offline synthesis word by word with micro-delay
            fallback = self.generate_grounded_fallback(query, retrieved_properties)
            words = fallback.split(" ")
            for w in words:
                yield {"type": "token", "token": w + " "}
                time.sleep(0.015)
            yield {"type": "done", "model": "RAG Knowledge Synthesizer (Offline)"}
            return

        _, messages = self._build_context_and_messages(query, retrieved_properties, history)
        models_to_try = [model_override] if model_override else []
        for m in OPENROUTER_FREE_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)

        for model in models_to_try:
            try:
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 300,
                    "reasoning": {"max_tokens": 0},
                    "stream": True
                }

                req = urllib.request.Request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/darglobal-wasalt-ai",
                        "X-Title": "DarGlobal & Wasalt Real Estate AI"
                    }
                )

                with urllib.request.urlopen(req, timeout=25) as response:
                    for line in response:
                        line_str = line.decode("utf-8").strip()
                        if not line_str or line_str.startswith(":"):
                            continue
                        if line_str.startswith("data: "):
                            data_content = line_str[6:].strip()
                            if data_content == "[DONE]":
                                break
                            try:
                                chunk_json = json.loads(data_content)
                                delta = chunk_json.get("choices", [{}])[0].get("delta", {})
                                token = delta.get("content", "")
                                if token:
                                    yield {"type": "token", "token": token, "model": model}
                            except Exception:
                                continue
                    yield {"type": "done", "model": model}
                    return

            except Exception as e:
                print(f"[Streaming Failover] Model {model} failed: {e}")
                continue

        # If streaming failed across all models, fallback
        fallback = self.generate_grounded_fallback(query, retrieved_properties)
        words = fallback.split(" ")
        for w in words:
            yield {"type": "token", "token": w + " "}
            time.sleep(0.01)
        yield {"type": "done", "model": "RAG Knowledge Synthesizer (Fallback)"}

if __name__ == "__main__":
    adv = OpenRouterRealEstateAdvisor()
    test_p = [{"title": "Tierra Viva", "source": "DarGlobal", "price": "EUR 9.2M", "location": "Spain", "description": "Lamborghini villa", "url": "https://darglobal.co.uk"}]
    print("Testing streaming token generator:")
    for chunk in adv.chat_stream("Hello, tell me about Tierra Viva", test_p):
        if chunk.get("type") == "token":
            print(chunk.get("token"), end="", flush=True)
    print("\n[Done Streaming Test]")
