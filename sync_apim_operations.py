import os
import json
import subprocess
from pathlib import Path

# --- Configuration ---
SWAGGER_URL = "https://pythonapps-e0hmd6eucuf9acg5.canadacentral-01.azurewebsites.net/swagger/v1/swagger.json"
SWAGGER_FILE = "swagger.json"
SPLIT_DIR = "split"

# Environment-based APIM Config
API_NAME = os.environ.get("APIM_API_NAME", "python-api")
RESOURCE_GROUP = os.environ.get("APIM_RESOURCE_GROUP", "rg-23-6")
SERVICE_NAME = os.environ.get("APIM_SERVICE_NAME", "python-api")
SUBSCRIPTION_ID = os.environ.get("APIM_SUBSCRIPTION_ID", "85b61d1d-92dd-4311-90eb-4f3e1263adca")

# --- Utility Functions ---
def sanitize_filename(path, method):
    return f"{method.upper()}_{path.strip('/').replace('/', '_').replace('{','').replace('}','')}"

def download_swagger():
    print(f"🔽 Downloading Swagger from: {SWAGGER_URL}")
    result = subprocess.run(["curl", "-sSL", SWAGGER_URL, "-o", SWAGGER_FILE])
    if result.returncode != 0 or not Path(SWAGGER_FILE).exists():
        raise RuntimeError("❌ Failed to download Swagger file.")
    print(f"✔ Swagger downloaded to {SWAGGER_FILE}")

def split_swagger():
    print("✂️ Splitting Swagger into per-operation files...")
    with open(SWAGGER_FILE, "r") as f:
        swagger = json.load(f)

    os.makedirs(SPLIT_DIR, exist_ok=True)
    count = 0

    for path, methods in swagger.get("paths", {}).items():
        for method, operation in methods.items():
            new_spec = {
                "openapi": swagger.get("openapi", "3.0.0"),
                "info": swagger.get("info", {}),
                "servers": swagger.get("servers", []),
                "paths": {path: {method: operation}},
                "components": swagger.get("components", {})
            }
            filename = sanitize_filename(path, method) + ".json"
            out_path = Path(SPLIT_DIR) / filename
            with open(out_path, "w") as out_file:
                json.dump(new_spec, out_file, indent=2)
            print(f"📄 Created: {out_path}")
            count += 1

    if count == 0:
        raise RuntimeError("❌ No paths found in swagger.json!")
    print(f"✅ Split complete: {count} files created.")

def import_to_apim():
    print("☁️ Importing each operation into Azure API Management...")
    for file in Path(SPLIT_DIR).glob("*.json"):
        api_id = file.stem
        print(f"📤 Importing: {api_id}")

        cmd = [
            "az", "apim", "api", "import",
            "--resource-group", RESOURCE_GROUP,
            "--service-name", SERVICE_NAME,
            "--api-id", api_id,
            "--path", api_id,
            "--specification-format", "OpenApiJson",
            "--specification-path", str(file),
            "--api-revision", "1",
            "--display-name", api_id,
            "--subscription-required", "false",
            "--service-url", SWAGGER_URL,
            "--subscription-id", SUBSCRIPTION_ID,
            "--overwrite", "true"  # Overwrite if exists
        ]

        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"❌ Failed to import {api_id}")
            continue

    print("✅ All APIs imported successfully.")

# --- Run Script ---
if __name__ == "__main__":
    try:
        download_swagger()
        split_swagger()
        import_to_apim()
    except Exception as e:
        print(f"💥 Error: {e}")
        exit(1)
