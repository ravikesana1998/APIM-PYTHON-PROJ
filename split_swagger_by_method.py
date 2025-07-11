import os
import json
import hashlib
import requests

SWAGGER_URL = "https://pythonapps-e0hmd6eucuf9acg5.canadacentral-01.azurewebsites.net/swagger/v1/swagger.json"
OUTPUT_DIR = "./split"

def generate_operation_id(method, path, tag):
    base = f"{method}_{path.replace('/', '_')}"
    hash_suffix = hashlib.md5(base.encode()).hexdigest()[:8]
    return f"{method}_{path.strip('/').replace('/', '_')}_{hash_suffix}"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    print("📥 Downloading Swagger...")
    response = requests.get(SWAGGER_URL)
    response.raise_for_status()
    swagger = response.json()

    components = swagger.get("components", {})
    paths = swagger.get("paths", {})

    ensure_dir(OUTPUT_DIR)
    total = 0
    generated = []

    for path, methods in paths.items():
        for method, operation in methods.items():
            tag = (operation.get("tags") or ["Default"])[0]
            operation_id = operation.get("operationId")
            if not operation_id:
                operation_id = generate_operation_id(method, path, tag)
                operation["operationId"] = operation_id
                generated.append(operation_id)

            out_dir = os.path.join(OUTPUT_DIR, tag)
            ensure_dir(out_dir)
            out_file = os.path.join(out_dir, f"{method.upper()}_{operation_id}.json")

            new_spec = {
                "openapi": swagger.get("openapi", "3.0.0"),
                "info": swagger.get("info", {}),
                "paths": {
                    path: {
                        method: operation
                    }
                },
                "components": components
            }

            with open(out_file, "w") as f:
                json.dump(new_spec, f, indent=2)

            print(f"✅ Split: {tag}/{method.upper()}_{operation_id}.json")
            total += 1

    print(f"\n✨ Total operations split: {total}")
    if generated:
        print("\n⚠️ Missing operationId generated for:")
        for op_id in generated:
            print(f" - {op_id}")

if __name__ == "__main__":
    main()
