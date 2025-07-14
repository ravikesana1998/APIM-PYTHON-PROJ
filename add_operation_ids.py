import json
import re
import sys

def sanitize_segment(segment):
    return re.sub(r"[{}]", "", segment)

def generate_operation_id(method, path):
    segments = path.strip("/").split("/")
    clean_segments = [sanitize_segment(s) for s in segments]
    return method.capitalize() + "".join([s.capitalize() for s in clean_segments])

def add_operation_ids(swagger_path):
    with open(swagger_path, "r") as f:
        swagger = json.load(f)

    modified = False
    existing_ids = set()

    for path, methods in swagger.get("paths", {}).items():
        for method, operation in methods.items():
            if "operationId" not in operation or not operation["operationId"].strip():
                op_id = generate_operation_id(method, path)

                # Ensure uniqueness by appending a counter if needed
                base_op_id = op_id
                counter = 1
                while op_id in existing_ids:
                    op_id = f"{base_op_id}{counter}"
                    counter += 1

                operation["operationId"] = op_id
                existing_ids.add(op_id)

                print(f"➕ Added operationId: {op_id} for {method.upper()} {path}")
                modified = True
            else:
                existing_ids.add(operation["operationId"])

    if modified:
        with open(swagger_path, "w") as f:
            json.dump(swagger, f, indent=2)
        print("✅ Swagger updated with missing operationId fields.")
    else:
        print("✅ All operations already have operationId fields. No changes made.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_operation_ids.py <swagger-file>")
        sys.exit(1)
    add_operation_ids(sys.argv[1])
