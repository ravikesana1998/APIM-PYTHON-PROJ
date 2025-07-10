import os
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
from azure.mgmt.apimanagement.models import (
    OperationContract,
    RequestContract,
    ResponseContract,
    ParameterContract,
)

# Load environment variables
subscription_id = os.environ["APIM_SUBSCRIPTION_ID"]
resource_group = os.environ["APIM_RESOURCE_GROUP"]
service_name = os.environ["APIM_SERVICE_NAME"]
api_name = os.environ["APIM_API_NAME"]
split_dir = "./split"

credential = DefaultAzureCredential()
client = ApiManagementClient(credential, subscription_id)

def sync_operation(file_path):
    with open(file_path, "r") as f:
        swagger = json.load(f)

    path = list(swagger["paths"].keys())[0]
    method = list(swagger["paths"][path].keys())[0].lower()
    op_data = swagger["paths"][path][method]

    # Extract parameters
    parameters = []
    for param in op_data.get("parameters", []):
        parameters.append(ParameterContract(
            name=param["name"],
            required=param.get("required", False),
            type=param.get("schema", {}).get("type", "string"),
            description=param.get("description", ""),
            default_value=param.get("schema", {}).get("default"),
        ))

    # Extract request body
    request = None
    if "requestBody" in op_data:
        content = op_data["requestBody"].get("content", {})
        app_json = content.get("application/json", {})
        schema = app_json.get("schema", {})
        request = RequestContract(
            description=op_data["requestBody"].get("description", ""),
            query_parameters=[],
            headers=[],
            representations=[],
        )

    # Extract responses
    responses = []
    for status_code, resp in op_data.get("responses", {}).items():
        responses.append(ResponseContract(
            status_code=status_code,
            description=resp.get("description", ""),
        ))

    op_id = os.path.splitext(os.path.basename(file_path))[0]

    print(f"📤 Syncing operation: {op_id}")
    try:
        client.api_operation.create_or_update(
            resource_group_name=resource_group,
            service_name=service_name,
            api_id=api_name,
            operation_id=op_id,
            parameters=parameters,
            display_name=op_data.get("summary", op_id),
            method=method.upper(),
            url_template=path,
            request=request,
            responses=responses
        )
        print(f"✅ Synced: {op_id}")
    except Exception as e:
        print(f"❌ Failed: {op_id}")
        print(f"ERROR: {e}")

# Run all
if not os.path.exists(split_dir):
    print(f"❌ Split directory not found: {split_dir}")
    exit(1)

for file_name in os.listdir(split_dir):
    if file_name.endswith(".json"):
        sync_operation(os.path.join(split_dir, file_name))
