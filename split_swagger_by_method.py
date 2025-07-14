# split_swagger_by_method.py
import os
import sys
import json
import re
from pathlib import Path
from hashlib import md5

def sanitize_filename(s):
    return re.sub(r'[^\w\-]', '_', s)

def generate_operation_id(method, path):
    clean_path = path.strip('/').replace('/', '_').replace('{', '').replace('}', '')
    base = f"{method}_{clean_path}"
    return sanitize_filename(base[:80]) + '_' + md5(base.encode()).hexdigest()[:6]

def split_swagger_by_method(swagger_path, output_dir):
    with open(swagger_path, "r") as f:
        swagger = json.load(f)

    paths = swagger.get("paths", {})
    count = 0

    for path, methods in paths.items():
        for method, operation in methods.items():
            if "operationId" not in operation or not operation["operationId"].strip():
                generated_id = generate_operation_id(method, path)
                print(f"⚠️ Missing operationId for {method.upper()} {path}, generating: {generated_id}")
                operation["operationId"] = generated_id
            else:
                generated_id = sanitize_filename(operation["operationId"])

            new_spec = {
                "openapi": swagger.get("openapi", "3.0.1"),
                "info": swagger.get("info", {}),
                "paths": {
                    path: {
                        method: operation
                    }
                },
                "components": swagger.get("components", {})
            }

            tag_folder = sanitize_filename(operation.get("tags", ["default"])[0])
            filename = f"{method.lower()}_{generated_id}.json"

            full_dir = Path(output_dir) / tag_folder
            full_dir.mkdir(parents=True, exist_ok=True)
            full_path = full_dir / filename

            with open(full_path, "w") as f:
                json.dump(new_spec, f, indent=2)

            print(f"✅ Wrote {full_path}")
            count += 1

    print(f"\n✂️ Split complete: {count} operations written to {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python split_swagger_by_method.py <swagger-file> <output-dir>")
        sys.exit(1)

    split_swagger_by_method(sys.argv[1], sys.argv[2])
