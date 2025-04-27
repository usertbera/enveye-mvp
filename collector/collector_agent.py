import os
import json
import platform
import subprocess
import xml.etree.ElementTree as ET
import threading
import itertools
import sys
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime

# --- Spinner utilities ---
spinner_running = False

def spinner_task():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if not spinner_running:
            break
        sys.stdout.write(f'\rCollecting... {c}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r')

# --- Helper Functions ---
def get_os_info():
    return {
        "name": platform.system(),
        "version": platform.version(),
        "build": platform.release(),
        "architecture": platform.machine()
    }

def get_dotnet_versions():
    try:
        output = subprocess.check_output([
            "powershell", "-Command",
            "Get-ChildItem 'HKLM:\\SOFTWARE\\Microsoft\\NET Framework Setup\\NDP' -Recurse | "
            "Get-ItemProperty -Name Version -ErrorAction SilentlyContinue | "
            "Where { $_.PSChildName -match '^(?!S)\\p{L}'} | "
            "Select-Object -ExpandProperty Version"
        ], text=True)
        versions = [line.strip() for line in output.splitlines() if line.strip()]
        return versions
    except Exception as e:
        return [f"Error retrieving .NET versions: {e}"]

def list_dll_versions(app_folder_path):
    dll_versions = {}
    if not os.path.exists(app_folder_path):
        return {"error": "App folder not found."}

    for root, dirs, files in os.walk(app_folder_path):
        for file in files:
            if file.endswith(".dll"):
                file_path = os.path.join(root, file)
                try:
                    file_version_output = subprocess.check_output([
                        "powershell", "-Command",
                        f"(Get-Item '{file_path}').VersionInfo.FileVersion"
                    ], text=True, timeout=10)
                    file_version = file_version_output.strip()

                    try:
                        assembly_version_output = subprocess.check_output([
                            "powershell", "-Command",
                            f"([Reflection.AssemblyName]::GetAssemblyName('{file_path}')).Version.ToString()"
                        ], text=True, timeout=10)
                        assembly_version = assembly_version_output.strip()
                    except:
                        assembly_version = "Not .NET Assembly"

                    dll_versions[file_path] = {
                        "file_version": file_version,
                        "assembly_version": assembly_version
                    }
                except subprocess.TimeoutExpired:
                    dll_versions[file_path] = {"file_version": "Timeout", "assembly_version": "Timeout"}
                except Exception as e:
                    dll_versions[file_path] = {
                        "file_version": "Unknown",
                        "assembly_version": "Unknown",
                        "error": str(e)
                    }
    return dll_versions

def find_config_file(app_folder, app_type):
    if app_type.lower() == "desktop":
        for file in os.listdir(app_folder):
            if file.endswith(".exe.config"):
                return os.path.join(app_folder, file)
    elif app_type.lower() == "web":
        config_path = os.path.join(app_folder, "web.config")
        if os.path.exists(config_path):
            return config_path
    return None

def read_app_config(config_path):
    config_data = {}
    if not os.path.exists(config_path):
        return {"error": f"Config file not found at {config_path}"}

    try:
        tree = ET.parse(config_path)
        root = tree.getroot()

        app_settings = {}
        for setting in root.findall(".//appSettings/add"):
            key = setting.attrib.get('key')
            value = setting.attrib.get('value')
            app_settings[key] = value

        connection_strings = {}
        for conn in root.findall(".//connectionStrings/add"):
            name = conn.attrib.get('name')
            conn_string = conn.attrib.get('connectionString')
            connection_strings[name] = conn_string

        config_data['app_settings'] = app_settings
        config_data['connection_strings'] = connection_strings

    except Exception as e:
        config_data["error"] = str(e)

    return config_data

def read_registry_keys(keys_to_read):
    registry_data = {}
    for reg_path in keys_to_read:
        try:
            output = subprocess.check_output([
                "powershell", "-Command",
                f"Get-ItemProperty -Path '{reg_path}' | Select-Object *"
            ], text=True)

            props = {}
            for line in output.splitlines():
                if ':' in line:
                    parts = line.split(':', 1)
                    key = parts[0].strip()
                    value = parts[1].strip()
                    props[key] = value

            registry_data[reg_path] = props

        except Exception as e:
            registry_data[reg_path] = {"error": str(e)}
    return registry_data

def check_services(service_names):
    service_status = {}
    for service in service_names:
        try:
            output = subprocess.check_output([
                "powershell", "-Command",
                f"(Get-Service -Name '{service}').Status"
            ], text=True)
            status = output.strip()
            service_status[service] = status
        except Exception as e:
            service_status[service] = "Service not found or error"
    return service_status

def read_environment_variables(variable_names):
    env_vars = {}
    for var in variable_names:
        value = os.environ.get(var, "Not Set")
        env_vars[var] = value
    return env_vars

# --- Main ---
def main():
    global spinner_running
    print("Welcome to EnvEye Collector!")

    parser = argparse.ArgumentParser()
    parser.add_argument("--app-folder", help="Path to the application folder")
    parser.add_argument("--app-type", help="Type of application: desktop or web")
    parser.add_argument("--upload-url", help="Optional: Upload URL to send snapshot")
    args = parser.parse_args()

    if not args.app_folder or not args.app_type:
        print("\u274c Missing required arguments --app-folder and --app-type")
        return

    app_folder = args.app_folder
    app_type = args.app_type

    config_file_path = find_config_file(app_folder, app_type)

    spinner_running = True
    spinner_thread = threading.Thread(target=spinner_task)
    spinner_thread.start()

    registry_keys_to_read = [r"HKEY_LOCAL_MACHINE\\SOFTWARE\\SampleApp\\Settings"]
    services_to_check = ["MSSQL$SQLEXPRESS", "W3SVC"]
    environment_variables_to_read = ["APP_ENV", "ENVIRONMENT"]

    mcp_context = {
        "application_name": Path(app_folder).name,
        "application_type": app_type,
        "environment_context": {
            "os_info": get_os_info(),
            "dotnet_frameworks_installed": get_dotnet_versions(),
            "app_folder_dlls": list_dll_versions(app_folder),
            "app_config_settings": read_app_config(config_file_path) if config_file_path else {},
            "critical_registry_keys": read_registry_keys(registry_keys_to_read),
            "required_services_status": check_services(services_to_check),
            "critical_environment_variables": read_environment_variables(environment_variables_to_read)
        },
        "timestamp": datetime.now().astimezone().isoformat()
    }

    output_file = "context_snapshot.json"
    with open(output_file, "w") as f:
        json.dump(mcp_context, f, indent=4)

    spinner_running = False
    spinner_thread.join()

    print(f"\n Context snapshot saved successfully to {output_file}")

    # --- Try uploading if upload-url provided ---
    if args.upload_url:
        try:
            with open(output_file, "rb") as f:
                files = {"snapshot": (output_file, f, "application/json")}
                data = {
                        "hostname": platform.node(),
                        "app_path": args.app_folder
                    }


                print(f"Uploading to {args.upload_url} with hostname {platform.node()}...")

                response = requests.post(args.upload_url, files=files, data=data, timeout=120)

            if response.status_code == 200:
                print(" Successfully uploaded snapshot to backend!")
            else:
                print(f" Failed to upload snapshot. Status: {response.status_code} Response: {response.text}")
        except Exception as e:
            print(f" Exception during upload: {e}")

if __name__ == "__main__":
    main()