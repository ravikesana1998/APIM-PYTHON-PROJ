import os
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--swagger-url", required=True)
args = parser.parse_args()

swagger_url = args.swagger_url
swagger_json_path = 'swagger.json'

# Download Swagger file
os.system(f'curl -sSL "{swagger_url}" -o {swagger_json_path}')

# Load and split by method
with open(swagger_json_path) as f:
    swagger = json.load(f)

paths = swagger.get("paths", {})
os.makedirs("split", exist_ok=True)

for path, methods in paths.items():
    for method, operation in methods.items():
        operation_id = operation.get("operationId", f"{method}_{path.strip('/').replace('/', '_')}")
        filename = f"{method.upper()}_{path.strip('/').replace('/', '_')}.json"
        output = {
            "method": method.upper(),
            "path": path,
            "operationId": operation_id,
            "operation": operation
        }
        with open(os.path.join("split", filename), "w") as out:
            json.dump(output, out, indent=2)
        print(f"✔ Created: {filename}")
