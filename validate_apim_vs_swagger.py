import os
import requests
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient

SUBSCRIPTION_ID = os.environ["APIM_SUBSCRIPTION_ID"]
RESOURCE_GROUP = os.environ["APIM_RESOURCE_GROUP"]
SERVICE_NAME = os.environ["APIM_SERVICE_NAME"]
API_ID = os.environ["APIM_API_NAME"]
SWAGGER_URL = os.environ["SWAGGER_URL"]

def get_operations_from_swagger():
    print(f"🌐 Fetching Swagger from: {SWAGGER_URL}")
    resp = requests.get(SWAGGER_URL)
    resp.raise_for_status()
    swagger = resp.json()

    operations = set()
    for path, methods in swagger.get('paths', {}).items():
        for method in methods:
            operations.add(f"{method.upper()} {path}")
    return operations

def get_operations_from_apim():
    print("🔍 Fetching operations from APIM...")
    credential = DefaultAzureCredential()
    client = ApiManagementClient(credential, SUBSCRIPTION_ID)
    operations = client.api_operation.list_by_api(RESOURCE_GROUP, SERVICE_NAME, API_ID)

    op_set = set()
    for op in operations:
        if op.request and op.request.method and op.request.url_template:
            op_set.add(f"{op.request.method.upper()} {op.request.url_template}")
        else:
            print(f"⚠️ Skipping operation '{op.name}' due to missing method/url_template.")
    return op_set

def main():
    print("🔄 Comparing Swagger vs APIM operations...")
    swagger_ops = get_operations_from_swagger()
    apim_ops = get_operations_from_apim()

    only_in_swagger = swagger_ops - apim_ops
    only_in_apim = apim_ops - swagger_ops
    in_both = swagger_ops & apim_ops

    print(f"✅ Present in both: {len(in_both)}")
    for op in sorted(in_both): print(f"  ✔ {op}")

    if only_in_swagger:
        print(f"\n➕ In Swagger but NOT in APIM: {len(only_in_swagger)}")
        for op in sorted(only_in_swagger): print(f"  ➕ {op}")

    if only_in_apim:
        print(f"\n🗑️ In APIM but NOT in Swagger: {len(only_in_apim)}")
        for op in sorted(only_in_apim): print(f"  🗑️ {op}")

if __name__ == "__main__":
    main()
