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


def get_apim_operation_ids():
    print("🔍 Fetching operation IDs from APIM...")
    credential = DefaultAzureCredential()
    client = ApiManagementClient(credential, subscription_id)
    try:
        pager = client.api_operation.list_by_api(resource_group, apim_name, api_id)
        return [op.name for op in pager]
    except ResourceNotFoundError as e:
        print(f"⚠️ Cannot retrieve operations from APIM: {e.message}")
        return []


def get_swagger_operation_ids():
    print("📂 Reading split Swagger files for operation IDs...")
    ids = []
    for root, _, files in os.walk(split_dir):
        for file in files:
            if file.endswith(".json"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r") as f:
                        swagger = json.load(f)
                        op_id = swagger.get("operationId")
                        if op_id:
                            ids.append(op_id)
                        else:
                            print(f"⚠️ No operationId found in {path}")
                except Exception as e:
                    print(f"⚠️ Error reading {path}: {e}")
    return ids


def main():
    swagger_ops = get_swagger_operation_ids()
    apim_ops = get_apim_operation_ids()

    swagger_set = set(swagger_ops)
    apim_set = set(apim_ops)

    only_in_swagger = sorted(swagger_set - apim_set)
    only_in_apim = sorted(apim_set - swagger_set)

    print("✅ Validation Complete")
    print(f"Total in Swagger: {len(swagger_ops)}")
    print(f"Total in APIM: {len(apim_ops)}")
    print(f"In Swagger but NOT in APIM: {len(only_in_swagger)}")
    for op in only_in_swagger:
        print(f"  - {op}")
    print(f"In APIM but NOT in Swagger: {len(only_in_apim)}")
    for op in only_in_apim:
        print(f"  - {op}")


if __name__ == "__main__":
    main()
