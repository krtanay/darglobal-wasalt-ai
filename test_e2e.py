"""
Automated End-to-End Test Suite for DarGlobal & Wasalt Real Estate AI
Tests server endpoints, RAG retrieval accuracy, and response generation.
"""

import threading
import time
import urllib.request
import json
import sys

from src.server import run_server

def run_tests():
    port = 8765
    server_thread = threading.Thread(target=run_server, kwargs={"port": port}, daemon=True)
    server_thread.start()
    time.sleep(1.5)  # Wait for server to bind

    base_url = f"http://127.0.0.1:{port}"
    print(f"[TEST] Probing server at {base_url}...")

    # Test 1: Health Check
    with urllib.request.urlopen(f"{base_url}/api/health", timeout=5) as res:
        assert res.status == 200, f"Expected 200, got {res.status}"
        data = json.loads(res.read().decode())
        print(f"[TEST 1 PASS] Health: status={data.get('status')}, properties={data.get('properties_indexed')}")
        assert data.get("properties_indexed", 0) >= 20, "Expected at least 20 properties indexed"

    # Test 2: Properties Catalog Endpoint
    with urllib.request.urlopen(f"{base_url}/api/properties", timeout=5) as res:
        assert res.status == 200
        data = json.loads(res.read().decode())
        print(f"[TEST 2 PASS] Properties Catalog: retrieved {data.get('count')} listings")

    # Test 3: Chat Query - DarGlobal Lamborghini Villa
    query_payload = json.dumps({
        "message": "Tell me about the Lamborghini villas in Spain by DarGlobal",
        "source_filter": "DarGlobal"
    }).encode()
    req = urllib.request.Request(
        f"{base_url}/api/chat",
        data=query_payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as res:
        assert res.status == 200
        data = json.loads(res.read().decode())
        print(f"[TEST 3 PASS] Chat (DarGlobal): model={data.get('model_used')}, sources={len(data.get('sources', []))}")
        assert len(data.get("sources", [])) > 0, "Expected matching sources for Lamborghini query"
        first_source = data["sources"][0]
        assert "Tierra Viva" in first_source["title"] or "Lamborghini" in first_source["title"]

    # Test 4: Chat Query - Wasalt Riyadh Villa
    query_payload2 = json.dumps({
        "message": "I want a luxury villa in Riyadh under 4 million SAR on Wasalt",
        "source_filter": "Wasalt"
    }).encode()
    req2 = urllib.request.Request(
        f"{base_url}/api/chat",
        data=query_payload2,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req2, timeout=5) as res:
        assert res.status == 200
        data = json.loads(res.read().decode())
        print(f"[TEST 4 PASS] Chat (Wasalt): model={data.get('model_used')}, sources={len(data.get('sources', []))}")
        assert len(data.get("sources", [])) > 0, "Expected matching sources for Wasalt query"
        assert any(s["source"] == "Wasalt" for s in data["sources"])

    # Test 5: Static Index HTML
    with urllib.request.urlopen(f"{base_url}/", timeout=5) as res:
        assert res.status == 200
        html = res.read().decode()
        assert "DarGlobal" in html and "Wasalt" in html
        print("[TEST 5 PASS] Frontend: index.html served successfully with branding")

    print("\n=======================================================")
    print(" ALL 5 END-TO-END TESTS PASSED SUCCESSFULLY!")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
