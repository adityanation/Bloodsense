from flask import Flask, render_template, request, send_file, jsonify, abort
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, timedelta
import threading
import time
from dotenv import load_dotenv
import logging
from utils.ocr import extract_text_from_file
from utils.pdf import generate_pdf_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}  # Removed PDF support
app.config['FILE_CLEANUP_HOURS'] = 24  # Files older than this will be cleaned up

# Ensure upload and temp folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('temp', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def secure_file_path(filename):
    """Generate a secure file path with UUID to prevent conflicts and security issues."""
    ext = filename.rsplit('.', 1)[1].lower()
    secure_name = f"{uuid.uuid4()}.{ext}"
    return os.path.join(app.config['UPLOAD_FOLDER'], secure_name)

def cleanup_old_files():
    """Clean up files older than FILE_CLEANUP_HOURS."""
    while True:
        try:
            cutoff = datetime.now() - timedelta(hours=app.config['FILE_CLEANUP_HOURS'])
            
            # Clean uploads folder
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.getctime(filepath) < cutoff.timestamp():
                    try:
                        os.remove(filepath)
                    except OSError:
                        pass
            
            # Clean temp folder
            for filename in os.listdir('temp'):
                filepath = os.path.join('temp', filename)
                if os.path.getctime(filepath) < cutoff.timestamp():
                    try:
                        os.remove(filepath)
                    except OSError:
                        pass
                        
        except Exception:
            pass  # Don't let cleanup errors affect the application
            
        # Run every hour
        time.sleep(3600)

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logger.warning('No file uploaded in request')
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if not file or file.filename == '':
        logger.warning('No file selected')
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        logger.warning(f'Invalid file type: {file.filename}')
        return jsonify({'error': 'Invalid file type. Please upload PNG, JPG, or JPEG files.'}), 400
        
    try:
        if isinstance(file.filename, str):
            filename = secure_filename(file.filename)
            file_path = secure_file_path(filename)
            file.save(file_path)
            logger.info(f'File successfully uploaded: {file_path}')
            return jsonify({'file_path': file_path})
        else:
            logger.error('Invalid filename type')
            return jsonify({'error': 'Invalid filename'}), 400
    except Exception as e:
        logger.error(f'Error uploading file: {str(e)}')
        return jsonify({'error': f'Error uploading file: {str(e)}'}), 500

@app.route('/form')
def form():
    file_path = request.args.get('file_path')
    if not file_path:
        return 'No file path provided', 400
    
    # Validate file path is within uploads directory
    if not os.path.abspath(file_path).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
        abort(403)  # Forbidden
    
    if not os.path.exists(file_path):
        return 'File not found', 404
        
    return render_template('form.html', file_path=file_path)

@app.route('/result', methods=['POST'])
def result():
    try:
        # Validate required fields
        required_fields = ['name', 'age', 'gender', 'height', 'weight', 'diet', 'activity', 'smoke', 'drink']
        for field in required_fields:
            if field not in request.form:
                logger.warning(f'Missing required field: {field}')
                return f'Missing required field: {field}', 400

        # Get user data from form
        user_data = {field: request.form[field] for field in required_fields}
        logger.info(f'Processing report for user: {user_data["name"]}')

        # Validate file path
        file_path = request.form.get('file_path')
        if not file_path:
            logger.warning('No file path provided')
            return 'No file path provided', 400
            
        # Security check for file path
        if not os.path.abspath(file_path).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
            logger.error(f'Attempted path traversal: {file_path}')
            abort(403)  # Forbidden
            
        if not os.path.exists(file_path):
            logger.error(f'File not found: {file_path}')
            return 'File not found', 404
        
        try:
            # Extract text from the report
            logger.info('Starting OCR text extraction')
            report_text = extract_text_from_file(file_path)
            if not report_text.strip():
                logger.warning('No text extracted from report')
                return 'No text could be extracted from the report. Please ensure the file is clear and readable.', 400
            logger.info('OCR text extraction completed')
        except Exception as e:
            logger.error(f'Error in OCR processing: {str(e)}')
            return f'Error extracting text from report: {str(e)}', 500

        # Set basic analysis without GPT
        analysis = "Basic report generated without GPT."
        
        try:
            # Generate PDF report
            logger.info('Starting PDF generation')
            pdf_path = generate_pdf_report(user_data, analysis)
            if not pdf_path or not os.path.exists(pdf_path):
                logger.error('PDF generation failed')
                return 'Error generating PDF report', 500
            logger.info(f'PDF report generated: {pdf_path}')
        except Exception as e:
            logger.error(f'Error in PDF generation: {str(e)}')
            return f'Error generating PDF report: {str(e)}', 500
        
        # Sample biomarker data for testing
        biomarkers = [
            {
                'name': 'LDL Cholesterol',
                'value': 165,
                'unit': 'mg/dL',
                'reference_range': '< 130 mg/dL',
                'status': 'critical',
                'nutrition_recommendation': 'Reduce saturated fats, increase fiber intake with whole grains and legumes.',
                'fitness_recommendation': '30 minutes of moderate aerobic exercise 5 times per week.'
            },
            {
                'name': 'HDL Cholesterol',
                'value': 55,
                'unit': 'mg/dL',
                'reference_range': '> 40 mg/dL',
                'status': 'normal'
            },
            {
                'name': 'Triglycerides',
                'value': 180,
                'unit': 'mg/dL',
                'reference_range': '< 150 mg/dL',
                'status': 'moderate'
            },
            {
                'name': 'Fasting Blood Sugar',
                'value': 170,
                'unit': 'mg/dL',
                'reference_range': '70-100 mg/dL',
                'status': 'critical',
                'nutrition_recommendation': 'Limit simple carbs, increase protein and healthy fats.',
                'fitness_recommendation': 'Include both cardio and strength training to improve insulin sensitivity.'
            }
        ]

        return render_template(
            'result.html',
            user_data=user_data,
            report_text=report_text,
            analysis=analysis,
            pdf_path=pdf_path,
            datetime=datetime,
            biomarkers=biomarkers
        )

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/download_report')
def download_report():
    path = request.args.get('path')
    if not path:
        return 'No report path provided', 400
        
    # Security check for file path
    if not os.path.abspath(path).startswith(os.path.abspath('temp')):
        abort(403)  # Forbidden
        
    if not os.path.exists(path):
        return 'Report not found', 404
        
    try:
        return send_file(path, as_attachment=True, download_name='BloodSense_Report.pdf')
    except Exception as e:
        return f'Error downloading report: {str(e)}', 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File is too large. Maximum size is 16MB'}), 413

@app.errorhandler(403)
def forbidden(e):
    return jsonify({'error': 'Access forbidden'}), 403

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True) 