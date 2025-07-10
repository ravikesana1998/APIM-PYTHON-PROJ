# split_swagger_by_method.py
import json
import os

with open('swagger.json') as f:
    swagger = json.load(f)

os.makedirs('split', exist_ok=True)

for path, path_item in swagger['paths'].items():
    for method, operation in path_item.items():
        op_id = operation.get('operationId') or f"{method.upper()}_{path.replace('/', '_').strip('_')}"
        file_name = f"{method.upper()}_{path.replace('/', '_').strip('_')}.json"
        full_path = os.path.join('split', file_name)

        parameters = operation.get('parameters', [])

        # Extract path params from path template
        path_params = [seg.strip('{}') for seg in path.split('/') if seg.startswith('{') and seg.endswith('}')]
        for p in path_params:
            if not any(p == param.get('name') and param.get('in') == 'path' for param in parameters):
                parameters.append({"name": p, "in": "path", "required": True, "type": "string"})

        # Create minimal OpenAPI doc
        op_doc = {
            "openapi": "3.0.1",
            "info": {"title": swagger['info']['title'], "version": swagger['info']['version']},
            "paths": {
                path: {
                    method: {
                        "operationId": op_id,
                        "parameters": parameters,
                        "responses": operation.get('responses', {})
                    }
                }
            }
        }

        with open(full_path, 'w') as f:
            json.dump(op_doc, f, indent=2)
        print(f"✔ Created: {file_name}")
