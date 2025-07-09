# sync_apim_operations.py

import os
import subprocess

API_NAME = os.environ.get("APIM_API_NAME", "python-api")
RESOURCE_GROUP = os.environ.get("APIM_RESOURCE_GROUP", "rg-23-6")
SERVICE_NAME = os.environ.get("APIM_SERVICE_NAME", "python-api")
SUBSCRIPTION_ID = os.environ.get("APIM_SUBSCRIPTION_ID", "")
SERVICE_URL = os.environ.get("APIM_SWAGGER_URL", "")

def import_operation(file_path, api_id):
    print(f"📤 Importing {file_path} into APIM...")

    cmd = [
        "az", "apim", "api", "import",
        "--resource-group", RESOURCE_GROUP,
        "--service-name", SERVICE_NAME,
        "--api-id", api_id,
        "--path", api_id,
        "--specification-format", "OpenApiJson",
        "--specification-path", file_path,
        "--display-name", api_id,
        "--api-revision", "1",
        "--service-url", SERVICE_URL,
        "--subscription-required", "false"
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Imported {api_id}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to import {api_id}: {e}")
        exit(1)

def main():
    split_dir = "split"
    if not os.path.isdir(split_dir):
        print("❌ Directory 'split/' not found.")
        return

    for file in os.listdir(split_dir):
        if file.endswith(".json"):
            file_path = os.path.join(split_dir, file)
            api_id = os.path.splitext(file)[0]

            import_operation(file_path, api_id)

    print("✅ All APIs imported successfully.")

if __name__ == "__main__":
    main()
