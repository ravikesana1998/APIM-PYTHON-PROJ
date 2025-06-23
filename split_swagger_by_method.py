# split_swagger_by_method.py

import json
import os

def sanitize_filename(path, method):
    return f"{method.upper()}_{path.strip('/').replace('/', '_').replace('{','').replace('}','')}.json"

def main():
    input_file = "swagger.json"
    output_dir = "split"
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, "r") as f:
        swagger = json.load(f)

    for path, methods in swagger.get("paths", {}).items():
        for method, operation in methods.items():
            new_swagger = dict(swagger)
            new_swagger["paths"] = {
                path: {method: operation}
            }

            filename = sanitize_filename(path, method)
            with open(os.path.join(output_dir, filename), "w") as out_file:
                json.dump(new_swagger, out_file, indent=2)

    print(f"✅ Split complete. Files written to '{output_dir}/'.")

if __name__ == "__main__":
    main()
