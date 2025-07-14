import os
import json
import re
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
from azure.mgmt.apimanagement.models import (
    OperationContract,
    RequestContract,
    ResponseContract,
    ParameterContract,
    RepresentationContract,
)

subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
resource_group = os.environ["AZURE_RESOURCE_GROUP"]
service_name = os.environ["AZURE_APIM_NAME"]
api_id = os.environ["AZURE_APIM_API_ID"]

SPLIT_DIR = "./split"

credential = DefaultAzureCredential()
client = ApiManagementClient(credential, subscription_id)

def parse_operation_file(file_path):
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in file: {file_path}")
            return None

    # Try to extract metadata
    method = data.get("method")
    path = data.get("path")
    operation_id = data.get("operationId")

    if not all([method, path, operation_id]):
        print(f"⚠️ Skipping file missing metadata: {file_path}")
        return None

    parameters = data.get("parameters", [])
    request_body = data.get("requestBody", {})
    responses = data.get("responses", {})

    return {
        "method": method.upper(),
        "path": path,
        "operation_id": operation_id,
        "parameters": parameters,
        "request_body": request_body,
        "responses": responses,
    }

def extract_parameters(parameters, path):
    query_params = []
    path_params = []

    for p in parameters:
        param = ParameterContract(
            name=p["name"],
            required=p.get("required", False),
            type=p.get("schema", {}).get("type", "string"),
            description=p.get("description", ""),
        )
        if p["in"] == "query":
            query_params.append(param)
        elif p["in"] == "path":
            path_params.append(param)

    # Auto-detect any template parameters in path that are not listed
    template_vars = re.findall(r"{(.*?)}", path)
    listed_path_param_names = [p.name for p in path_params]
    for var in template_vars:
        if var not in listed_path_param_names:
            path_params.append(ParameterContract(name=var, required=True, type="string"))

    return query_params, path_params

def build_representation(body, content_type="application/json"):
    if not body or "content" not in body:
        return None
    content = body["content"]
    if content_type not in content:
        return None
    schema = content[content_type].get("schema", {})
    return RepresentationContract(content_type=content_type, schema=schema)

def create_or_update_operation(op_data):
    method = op_data["method"]
    path = op_data["path"]
    operation_id = op_data["operation_id"]
    parameters = op_data["parameters"]
    request_body = op_data["request_body"]
    responses = op_data["responses"]

    print(f"🔄 Syncing {method} {path} ({operation_id})")

    query_params, path_params = extract_parameters(parameters, path)

    request = RequestContract(
        description=f"{method} {path}",
        query_parameters=query_params,
        headers=[],
        representations=[
            build_representation(request_body)
        ] if request_body else []
    )

    response_list = []
    for status_code, response_data in responses.items():
        rep = build_representation(response_data)
        resp = ResponseContract(
            status_code=int(status_code) if status_code.isdigit() else 200,
            description=response_data.get("description", ""),
            representations=[rep] if rep else []
        )
        response_list.append(resp)

    op_contract = OperationContract(
        display_name=operation_id,
        method=method,
        url_template=path,
        request=request,
        responses=response_list,
        template_parameters=path_params
    )

    client.api_operation.create_or_update(
        resource_group_name=resource_group,
        service_name=service_name,
        api_id=api_id,
        operation_id=operation_id,
        parameters={},
        if_match="*",
        value=op_contract
    )
    print(f"✅ Operation synced to APIM: {operation_id}")

def main():
    operation_files = []
    for root, _, files in os.walk(SPLIT_DIR):
        for file in files:
            if file.endswith(".json"):
                operation_files.append(os.path.join(root, file))

    print(f"🚀 Syncing {len(operation_files)} Swagger operations to APIM...")

    for file_path in sorted(operation_files):
        print(f"📂 Reading: {file_path}")
        op_data = parse_operation_file(file_path)
        if not op_data:
            continue
        try:
            create_or_update_operation(op_data)
        except Exception as e:
            print(f"❌ Failed to sync {file_path}: {e}")

    print("📢 Publishing latest API revision...")
    os.system(
        f"az apim api revision publish --resource-group {resource_group} --service-name {service_name} --api-id {api_id} --yes"
    )

if __name__ == "__main__":
    main()
