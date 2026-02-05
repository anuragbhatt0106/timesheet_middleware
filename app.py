from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
import logging
from services.ocr_service import OCRService
from services.excel_service import ExcelService
from services.chatgpt_service import ChatGPTService
from config import Config, setup_logging

app = Flask(__name__)
app.config.from_object(Config)
setup_logging(app)

ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls', 'docx', 'doc', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/validate-timesheet', methods=['POST'])
def validate_timesheet():
    try:
        app.logger.info(f"Received timesheet validation request")
        
        if 'file' not in request.files:
            app.logger.warning("No file provided in request")
            return jsonify({'status': 'error', 'reason': 'No file provided'}), 400
        
        file = request.files['file']
        claimed_hours = request.form.get('claimed_hours')
        
        if file.filename == '':
            app.logger.warning("Empty filename provided")
            return jsonify({'status': 'error', 'reason': 'No file selected'}), 400
        
        if not claimed_hours:
            app.logger.warning("No claimed hours provided")
            return jsonify({'status': 'error', 'reason': 'No claimed hours provided'}), 400
        
        if not allowed_file(file.filename):
            app.logger.warning(f"Unsupported file type: {file.filename}")
            return jsonify({'status': 'error', 'reason': 'File type not supported'}), 400
        
        try:
            claimed_hours_float = float(claimed_hours)
        except ValueError:
            app.logger.warning(f"Invalid claimed hours value: {claimed_hours}")
            return jsonify({'status': 'error', 'reason': 'Invalid claimed hours value'}), 400
        
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        app.logger.info(f"Processing file: {filename}, claimed hours: {claimed_hours_float}")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
            file.save(tmp_file.name)
            
            try:
                extracted_hours = None
                
                if file_extension in ['png', 'jpg', 'jpeg', 'pdf']:
                    app.logger.info("Using OCR service for image/PDF")
                    ocr_service = OCRService()
                    extracted_hours = ocr_service.extract_hours(tmp_file.name)
                elif file_extension in ['xlsx', 'xls']:
                    app.logger.info("Using Excel service for spreadsheet")
                    excel_service = ExcelService()
                    extracted_hours = excel_service.extract_hours(tmp_file.name)
                elif file_extension in ['docx', 'doc']:
                    app.logger.info("Using OCR service for Word document")
                    ocr_service = OCRService()
                    extracted_hours = ocr_service.extract_hours(tmp_file.name)
                
                if extracted_hours is None:
                    app.logger.error("Could not extract hours from file")
                    return jsonify({'status': 'error', 'reason': 'Could not extract hours from file'}), 500
                
                app.logger.info(f"Extracted hours: {extracted_hours}")
                
                chatgpt_service = ChatGPTService()
                validation_result = chatgpt_service.validate_hours(extracted_hours, claimed_hours_float)
                
                app.logger.info(f"Validation result: {validation_result}")
                
                response_data = {
                    'status': 'success',
                    'extracted_hours': extracted_hours,
                    'claimed_hours': claimed_hours_float,
                    'match': validation_result['match'],
                    'reason': validation_result['reason'],
                    'difference': validation_result.get('difference', abs(extracted_hours - claimed_hours_float))
                }
                
                return jsonify(response_data)
                
            finally:
                os.unlink(tmp_file.name)
                
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'status': 'error', 'reason': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)