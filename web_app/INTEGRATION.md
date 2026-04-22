# Web Application Integration Guide

## Overview

This guide explains how the TypeScript web application integrates with the AutoGen CSV Analysis System.

## Architecture Flow

```
1. User uploads CSV → 2. Backend saves to generated_code/Input/input.csv
                                                    ↓
3. User enters request → 4. Backend calls analyze_request()
                                                    ↓
5. AutoGen generates code → 6. Code executes on CSV
                                                    ↓
7. Markdown report → 8. Frontend displays results
```

## Detailed Integration Steps

### Step 1: File Upload

**Frontend (app.ts):**
```typescript
const formData = new FormData();
formData.append('file', file);

await fetch(`${this.apiUrl}/api/upload`, {
    method: 'POST',
    body: formData
});
```

**Backend (app.py):**
```python
# Save file as input.csv
input_path = os.path.join(INPUT_DIR, 'input.csv')
file.save(input_path)

# Generate metadata
df = pd.read_csv(input_path)
metadata = generate_metadata(df)
```

**Result:** File saved to `generated_code/Input/input.csv`

### Step 2: Analysis Request

**Frontend (app.ts):**
```typescript
await fetch(`${this.apiUrl}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        request: requestText,
        metadata: metadataText
    })
});
```

**Backend (app.py):**
```python
def run_analysis(conv_id, request_text, metadata_text):
    # Load CSV
    csv_path = os.path.join(INPUT_DIR, 'input.csv')
    agent = CSVAnalysisAgent()
    agent.load_csv(csv_path)

    # Run analysis
    results = agent.analyze(detailed=True)

    # Generate report
    report_path = os.path.join(REPORTS_DIR, report_filename)
    agent.generate_report(output_path=report_path)

    return {'success': True, 'report_filename': report_filename}
```

### Step 3: Integration with main.py

The web app integrates with your existing `main.py` configuration:

```python
# From main.py (already configured)
config_list = {
    'model': 'minimax-m2:cloud',
    'base_url': 'http://localhost:11434/v1',
    'api_key': 'ollama',
    'api_type': 'openai',
}
```

This config is used by:
- `CSVAnalysisAgent` in the backend
- AutoGen agents for code generation

### Step 4: Report Generation

**Generated files:**
```
Project Root/
├── generated_code/
│   ├── Input/
│   │   └── input.csv           # User's uploaded CSV
│   └── [Generated Python files]
├── report_YYYYMMDD_HHMMSS.md    # Analysis report
└── s.md                         # Metadata report
```

**The analyze_request() Function:**

```python
def analyze_request(request, metadata_text):
    """
    Main function that:
    1. Takes user request and CSV metadata
    2. Uses AutoGen to generate code
    3. Executes code on CSV data
    4. Returns markdown report
    """
    # Implementation in app.py's run_analysis()
```

## Conversation Placeholder

The web app creates a real-time conversation display:

```typescript
// Shows conversation in real-time
<div class="conversation-history">
    <div class="message user">
        <div class="message-header">You - 10:30:45</div>
        <div class="message-content">Show statistics for numeric columns</div>
    </div>
    <div class="message system">
        <div class="message-header">System - 10:30:45</div>
        <div class="message-content">Analysis started...</div>
    </div>
</div>
```

**Polling for Updates:**
```typescript
const pollInterval = setInterval(async () => {
    const response = await fetch(`${this.apiUrl}/api/conversation/${convId}`);
    const data = await response.json();

    if (data.status === 'completed') {
        clearInterval(pollInterval);
        // Load report
    }
}, 2000);
```

## File Structure Integration

```
C:\Users\hariharan.balaji\Desktop\Personal\Codebase\Agents_openai\
├── main.py                           # Your LLM config
├── agents\                          # AutoGen agents
│   └── csv_analyzer\
├── eda_utils\                       # EDA utilities
├── generated_code\                  # AutoGen output
│   ├── Input\
│   │   └── input.csv               # ← Web app uploads here
│   └── [Generated analysis files]
├── s.md                             # Metadata report
├── web_app\                         # Web application
│   ├── src\                         # TypeScript source
│   ├── backend\                     # Flask API
│   └── dist\                        # Compiled JS
└── report_*.md                       # Generated reports
```

## Usage Example

### User Workflow:

1. **Upload CSV**
   - User drags `data.csv` to upload area
   - Backend renames it to `input.csv`
   - Saves to `generated_code/Input/input.csv`
   - Shows metadata: "144 rows × 11 columns"

2. **Enter Request**
   ```
   Show basic statistics for all numeric columns
   ```

3. **Backend Processes**
   ```python
   # In app.py run_analysis():
   agent = CSVAnalysisAgent()
   agent.load_csv('generated_code/Input/input.csv')
   results = agent.analyze(detailed=True)
   agent.generate_report(output_path='report_20250325_143052.md')
   ```

4. **Display Results**
   - Conversation shows: "You: Show basic statistics..." → "System: Analysis complete!"
   - Markdown report loads
   - User can download `report_20250325_143052.md`

## Key Integration Points

### 1. Uses Your Existing Code

The web app doesn't duplicate functionality - it uses:
- `CSVAnalysisAgent` from `agents/csv_analyzer/`
- `config_llm` from `main.py`
- `eda_utils` for analysis

### 2. File Path Convention

- **Upload path:** `generated_code/Input/input.csv`
- **Report path:** `/project_root/report_TIMESTAMP.md`
- **Metadata:** Auto-generated from CSV

### 3. analyze_request() Function

This is the main integration function:

```python
def analyze_request(request: str, metadata_text: str) -> dict:
    """
    Args:
        request: User's natural language request
        metadata_text: CSV metadata for context

    Returns:
        dict: {
            'success': bool,
            'conv_id': str,
            'report_filename': str,
            'message': str
        }
    """
    # Implementation in backend/app.py
```

## Running Everything Together

### Start the Web App
```bash
cd web_app
./start.sh        # Linux/Mac
# or
start.bat         # Windows
```

### Access the Application
```
http://localhost:5000
```

### What Happens:

1. TypeScript compiles to `dist/`
2. Flask backend starts on port 5000
3. Frontend served from `dist/`
4. API endpoints ready for requests
5. AutoGen integration ready

## Testing the Integration

### Test 1: Upload
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@test.csv"
```
Expected: `{"success": true, ...}`

### Test 2: Analyze
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"request":"Show statistics", "metadata":"..."}'
```
Expected: `{"success": true, "report_filename": "..."}`

### Test 3: View Report
```
http://localhost:5000/api/report/report_20250325_143052.md
```
Expected: Markdown report downloads

## Customization

### Modify Analysis Behavior
Edit `backend/app.py` `run_analysis()` function:

```python
def run_analysis(conv_id, request_text, metadata_text):
    # Add custom analysis logic here
    # Use AutoGen agents
    # Generate custom reports
```

### Change UI
Edit `src/app.ts` and `src/styles.css`

### Add Features
- New API endpoints in `backend/app.py`
- New UI components in `src/index.html`
- New styles in `src/styles.css`

## Troubleshooting Integration

### "CSV file not found"
- Check `generated_code/Input/input.csv` exists
- Verify upload worked in UI

### "AutoGen not working"
- Check `main.py` has correct config
- Verify LLM endpoint is running

### "Report not generated"
- Check backend logs
- Verify permissions on report directory

## Summary

The web application provides a modern UI for your AutoGen system:
- ✅ Upload CSV → saves to `generated_code/Input/input.csv`
- ✅ Enter request → calls `analyze_request(request, metadata)`
- ✅ Shows real-time conversation
- ✅ Displays markdown report
- ✅ Integrated with your existing AutoGen setup

Everything works together seamlessly!