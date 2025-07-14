import unittest
import tempfile
import json
import os
from add_operation_ids import add_operation_ids

class TestAddOperationIds(unittest.TestCase):

    def setUp(self):
        self.swagger_without_op_id = {
            "openapi": "3.0.1",
            "paths": {
                "/user/{id}": {
                    "get": {
                        "summary": "Get user by ID",
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                        # No operationId
                    }
                }
            }
        }

        self.swagger_with_op_id = {
            "openapi": "3.0.1",
            "paths": {
                "/user/{id}": {
                    "get": {
                        "operationId": "GetUserById",
                        "summary": "Get user by ID",
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    }
                }
            }
        }

    def _write_temp_swagger(self, swagger_data):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w+')
        json.dump(swagger_data, tmp)
        tmp.close()
        return tmp.name

    def test_adds_missing_operation_id(self):
        tmp_path = self._write_temp_swagger(self.swagger_without_op_id)

        add_operation_ids(tmp_path)

        with open(tmp_path, "r") as f:
            updated = json.load(f)

        op_id = updated["paths"]["/user/{id}"]["get"].get("operationId")
        self.assertIsNotNone(op_id)
        self.assertTrue(op_id.startswith("GetUser"))

        os.remove(tmp_path)

    def test_preserves_existing_operation_id(self):
        tmp_path = self._write_temp_swagger(self.swagger_with_op_id)

        add_operation_ids(tmp_path)

        with open(tmp_path, "r") as f:
            updated = json.load(f)

        op_id = updated["paths"]["/user/{id}"]["get"].get("operationId")
        self.assertEqual(op_id, "GetUserById")

        os.remove(tmp_path)

if __name__ == '__main__':
    unittest.main()
