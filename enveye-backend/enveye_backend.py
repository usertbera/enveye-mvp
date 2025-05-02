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
from fastapi import Body
from PIL import Image
import pytesseract
import base64
import io
import re
import unicodedata
from openai import OpenAI



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
#genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Serve Frontend Static Files ---
app.mount("/static", StaticFiles(directory="../enveye-frontend/dist"), name="static")

# --- Setup Snapshot Directory ---
BASE_DIR = Path(__file__).resolve().parent
SNAPSHOT_DIR = BASE_DIR / "snapshots"
SNAPSHOT_DIR.mkdir(exist_ok=True)

# --- Mount Snapshots as Static ---
app.mount("/snapshots", StaticFiles(directory=SNAPSHOT_DIR), name="snapshots")


@app.get("/")
async def serve_spa():
    return FileResponse("../enveye-frontend/dist/index.html")
    
@app.get("/snapshots")
async def serve_spa():
    return FileResponse("../enveye-frontend/dist/index.html")

# --- Upload Snapshot API ---
@app.post("/upload_snapshot")
async def upload_snapshot(request: Request, snapshot: UploadFile = File(...)):
    try:
        form_data = await request.form()
        hostname = form_data.get("hostname", "unknown_host")
        app_folder = form_data.get("app_path", "unknown_app")
        app_name = os.path.basename(app_folder)
        app_name = app_name.replace(" ","")
        
        print(f"app name:{app_name}")

        content = await snapshot.read()
        parsed_content = json.loads(content)

        filename = SNAPSHOT_DIR / f"{hostname}_{app_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

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
async def explain_diff(payload: dict = Body(...)):
    try:
        diff = payload.get("diff", {})
        error_message = payload.get("error_message", "").strip()
        error_screenshot = payload.get("error_screenshot", None)
        log_path = payload.get("log_path", "").strip()

        # Extract log content
        log_content = ""
        if log_path:
            full_log = read_log_file(log_path)
            log_content = extract_important_log_lines(full_log)

        # Extract text from image if present
        screenshot_text = ""
        if error_screenshot:
            screenshot_text = extract_text_from_screenshot(error_screenshot)

        # Construct the prompt
        prompt = f"""
You are a helpful assistant specialized in IT system configuration comparisons.
Given the following DeepDiff output between two VMs, do the following:

1. Give a summary of what has changed
2. If an error message is provided or found in a screenshot, analyze it in context of the diff.
3. Incorporate log file clues if available.
4. Suggest possible root causes or solutions
5. Be concise and highlight important issues

Diff data:
{json.dumps(diff, indent=2)}

Error message (if any):
{error_message or 'None'}

Error message (from screenshot):
{screenshot_text or 'None'}

Log Content (if any):
{log_content or 'None'}
"""

        # Use OpenAI GPT-4. If "gpt-4.1" is not supported, fallback to "gpt-4"
        response = client.chat.completions.create(
            model="gpt-4",  # Adjust this if "gpt-4.1" is confirmed supported
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )

        # Aggregate streamed content
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content

        return {"explanation": full_response}

    except Exception as e:
        print("❌ Error during AI explanation:", e)
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
        
# --- Utilities ---
def normalize_log_block(block):
    # Remove timestamps and join for deduplication
    clean = re.sub(r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}(?:[,\.]\d+)?', '', block)
    clean = re.sub(r'\d{2}:\d{2}:\d{2}(?:[,\.]\d+)?', '', clean)
    return clean.strip()

def extract_important_log_blocks(log_text, keywords=None, max_blocks=30):
    """
    Extracts important log blocks, including multi-line stack traces,
    filters by keyword, deduplicates by content (ignoring timestamps),
    and limits output to the latest N unique blocks.
    """
    keywords = keywords or ['ERROR', 'Exception', 'Traceback', 'CRITICAL', 'Failed', 'Caused by']
    lines = log_text.splitlines()

    blocks = []
    current_block = []
    seen = set()

    def commit_block():
        if current_block:
            full_block = "\n".join(current_block).strip()
            norm = normalize_log_block(full_block)
            if norm not in seen:
                seen.add(norm)
                blocks.append(full_block)
            current_block.clear()

    for line in lines:
        if any(k in line for k in keywords):
            commit_block()  # Save previous block before starting new one
            current_block.append(line)
        elif current_block and (line.startswith(" ") or line.startswith("\t") or line.strip() == ""):
            # Likely a stack trace or continuation
            current_block.append(line)
        else:
            commit_block()

    commit_block()  # Final block

    return "\n\n---\n\n".join(blocks[-max_blocks:])



def read_log_file(path):
    try:
        if os.path.exists(path) and path.endswith('.log'):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        print("⚠️ Failed to read log:", e)
    return ""


def extract_text_from_screenshot(base64_image):
    try:
        image_data = base64.b64decode(base64_image.split(",")[-1])
        image = Image.open(io.BytesIO(image_data))
        raw_text = pytesseract.image_to_string(image)
        cleaned_text = clean_ocr_text(raw_text)
        return cleaned_text
    except Exception as e:
        print("Error extracting text from screenshot:", e)
        return ""
        
def clean_ocr_text(text):
    # Normalize Unicode (e.g., accented characters)
    text = unicodedata.normalize("NFKD", text)

    # Remove non-printable characters (keep ASCII)
    text = re.sub(r'[^\x20-\x7E]+', '', text)

    # Collapse multiple spaces, remove leading/trailing whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text

