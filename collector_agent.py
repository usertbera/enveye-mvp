import os
import json
import platform
import subprocess
import xml.etree.ElementTree as ET
import threading
import itertools
import sys
import time
from pathlib import Path
from datetime import datetime

# ---- [ Functions start here ] ----

def get_os_info():
    return {
        "name": platform.system(),
        "version": platform.version(),
        "build": platform.release(),
        "architecture": platform.machine()
    }

def get_dotnet_versions():
    try:
        output = subprocess.check_output(["powershell", "-Command", 
            "Get-ChildItem 'HKLM:\\SOFTWARE\\Microsoft\\NET Framework Setup\\NDP' -Recurse | "
            "Get-ItemProperty -Name Version -ErrorAction SilentlyContinue | "
            "Where { $_.PSChildName -match '^(?!S)\\p{L}'} | "
            "Select-Object -ExpandProperty Version"], text=True)
        versions = [line.strip() for line in output.splitlines() if line.strip()]
        return versions
    except Exception as e:
        return ["Error retrieving .NET versions: " + str(e)]

def list_dll_versions(app_folder_path):
    dll_versions = {}
    if not os.path.exists(app_folder_path):
        return {"error": "App folder not found."}

    for file in os.listdir(app_folder_path):
        if file.endswith(".dll"):
            file_path = os.path.join(app_folder_path, file)
            try:
                file_version_output = subprocess.check_output([
                    "powershell", "-Command",
                    f"(Get-Item '{file_path}').VersionInfo.FileVersion"
                ], text=True)
                file_version = file_version_output.strip()

                assembly_version_output = subprocess.check_output([
                    "powershell", "-Command",
                    f"([Reflection.AssemblyName]::GetAssemblyName('{file_path}')).Version.ToString()"
                ], text=True)
                assembly_version = assembly_version_output.strip()

                dll_versions[file] = {
                    "file_version": file_version,
                    "assembly_version": assembly_version
                }
            except Exception as e:
                dll_versions[file] = {
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

# ---- [ Main Application Starts Here ] ----

def main():
    global spinner_running
    print("Welcome to EnvEye Collector!")
    app_folder = input("Enter the Application Folder Path (e.g., C:\\Program Files\\SampleApp): ").strip()
    app_type = input("Is this a 'desktop' or 'web' application? ").strip().lower()

    if not os.path.exists(app_folder):
        print(f"Error: The folder {app_folder} does not exist.")
        return

    config_file_path = find_config_file(app_folder, app_type)
    if not config_file_path:
        print(f"Warning: Could not find config file for {app_type} app in {app_folder}")

    spinner_running = True
    spinner_thread = threading.Thread(target=spinner_task)
    spinner_thread.start()

    registry_keys_to_read = [
        r"HKEY_LOCAL_MACHINE\\SOFTWARE\\SampleApp\\Settings"
    ]
    services_to_check = [
        "MSSQL$SQLEXPRESS",
        "W3SVC"
    ]
    environment_variables_to_read = [
        "APP_ENV", "ENVIRONMENT"
    ]

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
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    output_file = "context_snapshot.json"
    with open(output_file, "w") as f:
        json.dump(mcp_context, f, indent=4)

    spinner_running = False
    spinner_thread.join()

    print("\nContext snapshot saved successfully to", output_file)

if __name__ == "__main__":
    main()