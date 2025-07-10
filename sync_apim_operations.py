import os
import json
import glob
import subprocess

apim_rg = os.environ["APIM_RESOURCE_GROUP"]
apim_service = os.environ["APIM_SERVICE_NAME"]
apim_api = os.environ["APIM_API_NAME"]

for filepath in glob.glob("split/*.json"):
    with open(filepath) as f:
        data = json.load(f)

    path = list(data["paths"].keys())[0]
    method = list(data["paths"][path].keys())[0].upper()
    operation_id = os.path.splitext(os.path.basename(filepath))[0]

    # Create or update operation
    print(f"📤 Syncing operation: {operation_id}")
    result = subprocess.run([
        "az", "apim", "api", "operation", "create",
        "--resource-group", apim_rg,
        "--service-name", apim_service,
        "--api-id", apim_api,
        "--operation-id", operation_id,
        "--display-name", operation_id,
        "--method", method,
        "--url-template", path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        print(f"✅ Synced: {operation_id}")
    else:
        print(f"❌ Failed: {operation_id}\n{result.stderr}")
