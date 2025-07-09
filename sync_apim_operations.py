import os, json, subprocess

def sync_operation(swagger_file):
    with open(swagger_file) as f:
        swagger = json.load(f)

    path = list(swagger["paths"].keys())[0]
    method = list(swagger["paths"][path].keys())[0]
    operation_id = swagger["paths"][path][method].get("operationId", f"{method.upper()}_{path.strip('/').replace('/', '_')}")
    display_name = swagger["paths"][path][method].get("summary", operation_id)

    print(f"🔁 Syncing: {operation_id} | {method.upper()} {path}")

    cmd = [
        "az", "apim", "api", "operation", "create",
        "--resource-group", os.environ["APIM_RESOURCE_GROUP"],
        "--service-name", os.environ["APIM_SERVICE_NAME"],
        "--api-id", os.environ["APIM_API_NAME"],
        "--operation-id", operation_id,
        "--display-name", display_name,
        "--method", method.upper(),
        "--url-template", path,
        "--response-status-code", "200",
        "--no-wait"
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Synced {operation_id}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to sync {operation_id}: {e}")

def main():
    split_dir = "split"
    for file in os.listdir(split_dir):
        if file.endswith(".json"):
            sync_operation(os.path.join(split_dir, file))

if __name__ == "__main__":
    main()
