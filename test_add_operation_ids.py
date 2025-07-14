import json
import tempfile
import os
from add_operation_ids import add_operation_ids

def test_add_operation_ids_to_missing():
    swagger = {
        "paths": {
            "/test": {
                "get": {
                    "summary": "Test GET"
                }
            }
        }
    }

    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
        json.dump(swagger, tmp)
        tmp_path = tmp.name

    add_operation_ids(tmp_path)

    with open(tmp_path) as f:
        result = json.load(f)
        op_id = result["paths"]["/test"]["get"].get("operationId")
        assert op_id is not None
        assert op_id.startswith("get_test_")

    os.remove(tmp_path)

if __name__ == "__main__":
    test_add_operation_ids_to_missing()
    print("✅ Unit test passed")
