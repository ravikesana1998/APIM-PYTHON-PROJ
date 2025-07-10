import requests
import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient

subscription_id = os.environ["APIM_SUBSCRIPTION_ID"]
resource_group = os.environ["APIM_RESOURCE_GROUP"]
service_name = os.environ["APIM_SERVICE_NAME"]
api_id = os.environ["APIM_API_NAME"]
swagger_url = os.environ["SWAGGER_URL"]

def get_operations_from_swagger():
    resp = requests.get(swagger_url)
    resp.raise_for_status()
    swagger = resp.json()

    operations = []
    for path, methods in swagger.get("paths", {}).items():
        for method in methods:
            operations.append(f"{method.upper()} {path}")
    return set(operations)

def get_operations_from_apim():
    credential = DefaultAzureCredential()
    client = ApiManagementClient(credential, subscription_id)
    ops = client.api_operation.list_by_api(resource_group, service_name, api_id)
    return set(f"{op.method.upper()} {op.url_template}" for op in ops if op.method)

def main():
    print("🔍 Comparing Swagger and APIM operations...")
    swagger_ops = get_operations_from_swagger()
    apim_ops = get_operations_from_apim()

    print(f"✅ In both: {len(swagger_ops & apim_ops)}")
    print(f"➕ In Swagger only: {len(swagger_ops - apim_ops)}")
    print(f"🗑️ In APIM only: {len(apim_ops - swagger_ops)}")

if __name__ == "__main__":
    main()
