import json
import os
import hashlib

# Load Swagger JSON
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

        # Use existing operationId if present
        operation_id = operation.get("operationId")
        if not operation_id:
            clean_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
            # Stable deterministic ID using hash
            hash_id = hashlib.md5(f"{method.lower()}:{path}".encode()).hexdigest()[:8]
            operation_id = f"{method.lower()}_{clean_path}_{hash_id}"
            print(f"⚠️  Missing operationId – generated: {operation_id}")

        # Detect main folder from path (e.g., SharePoint)
        top_folder = path.strip("/").split("/")[1] if "/" in path.strip("/") else "general"
        folder_path = os.path.join(output_dir, top_folder)
        os.makedirs(folder_path, exist_ok=True)

        filename = f"{method.upper()}_{operation_id}.json"
        output_path = os.path.join(folder_path, filename)

        # Combine parameters from path and operation
        path_parameters = []
        if "parameters" in methods:
            path_parameters += methods["parameters"]
        if "parameters" in operation:
            path_parameters += operation["parameters"]

        # Filter path parameters
        template_parameters = []
        for param in path_parameters:
            if param.get("in") == "path":
                template_parameters.append({
                    "name": param["name"],
                    "type": "string",
                    "required": True,
                    "description": param.get("description", f"Path parameter: {param['name']}")
                })

        # Compose final JSON output
        operation_json = {
            "operationId": operation_id,
            "method": method.upper(),
            "urlTemplate": path,
            "templateParameters": template_parameters,
            "description": operation.get("description", "")
        }

        # Write to file
        with open(output_path, "w") as out_file:
            json.dump(operation_json, out_file, indent=2)

        print(f"✅ Split: {top_folder}/{filename}")
        split_count += 1

print(f"\n📊 Total operations split: {split_count}")
