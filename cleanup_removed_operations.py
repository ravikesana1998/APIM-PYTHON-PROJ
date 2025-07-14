
import os
import json
import glob
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
from azure.core.exceptions import ResourceNotFoundError

# ENV
SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
RESOURCE_GROUP = os.environ["AZURE_RESOURCE_GROUP"]
APIM_NAME = os.environ["AZURE_APIM_NAME"]
API_ID = os.environ["AZURE_APIM_API_ID"]

credential = DefaultAzureCredential()
client = ApiManagementClient(credential, SUBSCRIPTION_ID)

def get_apim_operations():
    try:
        pager = client.api_operation.list_by_api(RESOURCE_GROUP, APIM_NAME, API_ID)
        return [op.name for op in pager]
    except ResourceNotFoundError:
        print("⚠️ API not found in APIM.")
        return []

def get_swagger_operation_ids():
    files = glob.glob("split/**/*.json", recursive=True)
    ids = []
    for file in files:
        with open(file) as f:
            data = json.load(f)
            if "operationId" in data:
                ids.append(data["operationId"])
    return ids

def delete_apim_operation(op_id):
    try:
        client.api_operation.delete(RESOURCE_GROUP, APIM_NAME, API_ID, op_id, if_match="*")
        print(f"🗑️ Deleted stale operation: {op_id}")
    except Exception as e:
        print(f"❌ Failed to delete {op_id}: {e}")

def main():
    print("🧹 Removing stale APIM operations...")
    apim_ops = get_apim_operations()
    swagger_ops = get_swagger_operation_ids()

    stale_ops = [op for op in apim_ops if op not in swagger_ops]
    if not stale_ops:
        print("✅ No stale operations to delete.")
        return

    for op_id in stale_ops:
        delete_apim_operation(op_id)

if __name__ == "__main__":
    main()
