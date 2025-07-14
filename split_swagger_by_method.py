# split_swagger_by_method.py
import os
import sys
import json
import re
from pathlib import Path

def sanitize_filename(s):
    return re.sub(r'[^\w\-]', '', s)

def split_swagger_by_method(swagger_path, output_dir):
    with open(swagger_path, "r") as f:
        swagger = json.load(f)

    paths = swagger.get("paths", {})
    count = 0
    missing_ops = 0

    for path, methods in paths.items():
        for method, operation in methods.items():
            op_id = operation.get("operationId")
            if not op_id:
                print(f"⚠️ Skipping {method.upper()} {path} (no operationId)")
                missing_ops += 1
                continue

            # Build operation-specific Swagger
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
            method_prefix = method.lower()
            filename = f"{method_prefix}_{op_id}.json"

            full_dir = Path(output_dir) / tag_folder
            full_dir.mkdir(parents=True, exist_ok=True)
            full_path = full_dir / filename

            with open(full_path, "w") as f:
                json.dump(new_spec, f, indent=2)

            print(f"✅ Wrote {full_path}")
            count += 1

    print(f"✂️ Split complete: {count} operations written to {output_dir}")

    if missing_ops > 0:
        print(f"❌ Split failed: {missing_ops} operations were missing operationId.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python split_swagger_by_method.py <swagger-file> <output-dir>")
        sys.exit(1)

    split_swagger_by_method(sys.argv[1], sys.argv[2])

    print(f"  - {os}")

# if __name__ == "__main__":
#     main()
