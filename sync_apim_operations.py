import os
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
from azure.mgmt.apimanagement.models import OperationContract, RequestContract, ResponseContract, ParameterContract

# Get environment variables
subscription_id = os.environ["APIM_SUBSCRIPTION_ID"]
resource_group = os.environ["APIM_RESOURCE_GROUP"]
service_name = os.environ["APIM_SERVICE_NAME"]
api_id = os.environ["APIM_API_NAME"]

client = ApiManagementClient(credential=DefaultAzureCredential(), subscription_id=subscription_id)

split_dir = "./split"

for file_name in os.listdir(split_dir):
    if not file_name.endswith(".json"):
        continue

    with open(os.path.join(split_dir, file_name)) as f:
        swagger = json.load(f)

    path = list(swagger["paths"].keys())[0]
    method = list(swagger["paths"][path].keys())[0].upper()
    operation_id = file_name.replace(".json", "")

    print(f"📤 Syncing operation: {operation_id}")

    try:
        # Extract parameters
        parameters = swagger["paths"][path][method.lower()].get("parameters", [])
        param_contracts = []
        for param in parameters:
            param_contracts.append(ParameterContract(
                name=param["name"],
                required=param.get("required", False),
                type=param.get("schema", {}).get("type", "string"),
                description=param.get("description", ""),
                default_value=param.get("schema", {}).get("default", None),
                values=None,
                # 'in_' is a reserved word; use **kwargs
                **{"in": param["in"]}
            ))

        # Build request contract
        request_contract = RequestContract(
            query_parameters=[p for p in param_contracts if p.in_ == "query"],
            headers=[p for p in param_contracts if p.in_ == "header"],
            url_template_parameters=[p for p in param_contracts if p.in_ == "path"]
        )

        # Build response contract
        response_contract = ResponseContract(status_code=200, description="OK")

        # Create operation
        operation = OperationContract(
            display_name=operation_id,
            method=method,
            url_template=path,
            request=request_contract,
            responses=[response_contract]
        )

        client.api_operation.create_or_update(
            resource_group_name=resource_group,
            service_name=service_name,
            api_id=api_id,
            operation_id=operation_id,
            parameters={},
            if_match="*",
            value=operation
        )

        print(f"✅ Synced: {operation_id}")

    except Exception as e:
        print(f"❌ Failed: {operation_id}")
        print(str(e))
