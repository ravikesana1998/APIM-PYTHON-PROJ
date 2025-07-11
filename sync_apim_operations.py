import os
import json
import subprocess

# Get env vars
split_dir = "./split"
apim_name = os.environ["APIM_NAME"]
apim_rg = os.environ["APIM_RESOURCE_GROUP"]
apim_api = os.environ["APIM_API_NAME"]

print("📦 Syncing Swagger operations to APIM...")

synced, failed = [], []

for file_name in sorted(os.listdir(split_dir)):
    if not file_name.endswith(".json"):
        continue

    file_path = os.path.join(split_dir, file_name)

    try:
        with open(file_path, "r") as f:
            op = json.load(f)

        operation_id = op["operationId"]
        method = op["method"]
        path = op["urlTemplate"]
        description = op.get("description", operation_id)
        template_params = op.get("templateParameters", [])

        cmd = [
            "az", "apim", "api", "operation", "create",
            "--resource-group", apim_rg,
            "--service-name", apim_name,
            "--api-id", apim_api,
            "--operation-id", operation_id,
            "--url-template", path,
            "--method", method,
            "--display-name", operation_id,
            "--description", description
        ]

        for param in template_params:
            cmd += ["--template-parameters", json.dumps(param)]

        print(f"📤 Syncing operation: {file_name}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Synced: {file_name}")
            synced.append(file_name)
        else:
            print(f"❌ Failed: {file_name}")
            print("ERROR:", result.stderr.strip())
            failed.append(file_name)

    except Exception as e:
        print(f"❌ Error in {file_name}: {e}")
        failed.append(file_name)

# Summary
print(f"\n📊 Sync Summary: {len(synced)} succeeded, {len(failed)} failed.")
if failed:
    print("❌ Failed operations:")
    for f in failed:
        print(f"- {f}")
