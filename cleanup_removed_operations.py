# cleanup_removed_operations.py
import os
import json
import subprocess

API_NAME = os.environ.get("APIM_API_NAME")
RESOURCE_GROUP = os.environ.get("APIM_RESOURCE_GROUP")
SERVICE_NAME = os.environ.get("APIM_SERVICE_NAME")

def list_current_apim_operations():
    try:
        print("📡 Listing existing APIM operations...")
        output = subprocess.check_output([
            "az", "apim", "api", "operation", "list",
            "--resource-group", RESOURCE_GROUP,
            "--service-name", SERVICE_NAME,
            "--api-id", API_NAME,
            "-o", "json"
        ], text=True)
        return {op["name"] for op in json.loads(output)}
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to list operations: {e.output}")
        return set()

def list_operation_ids_from_split(split_dir="split"):
    operation_ids = set()
    for f in os.listdir(split_dir):
        if f.endswith(".json"):
            with open(os.path.join(split_dir, f)) as file:
                swagger = json.load(file)
                path = list(swagger["paths"].keys())[0]
                method = list(swagger["paths"][path].keys())[0]
                op = swagger["paths"][path][method]
                op_id = op.get("operationId", f"{method.upper()}_{path.strip('/').replace('/', '_')}")
                operation_ids.add(op_id)
    return operation_ids

def delete_operation(op_name):
    print(f"🗑 Deleting stale operation: {op_name}")
    try:
        subprocess.run([
            "az", "apim", "api", "operation", "delete",
            "--resource-group", RESOURCE_GROUP,
            "--service-name", SERVICE_NAME,
            "--api-id", API_NAME,
            "--operation-id", op_name,
            "--yes"
        ], check=True)
        print(f"✅ Deleted: {op_name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to delete {op_name}: {e}")

def main():
    split_ops = list_operation_ids_from_split()
    apim_ops = list_current_apim_operations()

    stale_ops = apim_ops - split_ops
    print(f"🔍 Found {len(stale_ops)} stale operations to delete.")

    for op in stale_ops:
        delete_operation(op)

if __name__ == "__main__":
    main()
