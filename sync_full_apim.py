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
from collections import defaultdict

# ------------------- Configuration ------------------- #
SWAGGER_URL = os.getenv("SWAGGER_URL")
SWAGGER_FILE = "swagger.json"
API_VERSION = os.getenv("API_VERSION", "v1")
AZURE_RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")
AZURE_APIM_NAME = os.getenv("AZURE_APIM_NAME")

# ------------------- Utility ------------------- #
def run(cmd):
    print(f"> {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stderr)
        sys.exit(res.returncode)
    return res.stdout

# ------------------- Steps ------------------- #
def fetch_swagger():
    print(f"🌐 Downloading Swagger from {SWAGGER_URL}")
    res = requests.get(SWAGGER_URL)
    res.raise_for_status()
    with open(SWAGGER_FILE, "w") as f:
        json.dump(res.json(), f, indent=2)
    print(f"✅ Swagger saved to {SWAGGER_FILE}")

def load_swagger():
    with open(SWAGGER_FILE) as f:
        return json.load(f)

def ensure_operation_ids(swagger):
    count = 0
    for path, methods in swagger.get("paths", {}).items():
        for method, op in methods.items():
            prefix = method.upper()
            clean_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
            op_id = f"{prefix}__{clean_path}"
            op["operationId"] = op_id
            count += 1
            print(f"🆔 Ensured: {op_id}")
    return swagger

def ensure_api_exists(api_id, api_path, display_name, version_set_id):
    check = subprocess.run(
        f"az apim api show --resource-group {AZURE_RESOURCE_GROUP} --service-name {AZURE_APIM_NAME} --api-id {api_id}",
        shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if check.returncode != 0:
        print(f"➕ API {api_id} not found, creating...")
        run(
            f"az apim api import --resource-group {AZURE_RESOURCE_GROUP} "
            f"--service-name {AZURE_APIM_NAME} --api-id {api_id} "
            f"--path {api_path} --display-name {display_name} "
            f"--specification-format OpenApi --specification-path {SWAGGER_FILE} "
            f"--api-version {API_VERSION} --api-version-set-id {version_set_id}"
        )
    else:
        print(f"✅ API {api_id} already exists.")

def ensure_version_set(version_set_id, title):
    check = subprocess.run(
        f"az apim api versionset show --resource-group {AZURE_RESOURCE_GROUP} "
        f"--service-name {AZURE_APIM_NAME} --version-set-id {version_set_id}",
        shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if check.returncode != 0:
        run(
            f"az apim api versionset create --resource-group {AZURE_RESOURCE_GROUP} "
            f"--service-name {AZURE_APIM_NAME} --version-set-id {version_set_id} "
            f"--display-name '{title} Version Set' --versioning-scheme Segment"
        )
    else:
        print(f"✅ Version set {version_set_id} already exists.")

def cleanup_removed_operations(api_id, local_op_ids):
    remote_json = run(
        f"az apim api operation list --resource-group {AZURE_RESOURCE_GROUP} "
        f"--service-name {AZURE_APIM_NAME} --api-id {api_id}"
    )
    remote_ops = json.loads(remote_json)
    for op in remote_ops:
        if op['name'] not in local_op_ids:
            print(f"🗑️ Removing stale operation: {op['name']}")
            run(
                f"az apim api operation delete --resource-group {AZURE_RESOURCE_GROUP} "
                f"--service-name {AZURE_APIM_NAME} --api-id {api_id} "
                f"--operation-id {op['name']}"
            )

def sync_operations(api_id, method, operations):
    for op_data in operations:
        path = op_data["path"]
        op = op_data["operation"]
        operation_id = op["operationId"]
        method_upper = method.upper()

        template_args = ""
        for match in re.findall(r"{(.*?)}", path):
            template_args += (
                f"--template-parameters name={match} required=true type=string "
                f"description='{match} path parameter' "
            )

        exists = subprocess.run(
            f"az apim api operation show --resource-group {AZURE_RESOURCE_GROUP} "
            f"--service-name {AZURE_APIM_NAME} --api-id {api_id} "
            f"--operation-id {operation_id}",
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        if exists.returncode == 0:
            print(f"✏️ Updating existing operation: {operation_id}")
            cmd = (
                f"az apim api operation update "
                f"--resource-group {AZURE_RESOURCE_GROUP} --service-name {AZURE_APIM_NAME} "
                f"--api-id {api_id} --operation-id {operation_id} "
                f"--set method={method_upper} urlTemplate={path} displayName={operation_id}"
            )
        else:
            print(f"🆕 Creating new operation: {operation_id}")
            cmd = (
                f"az apim api operation create "
                f"--resource-group {AZURE_RESOURCE_GROUP} --service-name {AZURE_APIM_NAME} "
                f"--api-id {api_id} --operation-id {operation_id} "
                f"--method {method_upper} --url-template {path} "
                f"--display-name {operation_id} {template_args}"
            )
        run(cmd)

def publish_revision(api_id):
    run(
        f"az apim api update --resource-group {AZURE_RESOURCE_GROUP} "
        f"--service-name {AZURE_APIM_NAME} --api-id {api_id} --set isCurrent=true"
    )
    print(f"🚀 Published revision for {api_id}")

# ------------------- Entry Point ------------------- #
def main():
    print("🚚 Starting full sync...")
    fetch_swagger()
    swagger = load_swagger()
    swagger = ensure_operation_ids(swagger)

    project_title = swagger["info"]["title"].replace(" ", "").lower()  # e.g. mg
    version_set_id = f"{project_title}-versionset"
    ensure_version_set(version_set_id, project_title)

    # Group operations by method
    grouped_ops = defaultdict(list)
    for path, methods in swagger.get("paths", {}).items():
        for method, op in methods.items():
            grouped_ops[method].append({"path": path, "operation": op})

    for method in grouped_ops:
        method_lower = method.lower()
        api_id = f"{project_title}-{API_VERSION}-{method_lower}"
        api_path = f"{API_VERSION}/{method_lower}"
        display_name = f"{project_title}-{API_VERSION}-{method_lower}"

        ensure_api_exists(api_id, api_path, display_name, version_set_id)

        ops = grouped_ops[method]
        op_ids = [op["operation"]["operationId"] for op in ops]
        cleanup_removed_operations(api_id, op_ids)
        sync_operations(api_id, method, ops)
        publish_revision(api_id)

if __name__ == "__main__":
    main()
