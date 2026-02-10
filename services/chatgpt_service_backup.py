from openai import OpenAI
import os
import json

class ChatGPTService:
    def __init__(self, api_key=None):
        self.client = OpenAI(
            api_key=api_key or os.getenv('OPENAI_API_KEY')
        )
    
    def validate_hours(self, extracted_hours, claimed_hours, tolerance=0.5):
        try:
            prompt = f"""
You are a timesheet validation assistant. Your job is to compare extracted hours from a timesheet document with claimed hours and determine if they match within a reasonable tolerance.

Extracted hours from document: {extracted_hours}
Claimed hours by user: {claimed_hours}
Tolerance: {tolerance} hours

Please analyze these values and respond with a JSON object containing:
1. "match": boolean (true if they match within tolerance, false otherwise)
2. "reason": string explaining your decision
3. "difference": number representing the absolute difference between the values

Consider the following factors:
- If the difference is within the tolerance ({tolerance} hours), consider it a match
- Account for rounding differences
- Consider if one value might be daily vs weekly totals
- Flag significant discrepancies that might indicate fraud

Example response format:
{{
    "match": true,
    "reason": "Values match within tolerance - difference of 0.25 hours",
    "difference": 0.25
}}
"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a precise timesheet validation assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                result = json.loads(content)
                
                if not isinstance(result.get('match'), bool):
                    raise ValueError("Invalid match value")
                
                return {
                    'match': result['match'],
                    'reason': result.get('reason', 'No reason provided'),
                    'difference': abs(extracted_hours - claimed_hours)
                }
                
            except json.JSONDecodeError:
                return self._fallback_validation(extracted_hours, claimed_hours, tolerance)
            
        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            return self._fallback_validation(extracted_hours, claimed_hours, tolerance)
    
    def _fallback_validation(self, extracted_hours, claimed_hours, tolerance=0.5):
        difference = abs(extracted_hours - claimed_hours)
        match = difference <= tolerance
        
        if match:
            reason = f"Values match within tolerance - difference of {difference:.2f} hours"
        else:
            reason = f"Values do not match - difference of {difference:.2f} hours exceeds tolerance of {tolerance} hours"
        
        return {
            'match': match,
            'reason': reason,
            'difference': difference
        }