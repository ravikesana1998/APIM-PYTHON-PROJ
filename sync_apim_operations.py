import os
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
from azure.mgmt.apimanagement.models import (
    OperationContract,
    ParameterContract,
    RequestContract,
    ResponseContract,
    RepresentationContract,
    ApiCreateOrUpdateParameter
)
from azure.core.exceptions import HttpResponseError

def build_operation_contract(op_data):
    method = op_data["method"].upper()
    url_template = op_data["path"]
    display_name = op_data["operationId"]
    parameters = op_data.get("parameters", [])
    request_body = op_data.get("requestBody", {})
    responses = op_data.get("responses", {})

    query_parameters = []
    template_parameters = []

    for param in parameters:
        param_contract = ParameterContract(
            name=param["name"],
            required=param.get("required", False),
            type=param.get("schema", {}).get("type", "string"),
            default_value=param.get("schema", {}).get("default"),
            description=param.get("description", ""),
        )
        if param["in"] == "query":
            query_parameters.append(param_contract)
        elif param["in"] == "path":
            template_parameters.append(param_contract)

    request_representation = None
    if request_body:
        content = request_body.get("content", {})
        json_content = content.get("application/json")
        if json_content:
            schema = json_content.get("schema")
            request_representation = RepresentationContract(
                content_type="application/json",
                schema=schema
            )

    request_contract = RequestContract(
        query_parameters=query_parameters,
        template_parameters=template_parameters,
        representations=[request_representation] if request_representation else []
    )

    response_contracts = []
    for status_code, resp in responses.items():
        content = resp.get("content", {})
        json_content = content.get("application/json")
        representation = None
        if json_content:
            schema = json_content.get("schema")
            representation = RepresentationContract(
                content_type="application/json",
                schema=schema
            )
        response_contracts.append(ResponseContract(
            status_code=status_code,
            representations=[representation] if representation else []
        ))

    operation = OperationContract(
        display_name=display_name,
        method=method,
        url_template=url_template,
        request=request_contract,
        responses=response_contracts
    )
    return operation

def create_or_update_operation(client, resource_group, service_name, api_id, operation_id, operation_contract):
    try:
        print(f"[🔄] Syncing {operation_contract.method} {operation_contract.url_template} ({operation_id})")
        client.api_operation.create_or_update(
            resource_group_name=resource_group,
            service_name=service_name,
            api_id=api_id,
            operation_id=operation_id,
            parameters=operation_contract
        )
        print(f"✅ Operation synced to APIM: {operation_id}")
    except HttpResponseError as e:
        print(f"❌ Failed to sync operation {operation_id}: {e.message}")

def ensure_api_exists(client, resource_group, service_name, api_id):
    try:
        client.api.get(resource_group, service_name, api_id)
        print(f"✅ API '{api_id}' already exists.")
    except HttpResponseError as e:
        if "not found" in str(e).lower():
            print(f"⚠️ API '{api_id}' not found. Creating it...")
            client.api.create_or_update(
                resource_group,
                service_name,
                api_id,
                parameters=ApiCreateOrUpdateParameter(
                    display_name=api_id,
                    path=api_id,
                    protocols=["https"]
                )
            )
            print(f"✅ Created API '{api_id}'.")
        else:
            raise

def main():
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    resource_group = os.environ["APIM_RESOURCE_GROUP"]
    service_name = os.environ["APIM_SERVICE_NAME"]
    api_id = os.environ["APIM_API_ID"]
    split_dir = "./split"

    credential = DefaultAzureCredential()
    client = ApiManagementClient(credential, subscription_id)

    ensure_api_exists(client, resource_group, service_name, api_id)

    from glob import glob
    import re

    swagger_files = glob(f"{split_dir}/**/*.json", recursive=True)
    print(f"Syncing {len(swagger_files)} Swagger operations to APIM...")
    for file_path in swagger_files:
        try:
            with open(file_path, "r") as f:
                swagger = json.load(f)

            method = swagger["method"]
            path = swagger["path"]
            operation_id = swagger["operationId"]
            op_data = {
                "method": method,
                "path": path,
                "operationId": operation_id,
                "parameters": swagger.get("parameters", []),
                "requestBody": swagger.get("requestBody", {}),
                "responses": swagger.get("responses", {})
            }
            operation_contract = build_operation_contract(op_data)
            create_or_update_operation(
                client, resource_group, service_name, api_id, operation_id, operation_contract
            )
        except Exception as e:
            print(f"❌ Failed to sync {file_path}: {e}")

if __name__ == "__main__":
    main()
