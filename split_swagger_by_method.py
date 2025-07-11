import os
import json
import hashlib
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient

# Env vars required from pipeline
SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
RESOURCE_GROUP = os.environ["AZURE_RESOURCE_GROUP"]
SERVICE_NAME = os.environ["AZURE_APIM_NAME"]
API_ID = os.environ["AZURE_APIM_API_ID"]
SWAGGER_OPERATIONS_DIR = "./split"

credential = DefaultAzureCredential()
client = ApiManagementClient(credential, SUBSCRIPTION_ID)

def compute_hash(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()

def list_operation_files():
    for root, _, files in os.walk(SWAGGER_OPERATIONS_DIR):
        for f in files:
            if f.endswith(".json"):
                yield os.path.join(root, f)

def extract_operation_info(swagger_file_path):
    with open(swagger_file_path, "r") as f:
        swagger = json.load(f)

    path, path_item = next(iter(swagger["paths"].items()))
    method, op = next(iter(path_item.items()))
    operation_id = op.get("operationId")

    return {
        "file": swagger_file_path,
        "path": path,
        "method": method.lower(),
        "operation_id": operation_id,
        "definition": op,
        "hash": compute_hash(op)
    }

def operation_exists(operation_id):
    try:
        op = client.api_operation.get(RESOURCE_GROUP, SERVICE_NAME, API_ID, operation_id)
        return op
    except:
        return None

def get_remote_operation_hash(op):
    # You can optionally store hashes in a custom tag or use the full operation content
    return None  # Simplify logic by always updating for now

def create_or_update_operation(info):
    op_id = info["operation_id"]
    path = info["path"]
    method = info["method"]
    op_def = info["definition"]

    params = op_def.get("parameters", [])
    responses = op_def.get("responses", {})

    # Simplified request body support
    request_body = op_def.get("requestBody", {})
    req_desc = request_body.get("description", "")
    req_schema = request_body.get("content", {}).get("application/json", {}).get("schema", {})

    print(f"🔄 Syncing operation: {op_id} ({method.upper()} {path})")

    client.api_operation.create_or_update(
        resource_group_name=RESOURCE_GROUP,
        service_name=SERVICE_NAME,
        api_id=API_ID,
        operation_id=op_id,
        parameters={
            "display_name": op_id,
            "method": method.upper(),
            "url_template": path,
            "request": {
                "query_parameters": [p for p in params if p["in"] == "query"],
                "template_parameters": [p for p in params if p["in"] == "path"],
                "description": req_desc,
                "representation": [{
                    "content_type": "application/json",
                    "schema": req_schema,
                }] if req_schema else [],
            },
            "responses": [
                {
                    "status_code": status,
                    "description": response.get("description", "")
                }
                for status, response in responses.items()
            ]
        }
    )

def main():
    operation_files = list(list_operation_files())
    print(f"📁 Found {len(operation_files)} Swagger operation files to sync.")

    if len(operation_files) == 0:
        print("⚠️ No Swagger operation files found. Exiting.")
        return

    synced = 0
    for file_path in operation_files:
        try:
            info = extract_operation_info(file_path)
            op_id = info["operation_id"]
            if not op_id:
                print(f"⚠️ Skipping: No operationId in {file_path}")
                continue

            existing = operation_exists(op_id)
            if not existing:
                print(f"🆕 Creating new operation: {op_id}")
                create_or_update_operation(info)
                synced += 1
            else:
                # For now, always update. (You can add hash comparison here if needed.)
                print(f"🔁 Updating existing operation: {op_id}")
                create_or_update_operation(info)
                synced += 1

        except Exception as e:
            print(f"❌ Failed to sync {file_path}: {e}")

    print(f"✅ Sync Summary: {synced} succeeded.")

if __name__ == "__main__":
    main()
