import json
import sys
import hashlib

def generate_operation_id(method, path):
    base = f"{method}_{path}"
    clean = base.replace("{", "").replace("}", "").replace("/", "_").replace("-", "_").strip("_")
    hashed = hashlib.md5(base.encode()).hexdigest()[:6]
    return f"{clean}_{hashed}"

def add_operation_ids(swagger_path):
    with open(swagger_path, "r") as f:
        swagger = json.load(f)

    modified = False
    for path, methods in swagger.get("paths", {}).items():
        for method, operation in methods.items():
            if "operationId" not in operation:
                operation_id = generate_operation_id(method, path)
                operation["operationId"] = operation_id
                print(f"➕ Added operationId to {method.upper()} {path}: {operation_id}")
                modified = True

    if modified:
        with open(swagger_path, "w") as f:
            json.dump(swagger, f, indent=2)
        print("✅ Updated Swagger with missing operationId values.")
    else:
        print("✅ All operations already have operationId.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_operation_ids.py <swagger-path>")
        sys.exit(1)

    add_operation_ids(sys.argv[1])
