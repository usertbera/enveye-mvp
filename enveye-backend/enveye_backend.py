from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from deepdiff import DeepDiff
import google.generativeai as genai
import json
import os

app = FastAPI(title="EnvEye - Context Comparator API 🚀")

# --- CORS to allow frontend connection ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins during dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Setup Gemini Client ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- Serve Frontend Static Files (React Build) ---
app.mount("/static", StaticFiles(directory="../enveye-frontend/dist"), name="static")

# --- Root Endpoint ---
@app.get("/")
async def serve_spa():
    return FileResponse("../enveye-frontend/dist/index.html")

# --- Compare Endpoint ---
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
        print(f"❌ Exception during /compare: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=400)

# --- Explain Differences Endpoint ---
@app.post("/explain")
async def explain_diff(diff: dict):
    try:
        prompt = f"""
You are a helpful assistant specialized in IT system configuration comparisons.
Given the following DeepDiff output between two VMs, do the following:

1. List each DLL file that changed, added, or removed, mentioning the file name and old/new version.
2. List services that were stopped, missing, or started.
3. List environment variables that changed.
4. Provide findings as bullet points, one finding per line.
5. Be detailed but concise.
6. Do NOT repeat generic summary, focus on concrete facts.

Here is the diff data:
{diff}
"""

        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)

        explanation = response.text

        return {"explanation": explanation}

    except Exception as e:
        print(f"❌ Error during AI explanation: {e}")
        return {"error": str(e)}
