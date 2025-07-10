import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient

SUBSCRIPTION_ID = os.environ["APIM_SUBSCRIPTION_ID"]
RESOURCE_GROUP = os.environ["APIM_RESOURCE_GROUP"]
SERVICE_NAME = os.environ["APIM_SERVICE_NAME"]
API_ID = os.environ["APIM_API_NAME"]

def get_apim_operations():
    credential = DefaultAzureCredential()
    client = ApiManagementClient(credential, SUBSCRIPTION_ID)
    return list(client.api_operation.list_by_api(RESOURCE_GROUP, SERVICE_NAME, API_ID))

def get_split_operations():
    from os import listdir
    return set(f.replace(".json", "") for f in listdir("split") if f.endswith(".json"))

def delete_operation(op_id):
    print(f"🗑️ Deleting stale operation: {op_id}")
    credential = DefaultAzureCredential()
    client = ApiManagementClient(credential, SUBSCRIPTION_ID)
    client.api_operation.delete(
        RESOURCE_GROUP,
        SERVICE_NAME,
        API_ID,
        op_id,
        if_match="*"
    )

def main():
    print("🧹 Cleaning up stale operations from APIM...")
    apim_ops = get_apim_operations()
    split_ops = get_split_operations()

    stale_ops = [op for op in apim_ops if op.name not in split_ops]
    print(f"🔍 Found {len(stale_ops)} stale operations to delete.")

    for op in stale_ops:
        delete_operation(op.name)

if __name__ == "__main__":
    main()
