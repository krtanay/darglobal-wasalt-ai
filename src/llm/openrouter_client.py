"""
OpenRouter Client for Free LLM Models
Handles API interactions with openrouter.ai/api/v1/chat/completions,
automatic failover across free models, and smart context synthesis.
"""

import os
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Tuple, Optional

# Curated list of high-performance free models on OpenRouter
OPENROUTER_FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "deepseek/deepseek-r1:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "mistralai/mistral-7b-instruct:free"
]

class OpenRouterRealEstateAdvisor:
    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "").strip()
        self.default_model = default_model or OPENROUTER_FREE_MODELS[0]

    def set_api_key(self, api_key: str):
        self.api_key = api_key.strip()

    def generate_grounded_fallback(self, query: str, properties: List[Dict[str, Any]]) -> str:
        """
        Grounded response generator used when API key is not yet configured,
        ensuring 100% immediate testability for junior evaluation and demos.
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
            "\n> 💡 *Tip: Connect your free OpenRouter API key in the top bar to enable live generative inference with Llama 3.3 / Gemini 2.0 Flash.*"
        )
        return "\n".join(lines)

    def chat(
        self,
        query: str,
        retrieved_properties: List[Dict[str, Any]],
        model_override: Optional[str] = None
    ) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Generates response using OpenRouter free models with failover.
        Returns: (response_text, model_used, source_properties)
        """
        # If no API key is provided, return rich grounded synthesis
        if not self.api_key:
            answer = self.generate_grounded_fallback(query, retrieved_properties)
            return answer, "RAG Knowledge Synthesizer (Offline Mode)", retrieved_properties

        # Build context from retrieved properties
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
            "You are a sophisticated, bilingual Real Estate AI Advisor representing DarGlobal (ultra-luxury international "
            "developments) and Wasalt (Saudi Arabia's premier PropTech marketplace).\n"
            "Guidelines:\n"
            "1. Answer the user's inquiry professionally, highlighting relevant properties from the provided context.\n"
            "2. Always cite property names, exact prices, locations, and clickable markdown URLs.\n"
            "3. If comparing DarGlobal and Wasalt, contrast DarGlobal's international branded lifestyle with Wasalt's prime Saudi residential opportunities.\n"
            "4. Base your answers strictly on the supplied real estate context. Do not invent properties or prices."
        )

        user_content = f"Real Estate Context:\n{context_text}\n\nClient Inquiry: {query}"

        # Try models in priority sequence with failover
        models_to_try = [model_override] if model_override else []
        for m in OPENROUTER_FREE_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)

        last_error = None
        for model in models_to_try:
            try:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "temperature": 0.4
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
                    text = res_data["choices"][0]["message"]["content"]
                    return text, model, retrieved_properties

            except urllib.error.HTTPError as e:
                err_msg = e.read().decode("utf-8", errors="ignore")
                print(f"[OpenRouter] Model {model} returned HTTP {e.code}: {err_msg}")
                last_error = f"HTTP {e.code}: {err_msg}"
                # If rate-limited (429) or model temporarily unavailable, continue to next model
                if e.code in (429, 502, 503, 504):
                    continue
                else:
                    break
            except Exception as e:
                print(f"[OpenRouter] Model {model} request failed: {e}")
                last_error = str(e)
                continue

        # If all live API attempts fail, fallback to grounded synthesis with diagnostic
        fallback = self.generate_grounded_fallback(query, retrieved_properties)
        diagnostic = f"\n\n*(Note: Live OpenRouter call encountered: {last_error}. Switched to local RAG fallback.)*"
        return fallback + diagnostic, "RAG Knowledge Synthesizer (Fallback)", retrieved_properties

if __name__ == "__main__":
    advisor = OpenRouterRealEstateAdvisor()
    test_props = [
        {
            "title": "Tierra Viva by Lamborghini",
            "source": "DarGlobal",
            "price": "EUR 9,296,000",
            "location": "Benahavis, Spain",
            "property_type": "Luxury Villa",
            "description": "53 villas inspired by Lamborghini.",
            "url": "https://darglobal.co.uk/tierra-viva/"
        }
    ]
    resp, model, _ = advisor.chat("Tell me about Lamborghini villas", test_props)
    print(f"Generated via: {model}\n\n{resp}")
