import base64
import json
import os
from anthropic import Anthropic

class ClaudeService:
    def __init__(self, api_key=None):
        self.client = Anthropic(
            api_key=api_key or os.environ.get('ANTHROPIC_API_KEY')
        )
        self.model = "claude-sonnet-4-5-20250929"
    
    def extract_timesheet_data(self, file_bytes, file_type):
        """
        Extract timesheet data from PDF or image files by sending raw bytes to Claude
        
        Args:
            file_bytes: Raw file bytes
            file_type: File extension (pdf, png, jpg, jpeg)
            
        Returns:
            dict: Structured JSON with extracted timesheet data
        """
        try:
            # Convert file bytes to base64
            file_base64 = base64.b64encode(file_bytes).decode('utf-8')
            
            # Determine media type
            media_type_map = {
                'pdf': 'application/pdf',
                'png': 'image/png', 
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg'
            }
            media_type = media_type_map.get(file_type.lower(), 'application/octet-stream')
            
            prompt = """Analyze this timesheet document and extract detailed time tracking information. 

Return ONLY a valid JSON object with the following exact structure:
{
    "extracted_hours": <total_hours_as_number>,
    "confidence_score": <0_to_1_decimal_confidence>,
    "summary": "<brief_description_of_what_was_found>",
    "daily_breakdown": [
        {
            "date": "<YYYY-MM-DD_or_day_of_week>",
            "start_time": "<HH:MM_or_null>", 
            "end_time": "<HH:MM_or_null>",
            "hours": <hours_as_number>,
            "notes": "<task_description_or_project>"
        }
    ],
    "anomalies": ["<any_unusual_patterns_or_issues>"]
}

Look for:
- Total hours worked (main focus)
- Daily time entries with start/end times
- Project names, task descriptions
- Any inconsistencies or unusual patterns
- Time formats like 8:00 AM - 5:00 PM or decimal hours

If no clear time data is found, set extracted_hours to 0 and confidence_score to 0.1."""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "document" if media_type == 'application/pdf' else "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": file_base64
                            }
                        }
                    ]
                }]
            )
            
            response_text = message.content[0].text
            # Strip markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.strip('`')
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            try:
                result = json.loads(response_text)
                return self._validate_and_format_response(result)
            except json.JSONDecodeError:
                return {
                    "extracted_hours": 0,
                    "confidence_score": 0.0,
                    "summary": f"Invalid JSON response: {response_text}",
                    "daily_breakdown": [],
                    "anomalies": ["Failed to parse Claude response as JSON"]
                }
                
        except Exception as e:
            return {
                "extracted_hours": 0,
                "confidence_score": 0.0,
                "summary": f"Error processing file: {str(e)}",
                "daily_breakdown": [],
                "anomalies": [f"Processing error: {str(e)}"]
            }
    
    def extract_from_text(self, text_content):
        """
        Extract timesheet data from plain text (for Word/Excel extracted text)
        
        Args:
            text_content: Extracted text from document
            
        Returns:
            dict: Structured JSON with extracted timesheet data  
        """
        try:
            prompt = f"""Analyze this timesheet text and extract detailed time tracking information.

Text content:
{text_content}

Return ONLY a valid JSON object with the following exact structure:
{{
    "extracted_hours": <total_hours_as_number>,
    "confidence_score": <0_to_1_decimal_confidence>,
    "summary": "<brief_description_of_what_was_found>",
    "daily_breakdown": [
        {{
            "date": "<YYYY-MM-DD_or_day_of_week>",
            "start_time": "<HH:MM_or_null>", 
            "end_time": "<HH:MM_or_null>",
            "hours": <hours_as_number>,
            "notes": "<task_description_or_project>"
        }}
    ],
    "anomalies": ["<any_unusual_patterns_or_issues>"]
}}

Look for:
- Total hours worked (main focus)
- Daily time entries with start/end times  
- Project names, task descriptions
- Any inconsistencies or unusual patterns
- Time formats like 8:00 AM - 5:00 PM or decimal hours

If no clear time data is found, set extracted_hours to 0 and confidence_score to 0.1."""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text
            # Strip markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.strip('`')
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            try:
                result = json.loads(response_text)
                return self._validate_and_format_response(result)
            except json.JSONDecodeError:
                return {
                    "extracted_hours": 0,
                    "confidence_score": 0.0,
                    "summary": f"Invalid JSON response: {response_text}",
                    "daily_breakdown": [],
                    "anomalies": ["Failed to parse Claude response as JSON"]
                }
                
        except Exception as e:
            return {
                "extracted_hours": 0,
                "confidence_score": 0.0,
                "summary": f"Error processing text: {str(e)}",
                "daily_breakdown": [],
                "anomalies": [f"Processing error: {str(e)}"]
            }
    
    def _validate_and_format_response(self, result):
        """Validate and ensure proper formatting of Claude response"""
        try:
            # Ensure required fields exist with proper types
            validated = {
                "extracted_hours": float(result.get("extracted_hours", 0)),
                "confidence_score": max(0.0, min(1.0, float(result.get("confidence_score", 0)))),
                "summary": str(result.get("summary", "No summary provided")),
                "daily_breakdown": [],
                "anomalies": []
            }
            
            # Validate daily_breakdown
            if isinstance(result.get("daily_breakdown"), list):
                for entry in result["daily_breakdown"]:
                    if isinstance(entry, dict):
                        validated_entry = {
                            "date": str(entry.get("date", "")),
                            "start_time": entry.get("start_time") if entry.get("start_time") else None,
                            "end_time": entry.get("end_time") if entry.get("end_time") else None,
                            "hours": float(entry.get("hours", 0)),
                            "notes": str(entry.get("notes", ""))
                        }
                        validated["daily_breakdown"].append(validated_entry)
            
            # Validate anomalies
            if isinstance(result.get("anomalies"), list):
                validated["anomalies"] = [str(anomaly) for anomaly in result["anomalies"]]
            
            return validated
            
        except (ValueError, TypeError) as e:
            return {
                "extracted_hours": 0,
                "confidence_score": 0.0,
                "summary": f"Response validation error: {str(e)}",
                "daily_breakdown": [],
                "anomalies": ["Failed to validate Claude response structure"]
            }