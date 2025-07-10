import os
import json
import traceback
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient

subscription_id = os.environ["APIM_SUBSCRIPTION_ID"]
resource_group = os.environ["APIM_RESOURCE_GROUP"]
service_name = os.environ["APIM_SERVICE_NAME"]
api_id = os.environ["APIM_API_NAME"]

split_dir = "./split"
credential = DefaultAzureCredential()
client = ApiManagementClient(credential, subscription_id)

for file_name in os.listdir(split_dir):
    if not file_name.endswith(".json"):
        continue

    try:
        with open(os.path.join(split_dir, file_name), "r") as f:
            data = json.load(f)

        path = data["path"]
        method = data["method"].lower()
        operation = data["operation"]
        operation_id = data["operationId"]

        # Validate requestBody schema
        schema = None
        if "requestBody" in operation and "content" in operation["requestBody"]:
            content = operation["requestBody"]["content"]
            if "application/json" in content:
                schema = content["application/json"].get("schema")

        # Validate responses
        responses = {}
        if "responses" in operation:
            for code, resp in operation["responses"].items():
                responses[code] = {"description": resp.get("description", "")}

        # Handle parameters
        parameters = []
        for param in operation.get("parameters", []):
            if "name" in param and "in" in param:
                parameters.append({
                    "name": param["name"],
                    "in": param["in"],
                    "required": param.get("required", False),
                    "type": param.get("schema", {}).get("type", "string")
                })

        operation_contract = {
            "display_name": operation_id,
            "method": method.upper(),
            "url_template": path,
            "request": {
                "query_parameters": [p for p in parameters if p["in"] == "query"],
                "template_parameters": [p for p in parameters if p["in"] == "path"],
                "headers": [p for p in parameters if p["in"] == "header"]
            },
            "responses": responses
        }

        if schema:
            operation_contract["request"]["representations"] = [{
                "content_type": "application/json"
            }]

        print(f"📤 Syncing operation: {operation_id}")

        client.api_operation.create_or_update(
            resource_group,
            service_name,
            api_id,
            operation_id,
            operation_contract
        )

        print(f"✅ Synced: {operation_id}")

    except Exception as e:
        print(f"❌ Failed: {file_name}")
        print("ERROR:", e)
        traceback.print_exc()
