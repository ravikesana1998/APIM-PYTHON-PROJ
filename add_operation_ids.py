import json
import sys
import hashlib

def generate_operation_id(method, path):
    # Create a safe and unique operationId using method + path hash
    clean_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
    base = f"{method.lower()}_{clean_path}"
    hash_suffix = hashlib.md5(path.encode()).hexdigest()[:6]
    return f"{base}_{hash_suffix}"

def add_operation_ids(swagger_file):
    with open(swagger_file, "r") as f:
        swagger = json.load(f)

    updated = False
    for path, methods in swagger.get("paths", {}).items():
        for method, operation in methods.items():
            if "operationId" not in operation:
                generated_id = generate_operation_id(method, path)
                operation["operationId"] = generated_id
                print(f"🆕 Added operationId for {method.upper()} {path}: {generated_id}")
                updated = True
            else:
                print(f"✅ Found operationId for {method.upper()} {path}: {operation['operationId']}")

    if updated:
        with open(swagger_file, "w") as f:
            json.dump(swagger, f, indent=2)
        print("💾 Updated Swagger file with missing operationIds.")
    else:
        print("👍 All operations already have operationIds. No changes made.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_operation_ids.py <swagger-file>")
        sys.exit(1)

    add_operation_ids(sys.argv[1])
