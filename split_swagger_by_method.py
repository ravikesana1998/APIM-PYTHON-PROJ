#!/usr/bin/env python3
import sys, os, json

def main():
    input_file, out_dir = sys.argv[1], sys.argv[2]
    with open(input_file) as f:
        spec = json.load(f)

    for path, methods in spec.get('paths', {}).items():
        for method, op in methods.items():
            op_id = op.get('operationId') or f"{method}_{path}"
            single = {
                "openapi": spec.get("openapi", "3.0.0"),
                "info": spec.get("info", {}),
                "paths": {
                    path: {
                        method: op
                    }
                },
                "components": spec.get("components", {})
            }
            safe_name = "".join(c if c.isalnum() or c in "_-." else "_" for c in op_id)
            filename = os.path.join(out_dir, f"{safe_name}.json")
            os.makedirs(out_dir, exist_ok=True)
            with open(filename, 'w') as outf:
                json.dump(single, outf, indent=2)
            print(f" Wrote {filename}")

if __name__ == '__main__':
    main()
