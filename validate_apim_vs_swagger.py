import requests
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
import os

subscription_id = os.environ["APIM_SUBSCRIPTION_ID"]
resource_group = os.environ["APIM_RESOURCE_GROUP"]
service_name = os.environ["APIM_SERVICE_NAME"]
api_id = os.environ["APIM_API_NAME"]
swagger_url = os.environ["SWAGGER_URL"]

def get_operations_from_swagger():
    resp = requests.get(swagger_url)
    resp.raise_for_status()
    swagger = resp.json()
    ops = set()
    for path, methods in swagger.get("paths", {}).items():
        for method in methods:
            ops.add(f"{method.upper()} {path}")
    return ops

def get_operations_from_apim():
    client = ApiManagementClient(DefaultAzureCredential(), subscription_id)
    operations = client.api_operation.list_by_api(resource_group, service_name, api_id)
    ops = set()
    for op in operations:
        if op.request:
            ops.add(f"{op.request.method.upper()} {op.request.url_template}")
    return ops

def main():
    swagger_ops = get_operations_from_swagger()
    apim_ops = get_operations_from_apim()

    only_in_swagger = swagger_ops - apim_ops
    only_in_apim = apim_ops - swagger_ops

    with open("to_delete.txt", "w") as f:
        for op in sorted(only_in_apim):
            f.write(op + "\n")

    print(f"✅ In Swagger but NOT in APIM: {len(only_in_swagger)}")
    print(f"🧹 In APIM but NOT in Swagger: {len(only_in_apim)}")

if __name__ == "__main__":
    main()
