import os
import json
import re
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
from azure.mgmt.apimanagement.models import OperationContract, RequestContract, ResponseContract, ParameterContract

# Required env variables
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
        if filename.endswith(".json"):
            with open(filename, "r") as f:
                data = json.load(f)

            method = list(data["paths"].values())[0]
            http_method = list(method.keys())[0].upper()
            operation_data = method[http_method.lower()]
            url_template = list(data["paths"].keys())[0]

            operation_id = filename.replace(".json", "")

            template_params = extract_template_parameters(url_template)
            parameters = [
                ParameterContract(name=param, required=True, type="string", in_="path")
                for param in template_params
            ]

            print(f"📤 Syncing operation: {operation_id}")

            try:
                op_contract = OperationContract(
                    display_name=operation_id,
                    method=http_method,
                    url_template=url_template,
                    request=RequestContract(
                        description=operation_data.get("summary", ""),
                        query_parameters=[],
                        headers=[]
                    ),
                    responses=[
                        ResponseContract(status_code=200, description="OK")
                    ],
                    template_parameters=parameters
                )

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
                print(f"{type(e).__name__}: {e}")

if __name__ == "__main__":
    main()
