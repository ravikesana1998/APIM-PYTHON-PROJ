import os
import json
import requests
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient

# Load environment variables
subscription_id = os.environ["APIM_SUBSCRIPTION_ID"]
resource_group = os.environ["APIM_RESOURCE_GROUP"]
service_name = os.environ["APIM_SERVICE_NAME"]
api_name = os.environ["APIM_API_NAME"]
swagger_url = os.environ["APIM_SWAGGER_URL"]

# Authenticate
credential = DefaultAzureCredential()
client = ApiManagementClient(credential, subscription_id)

def get_operations_from_apim():
    operations = client.api_operation.list_by_api(resource_group, service_name, api_name)
    return set(op.name for op in operations)

def get_operations_from_swagger():
    resp = requests.get(swagger_url)
    resp.raise_for_status()
    swagger = resp.json()
    ops = set()
    for path, methods in swagger["paths"].items():
        for method in methods:
            cleaned = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
            op_id = f"{method.upper()}_{cleaned or 'root'}"
            ops.add(op_id)
    return ops

def main():
    apim_ops = get_operations_from_apim()
    swagger_ops = get_operations_from_swagger()

    with open("to_delete.txt", "w") as f:
        for op in apim_ops - swagger_ops:
            f.write(op + "\n")

    with open("to_add.txt", "w") as f:
        for op in swagger_ops - apim_ops:
            f.write(op + "\n")

    print(f"✅ In Swagger but NOT in APIM: {len(swagger_ops - apim_ops)}")
    print(f"🧹 In APIM but NOT in Swagger: {len(apim_ops - swagger_ops)}")

if __name__ == "__main__":
    main()
