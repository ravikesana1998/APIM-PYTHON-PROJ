import json
import os

# Load the OpenAPI JSON
with open("swagger.json", "r") as f:
    swagger = json.load(f)

# Output directory
output_dir = "split"
os.makedirs(output_dir, exist_ok=True)

split_count = 0

# Valid HTTP methods
valid_methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']

# Loop through each path and method
for path, methods in swagger.get("paths", {}).items():
    for method, operation in methods.items():
        if method.lower() not in valid_methods:
            continue

        operation_id = operation.get("operationId")
        if not operation_id:
            safe_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
            operation_id = f"{method.lower()}_{safe_path}"
            print(f"⚠️  Missing operationId – generated: {operation_id}")

        # Output file name
        filename = f"{method.upper()}_{operation_id}.json"

        # Tag-based subfolder (optional)
        tags = operation.get("tags", ["General"])
        tag_dir = os.path.join(output_dir, tags[0])
        os.makedirs(tag_dir, exist_ok=True)
        output_path = os.path.join(tag_dir, filename)

        # Combine path-level and operation-level parameters
        all_parameters = []
        if "parameters" in methods:
            all_parameters += methods["parameters"]
        if "parameters" in operation:
            all_parameters += operation["parameters"]

        # Extract path & query parameters
        template_parameters = []
        for param in all_parameters:
            if param.get("in") in ["path", "query"]:
                template_parameters.append({
                    "name": param["name"],
                    "type": "string",
                    "required": param.get("required", False),
                    "in": param.get("in"),
                    "description": param.get("description", f"{param.get('in', 'unknown').title()} parameter: {param['name']}")
                })

        # Prepare operation JSON
        operation_json = {
            "operationId": operation_id,
            "method": method.upper(),
            "urlTemplate": path,
            "templateParameters": template_parameters,
            "description": operation.get("description", "")
        }

        # Add request body schema if applicable
        if "requestBody" in operation:
            content = operation["requestBody"].get("content", {})
            for media_type, media in content.items():
                schema = media.get("schema", {})
                operation_json["requestBody"] = {
                    "mediaType": media_type,
                    "schema": schema.get("$ref", schema)
                }
                break  # only one mediaType handled for now

        # Write to file
        with open(output_path, "w") as out_file:
            json.dump(operation_json, out_file, indent=2)

        print(f"✅ Split: {os.path.join(tags[0], filename)}")
        split_count += 1

print(f"\n📊 Total operations split: {split_count}")
