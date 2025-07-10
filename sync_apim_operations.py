import os
import json
import re
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
from azure.mgmt.apimanagement.models import OperationContract, RequestContract, ResponseContract, ParameterContract

SUBSCRIPTION_ID = os.environ["APIM_SUBSCRIPTION_ID"]
RESOURCE_GROUP = os.environ["APIM_RESOURCE_GROUP"]
SERVICE_NAME = os.environ["APIM_SERVICE_NAME"]
API_ID = os.environ["APIM_API_NAME"]

def extract_template_parameters(path):
    return re.findall(r'{(.*?)}', path)

def main():
    print("📦 Syncing Swagger operations to APIM...")
    credential = DefaultAzureCredential()
    client = ApiManagementClient(credential, SUBSCRIPTION_ID)

    for filename in os.listdir():
        if not filename.endswith(".json") or filename == "swagger.json":
            continue

        with open(filename, "r") as f:
            data = json.load(f)

        url_path = list(data["paths"].keys())[0]
        method = list(data["paths"][url_path].keys())[0].lower()
        op_data = data["paths"][url_path][method]
        operation_id = op_data.get("operationId", filename.replace(".json", ""))

        print(f"📤 Syncing operation: {operation_id}")

        param_names = extract_template_parameters(url_path)
        template_parameters = [
            ParameterContract(
                name=name,
                required=True,
                type="string",
                description=f"Path parameter {name}"
            )
            for name in param_names
        ]

        request = RequestContract(
            description=op_data.get("summary", operation_id),
            query_parameters=[],
            headers=[]
        )

        responses = [ResponseContract(status_code=200, description="Success")]

        op_contract = OperationContract(
            display_name=operation_id,
            method=method.upper(),
            url_template=url_path,
            request=request,
            responses=responses,
            template_parameters=template_parameters
        )

        try:
            client.api_operation.create_or_update(
                RESOURCE_GROUP,
                SERVICE_NAME,
                API_ID,
                operation_id,
                parameters=op_contract
            )
            print(f"✅ Synced: {operation_id}")
        except Exception as e:
            print(f"❌ Failed: {operation_id}")
            print(e)

if __name__ == "__main__":
    main()
