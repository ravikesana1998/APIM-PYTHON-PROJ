# sync_apim_operations.py with Option 1: Delete if Exists

import os
import subprocess

API_NAME = os.environ.get("APIM_API_NAME", "python-api")
RESOURCE_GROUP = os.environ.get("APIM_RESOURCE_GROUP", "rg-23-6")
SERVICE_NAME = os.environ.get("APIM_SERVICE_NAME", "python-api")
SUBSCRIPTION_ID = os.environ.get("APIM_SUBSCRIPTION_ID", "85b61d1d-92dd-4311-90eb-4f3e1263adca")
SERVICE_URL = os.environ.get("APIM_SERVICE_URL", "https://pythonapps-e0hmd6eucuf9acg5.canadacentral-01.azurewebsites.net")


def delete_api_if_exists(api_id):
    print(f"🗑 Checking if API '{api_id}' exists...")
    check_cmd = [
        "az", "apim", "api", "show",
        "--resource-group", RESOURCE_GROUP,
        "--service-name", SERVICE_NAME,
        "--api-id", api_id
    ]
    result = subprocess.run(check_cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"⚠️ API '{api_id}' exists. Deleting...")
        delete_cmd = [
            "az", "apim", "api", "delete",
            "--resource-group", RESOURCE_GROUP,
            "--service-name", SERVICE_NAME,
            "--api-id", api_id,
            "--yes"
        ]
        subprocess.run(delete_cmd, check=True)
        print(f"✅ Deleted API '{api_id}'")
    else:
        print(f"✅ API '{api_id}' does not exist. Skipping delete.")


def import_operation(file_path, api_id):
    cmd = [
        "az", "apim", "api", "import",
        "--resource-group", RESOURCE_GROUP,
        "--service-name", SERVICE_NAME,
        "--api-id", api_id,
        "--path", api_id,
        "--specification-format", "OpenApiJson",
        "--specification-path", file_path,
        "--subscription-id", SUBSCRIPTION_ID,
        "--display-name", api_id,
        "--api-revision", "1",
        "--service-url", SERVICE_URL,
        "--subscription-required", "false"
    ]
    subprocess.run(cmd, check=True)


def main():
    split_dir = "split"
    if not os.path.exists(split_dir):
        print("❌ 'split/' directory not found. Run split_swagger_by_method.py first.")
        return

    for file in os.listdir(split_dir):
        if file.endswith(".json"):
            api_id = os.path.splitext(file)[0]
            file_path = os.path.join(split_dir, file)
            print(f"📤 Importing {file} into APIM...")
            delete_api_if_exists(api_id)
            import_operation(file_path, api_id)

    print("✅ All operations synced to APIM.")


if __name__ == "__main__":
    main()
