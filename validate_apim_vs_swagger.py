# scripts/validate_apim_vs_swagger.py

from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
import os

SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")
SERVICE_NAME = os.getenv("APIM_SERVICE_NAME")
API_ID = os.getenv("API_ID")  # APIM API being synced

def get_existing_operations():
    client = ApiManagementClient(DefaultAzureCredential(), SUBSCRIPTION_ID)
    ops = client.api_operation.list_by_api(RESOURCE_GROUP, SERVICE_NAME, API_ID)
    return {op.name: op for op in ops}

def get_local_operations(split_dir="swagger/split"):
    return {
        f.stem for f in Path(split_dir).glob("*.json")
    }

def main():
    remote_ops = get_existing_operations()
    local_ops = get_local_operations()

    stale_ops = set(remote_ops.keys()) - local_ops
    if stale_ops:
        print(f"Stale operations in APIM: {stale_ops}")
        # Optional: delete them here or in a separate script

if __name__ == "__main__":
    from pathlib import Path
    main()
