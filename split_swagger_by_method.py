import json
import os

# Constants
SWAGGER_FILE = "swagger.json"
OUTPUT_DIR = "split"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the Swagger JSON
with open(SWAGGER_FILE, "r") as f:
    swagger = json.load(f)

paths = swagger.get("paths", {})
for path, path_item in paths.items():
    for method, operation in path_item.items():
        method_upper = method.upper()
        safe_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
        filename = f"{method_upper}_{safe_path}.json"

        operation_data = {
            "path": path,
            "method": method_upper,
            "operationId": operation.get("operationId", f"{method_upper}_{safe_path}"),
            "summary": operation.get("summary", ""),
            "parameters": operation.get("parameters", []),
            "responses": operation.get("responses", {}),
            "requestBody": operation.get("requestBody", None)
        }

        with open(os.path.join(OUTPUT_DIR, filename), "w") as f:
            json.dump(operation_data, f, indent=2)

        print(f"✔ Created: {filename}")
