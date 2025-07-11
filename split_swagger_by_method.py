import json
import os

# Input and output paths
with open("swagger.json", "r") as f:
    swagger = json.load(f)

output_dir = "split"
os.makedirs(output_dir, exist_ok=True)

split_count = 0

# Loop through paths and methods
for path, methods in swagger["paths"].items():
    for method, operation in methods.items():
        if method.lower() not in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
            continue

        operation_id = operation.get("operationId")
        if not operation_id:
            safe_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
            operation_id = f"{method.lower()}_{safe_path}"
            print(f"⚠️  Missing operationId – generated: {operation_id}")

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
                    "type": "string",
                    "required": True,
                    "description": param.get("description", f"Path parameter: {param['name']}")
                })

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
        split_count += 1

print(f"\n📊 Total operations split: {split_count}")
