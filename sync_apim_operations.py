import os, subprocess

def import_api(file_path):
    api_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"📤 Importing {api_name}...")

    subprocess.run([
        "az", "apim", "api", "import",
        "--resource-group", os.environ["APIM_RESOURCE_GROUP"],
        "--service-name", os.environ["APIM_SERVICE_NAME"],
        "--api-id", api_name,
        "--path", api_name,
        "--specification-format", "OpenApiJson",
        "--specification-path", file_path,
        "--subscription-id", os.environ["APIM_SUBSCRIPTION_ID"],
        "--display-name", api_name,
        "--api-revision", "1",
        "--service-url", os.environ["swaggerUrl"],
        "--subscription-required", "false"
    ], check=True)

def main():
    split_dir = "split"
    if not os.path.exists(split_dir):
        print("❌ Split directory not found.")
        return

    for f in os.listdir(split_dir):
        if f.endswith(".json"):
            import_api(os.path.join(split_dir, f))

    print("✅ All CRUD operations imported into APIM.")

if __name__ == "__main__":
    main()
