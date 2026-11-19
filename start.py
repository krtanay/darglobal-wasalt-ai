"""
Quick Start Entrypoint for DarGlobal & Wasalt Real Estate AI
"""

import os
import sys

def main():
    print("=================================================================")
    print("🏢 Starting DarGlobal & Wasalt Real Estate AI Advisor")
    print("=================================================================")
    # Ensure data exists, if not run scrapers
    if not os.path.exists("data/properties.json"):
        print("[Notice] Pre-indexed data not found, running scrapers pipeline...")
        from src.scrapers.run_all_scrapers import run_pipeline
        run_pipeline()

    # Run the server
    from src.server import run_server
    port = int(os.environ.get("PORT", 8080))
    run_server(port=port)

if __name__ == "__main__":
    main()
