"""
Production Real Estate AI Chatbot Server
Exposes REST API endpoints and serves the modern luxury frontend interface.
Built using standard library Python HTTP server for zero-dependency execution anywhere.
"""

import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Any

from src.rag.search_engine import HybridRealEstateRAG
from src.llm.openrouter_client import OpenRouterRealEstateAdvisor, OPENROUTER_FREE_MODELS

# Global Instances
rag_engine = HybridRealEstateRAG(data_path="data/properties.json")
advisor = OpenRouterRealEstateAdvisor()

class RealEstateRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Base directory for static files
        super().__init__(*args, directory="public", **kwargs)

    def _send_json(self, status: int, data: Dict[str, Any]):
        response_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            self._send_json(200, {
                "status": "healthy",
                "properties_indexed": len(rag_engine.properties),
                "openrouter_key_set": bool(advisor.api_key),
                "available_free_models": OPENROUTER_FREE_MODELS
            })
            return

        elif path == "/api/properties":
            query_params = urllib.parse.parse_qs(parsed.query)
            source_filter = query_params.get("source", [None])[0]
            country_filter = query_params.get("country", [None])[0]
            search_query = query_params.get("q", [None])[0]

            if search_query:
                results = rag_engine.search(search_query, top_k=20, source_filter=source_filter, country_filter=country_filter)
            else:
                results = rag_engine.properties
                if source_filter:
                    results = [p for p in results if p.get("source") == source_filter]
                if country_filter:
                    results = [p for p in results if p.get("country") == country_filter]

            self._send_json(200, {
                "count": len(results),
                "properties": results
            })
            return

        elif path == "/" or path == "/index.html":
            # Serve public/index.html
            self.path = "/index.html"
            return super().do_GET()

        else:
            # Fallback to static files
            return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON payload"})
            return

        if path == "/api/chat":
            user_message = data.get("message", "").strip()
            if not user_message:
                self._send_json(400, {"error": "Field 'message' is required."})
                return

            model = data.get("model")
            source_filter = data.get("source_filter")
            api_key_override = data.get("api_key")

            # Allow runtime key override from UI
            if api_key_override:
                advisor.set_api_key(api_key_override)

            # 1. RAG Search
            top_properties = rag_engine.search(user_message, top_k=4, source_filter=source_filter)

            # 2. OpenRouter Chat Completion
            reply, model_used, sources = advisor.chat(user_message, top_properties, model_override=model)

            self._send_json(200, {
                "reply": reply,
                "model_used": model_used,
                "sources": sources,
                "query": user_message
            })
            return

        elif path == "/api/config":
            new_key = data.get("api_key", "").strip()
            if new_key:
                advisor.set_api_key(new_key)
                self._send_json(200, {"status": "success", "message": "API key successfully updated."})
            else:
                self._send_json(400, {"error": "No API key provided."})
            return

        else:
            self._send_json(404, {"error": f"Endpoint {path} not found"})

def run_server(port: int = 8080):
    host = "0.0.0.0"
    server = HTTPServer((host, port), RealEstateRequestHandler)
    print(f"================================================================")
    print(f"🏢 DarGlobal & Wasalt Real Estate AI Chatbot Server")
    print(f"   Indexed Properties: {len(rag_engine.properties)}")
    print(f"   Listening on: http://localhost:{port}")
    print(f"   Health check: http://localhost:{port}/api/health")
    print(f"================================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
        server.server_close()

if __name__ == "__main__":
    port_env = int(os.environ.get("PORT", 8080))
    run_server(port=port_env)
