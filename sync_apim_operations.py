import os
import json
import subprocess

split_dir = "./split"
resource_group = os.environ["APIM_RESOURCE_GROUP"]
service_name = os.environ["APIM_SERVICE_NAME"]
api_id = os.environ["APIM_API_NAME"]

def operation_exists(operation_id):
    result = subprocess.run([
        "az", "apim", "api", "operation", "show",
        "--resource-group", resource_group,
        "--service-name", service_name,
        "--api-id", api_id,
        "--operation-id", operation_id
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return result.returncode == 0

for filename in os.listdir(split_dir):
    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(split_dir, filename)
    with open(filepath, "r") as f:
        data = json.load(f)

    method = list(data["paths"].values())[0]
    method_name = list(method.keys())[0].upper()

    url_template = list(data["paths"].keys())[0]
    operation_id = filename.replace(".json", "")
    display_name = operation_id

    exists = operation_exists(operation_id)

    cmd = [
        "az", "apim", "api", "operation", "update" if exists else "create",
        "--resource-group", resource_group,
        "--service-name", service_name,
        "--api-id", api_id,
        "--operation-id", operation_id,
        "--display-name", display_name,
        "--method", method_name,
        "--url-template", url_template,
        "--description", "Auto-synced via pipeline"
    ]

    print(f"{'🔁 Updating' if exists else '➕ Creating'} operation: {operation_id}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"❌ Failed: {operation_id}")
        print(result.stderr.decode())
    else:
        print(f"✅ Synced: {operation_id}")
