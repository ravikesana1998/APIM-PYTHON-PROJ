import requests
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
import os

subscription_id = os.environ["APIM_SUBSCRIPTION_ID"]
resource_group = os.environ["APIM_RESOURCE_GROUP"]
service_name = os.environ["APIM_SERVICE_NAME"]
api_id = os.environ["APIM_API_NAME"]
swagger_url = os.environ["SWAGGER_URL"] + "/swagger/v1/swagger.json"

def get_operations_from_swagger():
    resp = requests.get(swagger_url)
    resp.raise_for_status()
    swagger = resp.json()
    operations = set()
    for path, methods in swagger.get('paths', {}).items():
        for method in methods:
            operations.add(f"{method.upper()} {path}")
    return operations

def get_operations_from_apim():
    client = ApiManagementClient(DefaultAzureCredential(), subscription_id)
    operations = client.api_operation.list_by_api(resource_group, service_name, api_id)
    return set(f"{op.method.upper()} {op.url_template}" for op in operations)

swagger_ops = get_operations_from_swagger()
apim_ops = get_operations_from_apim()

only_in_apim = apim_ops - swagger_ops
with open("stale_operations.txt", "w") as f:
    for op in only_in_apim:
        f.write(op + "\n")

print(f"🧹 Found {len(only_in_apim)} stale operations to delete.")
