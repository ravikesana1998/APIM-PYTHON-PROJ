import json
import os

with open("swagger.json", "r") as f:
    swagger = json.load(f)

paths = swagger.get("paths", {})
output_dir = "."

for path, path_item in paths.items():
    for method, operation in path_item.items():
        operation_id = operation.get("operationId", f"{method}_{path}")
        safe_id = operation_id.replace("/", "_").replace("{", "").replace("}", "")
        filename = f"{method.upper()}_{safe_id}.json"
        filepath = os.path.join(output_dir, filename)

        single_path_spec = {
            "swagger": swagger.get("swagger"),
            "info": swagger.get("info"),
            "host": swagger.get("host"),
            "basePath": swagger.get("basePath"),
            "schemes": swagger.get("schemes"),
            "paths": {
                path: {
                    method: operation
                }
            },
            "definitions": swagger.get("definitions", {})
        }

        with open(filepath, "w") as out:
            json.dump(single_path_spec, out, indent=2)
            print(f"✔ Created: {filename}")
