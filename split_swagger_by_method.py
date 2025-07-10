import json
import os

with open("swagger.json") as f:
    swagger = json.load(f)

os.makedirs("split", exist_ok=True)
count = 0

for path, methods in swagger.get("paths", {}).items():
    for method, details in methods.items():
        op_id = details.get("operationId", f"{method}_{path}")
        sanitized_id = op_id.replace('/', '_').replace('{', '').replace('}', '').replace(':', '_')
        filename = f"split/{method.upper()}_{sanitized_id}.json"
        operation_swagger = {
            "swagger": swagger.get("swagger"),
            "info": swagger.get("info"),
            "paths": {path: {method: details}},
            "definitions": swagger.get("definitions", {}),
        }
        with open(filename, "w") as f:
            json.dump(operation_swagger, f, indent=2)
        print(f"✔ Created: {os.path.basename(filename)}")
        count += 1

print(f"✅ Total operations split: {count}")
