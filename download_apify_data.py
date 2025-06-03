import requests
import os
from dotenv import load_dotenv
load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
DATASET_ID = os.getenv("DATASET_SLEEP_ID")

url = f"https://api.apify.com/v2/datasets/{DATASET_ID}/items?format=json"
headers = {"Authorization": f"Bearer {APIFY_TOKEN}"}

response = requests.get(url, headers=headers)
data = response.json()

output_path = "data/content_sleep.json"
with open(output_path, "w", encoding="utf-8") as f:
    import json
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Data saved to", output_path)
