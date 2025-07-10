# Updated split_swagger_by_method.py

import json
import os

with open("swagger.json", "r") as f:
    swagger = json.load(f)

os.makedirs("split", exist_ok=True)

for path, methods in swagger.get("paths", {}).items():
    for method, details in methods.items():
        clean_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
        filename = f"{method.upper()}_{clean_path}.json"

        partial_swagger = {
            "swagger": "2.0",
            "info": swagger["info"],
            "paths": {
                path: {
                    method: details
                }
            },
            "definitions": swagger.get("definitions", {})
        }

        with open(os.path.join("split", filename), "w") as out:
            json.dump(partial_swagger, out, indent=2)

        print(f"✔ Created: {filename}")
