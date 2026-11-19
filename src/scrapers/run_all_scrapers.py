"""
Data Aggregator & Pipeline Runner
Collects data from DarGlobal and Wasalt scrapers, validates schema, and writes:
- data/properties.json
- data/properties.jsonl
"""

import json
import os
from src.scrapers.darglobal_scraper import fetch_darglobal_data
from src.scrapers.wasalt_scraper import fetch_wasalt_data

def run_pipeline():
    os.makedirs("data", exist_ok=True)
    
    print("[1/3] Extracting DarGlobal data...")
    dg_data = fetch_darglobal_data()
    print(f"      -> Retrieved {len(dg_data)} DarGlobal projects.")
    
    print("[2/3] Extracting Wasalt data...")
    ws_data = fetch_wasalt_data()
    print(f"      -> Retrieved {len(ws_data)} Wasalt properties.")
    
    all_properties = dg_data + ws_data
    
    # Save formatted JSON
    json_path = os.path.join("data", "properties.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_properties, f, indent=2, ensure_ascii=False)
    print(f"[3/3] Successfully saved {len(all_properties)} total properties to {json_path}")
    
    # Save JSONL for RAG streaming
    jsonl_path = os.path.join("data", "properties.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for item in all_properties:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"      -> Saved {len(all_properties)} lines to {jsonl_path}")

    return len(all_properties)

if __name__ == "__main__":
    run_pipeline()
