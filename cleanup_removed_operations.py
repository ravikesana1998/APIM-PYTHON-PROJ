import os
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
from azure.core.exceptions import ResourceNotFoundError

subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
resource_group = os.environ["AZURE_RESOURCE_GROUP"]
apim_name = os.environ["AZURE_APIM_NAME"]
api_id = os.environ["AZURE_APIM_API_ID"]
split_dir = os.environ.get("SPLIT_DIR", "./split")


def get_swagger_operation_ids():
    operation_ids = []
    for root, _, files in os.walk(split_dir):
        for file in files:
            if file.endswith(".json"):
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    try:
                        swagger = json.load(f)
                        op_id = swagger.get("operationId")
                        if op_id:
                            operation_ids.append(op_id)
                    except json.JSONDecodeError:
                        print(f"⚠️ Failed to parse JSON: {path}")
    return set(operation_ids)


def delete_removed_operations():
    credential = DefaultAzureCredential()
    client = ApiManagementClient(credential, subscription_id)

    try:
        existing_ops = list(client.api_operation.list_by_api(resource_group, apim_name, api_id))
    except ResourceNotFoundError:
        print("⚠️ API not found in APIM.")
        return

    swagger_ops = get_swagger_operation_ids()

    removed_ops = [op for op in existing_ops if op.name not in swagger_ops]

    if not removed_ops:
        print("✅ No stale operations to delete.")
        return

    print("🧹 Removing stale APIM operations...")
    for op in removed_ops:
        print(f"🗑️ Deleting: {op.name}")
        client.api_operation.delete(
            resource_group_name=resource_group,
            service_name=apim_name,
            api_id=api_id,
            operation_id=op.name,
            if_match="*"
        )


if __name__ == "__main__":
    delete_removed_operations()

