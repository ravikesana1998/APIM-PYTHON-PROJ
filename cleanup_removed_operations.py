#!/usr/bin/env python3
import os, sys, subprocess, json

def run(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return res.stdout if res.returncode == 0 else None

def main():
    rg = os.getenv("AZURE_RESOURCE_GROUP")
    svc = os.getenv("AZURE_APIM_NAME")
    api = os.getenv("AZURE_APIM_API_ID")

    local = json.load(open(sys.argv[1]))
    local_ids = {op.get('operationId') for ms in local.get('paths', {}).values() for op in ms.values()}

    remote_ops = run(f"az apim api operation list --resource-group {rg} --service-name {svc} --api-id {api}")
    remote_list = json.loads(remote_ops or "[]")

    for op in remote_list:
        oid = op.get('name')
        if oid not in local_ids:
            print(f"Deleting removed operation `{oid}`")
            run(f"az apim api operation delete --resource-group {rg} --service-name {svc} --api-id {api} --operation-id {oid} --yes")

if __name__ == '__main__':
    main()
