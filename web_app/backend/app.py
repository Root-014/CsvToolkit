"""
Flask Backend for CSV Analysis Web Application
Integrates with AutoGen system for interactive analysis.
"""

import os
import sys
import json
import shutil
import pandas as pd
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.csv_analyzer import CSVAnalysisAgent

app = Flask(__name__, static_folder='../dist', static_url_path='/')
CORS(app)

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, 'generated_code', 'Input')
OUTPUT_DIR = os.path.join(BASE_DIR, 'generated_code')
REPORTS_DIR = BASE_DIR

# Ensure directories exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Store conversation history
conversations = {}


@app.route('/')
def index():
    """Serve the main HTML file."""
    return send_file(os.path.join(app.static_folder, 'index.html'))


@app.route('/api/upload', methods=['POST'])
def upload_csv():
    """Handle CSV file upload."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Save file as input.csv in the Input directory
        filename = secure_filename(file.filename)
        input_path = os.path.join(INPUT_DIR, 'input.csv')
        file.save(input_path)

        # Generate metadata
        df = pd.read_csv(input_path)
        metadata = generate_metadata(df)

        return jsonify({
            'success': True,
            'filename': 'input.csv',
            'metadata': metadata
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Handle analysis request."""
    try:
        data = request.json
        request_text = data.get('request', '')
        metadata_text = data.get('metadata', '')

        if not request_text:
            return jsonify({'error': 'No request provided'}), 400

        # Create conversation ID
        conv_id = str(uuid.uuid4())
        conversations[conv_id] = {
            'request': request_text,
            'metadata': metadata_text,
            'status': 'processing',
            'messages': [],
            'report_path': None,
            'created_at': datetime.now().isoformat()
        }

        # Run analysis in background (for now, run synchronously)
        # In production, use Celery or similar for background tasks
        result = run_analysis(conv_id, request_text, metadata_text)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/conversation/<conv_id>')
def get_conversation(conv_id):
    """Get conversation history."""
    if conv_id not in conversations:
        return jsonify({'error': 'Conversation not found'}), 404

    return jsonify(conversations[conv_id])


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'CSV Analysis API is running'
    })


@app.route('/api/report/<path:filename>')
def get_report(filename):
    """Serve generated markdown report."""
    report_path = os.path.join(REPORTS_DIR, filename)

    if not os.path.exists(report_path):
        return jsonify({'error': 'Report not found'}), 404

    return send_file(report_path)


def generate_metadata(df):
    """Generate metadata from DataFrame."""
    metadata = {
        'shape': df.shape,
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist(),
        'missing_values': df.isnull().sum().to_dict(),
        'sample_data': df.head(5).to_dict('records')
    }

    # Convert to readable text
    metadata_text = f"""
CSV Data Metadata:
- Shape: {metadata['shape'][0]} rows × {metadata['shape'][1]} columns
- Columns: {', '.join(metadata['columns'])}
- Numeric columns: {', '.join(metadata['numeric_columns'])}
- Categorical columns: {', '.join(metadata['categorical_columns'])}
- Missing values: {sum(metadata['missing_values'].values())} total

Column Details:
"""
    for col in metadata['columns']:
        metadata_text += f"\n- {col} ({metadata['dtypes'][col]})"

    return metadata_text


def run_analysis(conv_id, request_text, metadata_text):
    """Run the AutoGen analysis."""
    try:
        conversations[conv_id]['messages'].append({
            'type': 'user',
            'content': request_text,
            'timestamp': datetime.now().isoformat()
        })

        # Load CSV
        csv_path = os.path.join(INPUT_DIR, 'input.csv')
        if not os.path.exists(csv_path):
            raise FileNotFoundError("CSV file not found. Please upload a file first.")

        # Initialize agent
        agent = CSVAnalysisAgent()
        agent.load_csv(csv_path)

        # Run analysis
        conversations[conv_id]['messages'].append({
            'type': 'system',
            'content': 'Starting analysis...',
            'timestamp': datetime.now().isoformat()
        })

        results = agent.analyze(detailed=True)

        # Generate report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'report_{timestamp}.md'
        report_path = os.path.join(REPORTS_DIR, report_filename)

        agent.generate_report(output_path=report_path, format='markdown')

        conversations[conv_id]['messages'].append({
            'type': 'system',
            'content': 'Analysis complete! Report generated.',
            'timestamp': datetime.now().isoformat()
        })

        conversations[conv_id]['status'] = 'completed'
        conversations[conv_id]['report_path'] = report_filename

        return {
            'success': True,
            'conv_id': conv_id,
            'report_filename': report_filename,
            'message': 'Analysis completed successfully'
        }

    except Exception as e:
        conversations[conv_id]['status'] = 'error'
        conversations[conv_id]['messages'].append({
            'type': 'error',
            'content': f'Error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })

        return {
            'success': False,
            'conv_id': conv_id,
            'error': str(e)
        }


if __name__ == '__main__':
    print("=" * 70)
    print("CSV ANALYSIS WEB APPLICATION")
    print("=" * 70)
    print(f"\nBackend API running on http://localhost:5000")
    print(f"Input directory: {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("\n" + "=" * 70)

    app.run(debug=True, port=5000, host='0.0.0.0')