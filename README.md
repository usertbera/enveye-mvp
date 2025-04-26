# EnvEye - Intelligent Snapshot Comparator

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

### Backend
```bash
cd enveye-backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> Make sure you set your `GOOGLE_API_KEY` as an environment variable for backend.

### Collector Agent (optional)
```bash
cd collector
python collector_agent.py --app-folder "C:\\Program Files\\YourApp" --app-type desktop --upload-url http://<backend-ip>:8000/upload_snapshot
```

---

## 🎓 Project Structure

```
/enveye-frontend     # React Frontend
/enveye-backend      # FastAPI Backend
/collector           # Snapshot collection agent
```

---

## 🏆 Hackathon Requirements

- **AI Usage**: Gemini used for intelligent diff explanation & suggestion.
- **Innovation**: Assists in root cause analysis using context + user errors.
- **Impact**: Saves hours for IT debugging teams.
- **Responsible AI**: Disclaimer added about AI output accuracy.

---

## ⚡ Limitations

- Currently tuned for Windows VMs.
- Large snapshots (>10MB) may slow comparison.
- AI suggestions are best-effort, manual validation needed.

---

## 🌈 Future Improvements

- Linux & Mac snapshot collection.
- Intelligent auto-prioritization of critical config changes.
- Caching and faster multi-comparison support.

---

## 🌍 Contributing

Pull requests are welcome. Open an issue first to discuss major changes!

---

## 🙏 Acknowledgements

- Google Gemini API
- Microsoft Hackathon guidelines
- DeepDiff (for powerful JSON diffing)

---

## 📅 License

MIT License. See `LICENSE` file for details.

---

> Made with passion for simplifying DevOps and IT life 🚀

