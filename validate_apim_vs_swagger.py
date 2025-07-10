# validate_apim_vs_swagger.py (no SDK version)

import requests
import subprocess
import os

# ---------- CONFIG ----------
SUBSCRIPTION_ID = os.environ.get("APIM_SUBSCRIPTION_ID")
RESOURCE_GROUP = os.environ.get("APIM_RESOURCE_GROUP")
SERVICE_NAME = os.environ.get("APIM_SERVICE_NAME")
API_ID = os.environ.get("APIM_API_NAME")
SWAGGER_URL = os.environ.get("APIM_SWAGGER_URL") + "/swagger/v1/swagger.json"
# ----------------------------

def get_operations_from_swagger(swagger_url):
    response = requests.get(swagger_url)
    response.raise_for_status()
    swagger = response.json()

    operations = []
    for path, methods in swagger.get('paths', {}).items():
        for method in methods:
            operations.append(f"{method.upper()} {path}")
    return set(operations)

def get_operations_from_apim():
    cmd = [
        "az", "apim", "api", "operation", "list",
        "--resource-group", RESOURCE_GROUP,
        "--service-name", SERVICE_NAME,
        "--api-id", API_ID,
        "--subscription", SUBSCRIPTION_ID,
        "--query", "[].{method: method, urlTemplate: urlTemplate}",
        "--output", "tsv"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    operations = set()
    for line in result.stdout.strip().split("\n"):
        if line:
            method, path = line.split("\t")
            operations.add(f"{method.upper()} {path}")
    return operations

def main():
    print("🔍 Comparing Swagger and APIM operations...")

    swagger_ops = get_operations_from_swagger(SWAGGER_URL)
    apim_ops = get_operations_from_apim()

    only_in_swagger = swagger_ops - apim_ops
    only_in_apim = apim_ops - swagger_ops
    in_both = swagger_ops & apim_ops

    print(f"✅ In both: {len(in_both)}")
    for op in sorted(in_both): print(f"  ✔ {op}")

    if only_in_swagger:
        print(f"\n⚠️  In Swagger but NOT in APIM: {len(only_in_swagger)}")
        for op in sorted(only_in_swagger): print(f"  ➕ {op}")

    if only_in_apim:
        print(f"\n🧹 In APIM but NOT in Swagger: {len(only_in_apim)}")
        for op in sorted(only_in_apim): print(f"  🗑️ {op}")

if __name__ == "__main__":
    main()
