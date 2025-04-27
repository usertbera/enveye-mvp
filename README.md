# EnvEye - Intelligent Snapshot Comparator
![logo_96x96](https://github.com/user-attachments/assets/d894b153-d3d3-43ff-8703-98772fd544fc)

---

## 📈 Project Overview

**EnvEye** is a smart debugging assistant for IT environments. It compares snapshots of system states (from two Virtual Machines) and highlights key differences. Using Google Gemini AI, it analyzes configuration issues, error messages, and suggests potential root causes and fixes.

Built to accelerate troubleshooting and root cause analysis for developers, IT support, and system administrators.

---

## 🧬 Key Features

- 💾 **Snapshot Collection**: Remote or manual snapshot capture of VM environments.
- 🔍 **DeepDiff Comparison**: Analyze detailed differences in OS, services, DLLs, configs.
- 💡 **AI-Powered Analysis**: Get smart, context-driven explanations and suggestions.
- 📲 **Clean UI**: Upload, compare, view differences and download snapshots.
- ✉️ **Optional Error Message Input**: Helps AI provide even more precise debugging help.

---

## 🚀 Tech Stack

- **Frontend**: React + Vite + TailwindCSS
- **Backend**: FastAPI (Python)
- **AI Model**: Google Gemini 1.5 Pro
- **Snapshot Collector**: Python Agent using WinRM (Windows Remote Management)
- **Diff Engine**: DeepDiff (Python)

---

## 🔍 How It Works

1. **Capture Snapshots**: Collect environment context (services, registry keys, DLL versions, configs).
2. **Upload & Compare**: Upload two snapshots through UI and generate DeepDiff report.
3. **Analyze Differences**: Displayed in a beautiful sortable table.
4. **Request AI Assistance**: Submit differences and optional error messages to Gemini.
5. **Get Solutions**: Receive potential causes and fixes in seconds.

---

## 🌐 Local Setup Instructions

### Frontend
```bash
cd enveye-frontend
npm install
npm run build
npm run preview
```

**📍 Important:**  
In `enveye-frontend/src/api.js`, update the backend IP if needed:
```javascript
export const API_BASE_URL = "http://<backend-ip>:8000";
```
Replace `<backend-ip>` with your backend server's IP address (or `localhost` if running locally).

---

### Backend
```bash
cd enveye-backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

👉 Make sure you set your `GOOGLE_API_KEY` as an environment variable for backend access to Gemini API.

---

### Collector Agent (Optional)
```bash
cd collector
python collector_agent.py --app-folder "C:\\Program Files\\YourApp" --app-type desktop --upload-url http://<backend-ip>:8000/upload_snapshot
```

---

### ⚙️ Important Setup (For Remote Collection)

When performing **remote snapshot collection** for the **first time** on any new VM:

1. **Run the `WinRMFixScript.ps1` script** on the target VM to enable remote PowerShell (WinRM):

```powershell
# WinRM Fixer Script
Write-Host "🔧 Configuring WinRM..." -ForegroundColor Cyan

winrm quickconfig -q
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/service/auth '@{Basic="true"}'
New-NetFirewallRule -DisplayName "Allow WinRM (HTTP 5985)" -Name "AllowWinRM" -Protocol TCP -LocalPort 5985 -Action Allow

Write-Host "`n🔎 Current Listeners:" -ForegroundColor Green
winrm enumerate winrm/config/listener

Write-Host "`n✅ WinRM Setup Completed Successfully!" -ForegroundColor Green
```

2. **Prepare and Copy the Collector Agent Executable**:

- Use PyInstaller to create a `.exe` from `collector_agent.py`:
  ```bash
  pyinstaller --onefile collector_agent.py
  ```
- Copy the generated `collector_agent.exe` to the target VM at:
  ```
  C:\Tools\Collector\collector_agent.exe
  ```

After this setup, EnvEye can remotely collect snapshots from VMs!

---

## 🎓 Project Structure

```
/enveye-frontend     # React Frontend
/enveye-backend      # FastAPI Backend
/collector           # Snapshot collection agent
```

---

## ⚡ Limitations

- Currently tuned for Windows VMs only.
- Large snapshots (>10MB) might slow comparison and explanation.
- AI suggestions are best-effort; manual validation is recommended.

---

## 🌈 Future Improvements

- Linux and Mac snapshot support.
- Intelligent auto-prioritization of critical configuration differences.
- Caching, performance tuning for huge snapshots.
- More detailed AI debugging flows (e.g., step-by-step guided analysis).

---

## 🌍 Contributing

Pull requests are welcome! Open an issue first to discuss what you want to change.  
Let's build EnvEye stronger together!

---

## 🙏 Acknowledgements

- Google Gemini API
- Microsoft Hackathon guidelines
- DeepDiff (for powerful JSON diffing)

---

> Made with ❤️ for simplifying DevOps, IT management, and debugging 🚀

