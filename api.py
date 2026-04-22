from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from agents.csv_analyzer import CSVAnalysisAgent
import subprocess
from pydantic import BaseModel
import pandas as pd
import numpy as np
from typing import Optional, List, Any

app = FastAPI()

class CSVRequest(BaseModel):
    file_path: str
    filter_col: Optional[str] = None
    filter_val: Optional[Any] = None          # legacy single-value
    filter_vals: Optional[List[Any]] = None   # new multi-value list
    sort_col: Optional[str] = None
    sort_ascending: Optional[bool] = True
    limit_type: Optional[str] = None # 'top', 'bottom'
    limit_n: Optional[int] = 10

class ColumnValuesRequest(BaseModel):
    file_path: str
    column: str

# Enable CORS for the frontend Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INPUT_DIR = "generated_code/Input"
OUTPUT_DIR = "generated_code"

def clean_generated_code():
    """Remove all files inside generated_code/ while keeping the folder structure."""
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for f in files:
            try:
                os.remove(os.path.join(root, f))
            except Exception as e:
                print(f"[CLEANUP] Could not remove {os.path.join(root, f)}: {e}")
    print("[CLEANUP] generated_code folder cleaned.")

# Clean on startup, then ensure directories exist
clean_generated_code()
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Note: We will serve the Vite build folder in production, but for dev we use CORS
upload_progress_tracker = {}

@app.get("/api/upload_progress")
async def get_upload_progress(filename: str):
    return {"status": "success", "progress": upload_progress_tracker.get(filename, [])}

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    filename = file.filename
    if not filename: filename = "input.csv"
    upload_progress_tracker[filename] = []
    
    file_location = os.path.join(INPUT_DIR, "input.csv")
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    
    # Run the CSV Analysis
    try:
        agent = CSVAnalysisAgent()
        agent.load_csv(file_location)
        def progress_callback(msg):
            upload_progress_tracker[filename].append(msg)
        results = agent.analyze(detailed=True, progress_callback=progress_callback)
        report_path = "analysis.md"
        agent.generate_report(output_path=report_path)
        
        # Read the generated markdown
        with open(report_path, "r", encoding="utf-8") as md_file:
            md_content = md_file.read()
            
        return {"status": "success", "message": "File uploaded and analyzed", "markdown": md_content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

class CodeUpdate(BaseModel):
    code: str

@app.get("/api/code")
async def get_code():
    code_path = os.path.join(OUTPUT_DIR, "main.py")
    if os.path.exists(code_path):
        with open(code_path, "r", encoding="utf-8") as f:
            return {"status": "success", "code": f.read()}
    return {"status": "error", "message": "Code not found", "code": ""}

@app.post("/api/code")
async def save_code(payload: CodeUpdate):
    code_path = os.path.join(OUTPUT_DIR, "main.py")
    try:
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(payload.code)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/plan")
async def get_plan():
    plan_path = "implementation_plan.md"
    if os.path.exists(plan_path):
        with open(plan_path, "r", encoding="utf-8") as f:
            return {"status": "success", "content": f.read()}
    return {"status": "error", "message": "Plan not found", "content": ""}

@app.post("/api/plan")
async def save_plan(payload: CodeUpdate):
    plan_path = "implementation_plan.md"
    try:
        with open(plan_path, "w", encoding="utf-8") as f:
            f.write(payload.code)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/run_code")
def run_code():
    code_path = os.path.join(OUTPUT_DIR, "main.py")
    if not os.path.exists(code_path):
        return {"status": "error", "output": "main.py does not exist."}
    
    try:
        sub_env = os.environ.copy()
        sub_env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            ["python", os.path.abspath(code_path)],
            capture_output=True,
            text=True,
            env=sub_env,
            cwd=os.path.abspath(OUTPUT_DIR)
        )
        return {"status": "success", "output": result.stdout + (("\n" + result.stderr) if result.stderr else "")}
    except Exception as e:
        return {"status": "error", "output": str(e)}

@app.websocket("/ws/run")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    log_file = "conversation_log.md"
    if os.path.exists(log_file):
        os.remove(log_file)
        
    try:
        data = await websocket.receive_text()
        print(f"Received request: {data}")
        
        # Pass absolute path natively to strictly ensure LLM gets the robust path regardless of execution directory
        abs_csv_path = os.path.abspath(os.path.join("generated_code", "Input", "input.csv")).replace("\\", "/")
        enhanced_data = f"{data}. IMPORTANT: The absolute filepath for the input CSV is: '{abs_csv_path}'. You must use this complete path in any code."
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"# Conversation Log\n\n**Request**: {enhanced_data}\n\n---\n\n")
        
        # Subprocess env with correct encoding
        sub_env = os.environ.copy()
        sub_env["PYTHONIOENCODING"] = "utf-8"
        
        # Start agentic_runner.py as a subprocess using Popen to bypass Windows asyncio loop bugs
        process = subprocess.Popen(
            ["python", "-u", "agentic_runner.py", enhanced_data],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=sub_env
        )
        
        async def read_stdout():
            while True:
                line = await asyncio.to_thread(process.stdout.readline)
                if not line:
                    break
                
                decoded_line = line.decode('utf-8', errors='replace').strip()
                if decoded_line:
                    await websocket.send_text(decoded_line)
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(decoded_line + "\n")
            await asyncio.to_thread(process.wait)
            try:
                await websocket.send_text("[SYSTEM] Agent run completed.")
            except Exception:
                pass

        async def read_ws():
            try:
                while process.poll() is None:
                    # using receive_text to listen for verification
                    msg = await websocket.receive_text()
                    if process.stdin:
                        process.stdin.write(f"{msg}\n".encode('utf-8'))
                        process.stdin.flush()
            except WebSocketDisconnect:
                pass
            except Exception as e:
                print("Error reading websocket", e)

        try:
            # We run both the stdout reader and the websocket listener concurrently
            await asyncio.gather(read_stdout(), read_ws())
        except Exception as e:
            try:
                await websocket.send_text(f"[SYSTEM ERROR] {str(e)}")
            except:
                pass
            
    except WebSocketDisconnect:
        print("Client disconnected")
@app.get("/api/file_content")
async def get_file_content(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)

@app.get("/api/files")
async def list_files():
    def get_structure(path):
        items = []
        for item in os.listdir(path):
            if item.startswith('.'): continue
            item_path = os.path.join(path, item)
            is_dir = os.path.isdir(item_path)
            items.append({
                "name": item,
                "path": item_path.replace("\\", "/"),
                "isDir": is_dir,
                "children": get_structure(item_path) if is_dir else []
            })
        return items
    
    try:
        structure = get_structure(OUTPUT_DIR)
        return {"status": "success", "files": structure}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/column_values")
async def get_column_values(req: ColumnValuesRequest):
    """Return sorted unique values for a given column in a CSV file."""
    try:
        if not os.path.exists(req.file_path):
            return {"status": "error", "message": "File not found"}
        df = pd.read_csv(req.file_path, usecols=[req.column])
        values = sorted(
            df[req.column].dropna().astype(str).unique().tolist()
        )
        return {"status": "success", "values": values}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/view_csv")
async def view_csv(req: CSVRequest):
    try:
        if not os.path.exists(req.file_path):
            return {"status": "error", "message": "File not found"}
        
        df = pd.read_csv(req.file_path)
        total_rows = len(df)
        
        # Apply Filter — prefer multi-value list, fall back to single value
        active_vals = req.filter_vals if req.filter_vals else (
            [str(req.filter_val)] if req.filter_val not in (None, "") else []
        )
        if req.filter_col and active_vals and req.filter_col in df.columns:
            str_col = df[req.filter_col].astype(str)
            df = df[str_col.isin(active_vals)]
        
        # Apply Sort
        if req.sort_col and req.sort_col in df.columns:
            df = df.sort_values(by=req.sort_col, ascending=req.sort_ascending)
            
        # Apply Limit (Top/Bottom)
        if req.limit_type == 'top':
            df = df.head(req.limit_n)
        elif req.limit_type == 'bottom':
            df = df.tail(req.limit_n)
        
        # Format for JSON
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.astype(object).where(pd.notnull(df), None)
        
        return {
            "status": "success",
            "columns": list(df.columns),
            "data": df.to_dict(orient='records'),
            "total_rows": total_rows,
            "display_rows": len(df)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Serve static files from the built frontend/dist folder
frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    print(f"[WARNING] Frontend dist folder not found at {frontend_dist}. Did you run 'npm run build'?")

if __name__ == "__main__":
    import uvicorn
    import threading
    import webbrowser
    import time
    
    def open_browser():
        time.sleep(1.5) # Give uvicorn a moment to bind to the port
        webbrowser.open("http://127.0.0.1:8000")
        
    # Start the browser-opening thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
