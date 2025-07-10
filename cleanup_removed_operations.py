import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient

subscription_id = os.environ["APIM_SUBSCRIPTION_ID"]
resource_group = os.environ["APIM_RESOURCE_GROUP"]
service_name = os.environ["APIM_SERVICE_NAME"]
api_id = os.environ["APIM_API_NAME"]

client = ApiManagementClient(DefaultAzureCredential(), subscription_id)

if not os.path.exists("to_delete.txt"):
    print("No stale operations to delete.")
    exit(0)

with open("to_delete.txt") as f:
    stale_ops = [line.strip() for line in f if line.strip()]

for entry in stale_ops:
    method, path = entry.split(" ", 1)
    op_id = f"{method}_{path.strip('/').replace('/', '_').replace('{', '').replace('}', '')}"
    try:
        client.api_operation.delete(resource_group, service_name, api_id, op_id, if_match="*")
        print(f"🗑️ Deleted: {op_id}")
    except Exception as e:
        print(f"❌ Failed to delete {op_id}: {e}")
