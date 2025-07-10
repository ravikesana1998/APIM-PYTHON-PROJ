import json, os

with open('swagger.json') as f:
    swagger = json.load(f)

output_dir = 'split'
os.makedirs(output_dir, exist_ok=True)

for path, methods in swagger.get('paths', {}).items():
    for method, operation in methods.items():
        op_id = operation.get('operationId', f'{method}_{path.strip("/")}')
        safe_op_id = op_id.replace('/', '_').replace('{', '').replace('}', '').replace('-', '_')
        operation_spec = {
            "paths": {
                path: {
                    method: operation
                }
            },
            "swagger": "2.0",
            "info": swagger.get("info", {}),
            "host": swagger.get("host", ""),
            "schemes": swagger.get("schemes", []),
            "basePath": swagger.get("basePath", ""),
            "consumes": swagger.get("consumes", []),
            "produces": swagger.get("produces", []),
            "definitions": swagger.get("definitions", {})
        }
        with open(f"{output_dir}/{method.upper()}_{safe_op_id}.json", "w") as out:
            json.dump(operation_spec, out, indent=2)
        print(f"✔ Created: {method.upper()}_{safe_op_id}.json")
