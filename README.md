EnvEye - Environment Snapshot & Comparison Tool 🚀

EnvEye is a QA/Testing innovation tool designed to collect, compare, and explain differences between environment setups (VMs, servers, desktops) — using AI assistance!

📦 Components

Collector Agent (EXE): Portable executable that collects critical environment information (DLLs, Services, Registry, Configs) into a JSON snapshot.

FastAPI Backend: Provides APIs to compare snapshots and explain differences via OpenAI.

React Frontend: Web dashboard to upload, compare, and visualize environment differences.

AI Integration: GPT-3.5-Turbo used to explain detected configuration differences.

🚀 Quick Start

1. Clone the Repository

git clone https://github.com/YOUR_USERNAME/enveye-mvp.git
cd enveye-mvp

2. Setup Backend (FastAPI)

cd enveye-backend
pip install -r requirements.txt

✅ Set your OpenAI API key before running:

# Windows CMD
set OPENAI_API_KEY=your-openai-api-key

# PowerShell
$env:OPENAI_API_KEY="your-openai-api-key"

3. Setup Frontend (React)

cd enveye-frontend
npm install
npm run build

✅ This generates optimized production files inside /dist/.

4. Start Backend Server (Serving Frontend + APIs)

cd enveye-backend
uvicorn enveye_backend:app --reload

✅ Open http://localhost:8000 in browser!✅ Upload snapshots → Compare → Get AI explanations! 🚀

🛠️ Building Collector Agent EXE

To rebuild the portable EXE if needed:

pip install pyinstaller
pyinstaller --onefile --clean collector_agent.py

✅ Final EXE available inside /dist/ folder.

✅ This EXE can be copied to any VM without requiring Python!

📄 Environment Variables

Variable

Purpose

OPENAI_API_KEY

API key for GPT-3.5-Turbo integration

You can also create a .env file:

OPENAI_API_KEY=your-openai-api-key-here

📂 Project Folder Structure

VMCompare/
├── enveye-frontend/    # React Frontend App
│    ├── dist/          # Production build output
├── enveye-backend/     # FastAPI Backend API
│    └── enveye_backend.py
├── collector_agent.py  # Collector Agent Script
└── README.md           # This file

📢 Key Features

Portable Agent EXE (no Python needed at VM side)

DeepDiff JSON comparison

AI-generated intelligent explanations

Unified backend serving both frontend and APIs

Easy deployment and scaling possibilities

📜 License

This project is currently for internal use and testing automation purposes.(You can add a real license later if planning open-source!)

🌟 Happy Testing with EnvEye! 🚀
