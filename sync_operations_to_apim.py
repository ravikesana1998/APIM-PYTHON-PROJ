# scripts/sync_operations_to_apim.py

from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
import os, json
from pathlib import Path

SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")
SERVICE_NAME = os.getenv("APIM_SERVICE_NAME")
API_ID = os.getenv("API_ID")

def sync_operation(file_path):
    op_spec = json.load(open(file_path))
    path = next(iter(op_spec["paths"]))
    method = next(iter(op_spec["paths"][path]))
    operation = op_spec["paths"][path][method]
    operation_id = operation["operationId"]

    print(f"Syncing {operation_id}...")

    client = ApiManagementClient(DefaultAzureCredential(), SUBSCRIPTION_ID)
    client.api_operation.create_or_update(
        resource_group_name=RESOURCE_GROUP,
        service_name=SERVICE_NAME,
        api_id=API_ID,
        operation_id=operation_id,
        parameters={
            "display_name": operation.get("summary", operation_id),
            "method": method.upper(),
            "url_template": path,
            "request": {},
            "responses": {
                "200": {
                    "description": "Success"
                }
            }
        }
    )

def main():
    split_dir = Path("swagger/split")
    for file_path in split_dir.glob("*.json"):
        sync_operation(file_path)

if __name__ == "__main__":
    main()
