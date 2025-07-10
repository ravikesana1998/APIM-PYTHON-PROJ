import json
import os
import requests

swagger_url = os.environ["SWAGGER_URL"]
output_dir = "./split"

print("📥 Downloading Swagger...")
response = requests.get(swagger_url)
swagger = response.json()

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("🔨 Splitting Swagger into per-operation files...")

for path, methods in swagger["paths"].items():
    for method, op_data in methods.items():
        operation_id = op_data.get("operationId")
        if not operation_id:
            operation_id = f"{method.upper()}_{path.strip('/').replace('/', '_').replace('{', '').replace('}', '')}"

        op_object = {
            "operationId": operation_id,
            "method": method.upper(),
            "path": path,
            "summary": op_data.get("summary", operation_id),
            "parameters": op_data.get("parameters", [])
        }

        filename = f"{operation_id}.json"
        with open(os.path.join(output_dir, filename), "w") as f:
            json.dump(op_object, f, indent=2)

        print(f"✔ Created: {filename}")
