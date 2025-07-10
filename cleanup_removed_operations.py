import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient

# Inputs
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
resource_group = os.environ["APIM_RESOURCE_GROUP"]
apim_name = os.environ["APIM_NAME"]
api_id = os.environ["APIM_API_NAME"]

print("🧹 Removing stale APIM operations...")

if not os.path.exists("removed_operations.txt"):
    print("No stale operations to delete.")
    exit(0)

with open("removed_operations.txt", "r") as f:
    ops_to_delete = [line.strip() for line in f.readlines() if line.strip()]

if not ops_to_delete:
    print("No stale operations to delete.")
    exit(0)

credential = DefaultAzureCredential()
client = ApiManagementClient(credential, subscription_id)

for op_id in ops_to_delete:
    print(f"🗑️ Deleting operation: {op_id}")
    try:
        client.api_operation.delete(
            resource_group_name=resource_group,
            service_name=apim_name,
            api_id=api_id,
            operation_id=op_id,
            if_match="*"
        )
        print(f"✅ Deleted: {op_id}")
    except Exception as e:
        print(f"❌ Failed to delete {op_id}: {e}")
