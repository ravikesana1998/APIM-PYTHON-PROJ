import os
import requests
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient

# Inputs
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
resource_group = os.environ["APIM_RESOURCE_GROUP"]
apim_name = os.environ["APIM_NAME"]
api_id = os.environ["APIM_API_NAME"]
swagger_url = os.environ["SWAGGER_URL"]

print("🔎 Validating APIM operations against Swagger...")

# Load Swagger
swagger = requests.get(swagger_url).json()
swagger_ops = set()

for path, methods in swagger["paths"].items():
    for method, op_data in methods.items():
        op_id = op_data.get("operationId")
        if op_id:
            swagger_ops.add(op_id)

# Load APIM operations
credential = DefaultAzureCredential()
client = ApiManagementClient(credential, subscription_id)

apim_ops = client.api_operation.list_by_api(resource_group, apim_name, api_id)
apim_op_ids = set(op.name for op in apim_ops)

in_swagger_not_apim = swagger_ops - apim_op_ids
in_apim_not_swagger = apim_op_ids - swagger_ops

print("✅ In Swagger but NOT in APIM:", len(in_swagger_not_apim))
print("🧹 In APIM but NOT in Swagger:", len(in_apim_not_swagger))

# Save for cleanup script
with open("removed_operations.txt", "w") as f:
    for op in in_apim_not_swagger:
        f.write(op + "\n")
