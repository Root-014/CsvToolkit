# AutoGen CSV Analyst - Setup & Run Guide

This guide will walk you through running the application from scratch.



## 📋 Prerequisites

Before you begin, ensure you have the following installed on your Windows machine:
1. **Python 3.10+**: Make sure it's added to your system PATH.
2. **API Access**: 
   - This app is configured to use **Ollama** (local) or **OpenAI-compatible** APIs.
   - Ensure your local LLM server (like Ollama) is running if you're using it.
   - Or, update the `config_list` in `agent_runner.py` with your actual API keys.

---

## 🚀 How to Run (Normal Usage)

If the dependencies are already installed and the frontend is built, you only need one step:

1. **Double-click `start.bat`**:
   - This script starts the FastAPI backend server.
   - It will automatically open your default web browser to: `http://localhost:8000`.

---

## 🛠️ How to Run From Scratch (Step-by-Step)

If you are setting this up on a new machine or after cleaning your environment, follow these steps:

### 1. Install Python Dependencies
Open a terminal in the project root directory and run:
```powershell
pip install -r requirements.txt
```
*(Note: If you don't have a requirements.txt, ensure you have `fastapi`, `uvicorn`, `pyautogen`, `pandas`, and `lucide-react` installed.)*

### 2. Build the Frontend (Optional)
The frontend is already pre-built in `frontend/dist`. You only need to rebuild it if you make changes to the React code:
```powershell
cd frontend
npm install
npm run build
cd ..
```

### 3. Launch the Application
Run the launcher:
```powershell
.\start.bat
```

---

## 📂 Project Structure Explained

- **`api.py`**: The main entry point. It hosts the REST API, WebSocket for agent streaming, and serves the frontend.
- **`agent_runner.py`**: Contains the core AutoGen logic, agent definitions (Manager, Coder, etc.), and group chat workflow.
- **`frontend/dist/`**: The compiled React application served by the backend.
- **`generated_code/`**: The workspace where the "Coder" agent saves and executes its Python scripts.
- **`start.bat`**: The convenient one-click launcher for Windows.

---

## 💡 Troubleshooting

- **Port 8000 already in use**: If you see an "address already in use" error, a previous instance might still be running. Close the terminal windows and try again.
- **Agent Errors**: Check `agent_runner.py` to ensure the `base_url` and `api_key` match your LLM provider.
