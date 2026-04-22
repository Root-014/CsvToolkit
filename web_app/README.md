# CSV Analysis Web Application

A modern web interface for the AutoGen CSV Analysis System. Upload CSV files and analyze them using natural language requests.

## Features

- 📤 **Drag & Drop Upload**: Upload CSV files easily with drag and drop
- 💬 **Natural Language Interface**: Ask for analysis in plain English
- 📊 **Real-time Conversation**: See the analysis conversation in real-time
- 📈 **Interactive Results**: View markdown reports with full formatting
- 📥 **Download Reports**: Save analysis reports as markdown files
- 🎨 **Modern UI**: Beautiful, responsive interface

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Web Frontend (TypeScript)            │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ File Upload │  │ Analysis UI  │  │ Results Display│  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           │ HTTP/WebSocket
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Backend API (Flask)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ File Handler │  │ CSV Analyzer │  │ Report Builder │  │
│  └──────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│               AutoGen System Integration                │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ CSVAnalysis  │  │ AutoGen      │  │ Markdown       │  │
│  │ Agent        │  │ Agents       │  │ Report         │  │
│  └──────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

1. **Node.js** (v16 or higher)
   ```bash
   # Check version
   node --version
   ```

2. **Python** (3.8 or higher)
   ```bash
   # Check version
   python --version
   ```

3. **TypeScript Compiler**
   ```bash
   npm install -g typescript
   ```

### Setup

1. **Install Frontend Dependencies**
   ```bash
   cd web_app
   npm install
   ```

2. **Install Backend Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Compile TypeScript**
   ```bash
   npm run build
   ```

## Running the Application

### Option 1: Combined Start (Recommended)

```bash
cd web_app
npm start
```

This will:
- Compile TypeScript
- Start the Flask backend on http://localhost:5000
- Open your browser automatically

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd web_app/backend
python app.py
```

**Terminal 2 - Frontend (Dev Mode):**
```bash
cd web_app
npm run dev
```

## Usage

### 1. Upload CSV File

- Drag and drop a CSV file onto the upload area
- Or click "Choose File" to browse
- The file will be saved as `generated_code/Input/input.csv`

### 2. Enter Analysis Request

Type your request in plain English:

Examples:
```
Show basic statistics for all numeric columns
Create a histogram of Location values
Find correlations between numeric columns
Group data by Channel and show averages
Show rows where Location > 5000
```

### 3. View Conversation

The system displays:
- Your request (User)
- System messages (Processing status)
- Errors (if any)

### 4. View Results

After analysis completes:
- View the markdown report
- Scroll through results
- Download the report file

## API Endpoints

### POST /api/upload
Upload a CSV file.

**Request:**
- FormData with 'file' field

**Response:**
```json
{
  "success": true,
  "filename": "input.csv",
  "metadata": "CSV metadata text..."
}
```

### POST /api/analyze
Run analysis request.

**Request:**
```json
{
  "request": "Show statistics for numeric columns",
  "metadata": "CSV metadata..."
}
```

**Response:**
```json
{
  "success": true,
  "conv_id": "uuid-string",
  "report_filename": "report_20240125_143052.md"
}
```

### GET /api/conversation/<conv_id>
Get conversation history.

**Response:**
```json
{
  "request": "...",
  "status": "processing|completed|error",
  "messages": [...],
  "report_path": "report_*.md"
}
```

### GET /api/report/
Download markdown report.

**Response:**
- Markdown file download

## File Structure

```
web_app/
├── src/                    # TypeScript source files
│   ├── index.html         # Main HTML
│   ├── app.ts            # TypeScript application logic
│   └── styles.css        # CSS styles
├── backend/               # Python Flask backend
│   └── app.py           # Flask application
├── dist/                 # Compiled JavaScript (generated)
├── package.json         # Node.js dependencies
├── tsconfig.json        # TypeScript configuration
└── README.md           # This file
```

## Customization

### Styling
Edit `src/styles.css` to customize the appearance.

### Backend Logic
Edit `backend/app.py` to modify:
- Analysis workflow
- File handling
- API endpoints

### Frontend Behavior
Edit `src/app.ts` to modify:
- User interactions
- API calls
- UI updates

## Troubleshooting

### Issue: "Cannot connect to API"
**Solution:** Make sure the Flask backend is running on port 5000

### Issue: TypeScript compilation errors
**Solution:** Check TypeScript version and dependencies
```bash
npm install
npm run build
```

### Issue: CORS errors
**Solution:** Backend has CORS enabled. If still failing, check:
- Backend is running
- No browser extensions blocking requests
- Port 5000 is not blocked

### Issue: File upload fails
**Solution:**
- Check file size (max ~50MB)
- Ensure CSV format is valid
- Check generated_code/Input/ directory permissions

## Technology Stack

### Frontend
- **TypeScript** - Type-safe JavaScript
- **HTML5** - Markup
- **CSS3** - Styling
- **Marked** - Markdown parser
- **DOMPurify** - XSS protection

### Backend
- **Python 3.8+** - Runtime
- **Flask** - Web framework
- **Flask-CORS** - CORS support
- **Pandas** - Data analysis
- **Werkzeug** - Utilities

### Integration
- **AutoGen** - Multi-agent system
- **CSV Analysis Agent** - Custom analysis agent
- **Markdown Reports** - Report generation

## Development

### Watch Mode (Auto-recompile)
```bash
npm run dev
```

### Debug Backend
```bash
cd backend
python app.py
```

The backend runs with debug mode enabled, auto-reloading on code changes.

### Build for Production
```bash
npm run build
```

This creates optimized JavaScript in the `dist/` folder.

## Security Considerations

- File uploads are validated (CSV only)
- Input is sanitized using DOMPurify
- CORS is configured for local development
- No authentication (add if deploying publicly)

## Future Enhancements

- [ ] Authentication system
- [ ] User accounts
- [ ] Saved analyses
- [ ] More visualization options
- [ ] Real-time WebSocket updates
- [ ] Export to PDF
- [ ] Multiple file support

## License

MIT License - feel free to use and modify

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API endpoint documentation
3. Check browser console for errors
4. Check Flask backend logs