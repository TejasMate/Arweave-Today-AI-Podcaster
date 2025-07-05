#!/usr/bin/env python3
"""
Arweave Today AI Podcaster - Web Interface
A Flask web application for uploading or pasting JSON files to generate podcasts.
"""

import os
import json
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import threading
import time

# Import our podcast generator
from arweave_podcaster.core.podcast_generator import PodcastGenerator
from arweave_podcaster.utils.config import config

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'json'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global storage for job status
job_status = {}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_json_structure(data):
    """Validate that the JSON has the expected structure for podcast generation."""
    if not isinstance(data, dict):
        return False, "JSON must be an object"
    
    # Check for required fields - the data can have topics directly or nested
    if 'topics' not in data:
        return False, "Missing 'topics' field"
    
    topics = data['topics']
    if not isinstance(topics, list):
        return False, "'topics' must be an array"
    
    if len(topics) == 0:
        return False, "At least one topic is required"
    
    # Validate each topic - they should have headline and body
    for i, topic in enumerate(topics):
        if not isinstance(topic, dict):
            return False, f"Topic {i+1} must be an object"
        
        # Topics should have headline and body (not title and content)
        if 'headline' not in topic and 'title' not in topic:
            return False, f"Topic {i+1} missing 'headline' or 'title' field"
        
        if 'body' not in topic and 'content' not in topic:
            return False, f"Topic {i+1} missing 'body' or 'content' field"
    
    return True, "Valid JSON structure"

def generate_podcast_async(job_id, json_file_path):
    """Generate podcast asynchronously and update job status."""
    try:
        job_status[job_id]['status'] = 'processing'
        job_status[job_id]['message'] = 'Initializing podcast generator...'
        
        # Initialize podcast generator with base directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        generator = PodcastGenerator(base_dir)
        
        job_status[job_id]['message'] = 'Processing JSON file...'
        
        # Generate podcast
        output_dir = generator.generate_podcast_from_file(json_file_path)
        
        if output_dir and os.path.exists(output_dir):
            # Find generated files
            wav_files = list(Path(output_dir).glob("*.wav"))
            mp3_files = list(Path(output_dir).glob("*.mp3"))
            txt_files = list(Path(output_dir).glob("ArweaveToday-*.txt"))
            
            audio_file = None
            if mp3_files:
                audio_file = str(mp3_files[0])
            elif wav_files:
                audio_file = str(wav_files[0])
            
            script_file = str(txt_files[0]) if txt_files else None
            
            job_status[job_id]['status'] = 'completed'
            job_status[job_id]['message'] = 'Podcast generated successfully!'
            job_status[job_id]['audio_file'] = audio_file
            job_status[job_id]['script_file'] = script_file
            job_status[job_id]['output_dir'] = output_dir
        else:
            job_status[job_id]['status'] = 'error'
            job_status[job_id]['message'] = 'Failed to generate podcast - no output directory created'
            
    except Exception as e:
        job_status[job_id]['status'] = 'error'
        job_status[job_id]['message'] = f'Error generating podcast: {str(e)}'
    
    finally:
        # Clean up uploaded file
        if os.path.exists(json_file_path):
            os.remove(json_file_path)

@app.route('/')
def index():
    """Main page with upload and paste options."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only JSON files are allowed.'}), 400
    
    try:
        # Read and validate JSON
        json_content = file.read().decode('utf-8')
        data = json.loads(json_content)
        
        is_valid, error_msg = validate_json_structure(data)
        if not is_valid:
            return jsonify({'error': f'Invalid JSON structure: {error_msg}'}), 400
        
        # Save file temporarily
        job_id = str(uuid.uuid4())
        filename = secure_filename(f"{job_id}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(file_path, 'w') as f:
            f.write(json_content)
        
        # Initialize job status
        job_status[job_id] = {
            'status': 'queued',
            'message': 'Job queued for processing',
            'created_at': datetime.now().isoformat(),
            'filename': file.filename
        }
        
        # Start background processing
        thread = threading.Thread(target=generate_podcast_async, args=(job_id, file_path))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'File uploaded successfully. Processing started.'
        })
        
    except json.JSONDecodeError as e:
        return jsonify({'error': f'Invalid JSON format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/paste', methods=['POST'])
def paste_json():
    """Handle pasted JSON content."""
    try:
        json_content = request.json.get('content', '').strip()
        
        if not json_content:
            return jsonify({'error': 'No JSON content provided'}), 400
        
        # Parse and validate JSON
        data = json.loads(json_content)
        
        is_valid, error_msg = validate_json_structure(data)
        if not is_valid:
            return jsonify({'error': f'Invalid JSON structure: {error_msg}'}), 400
        
        # Save content temporarily
        job_id = str(uuid.uuid4())
        filename = f"{job_id}_pasted.json"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(file_path, 'w') as f:
            f.write(json_content)
        
        # Initialize job status
        job_status[job_id] = {
            'status': 'queued',
            'message': 'Job queued for processing',
            'created_at': datetime.now().isoformat(),
            'filename': 'pasted_content.json'
        }
        
        # Start background processing
        thread = threading.Thread(target=generate_podcast_async, args=(job_id, file_path))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'JSON content processed successfully. Processing started.'
        })
        
    except json.JSONDecodeError as e:
        return jsonify({'error': f'Invalid JSON format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error processing JSON: {str(e)}'}), 500

@app.route('/status/<job_id>')
def job_status_check(job_id):
    """Check the status of a podcast generation job."""
    if job_id not in job_status:
        return jsonify({'error': 'Job not found'}), 404
    
    status = job_status[job_id].copy()
    
    # Add download URLs if completed
    if status['status'] == 'completed':
        if 'audio_file' in status and status['audio_file']:
            status['audio_download_url'] = url_for('download_file', job_id=job_id, file_type='audio')
        if 'script_file' in status and status['script_file']:
            status['script_download_url'] = url_for('download_file', job_id=job_id, file_type='script')
    
    return jsonify(status)

@app.route('/download/<job_id>/<file_type>')
def download_file(job_id, file_type):
    """Download generated files."""
    if job_id not in job_status:
        return jsonify({'error': 'Job not found'}), 404
    
    status = job_status[job_id]
    
    if status['status'] != 'completed':
        return jsonify({'error': 'Job not completed yet'}), 400
    
    try:
        if file_type == 'audio' and 'audio_file' in status:
            file_path = status['audio_file']
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True)
        
        elif file_type == 'script' and 'script_file' in status:
            file_path = status['script_file']
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True)
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 500

@app.route('/example')
def example_json():
    """Show example JSON structure."""
    example = {
        "topics": [
            {
                "headline": "Arweave Network Upgrade Announcement",
                "body": "The Arweave team has announced a major network upgrade that will improve transaction throughput and reduce storage costs. This upgrade introduces new consensus mechanisms and optimizes data retrieval performance.",
                "url": "https://example.com/arweave-upgrade",
                "nature": "development",
                "video": "https://youtube.com/watch?v=example1"
            },
            {
                "headline": "New Permaweb Applications Launch", 
                "body": "Several innovative applications have been launched on the Permaweb this week, including a decentralized social media platform and a permanent document storage service.",
                "url": "https://example.com/permaweb-apps",
                "nature": "community"
            }
        ],
        "chitchat": {
            "headline": "Did you know?",
            "body": "Arweave provides permanent storage for data with a one-time payment, making it ideal for preserving important information forever.",
            "nature": "tip"
        },
        "suggested": {
            "headline": "Weekly Arweave Report",
            "body": "Catch up on the latest developments in the Arweave ecosystem with our comprehensive weekly report.",
            "url": "https://example.com/weekly-report",
            "nature": "suggested reading"
        }
    }
    
    return jsonify(example)

@app.route('/cleanup')
def cleanup():
    """Clean up old jobs and files (admin endpoint)."""
    try:
        current_time = datetime.now()
        cleaned_jobs = 0
        
        # Remove jobs older than 24 hours
        for job_id in list(job_status.keys()):
            job_time = datetime.fromisoformat(job_status[job_id]['created_at'])
            if (current_time - job_time).total_seconds() > 86400:  # 24 hours
                del job_status[job_id]
                cleaned_jobs += 1
        
        # Clean up old uploaded files
        cleaned_files = 0
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if (current_time - file_time).total_seconds() > 86400:  # 24 hours
                    os.remove(file_path)
                    cleaned_files += 1
        
        return jsonify({
            'success': True,
            'cleaned_jobs': cleaned_jobs,
            'cleaned_files': cleaned_files
        })
        
    except Exception as e:
        return jsonify({'error': f'Cleanup failed: {str(e)}'}), 500

if __name__ == '__main__':
    # Check if required environment variables are set
    if not config.GEMINI_API_KEY:
        print("⚠️  Warning: GEMINI_API_KEY not found in environment variables.")
        print("   Make sure to set up your .env file with required API keys.")
        print("   The web interface will still start, but podcast generation will fail.")
    
    print("🎙️  Starting Arweave Today AI Podcaster Web Interface...")
    print(f"📁 Upload folder: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"📁 Output folder: {os.path.abspath(OUTPUT_FOLDER)}")
    print()
    print("🌐 Access the web interface at: http://localhost:5000")
    print("📊 Check job status at: http://localhost:5000/status/<job_id>")
    print("📝 View example JSON at: http://localhost:5000/example")
    print()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
