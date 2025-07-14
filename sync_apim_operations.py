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

# Read environment variables
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
resource_group = os.environ["AZURE_RESOURCE_GROUP"]
apim_name = os.environ["AZURE_APIM_NAME"]
api_id = os.environ["AZURE_APIM_API_ID"]
split_dir = os.environ.get("SPLIT_DIR", "./split")

def extract_method_and_path(filename):
    match = re.match(r"^(get|post|put|delete|patch)_(.+)\.json$", filename, re.IGNORECASE)
    if match:
        method = match.group(1).lower()
        path = "/" + "/".join(match.group(2).split("_"))
        return method, path.replace(".json", "")
    return None, None

def parse_swagger_file(path):
    with open(path, "r") as f:
        return json.load(f)

def build_operation_contract(op_id, method, url_template, swagger):
    display_name = swagger.get("summary") or op_id

    request = swagger.get("requestBody", {})
    request_content = request.get("content", {}) if isinstance(request, dict) else {}
    representations = []

    for mime_type, content in request_content.items():
        schema = content.get("schema", {})
        representations.append(RepresentationContract(content_type=mime_type, schema=schema))

    query_params = []
    path_params = []

    for param in swagger.get("parameters", []):
        param_contract = ParameterContract(
            name=param["name"],
            required=param.get("required", False),
            type=param.get("schema", {}).get("type", "string"),
            description=param.get("description", ""),
            default_value=param.get("schema", {}).get("default", None)
        )
        if param.get("in") == "query":
            query_params.append(param_contract)
        elif param.get("in") == "path":
            path_params.append(param_contract)

    responses = []
    for status, resp in swagger.get("responses", {}).items():
        if isinstance(resp, dict):
            responses.append(ResponseContract(status_code=status, description=resp.get("description", "")))

    return OperationContract(
        display_name=display_name,
        method=method.upper(),
        url_template=url_template,
        request=RequestContract(
            query_parameters=query_params or None,
            headers=None,
            representations=representations or None
        ),
        responses=responses or None,
        template_parameters=path_params or None
    )

def sync_operations():
    credential = DefaultAzureCredential()
    client = ApiManagementClient(credential, subscription_id)

    synced_count = 0
    total_count = 0

    for root, _, files in os.walk(split_dir):
        for file in files:
            if file.endswith(".json"):
                total_count += 1
                filepath = os.path.join(root, file)
                print(f"\n📂 Reading file: {filepath}")

                swagger = parse_swagger_file(filepath)

                op_id = swagger.get("operationId")
                if not op_id:
                    print(f"⚠️ Skipping file (no operationId): {filepath}")
                    continue

                method, path = extract_method_and_path(file)
                print(f"🔎 Extracted method: {method}, path: {path}, operationId: {op_id}")

                if not method or not path:
                    print(f"❌ Could not determine method/path from filename: {file}")
                    continue

                print(f"🔄 Syncing {method.upper()} {path} ({op_id})")

                try:
                    op_contract = build_operation_contract(op_id, method, path, swagger)

                    print("📤 Built operation contract:")
                    print(json.dumps(op_contract.as_dict(), indent=2))

                    client.api_operation.create_or_update(
                        resource_group_name=resource_group,
                        service_name=apim_name,
                        api_id=api_id,
                        operation_id=op_id,
                        parameters=op_contract,
                        if_match="*"
                    )
                    print(f"✅ Synced operation: {op_id}")
                    synced_count += 1

                except Exception as e:
                    print(f"❌ Failed to sync {filepath}: {str(e)}")
                    raise  # 🔥 Important for fail-fast

    print(f"\n✅ Sync Summary: {synced_count}/{total_count} operations synced.")

if __name__ == "__main__":
    sync_operations()
