import json
import re
import sys

def camel_case(s):
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"[\s]+", "_", s)
    parts = s.split("_")
    return parts[0] + "".join([p.capitalize() for p in parts[1:]]) if parts else ""

def add_operation_ids(swagger_path):
    with open(swagger_path, "r") as f:
        swagger = json.load(f)

    for path, methods in swagger.get("paths", {}).items():
        for method, operation in methods.items():
            if "operationId" not in operation:
                base_name = path.strip("/").split("/")[-1]
                op_id = f"{method.lower().capitalize()}{camel_case(base_name)}"
                operation["operationId"] = op_id
                print(f"✅ Added operationId: {op_id} for {method.upper()} {path}")

    with open(swagger_path, "w") as f:
        json.dump(swagger, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_operation_ids.py <swagger-file>")
        sys.exit(1)
    add_operation_ids(sys.argv[1])
