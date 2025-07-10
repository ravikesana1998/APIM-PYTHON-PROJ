# split_swagger_by_method.py
import json
import os

with open("swagger.json", "r") as f:
    swagger = json.load(f)

output_dir = "split"
os.makedirs(output_dir, exist_ok=True)

for path, methods in swagger.get("paths", {}).items():
    for method, operation in methods.items():
        # Create operation ID like GET_api_SharePoint_GetListDetails
        clean_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
        operation_id = f"{method.upper()}_{clean_path or 'root'}"

        operation_json = {
            "openapi": swagger.get("openapi", "3.0.1"),
            "info": swagger["info"],
            "paths": {
                path: {
                    method: operation
                }
            },
            "components": swagger.get("components", {})
        }

        output_file = os.path.join(output_dir, f"{operation_id}.json")
        with open(output_file, "w") as out_f:
            json.dump(operation_json, out_f, indent=2)
        print(f"✔ Created: {operation_id}.json")
