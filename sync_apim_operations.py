# import os
# import json
# from azure.identity import DefaultAzureCredential
# from azure.mgmt.apimanagement import ApiManagementClient

# SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
# RESOURCE_GROUP = os.environ["AZURE_RESOURCE_GROUP"]
# SERVICE_NAME = os.environ["AZURE_APIM_NAME"]
# API_ID = os.environ["AZURE_APIM_API_ID"]
# SPLIT_DIR = "split"

# credential = DefaultAzureCredential()
# client = ApiManagementClient(credential, SUBSCRIPTION_ID)

# def get_operation_info(filepath):
#     with open(filepath, "r") as f:
#         data = json.load(f)

#     # Expect single path with single method
#     paths = data.get("paths", {})
#     if not paths or len(paths) != 1:
#         raise ValueError(f"Invalid or multiple paths in: {filepath}")
    
#     path = next(iter(paths))
#     method_dict = paths[path]
#     if not method_dict or len(method_dict) != 1:
#         raise ValueError(f"Invalid or multiple methods in: {filepath}")
    
#     method = next(iter(method_dict)).upper()
#     operation = method_dict[method.lower()]
#     operation_id = operation.get("operationId")
#     if not operation_id:
#         raise ValueError(f"Missing operationId in {filepath}")
    
#     return {
#         "id": operation_id,
#         "method": method,
#         "url_template": path,
#         "definition": operation,
#     }

# def create_or_update_operation(op):
#     print(f"🔄 Syncing {op['method']} {op['url_template']} ({op['id']})")

#     parameters = op["definition"].get("parameters", [])
#     request_body = op["definition"].get("requestBody", {})
#     responses = op["definition"].get("responses", {})

#     request_desc = request_body.get("description", "")
#     req_schema = request_body.get("content", {}).get("application/json", {}).get("schema", {})

#     client.api_operation.create_or_update(
#         resource_group_name=RESOURCE_GROUP,
#         service_name=SERVICE_NAME,
#         api_id=API_ID,
#         operation_id=op["id"],
#         display_name=op["id"],
#         method=op["method"],
#         url_template=op["url_template"],
#         request={
#             "query_parameters": [p for p in parameters if p["in"] == "query"],
#             "template_parameters": [p for p in parameters if p["in"] == "path"],
#             "description": request_desc,
#             "representations": [{
#                 "content_type": "application/json",
#                 "schema": req_schema,
#             }] if req_schema else [],
#         },
#         responses=[
#             {
#                 "status_code": str(status),
#                 "description": response.get("description", "")
#             }
#             for status, response in responses.items()
#         ]
#     )

# def main():
#     if not os.path.isdir(SPLIT_DIR):
#         print(f"❌ Folder '{SPLIT_DIR}' not found.")
#         return

#     files = [
#         os.path.join(root, f)
#         for root, _, fs in os.walk(SPLIT_DIR)
#         for f in fs if f.endswith(".json")
#     ]

#     print(f"📦 Syncing Swagger operations to APIM...")
#     success = 0

#     for file in files:
#         try:
#             op = get_operation_info(file)
#             create_or_update_operation(op)
#             success += 1
#         except Exception as e:
#             print(f"❌ Failed to sync {file}: {e}")

#     print(f"✅ Sync Summary: {success} operations synced.")

# if __name__ == "__main__":
#     main()


# import os
# import json
# from azure.identity import DefaultAzureCredential
# from azure.mgmt.apimanagement import ApiManagementClient
# from azure.mgmt.apimanagement.models import OperationContract, RequestContract, ResponseContract, ParameterContract, RepresentationContract

# SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
# RESOURCE_GROUP = os.environ["AZURE_RESOURCE_GROUP"]
# SERVICE_NAME = os.environ["AZURE_APIM_NAME"]
# API_ID = os.environ["AZURE_APIM_API_ID"]
# SPLIT_DIR = "split"

# credential = DefaultAzureCredential()
# client = ApiManagementClient(credential, SUBSCRIPTION_ID)

# def get_operation_info(filepath):
#     with open(filepath, "r") as f:
#         data = json.load(f)

#     # Expect single path with single method
#     paths = data.get("paths", {})
#     if not paths or len(paths) != 1:
#         raise ValueError(f"Invalid or multiple paths in: {filepath}")

#     path = next(iter(paths))
#     method_dict = paths[path]
#     if not method_dict or len(method_dict) != 1:
#         raise ValueError(f"Invalid or multiple methods in: {filepath}")

#     method = next(iter(method_dict)).upper()
#     operation = method_dict[method.lower()]
#     operation_id = operation.get("operationId")
#     if not operation_id:
#         raise ValueError(f"Missing operationId in {filepath}")

#     return {
#         "id": operation_id,
#         "method": method,
#         "url_template": path,
#         "definition": operation,
#     }

# def create_or_update_operation(op):
#     print(f"🔄 Syncing {op['method']} {op['url_template']} ({op['id']})")

#     parameters = op["definition"].get("parameters", [])
#     request_body = op["definition"].get("requestBody", {})
#     responses = op["definition"].get("responses", {})

#     request_desc = request_body.get("description", "")
#     req_schema = request_body.get("content", {}).get("application/json", {}).get("schema", {})

#     query_params = [ParameterContract(**p) for p in parameters if p["in"] == "query"]
#     path_params = [ParameterContract(**p) for p in parameters if p["in"] == "path"]

#     request = RequestContract(
#         description=request_desc,
#         query_parameters=query_params,
#         template_parameters=path_params,
#         representations=[
#             RepresentationContract(
#                 content_type="application/json",
#                 schema=req_schema
#             )
#         ] if req_schema else []
#     )

#     response_objs = [
#         ResponseContract(
#             status_code=str(status),
#             description=resp.get("description", "")
#         )
#         for status, resp in responses.items()
#     ]

#     operation = OperationContract(
#         display_name=op["id"],
#         method=op["method"],
#         url_template=op["url_template"],
#         request=request,
#         responses=response_objs
#     )

#     client.api_operation.create_or_update(
#         resource_group_name=RESOURCE_GROUP,
#         service_name=SERVICE_NAME,
#         api_id=API_ID,
#         operation_id=op["id"],
#         parameters=operation
#     )

# def main():
#     if not os.path.isdir(SPLIT_DIR):
#         print(f"❌ Folder '{SPLIT_DIR}' not found.")
#         return

#     files = [
#         os.path.join(root, f)
#         for root, _, fs in os.walk(SPLIT_DIR)
#         for f in fs if f.endswith(".json")
#     ]

#     print(f"📦 Syncing Swagger operations to APIM...")
#     success = 0

#     for file in files:
#         try:
#             op = get_operation_info(file)
#             create_or_update_operation(op)
#             success += 1
#         except Exception as e:
#             print(f"❌ Failed to sync {file}: {e}")

#     print(f"✅ Sync Summary: {success} operations synced.")

# if __name__ == "__main__":
#     main()

import os
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
from azure.mgmt.apimanagement.models import OperationContract, RequestContract, ParameterContract, ResponseContract, RepresentationContract

SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
RESOURCE_GROUP = os.environ["AZURE_RESOURCE_GROUP"]
SERVICE_NAME = os.environ["AZURE_APIM_NAME"]
API_ID = os.environ["AZURE_APIM_API_ID"]
SPLIT_DIR = "split"

credential = DefaultAzureCredential()
client = ApiManagementClient(credential, SUBSCRIPTION_ID)

def get_operation_info(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)

    # Expect a single path with a single method
    paths = data.get("paths", {})
    if not paths or len(paths) != 1:
        raise ValueError(f"Invalid or multiple paths in: {filepath}")
    
    path = next(iter(paths))
    method_dict = paths[path]
    if not method_dict or len(method_dict) != 1:
        raise ValueError(f"Invalid or multiple methods in: {filepath}")
    
    method = next(iter(method_dict)).upper()
    operation = method_dict[method.lower()]
    operation_id = operation.get("operationId")
    if not operation_id:
        raise ValueError(f"Missing operationId in {filepath}")
    
    return {
        "id": operation_id,
        "method": method,
        "url_template": path,
        "definition": operation,
    }

def create_or_update_operation(op):
    print(f"🔄 Syncing {op['method']} {op['url_template']} ({op['id']})")

    operation_def = op["definition"]
    parameters = operation_def.get("parameters", [])
    request_body = operation_def.get("requestBody", {})
    responses = operation_def.get("responses", {})

    # Parse parameters
    template_params = []
    query_params = []

    for p in parameters:
        param = ParameterContract(
            name=p["name"],
            required=p.get("required", False),
            type=p.get("schema", {}).get("type", "string"),
            default_value=p.get("default", None),
            description=p.get("description", ""),
        )
        if p["in"] == "path":
            template_params.append(param)
        elif p["in"] == "query":
            query_params.append(param)

    # Parse request body
    req_desc = request_body.get("description", "")
    req_schema = request_body.get("content", {}).get("application/json", {}).get("schema", {})

    request_contract = RequestContract(
        description=req_desc,
        query_parameters=query_params if query_params else None,
        template_parameters=template_params if template_params else None,
        representations=[
            RepresentationContract(
                content_type="application/json",
                schema=req_schema
            )
        ] if req_schema else None
    )

    # Parse responses
    response_contracts = []
    for status_code, response in responses.items():
        response_contracts.append(
            ResponseContract(
                status_code=str(status_code),
                description=response.get("description", "")
            )
        )

    # Final operation contract
    operation_contract = OperationContract(
        display_name=op["id"],
        method=op["method"],
        url_template=op["url_template"],
        request=request_contract,
        responses=response_contracts
    )

    # Call APIM
    client.api_operation.create_or_update(
        resource_group_name=RESOURCE_GROUP,
        service_name=SERVICE_NAME,
        api_id=API_ID,
        operation_id=op["id"],
        parameters=operation_contract
    )

def main():
    if not os.path.isdir(SPLIT_DIR):
        print(f"❌ Folder '{SPLIT_DIR}' not found.")
        return

    files = [
        os.path.join(root, f)
        for root, _, fs in os.walk(SPLIT_DIR)
        for f in fs if f.endswith(".json")
    ]

    print(f"📦 Syncing Swagger operations to APIM...")
    success = 0

    for file in files:
        try:
            op = get_operation_info(file)
            create_or_update_operation(op)
            success += 1
        except Exception as e:
            print(f"❌ Failed to sync {file}: {e}")

    print(f"✅ Sync Summary: {success} operations synced.")

if __name__ == "__main__":
    main()
