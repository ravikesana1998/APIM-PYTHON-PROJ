import os
import json
import glob
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
from azure.mgmt.apimanagement.models import (
    OperationContract,
    RequestContract,
    ParameterContract,
    ResponseContract,
    RepresentationContract
)

# Read environment variables
SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
RESOURCE_GROUP = os.environ["AZURE_RESOURCE_GROUP"]
APIM_NAME = os.environ["AZURE_APIM_NAME"]
API_ID = os.environ["AZURE_APIM_API_ID"]

# Authenticate with Azure
credential = DefaultAzureCredential()
client = ApiManagementClient(credential, SUBSCRIPTION_ID)

def extract_path_params(url_template):
    import re
    return re.findall(r"{(.*?)}", url_template)

def load_swagger_file(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def create_or_update_operation(swagger: dict, method: str, url_template: str, operation_id: str):
    parameters = swagger.get("parameters", [])
    request_body = swagger.get("requestBody", {})
    responses = swagger.get("responses", {})

    query_params = []
    path_params = []
    if parameters:
        for param in parameters:
            param_contract = ParameterContract(
                name=param.get("name"),
                required=param.get("required", False),
                type="string",  # Simplified; optionally parse from param['schema']['type']
                description=param.get("description", ""),
                default_value=param.get("schema", {}).get("default", ""),
                values=param.get("schema", {}).get("enum", []),
            )
            if param.get("in") == "query":
                query_params.append(param_contract)
            elif param.get("in") == "path":
                path_params.append(param_contract)

    representations = []
    if request_body and "content" in request_body:
        for mime_type, media in request_body["content"].items():
            schema = media.get("schema", {})
            representations.append(RepresentationContract(content_type=mime_type, schema=schema))

    request = RequestContract(
        query_parameters=query_params,
        headers=[],
        representations=representations
    )

    response_list = []
    for status_code, response in responses.items():
        representations = []
        if "content" in response:
            for mime_type, media in response["content"].items():
                schema = media.get("schema", {})
                representations.append(RepresentationContract(content_type=mime_type, schema=schema))
        response_list.append(ResponseContract(
            status_code=int(status_code) if status_code.isdigit() else 200,
            description=response.get("description", ""),
            representations=representations
        ))

    op_contract = OperationContract(
        display_name=operation_id,
        method=method.upper(),
        url_template=url_template,
        request=request,
        responses=response_list,
        template_parameters=path_params
    )

    print(f"🛠️ OperationContract built:\n"
          f"  - Display Name: {operation_id}\n"
          f"  - Method: {method.upper()}\n"
          f"  - URL Template: {url_template}\n"
          f"  - Query Params: {[p.name for p in query_params]}\n"
          f"  - Path Params: {[p.name for p in path_params]}\n"
          f"  - Representations: {len(representations)}\n"
          f"  - Responses: {len(response_list)}")

    try:
        client.api_operation.create_or_update(
            resource_group_name=RESOURCE_GROUP,
            service_name=APIM_NAME,
            api_id=API_ID,
            operation_id=operation_id,
            parameters=op_contract
        )
        print(f"✅ Operation synced to APIM: {operation_id}")
    except Exception as e:
        print(f"❌ Failed to sync {operation_id}: {e}")

def main():
    swagger_files = glob.glob("split/**/*.json", recursive=True)
    print(f"🚀 Syncing {len(swagger_files)} Swagger operations to APIM...")

    for file in swagger_files:
        print(f"📂 Reading: {file}")
        swagger = load_swagger_file(file)
        operation_id = swagger.get("operationId")
        method = swagger.get("x-method")
        url_template = swagger.get("x-path")

        if not all([operation_id, method, url_template]):
            print(f"⚠️ Skipping file missing metadata: {file}")
            continue

        print(f"✅ Parsed operationId={operation_id}, method={method}, path={url_template}")
        create_or_update_operation(swagger, method, url_template, operation_id)

if __name__ == "__main__":
    main()
