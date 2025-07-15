#!/usr/bin/env python3
# sync_full_apim.py

import os, sys, json, requests, subprocess
from pathlib import Path

# ----------------- Config ----------------- #
SWAGGER_URL = os.getenv("SWAGGER_URL")
SPLIT_DIR = "split"
SWAGGER_FILE = "swagger.json"

AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
AZURE_RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")
AZURE_APIM_NAME = os.getenv("AZURE_APIM_NAME")
AZURE_APIM_API_ID = os.getenv("AZURE_APIM_API_ID")

# ----------------- Helpers ----------------- #
def run(cmd):
    print(f"> {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stderr)
        sys.exit(res.returncode)
    return res.stdout

def fetch_swagger():
    print(f"🌐 Downloading Swagger from {SWAGGER_URL}")
    res = requests.get(SWAGGER_URL)
    res.raise_for_status()
    Path(SPLIT_DIR).mkdir(exist_ok=True)
    with open(SWAGGER_FILE, "w") as f:
        json.dump(res.json(), f, indent=2)
    print(f"✅ Swagger saved to {SWAGGER_FILE}")

def ensure_operation_ids():
    with open(SWAGGER_FILE) as f:
        spec = json.load(f)

    count = 0
    for path, methods in spec.get('paths', {}).items():
        for method, op in methods.items():
            if 'operationId' not in op:
                op_id = f"{method}_{path.strip('/').replace('/', '_').replace('{', '').replace('}', '')}"
                op['operationId'] = op_id
                count += 1
                print(f"🆔 Added: {op_id}")

    with open(SWAGGER_FILE, "w") as f:
        json.dump(spec, f, indent=2)

    print(f"✅ Added {count} missing operationIds")

def split_by_operation():
    with open(SWAGGER_FILE) as f:
        spec = json.load(f)

    for path, methods in spec.get('paths', {}).items():
        for method, op in methods.items():
            op_id = op.get("operationId")
            filename = os.path.join(SPLIT_DIR, f"{op_id}.json")
            data = {
                "openapi": spec.get("openapi", "3.0.0"),
                "info": spec.get("info", {}),
                "paths": {path: {method: op}},
                "components": spec.get("components", {})
            }
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            print(f"✂️ Wrote {filename}")

def ensure_api_exists():
    show_cmd = f"az apim api show --resource-group {AZURE_RESOURCE_GROUP} --service-name {AZURE_APIM_NAME} --api-id {AZURE_APIM_API_ID}"
    result = subprocess.run(show_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode != 0:
        print("➕ API not found, creating...")
        import_cmd = (
            f"az apim api import --resource-group {AZURE_RESOURCE_GROUP} "
            f"--service-name {AZURE_APIM_NAME} --api-id {AZURE_APIM_API_ID} "
            f"--path {AZURE_APIM_API_ID} --display-name {AZURE_APIM_API_ID} "
            f"--specification-format OpenApi --specification-path {SWAGGER_FILE}"
        )
        run(import_cmd)
    else:
        print("✅ API already exists in APIM.")

def cleanup_removed_operations():
    with open(SWAGGER_FILE) as f:
        spec = json.load(f)
    local_ops = {op.get('operationId') for m in spec['paths'].values() for op in m.values()}
    remote_json = run(f"az apim api operation list --resource-group {AZURE_RESOURCE_GROUP} --service-name {AZURE_APIM_NAME} --api-id {AZURE_APIM_API_ID}")
    remote_ops = json.loads(remote_json)
    for op in remote_ops:
        if op['name'] not in local_ops:
            print(f"🗑️ Removing stale operation: {op['name']}")
            run(f"az apim api operation delete --resource-group {AZURE_RESOURCE_GROUP} --service-name {AZURE_APIM_NAME} --api-id {AZURE_APIM_API_ID} --operation-id {op['name']} --yes")

def sync_operations():
    for file in os.listdir(SPLIT_DIR):
        if not file.endswith(".json"):
            continue

        path = os.path.join(SPLIT_DIR, file)
        with open(path) as f:
            op_spec = json.load(f)

        [swagger_path] = list(op_spec["paths"].keys())
        [method] = list(op_spec["paths"][swagger_path].keys())
        operation = op_spec["paths"][swagger_path][method]
        operation_id = operation.get("operationId")

        print(f"🔄 Syncing operation: {operation_id}")

        # Build command
        cmd = (
            f"az apim api operation create "
            f"--resource-group {AZURE_RESOURCE_GROUP} "
            f"--service-name {AZURE_APIM_NAME} "
            f"--api-id {AZURE_APIM_API_ID} "
            f"--operation-id {operation_id} "
            f"--method {method.upper()} "
            f"--url-template {swagger_path} "
            f"--display-name {operation_id} "
        )

        # Optional: Add description if available
        if "description" in operation:
            cmd += f"--description \"{operation['description']}\" "

        run(cmd)


def publish_revision():
    run(
        f"az apim api update --resource-group {AZURE_RESOURCE_GROUP} "
        f"--service-name {AZURE_APIM_NAME} --api-id {AZURE_APIM_API_ID} "
        f"--set isCurrent=true"
    )
    print("🚀 Published latest revision")

def main():
    fetch_swagger()
    ensure_operation_ids()
    split_by_operation()
    ensure_api_exists()
    cleanup_removed_operations()
    sync_operations()
    publish_revision()

if __name__ == "__main__":
    main()
