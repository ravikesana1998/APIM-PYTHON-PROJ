# sync_apim_operations.py

import os
import subprocess
import json

API_NAME = os.environ.get("APIM_API_NAME", "python-api")
RESOURCE_GROUP = os.environ.get("APIM_RESOURCE_GROUP", "rg-23-6")
SERVICE_NAME = os.environ.get("APIM_SERVICE_NAME", "python-api")
SUBSCRIPTION_ID = os.environ.get("APIM_SUBSCRIPTION_ID", "85b61d1d-92dd-4311-90eb-4f3e1263adca")

def import_operation(file_path):
    cmd = [
        "az", "apim", "api", "import",
        "--resource-group", RESOURCE_GROUP,
        "--service-name", SERVICE_NAME,
        "--api-id", API_NAME,
        "--path", API_NAME,
        "--specification-format", "OpenApiJson",
        "--specification-path", file_path,
        "--subscription-id", SUBSCRIPTION_ID,
        "--api-revision", "1",
        "--display-name", os.path.splitext(os.path.basename(file_path))[0]
    ]
    subprocess.run(cmd, check=True)

def main():
    split_dir = "split"
    if not os.path.exists(split_dir):
        print("❌ 'split/' directory not found. Run split_swagger_by_method.py first.")
        return

    for file in os.listdir(split_dir):
        if file.endswith(".json"):
            full_path = os.path.join(split_dir, file)
            print(f"📤 Importing {file} into APIM...")
            import_operation(full_path)

    print("✅ All operations synced to APIM.")

if __name__ == "__main__":
    main()
