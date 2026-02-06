import os
import tempfile
import mimetypes
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure Flask app with environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Supported file extensions and MIME types
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'png', 'jpg', 'jpeg'}
ALLOWED_MIMETYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
    'image/png',
    'image/jpeg'
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    """Determine file type from filename"""
    if '.' not in filename:
        return 'unknown'
    
    extension = filename.rsplit('.', 1)[1].lower()
    type_mapping = {
        'pdf': 'pdf',
        'docx': 'word', 
        'xlsx': 'excel',
        'png': 'image',
        'jpg': 'image',
        'jpeg': 'image'
    }
    return type_mapping.get(extension, 'unknown')

def mock_extract_text(file_path, file_type):
    """Mock text extraction - returns dummy content based on file type"""
    mock_responses = {
        'pdf': 'Mock text extracted from PDF: Employee worked 8 hours on project tasks including development and testing.',
        'word': 'Mock text from Word document: Daily timesheet shows 8.5 hours of work completed on various assignments.',
        'excel': 'Mock data from Excel: Total hours logged: 40 hours across 5 days with overtime calculations.',
        'image': 'Mock OCR from image: Timesheet scan shows employee worked 7.5 hours with lunch break deducted.'
    }
    return mock_responses.get(file_type, 'Mock text extracted from uploaded file.')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and return mock processing results"""
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided',
                'message': 'Please provide a file in the request'
            }), 400
        
        file = request.files['file']
        
        # Check if file was actually selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'message': 'Please select a file to upload'
            }), 400
        
        # Get optional parameters
        file_type_param = request.form.get('file_type', '').lower()
        claimed_hours = request.form.get('claimed_hours', '0')
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Unsupported file type',
                'message': f'Allowed types: {", ".join(ALLOWED_EXTENSIONS)}',
                'filename': file.filename
            }), 415
        
        # Secure the filename
        filename = secure_filename(file.filename)
        detected_file_type = get_file_type(filename)
        
        # Use provided file_type or detected one
        final_file_type = file_type_param if file_type_param in ['pdf', 'word', 'excel', 'image'] else detected_file_type
        
        # Create temporary file to simulate processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'_{filename}') as tmp_file:
            try:
                # Save uploaded file temporarily
                file.save(tmp_file.name)
                file_size = os.path.getsize(tmp_file.name)
                
                # Mock text extraction
                extracted_text = mock_extract_text(tmp_file.name, final_file_type)
                
                # Simulate processing success
                response_data = {
                    'success': True,
                    'file_name': filename,
                    'file_type': final_file_type,
                    'file_size_bytes': file_size,
                    'claimed_hours': claimed_hours,
                    'extracted_text': extracted_text,
                    'processing_time_ms': 150,  # Mock processing time
                    'timestamp': os.getenv('REQUEST_ID', 'mock-timestamp')
                }
                
                return jsonify(response_data), 200
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_file.name)
                except OSError:
                    pass  # File might already be deleted
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred during file processing',
            'details': str(e) if os.getenv('FLASK_ENV') == 'development' else 'Contact support'
        }), 500

@app.route('/')
def health():
    """Health check endpoint"""
    return jsonify({
        'message': 'Timesheet Middleware is alive!',
        'status': 'healthy',
        'environment': os.getenv('FLASK_ENV', 'development')
    })

@app.route('/health')
def health_check():
    """Alternative health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'timesheet-middleware'
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'api': 'timesheet-middleware',
        'version': '1.0.0',
        'status': 'operational',
        'supported_formats': list(ALLOWED_EXTENSIONS)
    })

@app.errorhandler(413)
def too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'File too large',
        'message': 'File size exceeds the maximum limit of 16MB'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': ['/', '/health', '/api/status', '/api/upload (POST)']
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle method not allowed errors"""
    return jsonify({
        'success': False,
        'error': 'Method Not Allowed',
        'message': 'This endpoint does not support the requested HTTP method'
    }), 405

if __name__ == '__main__':
    # This will only run when executed directly, not with gunicorn
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )