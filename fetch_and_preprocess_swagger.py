# scripts/fetch_and_preprocess_swagger.py

import requests
import json
import os
from pathlib import Path

SWAGGER_URL = os.getenv("SWAGGER_URL")  # e.g. https://myapp.azurewebsites.net/swagger/v1/swagger.json
OUTPUT_PATH = "swagger/processed_swagger.json"

def fetch_swagger(url):
    print(f"Fetching Swagger from {url}...")
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def ensure_operation_ids(swagger):
    """Ensure every operation has a unique operationId."""
    for path, methods in swagger.get("paths", {}).items():
        for method, details in methods.items():
            if not details.get("operationId"):
                # Create operationId from method and path
                operation_id = f"{method}_{path.strip('/').replace('/', '_')}".replace('{', '').replace('}', '')
                details["operationId"] = operation_id
    return swagger

def main():
    swagger = fetch_swagger(SWAGGER_URL)
    swagger = ensure_operation_ids(swagger)

    Path("swagger").mkdir(exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(swagger, f, indent=2)
    print(f"Processed Swagger written to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
