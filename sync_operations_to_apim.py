#!/usr/bin/env python3
import os, sys, subprocess

def run(cmd):
    print(">", cmd)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr)
    return r

def main():
    swagger = sys.argv[1]
    split_dir = sys.argv[2]
    rg = os.getenv("AZURE_RESOURCE_GROUP")
    svc = os.getenv("AZURE_APIM_NAME")
    api = os.getenv("AZURE_APIM_API_ID")

    for fname in os.listdir(split_dir):
        if not fname.endswith('.json'): continue
        full = os.path.join(split_dir, fname)
        spec = swagger_path = full
        print(f"Syncing {fname}")
        run(
            f"az apim api operation import --resource-group {rg} "
            f"--service-name {svc} --api-id {api} --path {fname[:-5]} "
            f"--specification-format OpenApi --specification-path {spec}"
        )

if __name__ == '__main__':
    main()
