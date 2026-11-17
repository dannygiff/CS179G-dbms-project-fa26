import json
import ijson
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2]/"data"
INPUT_PATH = DATA_DIR / "data_v3_recent.json"
OUTPUT_PATH = DATA_DIR / "data_v3_recent.jsonl"

review_count = 0

with open(INPUT_PATH, "rb") as infile, open(OUTPUT_PATH, "w") as outfile:
    for game in ijson.items(infile, "item", use_float=True):
        app_id = game["app_id"]

        for review in game.get("response", []):
            review["app_id"] = app_id
            # ensure_ascii writes the emoji characters as themselves
            outfile.write(json.dumps(review, ensure_ascii=False) + "\n")
            review_count += 1

print(f"Wrote {review_count} reviews to {OUTPUT_PATH}")