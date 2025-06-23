import os
import subprocess

def import_operation(api_name, apim_name, rg, swagger_file, op_display_name):
    command = [
        "az", "apim", "api", "import",
        "--resource-group", rg,
        "--service-name", apim_name,
        "--api-id", api_name,
        "--path", api_name,
        "--specification-format", "OpenApiJson",
        "--specification-path", swagger_file,
        "--display-name", op_display_name,
        "--api-revision", "1"
    ]
    subprocess.run(command, check=True)

if __name__ == '__main__':
    import sys
    input_dir = sys.argv[1]
    api_name = sys.argv[2]
    apim_name = sys.argv[3]
    rg = sys.argv[4]

    for file in os.listdir(input_dir):
        if file.endswith(".json"):
            import_operation(api_name, apim_name, rg, os.path.join(input_dir, file), file.split('.')[0])
