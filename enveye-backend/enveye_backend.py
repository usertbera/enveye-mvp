from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from deepdiff import DeepDiff
import google.generativeai as genai
import winrm
import json
import os
import concurrent.futures
import traceback
from pathlib import Path
from datetime import datetime
import base64

# --- FastAPI Application ---
app = FastAPI(title="EnvEye - Context Comparator API")

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configure Gemini API ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Serve Frontend Static Files ---
app.mount("/static", StaticFiles(directory="../enveye-frontend/dist"), name="static")

@app.get("/")
async def serve_spa():
    return FileResponse("../enveye-frontend/dist/index.html")

# --- Setup Snapshot Directory ---
BASE_DIR = Path(__file__).resolve().parent
SNAPSHOT_DIR = BASE_DIR / "snapshots"
SNAPSHOT_DIR.mkdir(exist_ok=True)

# --- Mount Snapshots as Static ---
app.mount("/snapshots", StaticFiles(directory=SNAPSHOT_DIR), name="snapshots")

# --- Upload Snapshot API ---
@app.post("/upload_snapshot")
async def upload_snapshot(request: Request, snapshot: UploadFile = File(...)):
    try:
        form_data = await request.form()
        hostname = form_data.get("hostname", "unknown_host")

        content = await snapshot.read()
        parsed_content = json.loads(content)

        filename = SNAPSHOT_DIR / f"{hostname}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

        with open(filename, "w") as f:
            f.write(json.dumps(parsed_content, indent=4))

        print(f"\u2705 Snapshot received and saved: {filename}")

        return {"message": f"Snapshot from {hostname} collected successfully!"}

    except Exception as e:
        print(f"\u274C Error while saving snapshot: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# --- Compare Snapshots API ---
@app.post("/compare")
async def compare_snapshots(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    try:
        file1_content = await file1.read()
        file2_content = await file2.read()

        data1 = json.loads(file1_content)
        data2 = json.loads(file2_content)

        diff = DeepDiff(data1.get('environment_context', {}), data2.get('environment_context', {}), view='tree')

        return JSONResponse(content={"differences": json.loads(diff.to_json())})

    except Exception as e:
        print(f"\u274C Exception during /compare: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=400)

# --- Explain Differences API ---
@app.post("/explain")
async def explain_diff(diff: dict):
    try:
        prompt = f"""
You are a helpful assistant specialized in IT system configuration comparisons.
Given the following DeepDiff output between two VMs, do the following:

1. Give a summary of what has changed
2. Give a solution if possible
3. Be concise and highlight important issues

Here is the diff data:
{diff}
"""
        model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
        response = model.generate_content(prompt)

        return {"explanation": response.text}

    except Exception as e:
        print(f"\u274C Error during AI explanation: {e}")
        return {"error": str(e)}

# --- Remote Collection API ---
@app.post("/remote_collect")
async def remote_collect(request: Request):
    try:
        body = await request.json()
        vm_ip = body.get("vm_ip")
        username = body.get("username")
        password = body.get("password")
        app_folder = body.get("app_folder")
        app_type = body.get("app_type")

        print(f"\u2705 Remote Collect Request: {vm_ip}, AppFolder={app_folder}")

        session = winrm.Session(
            f'http://{vm_ip}:5985/wsman',
            auth=(username, password),
            transport='ntlm'
        )

        backend_ip = "10.40.10.214"
        upload_url = f"http://{backend_ip}:8000/upload_snapshot"

        # Check if agent exists remotely
        check_command = "if (!(Test-Path 'C:\\Tools\\Collector\\collector_agent.exe')) { exit 1 }"
        check_result = session.run_ps(check_command)

        if check_result.status_code != 0:
            print("\u26A1 Remote agent not found, uploading...")

            local_agent_path = BASE_DIR / "collector" / "collector_agent.exe"
            with open(local_agent_path, "rb") as agent_file:
                encoded_agent = base64.b64encode(agent_file.read()).decode()

            ps_script = f"""
            $bytes = [System.Convert]::FromBase64String(\"{encoded_agent}\")
            $path = 'C:\\Tools\\Collector\\collector_agent.exe'
            New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null
            [System.IO.File]::WriteAllBytes($path, $bytes)
            """
            upload_result = session.run_ps(ps_script)
            print("✅ Agent upload result:", upload_result.status_code)

        collector_command = (
            f'cmd /c "C:\\Tools\\Collector\\collector_agent.exe '
            f'--app-folder \"{app_folder}\" '
            f'--app-type {app_type} '
            f'--upload-url {upload_url}"'
        )

        print(f"\u2705 Prepared Command: {collector_command}")

        def run_remote_cmd():
            return session.run_cmd(collector_command)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_remote_cmd)
            try:
                result = future.result(timeout=900)
            except concurrent.futures.TimeoutError:
                print("\u274C Remote Collector Timed Out after 10 minutes!")
                return JSONResponse(content={"error": "Timeout after 10 minutes."}, status_code=500)

        print(f"\u2705 Remote Collector exited with code {result.status_code}")
        print("✅ StdOut:", result.std_out.decode(errors="ignore"))
        print("✅ StdErr:", result.std_err.decode(errors="ignore"))

        if result.status_code == 0:
            return {
                "status": "success",
                "message": f"Snapshot from {vm_ip} collected and uploaded!",
                "vm_hostname": vm_ip
            }
        else:
            return JSONResponse(
                content={"error": f"Remote agent failed. Code {result.status_code}"},
                status_code=500
            )

    except Exception as e:
        print("\u274C FULL EXCEPTION in /remote_collect")
        print(traceback.format_exc())
        return JSONResponse(content={"error": str(e)}, status_code=500)
        
        
@app.get("/list_snapshots")
async def list_snapshots():
    try:
        snapshots = []
        for file in SNAPSHOT_DIR.glob("*.json"):
            snapshots.append(file.name)
        return {"snapshots": snapshots}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/download_snapshot/{filename}")
async def download_snapshot(filename: str):
    file_path = SNAPSHOT_DIR / filename
    if file_path.exists():
        return FileResponse(file_path, filename=filename, media_type='application/json')
    else:
        return JSONResponse(content={"error": "File not found."}, status_code=404)

