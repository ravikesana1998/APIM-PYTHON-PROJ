import os
import json
import traceback
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
from azure.mgmt.apimanagement.models import (
    OperationContract,
    RequestContract,
    ParameterContract,
    ResponseContract,
    RepresentationContract
)

SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
RESOURCE_GROUP = os.environ["AZURE_RESOURCE_GROUP"]
SERVICE_NAME = os.environ["AZURE_APIM_NAME"]
API_ID = os.environ["AZURE_APIM_API_ID"]
SPLIT_DIR = "split"

credential = DefaultAzureCredential()
client = ApiManagementClient(credential, SUBSCRIPTION_ID)

def get_operation_info(filepath):
    print(f"📂 Reading: {filepath}")
    with open(filepath, "r") as f:
        data = json.load(f)

    paths = data.get("paths", {})
    if not paths or len(paths) != 1:
        raise ValueError(f"Invalid or multiple paths in: {filepath}")
    
    path = next(iter(paths))
    method_dict = paths[path]
    if not method_dict or len(method_dict) != 1:
        raise ValueError(f"Invalid or multiple methods in: {filepath}")
    
    method = next(iter(method_dict)).upper()
    operation = method_dict[method.lower()]
    operation_id = operation.get("operationId")
    if not operation_id:
        raise ValueError(f"Missing operationId in {filepath}")
    
    print(f"✅ Parsed operationId={operation_id}, method={method}, path={path}")
    return {
        "id": operation_id,
        "method": method,
        "url_template": path,
        "definition": operation,
    }

def create_or_update_operation(op):
    print(f"\n🔄 Syncing {op['method']} {op['url_template']} ({op['id']})")
    definition = op["definition"]

    # Parse parameters
    parameters = definition.get("parameters", [])
    print(f"🔎 Found {len(parameters)} parameters")

    query_params = [
        ParameterContract(
            name=p["name"],
            required=p.get("required", False),
            type="string",
            description=p.get("description", "")
        )
        for p in parameters if p.get("in") == "query"
    ]
    path_params = [
        ParameterContract(
            name=p["name"],
            required=p.get("required", False),
            type="string",
            description=p.get("description", "")
        )
        for p in parameters if p.get("in") == "path"
    ]

    # Parse request body
    request_body = definition.get("requestBody", {})
    req_schema = request_body.get("content", {}).get("application/json", {}).get("schema", {})
    request_desc = request_body.get("description", "")

    print(f"📦 Request body schema: {'present' if req_schema else 'none'}")

    request = RequestContract(
        description=request_desc,
        query_parameters=query_params,
        template_parameters=path_params,
        representations=[
            RepresentationContract(content_type="application/json", schema=req_schema)
        ] if req_schema else []
    )

    # Parse responses
    responses = definition.get("responses", {})
    response_objs = [
        ResponseContract(
            status_code=str(status),
            description=resp.get("description", "")
        )
        for status, resp in responses.items()
    ]
    print(f"📨 Found {len(response_objs)} responses")

    # Build operation contract
    operation_contract = OperationContract(
        display_name=op["id"],
        method=op["method"],
        url_template=op["url_template"],
        request=request,
        responses=response_objs
    )

    # DEBUG OUTPUT OF CONTRACT
    print(f"🛠️ OperationContract built:\n"
          f"  - Display Name: {operation_contract.display_name}\n"
          f"  - Method: {operation_contract.method}\n"
          f"  - URL Template: {operation_contract.url_template}\n"
          f"  - Query Params: {[p.name for p in query_params]}\n"
          f"  - Path Params: {[p.name for p in path_params]}\n"
          f"  - Representations: {len(request.representations)}\n"
          f"  - Responses: {len(response_objs)}")

    # Call Azure API
    client.api_operation.create_or_update(
        resource_group_name=RESOURCE_GROUP,
        service_name=SERVICE_NAME,
        api_id=API_ID,
        operation_id=op["id"],
        parameters=operation_contract
    )
    print(f"✅ Operation synced to APIM: {op['id']}")

def main():
    if not os.path.isdir(SPLIT_DIR):
        print(f"❌ Folder '{SPLIT_DIR}' not found.")
        return

    files = [
        os.path.join(root, f)
        for root, _, fs in os.walk(SPLIT_DIR)
        for f in fs if f.endswith(".json")
    ]

    print(f"📦 Syncing {len(files)} Swagger operations to APIM...")
    success = 0

    for file in files:
        try:
            op = get_operation_info(file)
            create_or_update_operation(op)
            success += 1
        except Exception as e:
            print(f"❌ Failed to sync {file}: {e}")
            traceback.print_exc()

    print(f"\n✅ Sync Summary: {success} operations synced.")

if __name__ == "__main__":
    main()
