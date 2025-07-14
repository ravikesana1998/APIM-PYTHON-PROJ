import os
import json
import glob
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

# ENV vars
SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
RESOURCE_GROUP = os.environ["AZURE_RESOURCE_GROUP"]
APIM_NAME = os.environ["AZURE_APIM_NAME"]
API_ID = os.environ["AZURE_APIM_API_ID"]

# Auth
credential = DefaultAzureCredential()
client = ApiManagementClient(credential, SUBSCRIPTION_ID)

def get_apim_operation_ids():
    try:
        pager = client.api_operation.list_by_api(RESOURCE_GROUP, APIM_NAME, API_ID)
        return [op.name for op in pager]
    except (ResourceNotFoundError, HttpResponseError) as e:
        print(f"⚠️ Cannot retrieve operations from APIM: {e.message}")
        return []

def get_swagger_operation_ids():
    swagger_files = glob.glob("split/**/*.json", recursive=True)
    ids = []
    for file in swagger_files:
        with open(file, "r") as f:
            data = json.load(f)
            op_id = data.get("operationId")
            if op_id:
                ids.append(op_id)
    return ids

def main():
    print("🛡️ Validating APIM vs Swagger...")
    apim_ops = get_apim_operation_ids()
    swagger_ops = get_swagger_operation_ids()

    print(f"🔍 Validating APIM operations against Swagger...")
    print(f"Total in Swagger: {len(swagger_ops)}")
    print(f"Total in APIM: {len(apim_ops)}")

    swagger_not_in_apim = [op for op in swagger_ops if op not in apim_ops]
    apim_not_in_swagger = [op for op in apim_ops if op not in swagger_ops]

    print(f"In Swagger but NOT in APIM: {len(swagger_not_in_apim)}")
    for op in swagger_not_in_apim:
        print(f"  - {op}")

    print(f"In APIM but NOT in Swagger: {len(apim_not_in_swagger)}")
    for op in apim_not_in_swagger:
        print(f"  - {op}")

if __name__ == "__main__":
    main()
