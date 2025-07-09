# split_swagger_by_method.py
import json, os
from pathlib import Path

def sanitize_filename(path, method):
    return f"{method.upper()}_{path.strip('/').replace('/', '_').replace('{','').replace('}','')}"

def main():
    input_file = "swagger.json"
    output_dir = "split"
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file) as f:
        swagger = json.load(f)

    for path, methods in swagger.get("paths", {}).items():
        for method, details in methods.items():
            if method.lower() not in ["get", "post", "put", "delete"]:
                continue  # Skip non-CRUD

            op_id = details.get("operationId")
            if not op_id:
                op_id = sanitize_filename(path, method)
                details["operationId"] = op_id  # ✅ inject operationId if missing

            new_spec = {
                "openapi": swagger.get("openapi", "3.0.0"),
                "info": swagger.get("info", {}),
                "servers": swagger.get("servers", []),
                "paths": {path: {method: details}},
                "components": swagger.get("components", {})
            }
            filename = f"{op_id}.json"
            with open(Path(output_dir) / filename, "w") as out:
                json.dump(new_spec, out, indent=2)
            print(f"✔ Created: {filename}")

if __name__ == "__main__":
    main()

