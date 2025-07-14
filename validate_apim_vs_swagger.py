#!/usr/bin/env python3
import os, sys, json, subprocess

def run(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stderr)
        sys.exit(res.returncode)
    return res.stdout

def main():
    local = json.load(open(sys.argv[1]))
    sub = os.getenv("AZURE_SUBSCRIPTION_ID")
    rg = os.getenv("AZURE_RESOURCE_GROUP")
    svc = os.getenv("AZURE_APIM_NAME")
    api = os.getenv("AZURE_APIM_API_ID")

    # Export remote API spec
    remote = run(f"az apim api export --resource-group {rg} --service-name {svc} --api-id {api} --format openapi-link")
    remote_spec = json.loads(remote)
    # Compare operation counts
    local_ops = sum(len(m) for m in local.get("paths", {}).values())
    remote_ops = sum(len(m) for m in remote_spec.get("paths", {}).values())
    print(f"Local operations: {local_ops}, Remote operations: {remote_ops}")
    if local_ops != remote_ops:
        print("⚠️ Operation count mismatch! Please investigate.")
        sys.exit(1)

    print("✅ Local and remote APIs are in sync.")

if __name__ == '__main__':
    main()
