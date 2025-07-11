import json
import os
import hashlib

# Load Swagger/OpenAPI JSON
with open("swagger.json", "r") as f:
    swagger = json.load(f)

# Output directory
output_dir = "split"
os.makedirs(output_dir, exist_ok=True)

split_count = 0
valid_methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']

def generate_unique_id(method, path):
    clean = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
    hash_part = hashlib.md5(f"{method}_{path}".encode()).hexdigest()[:8]
    return f"{method}_{clean}_{hash_part}"

# Loop through each path and method
for path, methods in swagger.get("paths", {}).items():
    for method, operation in methods.items():
        if method.lower() not in valid_methods:
            continue

        operation_id = operation.get("operationId")
        if not operation_id:
            operation_id = generate_unique_id(method, path)
            print(f"⚠️  Missing operationId – generated: {operation_id}")

        filename = f"{method.upper()}_{operation_id}.json"

        # Organize into tag-based folder
        tags = operation.get("tags", ["General"])
        tag_name = tags[0].replace(" ", "").replace("/", "_")
        tag_dir = os.path.join(output_dir, tag_name)
        os.makedirs(tag_dir, exist_ok=True)
        output_path = os.path.join(tag_dir, filename)

        # Combine path + operation parameters
        all_parameters = []
        if "parameters" in methods:
            all_parameters += methods["parameters"]
        if "parameters" in operation:
            all_parameters += operation["parameters"]

        # Extract path/query parameters
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

        # Prepare operation object
        operation_json = {
            "operationId": operation_id,
            "method": method.upper(),
            "urlTemplate": path,
            "templateParameters": template_parameters,
            "description": operation.get("description", "")
        }

        # Optional: Add requestBody
        if "requestBody" in operation:
            content = operation["requestBody"].get("content", {})
            for media_type, media in content.items():
                schema = media.get("schema", {})
                operation_json["requestBody"] = {
                    "mediaType": media_type,
                    "schema": schema.get("$ref", schema)
                }
                break  # handle one content type for now

        # Save file
        with open(output_path, "w") as out_file:
            json.dump(operation_json, out_file, indent=2)

        print(f"✅ Split: {os.path.join(tag_name, filename)}")
        split_count += 1

print(f"\n📊 Total operations split: {split_count}")
