# import os
# import json

# SWAGGER_FILE = "swagger.json"
# OUTPUT_DIR = "split"

# def save_operation(tag, method, path, operation):
#     """Save a single operation to a file."""
#     operation_id = operation.get("operationId")
#     if not operation_id:
#         print(f"⚠️ Skipping operation without operationId for {method.upper()} {path}")
#         return

#     clean_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
#     filename = f"{method.lower()}_{clean_path or 'root'}.json"
#     tag_dir = os.path.join(OUTPUT_DIR, tag)
#     os.makedirs(tag_dir, exist_ok=True)
#     filepath = os.path.join(tag_dir, filename)

#     operation_data = {
#         "method": method.lower(),
#         "urlTemplate": path,
#         "operationId": operation_id,
#         "description": operation.get("description", operation_id),
#         "templateParameters": [
#             p for p in operation.get("parameters", []) if p.get("in") == "path"
#         ]
#     }

#     with open(filepath, "w") as f:
#         json.dump(operation_data, f, indent=2)

#     print(f"📁 Wrote: {filepath}")

# def main():
#     if not os.path.exists(SWAGGER_FILE):
#         print(f"❌ Swagger file not found: {SWAGGER_FILE}")
#         return

#     with open(SWAGGER_FILE, "r") as f:
#         swagger = json.load(f)

#     paths = swagger.get("paths", {})
#     if not paths:
#         print("⚠️ No paths found in Swagger.")
#         return

#     count = 0
#     for path, methods in paths.items():
#         for method, operation in methods.items():
#             tags = operation.get("tags", ["default"])
#             for tag in tags:
#                 save_operation(tag, method, path, operation)
#                 count += 1

#     print(f"\n✅ Total operations split: {count}")

# if __name__ == "__main__":
#     main()

import os
import json
import sys

def split_swagger_by_method(swagger_file):
    with open(swagger_file, 'r') as f:
        swagger = json.load(f)

    base_info = {
        "openapi": swagger.get("openapi", "3.0.1"),
        "info": swagger.get("info", {}),
        "components": swagger.get("components", {}),
        "tags": swagger.get("tags", []),
    }

    paths = swagger.get("paths", {})
    if not paths:
        print("❌ No paths found in Swagger file.")
        return

    os.makedirs("split", exist_ok=True)
    count = 0

    for path, methods in paths.items():
        for method, operation in methods.items():
            if not operation.get("operationId"):
                print(f"⚠️ Skipping {method.upper()} {path} (missing operationId)")
                continue

            op_id = operation["operationId"]
            tag = (operation.get("tags") or ["default"])[0].replace(" ", "_")
            tag_dir = os.path.join("split", tag)
            os.makedirs(tag_dir, exist_ok=True)

            new_doc = dict(base_info)
            new_doc["paths"] = {
                path: {
                    method: operation
                }
            }

            filename = f"{method.lower()}_{op_id}.json"
            filepath = os.path.join(tag_dir, filename)
            with open(filepath, "w") as out:
                json.dump(new_doc, out, indent=2)

            print(f"✅ Saved {method.upper()} {path} to {filepath}")
            count += 1

    print(f"🎉 Split complete. {count} operations written to ./split.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python split_swagger_by_method.py <swagger-file>")
        sys.exit(1)

    split_swagger_by_method(sys.argv[1])
