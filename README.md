# EnvEye - Environment Snapshot & Comparison Tool 🚀

EnvEye is a QA/Testing innovation tool designed to **collect**, **compare**, and **explain** differences between environment setups (VMs, servers, desktops) — using AI assistance!

---

## 📦 Components

- **Collector Agent (EXE)**: Portable executable that collects critical environment information (DLLs, Services, Registry, Configs) into a JSON snapshot.
- **FastAPI Backend**: Provides APIs to compare snapshots and explain differences via OpenAI.
- **React Frontend**: Web dashboard to upload, compare, and visualize environment differences.
- **AI Integration**: GPT-3.5-Turbo used to explain detected configuration differences.

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/enveye-mvp.git
cd enveye-mvp
