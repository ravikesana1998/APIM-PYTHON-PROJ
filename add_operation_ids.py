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
                op['operationId'] = f"{http_method}_{path.strip('/').replace('/', '_').replace('{', '').replace('}', '')}"
                cnt += 1

    with open(swagger_path, 'w') as f:
        json.dump(spec, f, indent=2)

    print(f"Added {cnt} operationIds.")

if __name__ == '__main__':
    main()
