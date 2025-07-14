# import os
# import json
# from azure.identity import DefaultAzureCredential
# from azure.mgmt.apimanagement import ApiManagementClient
# from azure.mgmt.apimanagement.models import OperationContract, RequestContract, ParameterContract, ResponseContract
# from azure.core.exceptions import ResourceNotFoundError

# subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
# resource_group = os.environ["AZURE_RESOURCE_GROUP"]
# apim_name = os.environ["AZURE_APIM_NAME"]
# api_id = os.environ["AZURE_APIM_API_ID"]
# split_dir = os.environ.get("SPLIT_DIR", "./split")

# def extract_method_and_path(filename):
#     parts = filename.split("_", 1)
#     if len(parts) != 2:
#         return None, None
#     method = parts[0].lower()
#     try:
#         with open(filename, "r") as f:
#             swagger = json.load(f)
#             path = list(swagger["paths"].keys())[0]
#             return method, path
#     except:
#         return method, None

# def sync_operation(filepath):
#     try:
#         with open(filepath, "r") as f:
#             swagger = json.load(f)
#     except Exception as e:
#         print(f"⚠️ Failed to load {filepath}: {e}")
#         return False

#     try:
#         operation_id = swagger.get("operationId")
#         if not operation_id:
#             print(f"⚠️ Skipping file missing metadata: {filepath}")
#             return False

#         method, path = extract_method_and_path(filepath)
#         if not path:
#             print(f"⚠️ Could not extract path from {filepath}")
#             return False

#         print(f"\n🔄 Syncing {method.upper()} {path} ({operation_id})")

#         credential = DefaultAzureCredential()
#         client = ApiManagementClient(credential, subscription_id)

#         parameters = []
#         for param in swagger.get("parameters", []):
#             parameters.append(ParameterContract(
#                 name=param["name"],
#                 required=param.get("required", False),
#                 type=param.get("schema", {}).get("type", "string"),
#                 description=param.get("description", ""),
#                 location=param.get("in")
#             ))

#         request = None
#         if "requestBody" in swagger:
#             content = swagger["requestBody"]["content"]
#             if "application/json" in content:
#                 schema = content["application/json"].get("schema", {})
#                 request = RequestContract(
#                     query_parameters=[p for p in parameters if p.location == "query"],
#                     headers=[],
#                     representations=[{
#                         "content_type": "application/json",
#                         "sample": json.dumps(schema)
#                     }]
#                 )

#         responses = []
#         for status_code, resp in swagger.get("responses", {}).items():
#             responses.append(ResponseContract(
#                 status_code=int(status_code) if status_code.isdigit() else 200,
#                 description=resp.get("description", "")
#             ))

#         contract = OperationContract(
#             display_name=operation_id,
#             method=method.upper(),
#             url_template=path,
#             request=request,
#             responses=responses,
#             template_parameters=[p for p in parameters if p.location == "path"]
#         )

#         client.api_operation.create_or_update(
#             resource_group_name=resource_group,
#             service_name=apim_name,
#             api_id=api_id,
#             operation_id=operation_id,
#             parameters=contract
#         )

#         print(f"✅ Synced operation: {operation_id}")
#         return True

#     except ResourceNotFoundError as e:
#         print(f"❌ Failed to sync {filepath}: {e.message}")
#         return False

# def main():
#     success_count = 0
#     total = 0
#     for root, _, files in os.walk(split_dir):
#         for file in files:
#             if file.endswith(".json"):
#                 total += 1
#                 full_path = os.path.join(root, file)
#                 if sync_operation(full_path):
#                     success_count += 1
#     print(f"\n✅ Sync Summary: {success_count}/{total} operations synced.")

# if __name__ == "__main__":
#     main()

import os
import json
import re
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
from azure.mgmt.apimanagement.models import OperationContract, RequestContract, ResponseContract, ParameterContract, RepresentationContract

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

    for root, _, files in os.walk(split_dir):
        for file in files:
            if file.endswith(".json"):
                filepath = os.path.join(root, file)
                print(f"📂 Reading: {filepath}")
                swagger = parse_swagger_file(filepath)

                op_id = swagger.get("operationId")
                if not op_id:
                    print(f"⚠️ Skipping file missing operationId: {filepath}")
                    continue

                method, path = extract_method_and_path(file)
                if not method or not path:
                    print(f"⚠️ Could not parse method/path from filename: {file}")
                    continue

                print(f"🔄 Syncing {method.upper()} {path} ({op_id})")

                try:
                    op_contract = build_operation_contract(op_id, method, path, swagger)
                    client.api_operation.create_or_update(
                        resource_group_name=resource_group,
                        service_name=apim_name,
                        api_id=api_id,
                        operation_id=op_id,
                        parameters=op_contract,
                        if_match="*"
                    )
                    synced_count += 1
                except Exception as e:
                    print(f"❌ Failed to sync {filepath}: {str(e)}")

    print(f"✅ Sync Summary: {synced_count} operations synced.")

if __name__ == "__main__":
    sync_operations()
