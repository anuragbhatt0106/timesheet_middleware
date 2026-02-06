import os
from flask import Flask, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure Flask app with environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

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
        'status': 'operational'
    })

if __name__ == '__main__':
    # This will only run when executed directly, not with gunicorn
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )