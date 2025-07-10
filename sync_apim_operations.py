import os
import json
import subprocess

split_dir = "./split"

# Environment variables
apim_name = os.environ["APIM_NAME"]
apim_rg = os.environ["APIM_RESOURCE_GROUP"]
apim_api = os.environ["APIM_API_NAME"]

print("📦 Syncing Swagger operations to APIM...")

for file_name in os.listdir(split_dir):
    if not file_name.endswith(".json"):
        continue

    file_path = os.path.join(split_dir, file_name)

    with open(file_path, "r") as f:
        data = json.load(f)

    try:
        operation_id = data.get("operationId") or file_name.replace(".json", "")
        method = data["method"]
        path = data["path"]
        summary = data.get("summary") or operation_id  # Fallback if summary missing
        parameters = data.get("parameters", [])

        # Build --template-parameters arguments
        template_args = []
        for p in parameters:
            if "name" in p and p.get("in") == "path":
                template_args += ["--template-parameters", f"name={p['name']}"]

        command = [
            "az", "apim", "api", "operation", "create",
            "--resource-group", apim_rg,
            "--service-name", apim_name,
            "--api-id", apim_api,
            "--operation-id", operation_id,
            "--url-template", path,
            "--method", method,
            "--display-name", summary,
            "--description", summary
        ]

        # Append path parameters if any
        command += template_args

        print(f"📤 Syncing operation: {file_name}")
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Synced: {file_name}")
        else:
            print(f"❌ Failed: {file_name}")
            print("ERROR:", result.stderr.strip())

    except KeyError as e:
        print(f"❌ Failed: {file_name}")
        print(f"ERROR: Missing key: {str(e)}")

    except Exception as e:
        print(f"❌ Failed: {file_name}")
        print("ERROR:", str(e))
