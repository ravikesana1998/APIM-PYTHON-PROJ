import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient

subscription_id = os.environ["APIM_SUBSCRIPTION_ID"]
resource_group = os.environ["APIM_RESOURCE_GROUP"]
service_name = os.environ["APIM_SERVICE_NAME"]
api_id = os.environ["APIM_API_NAME"]

split_dir = "./split"
local_operation_ids = set(f.replace(".json", "") for f in os.listdir(split_dir) if f.endswith(".json"))

credential = DefaultAzureCredential()
client = ApiManagementClient(credential, subscription_id)
remote_ops = client.api_operation.list_by_api(resource_group, service_name, api_id)

remote_operation_ids = set(op.name for op in remote_ops)

stale_ops = remote_operation_ids - local_operation_ids

for op_id in stale_ops:
    print(f"🗑️ Deleting stale operation: {op_id}")
    client.api_operation.delete(resource_group, service_name, api_id, op_id, if_match="*")
