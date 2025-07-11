import os
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient

# Required env vars
SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
RESOURCE_GROUP = os.environ["AZURE_RESOURCE_GROUP"]
SERVICE_NAME = os.environ["AZURE_APIM_NAME"]
API_ID = os.environ["AZURE_APIM_API_ID"]
SPLIT_DIR = "split"

credential = DefaultAzureCredential()
client = ApiManagementClient(credential, SUBSCRIPTION_ID)

def get_apim_operation_ids():
    """Fetch operationIds from APIM."""
    op_ids = set()
    pager = client.api_operation.list_by_api(RESOURCE_GROUP, SERVICE_NAME, API_ID)
    for op in pager:
        op_ids.add(op.name)
    return op_ids

def get_local_operation_ids():
    """Read operationIds from split/<tag>/*.json files."""
    op_ids = set()
    for root, _, files in os.walk(SPLIT_DIR):
        for f in files:
            if f.endswith(".json"):
                path = os.path.join(root, f)
                with open(path, "r") as j:
                    data = json.load(j)
                    if "operationId" in data:
                        op_ids.add(data["operationId"])
    return op_ids

def main():
    print("🔍 Validating APIM operations against Swagger...")
    apim_ops = get_apim_operation_ids()
    swagger_ops = get_local_operation_ids()

    extra_in_apim = apim_ops - swagger_ops
    missing_in_apim = swagger_ops - apim_ops

    print(f"✅ Total in Swagger: {len(swagger_ops)}")
    print(f"✅ Total in APIM: {len(apim_ops)}")

    print(f"\n📌 In Swagger but NOT in APIM: {len(missing_in_apim)}")
    for op in sorted(missing_in_apim):
        print(f"➕ {op}")

    print(f"\n📌 In APIM but NOT in Swagger: {len(extra_in_apim)}")
    for op in sorted(extra_in_apim):
        print(f"➖ {op}")

if __name__ == "__main__":
    main()
