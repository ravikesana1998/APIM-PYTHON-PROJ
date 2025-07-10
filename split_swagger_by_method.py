import json
import os
import re

split_dir = "./split"
os.makedirs(split_dir, exist_ok=True)

with open("swagger.json", "r") as f:
    swagger = json.load(f)

paths = swagger.get("paths", {})

for path, methods in paths.items():
    for method, details in methods.items():
        # Build a clean filename based on method and path
        filename = f"{method.upper()}_{path.strip('/').replace('/', '_').replace('{', '').replace('}', '')}.json"
        filepath = os.path.join(split_dir, filename)

        # Extract and define parameters
        parameters = details.get("parameters", [])
        defined_params = {param["name"] for param in parameters if "name" in param and param.get("in") == "path"}
        path_params = set(re.findall(r"{(.*?)}", path))

        # Auto-add missing path parameters
        for param in path_params - defined_params:
            parameters.append({
                "name": param,
                "in": "path",
                "required": True,
                "type": "string"
            })

        # Update parameters in operation details
        details["parameters"] = parameters

        # Create a minimal Swagger spec for the individual operation
        operation_swagger = {
            "swagger": "2.0",
            "info": swagger.get("info", {}),
            "host": swagger.get("host"),
            "basePath": swagger.get("basePath"),
            "schemes": swagger.get("schemes", ["https"]),
            "paths": {
                path: {
                    method: details
                }
            }
        }

        with open(filepath, "w") as op_file:
            json.dump(operation_swagger, op_file, indent=2)

        print(f"✔ Created: {filename}")
