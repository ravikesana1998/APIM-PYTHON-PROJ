import os
import subprocess
import json

# Read environment variables from the pipeline
API_NAME = os.environ.get("APIM_API_NAME")
RESOURCE_GROUP = os.environ.get("APIM_RESOURCE_GROUP")
SERVICE_NAME = os.environ.get("APIM_SERVICE_NAME")

def get_apim_operations():
    """List operation IDs currently in APIM."""
    result = subprocess.run([
        "az", "apim", "api", "operation", "list",
        "--resource-group", RESOURCE_GROUP,
        "--service-name", SERVICE_NAME,
        "--api-id", API_NAME
    ], capture_output=True, check=True, text=True)
    operations = json.loads(result.stdout)
    return [op['name'] for op in operations]

def list_operation_ids_from_split(split_dir="split"):
    """Extract expected operation IDs from split Swagger files."""
    operation_ids = set()
    for file in os.listdir(split_dir):
        if file.endswith(".json"):
            with open(os.path.join(split_dir, file)) as f:
                swagger = json.load(f)
                path = list(swagger["paths"].keys())[0]
                method = list(swagger["paths"][path].keys())[0]
                # Use the same ID logic as split_swagger_by_method.py
                op_id = f"{method.upper()}_{path.strip('/').replace('/', '_').replace('{','').replace('}','')}"
                operation_ids.add(op_id)
    return operation_ids

def delete_operation(operation_id):
    """Delete an operation from APIM."""
    print(f"🗑️ Deleting stale operation: {operation_id}")
    try:
        subprocess.run([
            "az", "apim", "api", "operation", "delete",
            "--resource-group", RESOURCE_GROUP,
            "--service-name", SERVICE_NAME,
            "--api-id", API_NAME,
            "--operation-id", operation_id,
            "--yes"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to delete operation {operation_id}: {e}")

def main():
    split_dir = "split"
    if not os.path.isdir(split_dir):
        print("❌ 'split/' directory not found.")
        return

    apim_operations = set(get_apim_operations())
    split_operations = list_operation_ids_from_split(split_dir)

    stale_operations = apim_operations - split_operations

    print(f"🔍 Found {len(stale_operations)} stale operations to delete.")
    for op in stale_operations:
        delete_operation(op)

if __name__ == "__main__":
    main()
