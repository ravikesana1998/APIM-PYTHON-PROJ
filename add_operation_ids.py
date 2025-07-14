#!/usr/bin/env python3
import sys
import json

def main():
    swagger_path = sys.argv[1]
    with open(swagger_path, 'r') as f:
        spec = json.load(f)

    cnt = 0
    for path, methods in spec.get('paths', {}).items():
        for http_method, op in methods.items():
            if 'operationId' not in op:
                generated_id = f"{http_method}_{path.strip('/').replace('/', '_').replace('{', '').replace('}', '')}"
                op['operationId'] = generated_id
                print(f"🆔 Added operationId: {generated_id} for {http_method.upper()} {path}")
                cnt += 1

    with open(swagger_path, 'w') as f:
        json.dump(spec, f, indent=2)

    print(f"✅ Added {cnt} missing operationIds.")

if __name__ == '__main__':
    main()
