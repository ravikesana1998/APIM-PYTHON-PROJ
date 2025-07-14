# scripts/split_swagger_by_operation.py

import json
import os
from pathlib import Path

INPUT_PATH = "swagger/processed_swagger.json"
SPLIT_DIR = "swagger/split"

def split_swagger(swagger):
    base_template = {
        "openapi": swagger.get("openapi", "3.0.1"),
        "info": swagger["info"],
        "paths": {},
        "components": swagger.get("components", {})
    }

    Path(SPLIT_DIR).mkdir(exist_ok=True)
    for path, methods in swagger["paths"].items():
        for method, details in methods.items():
            single_path_spec = base_template.copy()
            single_path_spec["paths"] = {
                path: {
                    method: details
                }
            }
            op_id = details["operationId"]
            file_name = f"{op_id}.json"
            with open(Path(SPLIT_DIR) / file_name, "w") as f:
                json.dump(single_path_spec, f, indent=2)
            print(f"Written: {file_name}")

def main():
    with open(INPUT_PATH) as f:
        swagger = json.load(f)
    split_swagger(swagger)

if __name__ == "__main__":
    main()
