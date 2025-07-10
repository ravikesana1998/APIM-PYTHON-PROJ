import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient

# Load environment variables
subscription_id = os.environ["APIM_SUBSCRIPTION_ID"]
resource_group = os.environ["APIM_RESOURCE_GROUP"]
service_name = os.environ["APIM_SERVICE_NAME"]
api_name = os.environ["APIM_API_NAME"]

credential = DefaultAzureCredential()
client = ApiManagementClient(credential, subscription_id)

def delete_operation(op_id):
    print(f"🗑️ Deleting stale operation: {op_id}")
    try:
        client.api_operation.delete(
            resource_group_name=resource_group,
            service_name=service_name,
            api_id=api_name,
            operation_id=op_id,
            if_match="*"
        )
        print(f"✅ Deleted: {op_id}")
    except Exception as e:
        print(f"❌ Failed to delete {op_id}: {e}")

def main():
    if not os.path.exists("to_delete.txt"):
        print("No stale operations to delete.")
        return

    with open("to_delete.txt", "r") as f:
        for op_id in f.read().splitlines():
            if op_id.strip():
                delete_operation(op_id)

if __name__ == "__main__":
    main()
