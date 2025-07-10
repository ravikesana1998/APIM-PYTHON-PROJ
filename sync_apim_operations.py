import os
import subprocess
import re
import json

API_NAME = os.environ.get("APIM_API_NAME", "python-api")
RESOURCE_GROUP = os.environ.get("APIM_RESOURCE_GROUP", "rg-23-6")
SERVICE_NAME = os.environ.get("APIM_SERVICE_NAME", "python-api")

def extract_method_and_path(operation_id):
    parts = operation_id.split('_', 1)
    method = parts[0]
    raw_path = '/' + parts[1].replace('_', '/')
    return method, raw_path

def extract_template_parameters(path):
    # Finds all variables in the path: {email}, {id}, etc.
    params = re.findall(r'{(\w+)}', path)
    flags = []
    for param in params:
        flags += ["--template-parameters", f"name={param}", "required=true", "type=string"]
    return flags

def import_operation(file_path, operation_id):
    print(f"📤 Syncing operation: {operation_id}")

    method, path = extract_method_and_path(operation_id)
    template_flags = extract_template_parameters(path)

    cmd = [
        "az", "apim", "api", "operation", "create",
        "--resource-group", RESOURCE_GROUP,
        "--service-name", SERVICE_NAME,
        "--api-id", API_NAME,
        "--operation-id", operation_id,
        "--display-name", operation_id,
        "--method", method,
        "--url-template", path
    ] + template_flags

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Synced {operation_id}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to sync {operation_id}: {e}")

def main():
    split_dir = "split"
    if not os.path.isdir(split_dir):
        print("❌ Directory 'split/' not found.")
        return

    for file in os.listdir(split_dir):
        if file.endswith(".json"):
            file_path = os.path.join(split_dir, file)
            operation_id = os.path.splitext(file)[0]
            import_operation(file_path, operation_id)

    print("✅ All operations synced to APIM.")

if __name__ == "__main__":
    main()
