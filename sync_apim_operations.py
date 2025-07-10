import os
import json
import subprocess

split_dir = "./split"
apim_api_name = os.environ["APIM_API_NAME"]
apim_resource_group = os.environ["APIM_RESOURCE_GROUP"]
apim_service_name = os.environ["APIM_SERVICE_NAME"]

for file_name in os.listdir(split_dir):
    if not file_name.endswith(".json"):
        continue

    file_path = os.path.join(split_dir, file_name)

    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        operation_id = data["operationId"]
        path = data["path"]
        method = data["method"]
        summary = data.get("summary", operation_id)
        parameters = data.get("parameters", [])

        print(f"📤 Syncing operation: {file_name}")

        # Start building the command
        command = [
            "az", "apim", "api", "operation", "create",
            "--resource-group", apim_resource_group,
            "--service-name", apim_service_name,
            "--api-id", apim_api_name,
            "--url-template", path,
            "--method", method,
            "--operation-id", operation_id,
            "--display-name", summary
        ]

        # Append template parameters (for path parameters)
        for param in parameters:
            if param.get("in") == "path":
                name = param.get("name")
                param_type = param.get("schema", {}).get("type", "string")
                command += ["--template-parameters", f"name={name}", f"type={param_type}"]

        # Run the command
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Synced: {file_name}")
        else:
            print(f"❌ Failed: {file_name}")
            print(result.stderr)

    except Exception as e:
        print(f"❌ Exception while processing {file_name}: {e}")
