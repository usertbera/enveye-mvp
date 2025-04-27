**LICENSE (MIT)**

```markdown
MIT License

Copyright (c) 2025 Tapabrata
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

# README.md

```markdown
<p align="center">
  <img src="./assets/logo_96x96.png" alt="EnvEye Logo" width="120" height="120"/>
</p>

<h1 align="center">EnvEye - Intelligent Snapshot Comparator</h1>

<p align="center">
  💻 Compare. 🧐 Analyze. 🚀 Fix. <br/>
  <em>Debugging environments smarter & faster.</em>
</p>

<p align="center">
  <img alt="Built With" src="https://img.shields.io/badge/Built%20with-React%20%7C%20FastAPI%20%7C%20Gemini-blue?style=for-the-badge"/>
  <img alt="License" src="https://img.shields.io/github/license/yourusername/enveye?style=for-the-badge"/>
  <img alt="Made with Python" src="https://img.shields.io/badge/Made%20with-Python%20%7C%20React-informational?style=for-the-badge"/>
</p>

---

## 📈 Project Overview

**EnvEye** is a smart debugging assistant for IT environments.
It compares snapshots of system states (two VMs) and highlights key differences.
Powered by **Google Gemini AI**, it explains issues and suggests fixes instantly.

Built for developers, DevOps, and IT support teams — to accelerate troubleshooting and root cause analysis.

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
3. 🧐 **Analyze Differences**: Visualize differences in a clean table.
4. 🧯 **Request AI Help**: Send differences + optional error message to Gemini.
5. 🛠️ **Get Solutions**: Receive possible causes and intelligent suggestions.

---

## 🌐 Local Setup Instructions

### Frontend Setup
```bash
cd enveye-frontend
npm install
npm run build
npm run preview
```

### Backend Setup
```bash
cd enveye-backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
✅ **Important:**  
Set your `GOOGLE_API_KEY` as an environment variable before starting the backend!

---

## ⚙️ Collector Agent Setup (Optional but Recommended)

```bash
cd collector
python collector_agent.py --app-folder "C:\\Program Files\\YourApp" --app-type desktop --upload-url http://<backend-ip>:8000/upload_snapshot
```

---

## 🛠 Important Setup for Remote Collection (First Time)

To enable remote snapshot collection (WinRM setup):

1. Copy `collector_agent.exe` to your target VM. (Use PyInstaller to generate `collector_agent.exe`)
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

✅ After this, remote collection will work seamlessly!

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
- AI diagnosis is best-effort — final judgment advised.

---

## 🌈 Future Enhancements

- 🐧 Linux and Mac snapshot support.
- 🚀 Prioritized intelligent diff reporting.
- 🔥 Faster batch comparisons.

---

## 📢 Important Configuration

🔹 **If needed**, update backend IP inside frontend:  
`enveye-frontend/src/api.js`
```javascript
export const API_BASE_URL = "http://<your-backend-ip>:8000";
```

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](./LICENSE) file.

---

## 🙏 Acknowledgements

- 🧠 Google Gemini AI
- ⚡ DeepDiff for intelligent diffing
- 📚 Microsoft Hackathon guidelines
- ❤️ Open-source community inspirations

---

> Made with passion to simplify IT and DevOps life! 🚀
```

---

Would you also like me to now create a short `CONTRIBUTING.md` to make it **100% hackathon ready**? 🚀

