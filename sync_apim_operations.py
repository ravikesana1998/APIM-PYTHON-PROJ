import os, json, subprocess

api_id = os.environ["APIM_API_NAME"]
resource_group = os.environ["APIM_RESOURCE_GROUP"]
service_name = os.environ["APIM_SERVICE_NAME"]

for filename in os.listdir("split"):
    if not filename.endswith(".json"):
        continue
    filepath = os.path.join("split", filename)
    with open(filepath) as f:
        data = json.load(f)
        method = list(data["paths"].values())[0].keys()[0].upper()
        url_template = list(data["paths"].keys())[0]
        operation_id = filename.replace(".json", "")
        display_name = operation_id
        try:
            subprocess.run([
                "az", "apim", "api", "operation", "create",
                "--resource-group", resource_group,
                "--service-name", service_name,
                "--api-id", api_id,
                "--operation-id", operation_id,
                "--display-name", display_name,
                "--method", method,
                "--url-template", url_template,
                "--template-parameters", "name=email",  # Add more as needed
                "--response-status-codes", "200"
            ], check=True)
            print(f"✅ Synced: {operation_id}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to sync {operation_id}: {e}")
