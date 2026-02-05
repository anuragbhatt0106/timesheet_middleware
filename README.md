# Timesheet Middleware API

A Python Flask API that validates timesheets by comparing extracted hours from uploaded files with claimed hours using AI validation.

## Features

- **Multi-format Support**: PDF, Excel (.xlsx/.xls), Word (.docx/.doc), Images (PNG/JPG)
- **OCR Processing**: Uses Tesseract OCR for text extraction from images and PDFs
- **Excel Parsing**: Intelligent parsing of Excel spreadsheets for hour values
- **AI Validation**: OpenAI GPT integration for smart hour comparison and validation
- **Salesforce Ready**: JSON API designed for Salesforce integration

## Setup

### Prerequisites

1. **Python 3.8+**
2. **Tesseract OCR**: Install on your system
   - macOS: `brew install tesseract`
   - Ubuntu: `sudo apt install tesseract-ocr`
   - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

### Installation

1. **Clone and setup virtual environment**:
```bash
cd timesheet_middleware
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Environment configuration**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. **Run the application**:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Usage

### Endpoint: `/validate-timesheet`

**Method**: POST  
**Content-Type**: multipart/form-data

**Parameters**:
- `file`: The timesheet file (PDF/Excel/Word/Image)
- `claimed_hours`: Number of hours claimed by the user

**Example Request**:
```bash
curl -X POST http://localhost:5000/validate-timesheet \
  -F "file=@timesheet.pdf" \
  -F "claimed_hours=40"
```

**Example Response**:
```json
{
  "status": "success",
  "extracted_hours": 39.5,
  "claimed_hours": 40.0,
  "match": true,
  "reason": "Values match within tolerance - difference of 0.5 hours",
  "difference": 0.5
}
```

### Health Check: `/health`

**Method**: GET

**Response**:
```json
{
  "status": "healthy"
}
```

## File Structure

```
timesheet_middleware/
├── app.py                 # Main Flask application
├── config.py             # Configuration and logging setup
├── requirements.txt      # Python dependencies
├── services/
│   ├── __init__.py
│   ├── ocr_service.py    # OCR processing for images/PDFs/Word
│   ├── excel_service.py  # Excel file parsing
│   └── chatgpt_service.py # OpenAI GPT validation
├── venv/                 # Virtual environment
├── .env.example          # Environment variables template
└── README.md
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `SECRET_KEY`: Flask secret key for security
- `FLASK_ENV`: Set to 'development' for debug mode

## Supported File Types

- **Images**: PNG, JPG, JPEG (via Tesseract OCR)
- **PDFs**: Text extraction + OCR fallback
- **Excel**: .xlsx, .xls (intelligent column detection)
- **Word Documents**: .docx, .doc (text and table extraction)

## Error Handling

The API returns structured error responses:

```json
{
  "status": "error", 
  "reason": "Descriptive error message"
}
```

Common error codes:
- `400`: Bad request (missing file, invalid hours, unsupported format)
- `500`: Processing error (OCR failed, OpenAI API error, etc.)

## Development

To run in development mode:
```bash
export FLASK_ENV=development
python app.py
```

## Future Enhancements

- Salesforce integration endpoints
- Batch processing capabilities
- Enhanced OCR accuracy with preprocessing
- Custom validation rules configuration
- Database logging and audit trails