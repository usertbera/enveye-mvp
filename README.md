<p align="center">
  <img src="https://github.com/usertbera/enveye-mvp/raw/main/enveye-frontend/src/assets/logo_96x96.png" alt="EnvEye Logo" width="120" height="120"/>
</p>

<h1 align="center">EnvEye - Intelligent Snapshot Comparator</h1>

<p align="center">
  💻 Compare. 🤮 Analyze. 🚀 Fix. <br/>
  <em>Debugging environments smarter & faster.</em>
</p>

<p align="center">
  <a href="https://github.com/usertbera/enveye-mvp"><img alt="Built With" src="https://img.shields.io/badge/Built%20with-React%20%7C%20FastAPI%20%7C%20Gemini-blue?style=for-the-badge"/></a>
  <a href="https://github.com/usertbera/enveye-mvp/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/usertbera/enveye-mvp?style=for-the-badge"/></a>
  <img alt="Made with Python" src="https://img.shields.io/badge/Made%20with-Python%20%7C%20React-informational?style=for-the-badge"/>
</p>

---

## 📈 Project Overview

**EnvEye** is a smart debugging assistant for IT environments.
It compares snapshots of system states (two VMs) and highlights key differences.
Powered by **Google Gemini AI**, it explains issues and suggests fixes instantly.

Built for developers, DevOps, and IT support teams — to accelerate troubleshooting and root cause analysis.

<p align="center">
  <a href="https://youtu.be/dB4ALbFPf3Y" target="_blank">
    <img src="https://img.youtube.com/vi/dB4ALbFPf3Y/0.jpg" alt="EnvEye Demo Video" width="600" style="border-radius: 8px;"/>
    <br>
    <strong>▶️ Watch Demo Video</strong>
  </a>
</p>

---

## 🧆 Key Features

- 💾 **Snapshot Collection**: Remote/manual VM snapshot capture.
- 🔍 **DeepDiff Comparison**: Detects changes across OS, DLLs, services, configs.
- 🧠 **AI-Powered Analysis**: Smart diagnosis using Gemini.
- 📋 **Clean & Friendly UI**: View, upload, download snapshots effortlessly.
- ✉️ **Error Message Assistance**: Input errors to get pinpointed AI help.

---

## 🚀 Tech Stack

| Layer       | Techs Used                            |
| ----------- | ------------------------------------- |
| Frontend    | React + Vite + TailwindCSS             |
| Backend     | FastAPI (Python)                      |
| AI Model    | Google Gemini 1.5 Pro                  |
| Collector   | Python Agent using WinRM (Windows Remote Management) |
| Diff Engine | DeepDiff (Python)                     |

---

## 🔍 How It Works

1. 📥 **Collect Snapshots**: Capture environment context (services, registry, DLLs, configs).
2. 🔍 **Upload & Compare**: Upload two snapshots to generate a DeepDiff report.
3. 🤮 **Analyze Differences**: Visualize differences in a clean table.
4. 🛧️ **Request AI Help**: Send differences + optional error message to Gemini.
5. 🛠️ **Get Solutions**: Receive possible causes and intelligent suggestions.

---

## 🌐 Local Setup Instructions

### 👉 Frontend Setup
```bash
cd enveye-frontend
npm install
npm run build
npm run preview
```

**📍 Important:**
Update the backend IP address in `enveye-frontend/src/api.js`:
```javascript
export const API_BASE_URL = "http://<your-backend-ip>:8000";
```

---

### 👉 Backend Setup
```bash
cd enveye-backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Environment Variable Required:**
```bash
export GOOGLE_API_KEY=your-api-key-here  # Linux/Mac
set GOOGLE_API_KEY=your-api-key-here     # Windows
```

---

### 👉 Collector Agent Setup (Optional)
```bash
cd collector
python collector_agent.py --app-folder "C:\\Program Files\\YourApp" --app-type desktop --upload-url http://<backend-ip>:8000/upload_snapshot
```

---

## ⚙️ Important Setup for Remote Collection (First Time)

To enable remote snapshot collection (WinRM setup):

1. Copy `collector_agent.exe` to your target VM in "C:\Tools\Collector" . (Use PyInstaller to generate `collector_agent.exe`)
2. On the target VM, **run the following PowerShell script once**:

```powershell
# WinRMFixScript.PS1
Write-Host "🔧 Configuring WinRM..." -ForegroundColor Cyan
winrm quickconfig -q
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/service/auth '@{Basic="true"}'
New-NetFirewallRule -DisplayName "Allow WinRM (HTTP 5985)" -Name "AllowWinRM" -Protocol TCP -LocalPort 5985 -Action Allow
Write-Host "\n🔎 Current Listeners:" -ForegroundColor Green
winrm enumerate winrm/config/listener
Write-Host "\n✅ WinRM Setup Completed Successfully!" -ForegroundColor Green
```

---

## 📂 Project Structure

```
/enveye-frontend     # React frontend (Vite based)
/enveye-backend      # FastAPI backend
/collector           # Python agent for snapshot collection
```

---

## ⚡ Limitations

- Currently supports only **Windows VMs**.
- Large snapshots (>10MB) may slightly slow comparisons.
- AI diagnosis is best-effort — manual validation recommended.

---

## 🌈 Future Enhancements

- 🐦 Linux and Mac snapshot support.
- 🚀 Prioritized intelligent diff reporting.
- 🔥 Faster batch comparisons.

---

## 📅 License

This project is licensed under the **MIT License**. See [LICENSE](./LICENSE) for more details.

---

## 🙏 Acknowledgements

- 🧠 Google Gemini AI
- ⚡ DeepDiff for intelligent diffing
- 📚 Microsoft Hackathon guidance
- ❤️ Open-source community inspirations

---

> Made with passion to simplify IT and DevOps life! 🚀

