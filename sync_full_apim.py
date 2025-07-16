# #!/usr/bin/env python3
# # sync_full_apim.py

# import os, sys, json, requests, subprocess, re
# from pathlib import Path

# # ------------------- Configuration ------------------- #
# SWAGGER_URL = os.getenv("SWAGGER_URL")
# SPLIT_DIR = "split"
# SWAGGER_FILE = "swagger.json"

# AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
# AZURE_RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")
# AZURE_APIM_NAME = os.getenv("AZURE_APIM_NAME")
# AZURE_APIM_API_ID = os.getenv("AZURE_APIM_API_ID")

# # ------------------- Utility Functions ------------------- #
# def run(cmd):
#     print(f"> {cmd}")
#     res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
#     if res.returncode != 0:
#         print(res.stderr)
#         sys.exit(res.returncode)
#     return res.stdout

# # ------------------- Core Sync Steps ------------------- #
# def fetch_swagger():
#     print(f"🌐 Downloading Swagger from {SWAGGER_URL}")
#     res = requests.get(SWAGGER_URL)
#     res.raise_for_status()
#     Path(SPLIT_DIR).mkdir(exist_ok=True)
#     with open(SWAGGER_FILE, "w") as f:
#         json.dump(res.json(), f, indent=2)
#     print(f"✅ Swagger saved to {SWAGGER_FILE}")

# def ensure_operation_ids():
#     with open(SWAGGER_FILE) as f:
#         spec = json.load(f)

#     count = 0
#     for path, methods in spec.get("paths", {}).items():
#         for method, op in methods.items():
#             if "operationId" not in op:
#                 op_id = f"{method}_{path.strip('/').replace('/', '_').replace('{', '').replace('}', '')}"
#                 op["operationId"] = op_id
#                 count += 1
#                 print(f"🆔 Added: {op_id}")

#     with open(SWAGGER_FILE, "w") as f:
#         json.dump(spec, f, indent=2)
#     print(f"✅ Added {count} missing operationIds")

# def split_by_operation():
#     with open(SWAGGER_FILE) as f:
#         spec = json.load(f)

#     for path, methods in spec.get("paths", {}).items():
#         for method, op in methods.items():
#             op_id = op.get("operationId")
#             filename = os.path.join(SPLIT_DIR, f"{op_id}.json")
#             data = {
#                 "openapi": spec.get("openapi", "3.0.0"),
#                 "info": spec.get("info", {}),
#                 "paths": {path: {method: op}},
#                 "components": spec.get("components", {})
#             }
#             with open(filename, "w") as f:
#                 json.dump(data, f, indent=2)
#             print(f"✂️ Wrote {filename}")

# def ensure_api_exists():
#     result = subprocess.run(
#         f"az apim api show --resource-group {AZURE_RESOURCE_GROUP} --service-name {AZURE_APIM_NAME} --api-id {AZURE_APIM_API_ID}",
#         shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#     if result.returncode != 0:
#         print("➕ API not found, creating...")
#         run(
#             f"az apim api import --resource-group {AZURE_RESOURCE_GROUP} "
#             f"--service-name {AZURE_APIM_NAME} --api-id {AZURE_APIM_API_ID} "
#             f"--path {AZURE_APIM_API_ID} --display-name {AZURE_APIM_API_ID} "
#             f"--specification-format OpenApi --specification-path {SWAGGER_FILE}"
#         )
#     else:
#         print("✅ API already exists in APIM.")

# def cleanup_removed_operations():
#     with open(SWAGGER_FILE) as f:
#         spec = json.load(f)
#     local_ops = {op.get('operationId') for m in spec['paths'].values() for op in m.values()}
#     remote_json = run(
#         f"az apim api operation list --resource-group {AZURE_RESOURCE_GROUP} "
#         f"--service-name {AZURE_APIM_NAME} --api-id {AZURE_APIM_API_ID}"
#     )
#     remote_ops = json.loads(remote_json)
#     for op in remote_ops:
#         if op['name'] not in local_ops:
#             print(f"🗑️ Removing stale operation: {op['name']}")
#             run(
#                 f"az apim api operation delete --resource-group {AZURE_RESOURCE_GROUP} "
#                 f"--service-name {AZURE_APIM_NAME} --api-id {AZURE_APIM_API_ID} "
#                 f"--operation-id {op['name']}"
#             )

# def sync_operations():
#     for fname in os.listdir(SPLIT_DIR):
#         if not fname.endswith(".json"):
#             continue

#         path = os.path.join(SPLIT_DIR, fname)
#         with open(path) as f:
#             spec = json.load(f)

#         paths = list(spec["paths"].keys())
#         if not paths:
#             continue

#         swagger_path = paths[0]
#         method = list(spec["paths"][swagger_path].keys())[0]
#         operation = spec["paths"][swagger_path][method]
#         operation_id = operation.get("operationId")

#         # Extract path parameters for create
#         template_params = re.findall(r"{(.*?)}", swagger_path)
#         template_args = ""
#         for param in template_params:
#             template_args += (
#                 f"--template-parameters name={param} required=true type=string "
#                 f"description='{param} path parameter' "
#             )

#         print(f"🔄 Syncing operation: {operation_id}")

#         # Check if the operation exists
#         check_cmd = (
#             f"az apim api operation show --resource-group {AZURE_RESOURCE_GROUP} "
#             f"--service-name {AZURE_APIM_NAME} "
#             f"--api-id {AZURE_APIM_API_ID} "
#             f"--operation-id {operation_id}"
#         )
#         exists = subprocess.run(check_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

#         if exists.returncode == 0:
#             print(f"✏️ Updating existing operation: {operation_id}")
#             # UPDATE: No --template-parameters allowed
#             cmd = (
#                 f"az apim api operation update "
#                 f"--resource-group {AZURE_RESOURCE_GROUP} "
#                 f"--service-name {AZURE_APIM_NAME} "
#                 f"--api-id {AZURE_APIM_API_ID} "
#                 f"--operation-id {operation_id} "
#                 f"--set method={method.upper()} urlTemplate={swagger_path} displayName={operation_id}"
#             )
#         else:
#             print(f"🆕 Creating new operation: {operation_id}")
#             cmd = (
#                 f"az apim api operation create "
#                 f"--resource-group {AZURE_RESOURCE_GROUP} "
#                 f"--service-name {AZURE_APIM_NAME} "
#                 f"--api-id {AZURE_APIM_API_ID} "
#                 f"--operation-id {operation_id} "
#                 f"--method {method.upper()} "
#                 f"--url-template {swagger_path} "
#                 f"--display-name {operation_id} "
#                 f"{template_args}"
#             )

#         run(cmd)

# def publish_revision():
#     run(
#         f"az apim api update --resource-group {AZURE_RESOURCE_GROUP} "
#         f"--service-name {AZURE_APIM_NAME} --api-id {AZURE_APIM_API_ID} "
#         f"--set isCurrent=true"
#     )
#     print("🚀 Published latest revision")

# # ------------------- Entry Point ------------------- #
# def main():
#     print("🚚 Starting full sync process...")
#     fetch_swagger()
#     ensure_operation_ids()
#     split_by_operation()
#     ensure_api_exists()
#     cleanup_removed_operations()
#     sync_operations()
#     publish_revision()

# if __name__ == "__main__":
#     main()


#!/usr/bin/env python3
# sync_full_apim.py

#!/usr/bin/env python3
# sync_full_apim.py
import os, sys, json, requests, subprocess, re
from pathlib import Path

# ------------------- Configuration ------------------- #
SWAGGER_URL = os.getenv("SWAGGER_URL")
SPLIT_DIR = "split"
SWAGGER_FILE = "swagger.json"

AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
AZURE_RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")
AZURE_APIM_NAME = os.getenv("AZURE_APIM_NAME")
API_BASE_ID = os.getenv("AZURE_APIM_API_ID")
API_VERSION = os.getenv("API_VERSION", "v1")  # default to v1
API_ID = f"{API_BASE_ID}-{API_VERSION}"
API_PATH = f"{API_VERSION}"
VERSION_SET_ID = f"{API_BASE_ID}-versionset"

# ------------------- Utility ------------------- #
def run(cmd):
    print(f"> {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stderr)
        sys.exit(res.returncode)
    return res.stdout

# ------------------- Sync Steps ------------------- #
def fetch_swagger():
    print(f"\U0001F310 Downloading Swagger from {SWAGGER_URL}")
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
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if "operationId" not in op:
                op_id = f"{method}_{path.strip('/').replace('/', '_').replace('{', '').replace('}', '')}"
                op["operationId"] = op_id
                count += 1
                print(f"🆔 Added: {op_id}")
            else:
                # Prefix with method for APIM UI grouping
                op_id = op["operationId"]
                if not op_id.lower().startswith(method.lower() + "_"):
                    prefixed = f"{method}_{op_id}"
                    op["operationId"] = prefixed
                    print(f"📝 Prefixed operationId: {prefixed}")
    with open(SWAGGER_FILE, "w") as f:
        json.dump(spec, f, indent=2)
    print(f"✅ OperationIds ensured/prefixed")

def split_by_operation():
    with open(SWAGGER_FILE) as f:
        spec = json.load(f)
    for path, methods in spec.get("paths", {}).items():
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

def ensure_version_set():
    print("📦 Creating version set (if not exists)...")
    check = subprocess.run(
        f"az apim api versionset show --resource-group {AZURE_RESOURCE_GROUP} "
        f"--service-name {AZURE_APIM_NAME} --version-set-id {VERSION_SET_ID}",
        shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if check.returncode != 0:
        run(
            f"az apim api versionset create --resource-group {AZURE_RESOURCE_GROUP} "
            f"--service-name {AZURE_APIM_NAME} --version-set-id {VERSION_SET_ID} "
            f"--display-name '{API_BASE_ID} Version Set' --versioning-scheme Segment"
        )
    else:
        print("✅ Version set already exists.")

def ensure_api_exists():
    check = subprocess.run(
        f"az apim api show --resource-group {AZURE_RESOURCE_GROUP} --service-name {AZURE_APIM_NAME} "
        f"--api-id {API_ID}",
        shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if check.returncode != 0:
        print("➕ API not found, importing...")
        run(
            f"az apim api import --resource-group {AZURE_RESOURCE_GROUP} "
            f"--service-name {AZURE_APIM_NAME} --api-id {API_ID} "
            f"--path {API_PATH} --display-name {API_ID} "
            f"--specification-format OpenApi --specification-path {SWAGGER_FILE} "
            f"--api-version {API_VERSION} --api-version-set-id {VERSION_SET_ID}"
        )
    else:
        print("✅ API already exists in APIM.")

def cleanup_removed_operations():
    with open(SWAGGER_FILE) as f:
        spec = json.load(f)
    local_ops = {op.get('operationId') for m in spec['paths'].values() for op in m.values()}
    remote_json = run(
        f"az apim api operation list --resource-group {AZURE_RESOURCE_GROUP} "
        f"--service-name {AZURE_APIM_NAME} --api-id {API_ID}"
    )
    remote_ops = json.loads(remote_json)
    for op in remote_ops:
        if op['name'] not in local_ops:
            print(f"🗑️ Removing stale operation: {op['name']}")
            run(
                f"az apim api operation delete --resource-group {AZURE_RESOURCE_GROUP} "
                f"--service-name {AZURE_APIM_NAME} --api-id {API_ID} "
                f"--operation-id {op['name']}"
            )

def sync_operations():
    for fname in os.listdir(SPLIT_DIR):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(SPLIT_DIR, fname)
        with open(path) as f:
            spec = json.load(f)
        paths = list(spec["paths"].keys())
        if not paths:
            continue
        swagger_path = paths[0]
        method = list(spec["paths"][swagger_path].keys())[0]
        operation = spec["paths"][swagger_path][method]
        operation_id = operation.get("operationId")

        template_params = re.findall(r"{(.*?)}", swagger_path)
        template_args = ""
        for param in template_params:
            template_args += (
                f"--template-parameters name={param} required=true type=string "
                f"description='{param} path parameter' "
            )

        print(f"🔄 Syncing operation: {operation_id}")
        exists = subprocess.run(
            f"az apim api operation show --resource-group {AZURE_RESOURCE_GROUP} "
            f"--service-name {AZURE_APIM_NAME} --api-id {API_ID} "
            f"--operation-id {operation_id}",
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        if exists.returncode == 0:
            print(f"✏️ Updating existing operation: {operation_id}")
            cmd = (
                f"az apim api operation update "
                f"--resource-group {AZURE_RESOURCE_GROUP} --service-name {AZURE_APIM_NAME} "
                f"--api-id {API_ID} --operation-id {operation_id} "
                f"--set method={method.upper()} urlTemplate={swagger_path} displayName={operation_id}"
            )
            run(cmd)
        else:
            print(f"🆕 Creating new operation: {operation_id}")
            cmd = (
                f"az apim api operation create "
                f"--resource-group {AZURE_RESOURCE_GROUP} --service-name {AZURE_APIM_NAME} "
                f"--api-id {API_ID} --operation-id {operation_id} "
                f"--method {method.upper()} --url-template {swagger_path} "
                f"--display-name {operation_id} {template_args}"
            )
            run(cmd)

        # 🏷️ Apply tag via REST API
        tag_payload = json.dumps({
            "properties": {
                "tags": [method.upper()]
            }
        })
        rest_cmd = (
            f"az rest --method patch "
            f"--uri https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/{AZURE_RESOURCE_GROUP}/"
            f"providers/Microsoft.ApiManagement/service/{AZURE_APIM_NAME}/apis/{API_ID}/operations/{operation_id}?api-version=2022-08-01 "
            f"--body '{tag_payload}'"
        )
        run(rest_cmd)

def publish_revision():
    run(
        f"az apim api update --resource-group {AZURE_RESOURCE_GROUP} "
        f"--service-name {AZURE_APIM_NAME} --api-id {API_ID} "
        f"--set isCurrent=true"
    )
    print("🚀 Published latest revision")

# ------------------- Entry Point ------------------- #
def main():
    print("🚚 Starting full sync process...")
    fetch_swagger()
    ensure_operation_ids()
    split_by_operation()
    ensure_version_set()
    ensure_api_exists()
    cleanup_removed_operations()
    sync_operations()
    publish_revision()

if __name__ == "__main__":
    main()
