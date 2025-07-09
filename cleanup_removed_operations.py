import os
import json
import subprocess

API_NAME = os.environ.get("APIM_API_NAME", "python-api")
RESOURCE_GROUP = os.environ.get("APIM_RESOURCE_GROUP", "rg-23-6")
SERVICE_NAME = os.environ.get("APIM_SERVICE_NAME", "python-api")


def list_current_api_operations():
    cmd = [
        "az", "apim", "api", "operation", "list",
        "--resource-group", RESOURCE_GROUP,
        "--service-name", SERVICE_NAME,
        "--api-id", API_NAME,
        "--query", "[].name",
        "-o", "json"
    ]
    try:
        output = subprocess.check_output(cmd, text=True)
        return set(json.loads(output))
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to list APIM operations: {e}")
        return set()


def list_split_operations(split_dir):
    return set(
        os.path.splitext(f)[0]
        for f in os.listdir(split_dir)
        if f.endswith(".json")
    )


def delete_operation(op_name):
    print(f"🗑 Deleting stale operation: {op_name}")
    cmd = [
        "az", "apim", "api", "operation", "delete",
        "--resource-group", RESOURCE_GROUP,
        "--service-name", SERVICE_NAME,
        "--api-id", API_NAME,
        "--operation-id", op_name,
        "--yes"
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Deleted: {op_name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to delete {op_name}: {e}")


def main():
    split_dir = "split"
    if not os.path.isdir(split_dir):
        print("❌ Directory 'split/' not found.")
        return

    apim_ops = list_current_api_operations()
    swagger_ops = list_split_operations(split_dir)

    stale_ops = apim_ops - swagger_ops
    if not stale_ops:
        print("✅ No stale operations to remove.")
    else:
        for op in stale_ops:
            delete_operation(op)


if __name__ == "__main__":
    main()

