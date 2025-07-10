import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient

subscription_id = os.environ["APIM_SUBSCRIPTION_ID"]
resource_group = os.environ["APIM_RESOURCE_GROUP"]
service_name = os.environ["APIM_SERVICE_NAME"]
api_id = os.environ["APIM_API_NAME"]

client = ApiManagementClient(DefaultAzureCredential(), subscription_id)

if not os.path.exists("stale_operations.txt"):
    print("✅ No stale operations to delete.")
    exit(0)

with open("stale_operations.txt") as f:
    for line in f:
        method, url_template = line.strip().split(" ", 1)
        operation_id = f"{method}_{url_template.strip('/').replace('/', '_').replace('{','').replace('}','')}"
        try:
            client.api_operation.delete(resource_group, service_name, api_id, operation_id, if_match="*")
            print(f"🗑️ Deleted stale operation: {operation_id}")
        except Exception as e:
            print(f"⚠️ Failed to delete operation {operation_id}: {e}")
