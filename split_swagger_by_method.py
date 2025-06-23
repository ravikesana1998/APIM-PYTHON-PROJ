import json
import os

def split_by_http_method(swagger_path, output_dir):
    with open(swagger_path, 'r') as f:
        swagger = json.load(f)

    paths = swagger.get('paths', {})

    for path, methods in paths.items():
        for method, operation in methods.items():
            single_op_swagger = {
                **swagger,
                'paths': {
                    path: {
                        method: operation
                    }
                }
            }

            filename = f"{method.upper()}_{path.strip('/').replace('/', '_').replace('{', '').replace('}', '')}.json"
            os.makedirs(output_dir, exist_ok=True)
            with open(os.path.join(output_dir, filename), 'w') as out_file:
                json.dump(single_op_swagger, out_file, indent=2)

if __name__ == '__main__':
    import sys
    split_by_http_method(sys.argv[1], sys.argv[2])
