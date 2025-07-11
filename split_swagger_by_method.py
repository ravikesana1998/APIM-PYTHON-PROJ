import json
import os

# Input and output paths
with open("swagger.json", "r") as f:
    swagger = json.load(f)

output_dir = "split_operations"
os.makedirs(output_dir, exist_ok=True)

# Loop through paths and methods
for path, methods in swagger["paths"].items():
    for method, operation in methods.items():
        operation_id = operation.get("operationId")
        if not operation_id:
            continue

        filename = f"{method.upper()}_{operation_id}.json"
        output_path = os.path.join(output_dir, filename)

        # Extract path-level parameters
        path_parameters = []
        if "parameters" in methods:
            path_parameters += methods["parameters"]
        if "parameters" in operation:
            path_parameters += operation["parameters"]

        # Filter only path params
        template_parameters = []
        for param in path_parameters:
            if param.get("in") == "path":
                template_parameters.append({
                    "name": param["name"],
                    "type": "string",  # assuming string for simplicity
                    "required": True,
                    "description": param.get("description", f"Path parameter: {param['name']}")
                })

        # Create minimal per-operation definition
        operation_json = {
            "operationId": operation_id,
            "method": method.upper(),
            "urlTemplate": path,
            "templateParameters": template_parameters,
            "description": operation.get("description", "")
        }

        with open(output_path, "w") as out_file:
            json.dump(operation_json, out_file, indent=2)

        print(f"✅ Split: {filename}")
