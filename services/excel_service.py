import openpyxl
import re

class ExcelService:
    def __init__(self):
        pass
    
    def extract_hours(self, file_path):
        try:
            file_extension = file_path.split('.')[-1].lower()
            
            if file_extension == 'xlsx':
                workbook = openpyxl.load_workbook(file_path)
                worksheet = workbook.active
                return self._extract_hours_from_worksheet(worksheet)
            else:
                raise ValueError(f"Unsupported Excel file type: {file_extension}")
            
        except Exception as e:
            print(f"Error processing Excel file: {e}")
            return None
    
    def _extract_hours_from_worksheet(self, worksheet):
        hours_keywords = [
            'hours', 'total hours', 'hours worked', 'time', 'total time',
            'hrs', 'total hrs', 'duration', 'total', 'hours_worked',
            'total_hours', 'work_hours', 'logged_hours'
        ]
        
        # Search through all cells
        for row in worksheet.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue
                    
                # Check if it's a number in reasonable range
                if isinstance(cell.value, (int, float)) and 0 <= cell.value <= 168:
                    return float(cell.value)
                
                # Check if it's text that might contain hours
                if isinstance(cell.value, str):
                    hours = self._extract_hours_from_text(cell.value)
                    if hours is not None:
                        return hours
        
        return None
    
    
    def _extract_hours_from_text(self, text):
        if not isinstance(text, str):
            return None
        
        text = text.lower()
        
        hour_patterns = [
            r'total\s*hours?\s*:?\s*(\d+(?:\.\d+)?)',
            r'hours?\s*worked\s*:?\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*hours?',
            r'hours?\s*:?\s*(\d+(?:\.\d+)?)',
            r'total\s*:?\s*(\d+(?:\.\d+)?)\s*hrs?',
            r'(\d+(?:\.\d+)?)\s*hrs?',
            r'time\s*:?\s*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in hour_patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    hours_value = float(matches[0])
                    if 0 <= hours_value <= 168:
                        return hours_value
                except ValueError:
                    continue
        
        number_pattern = r'\b(\d+(?:\.\d+)?)\b'
        numbers = re.findall(number_pattern, text)
        
        for num_str in numbers:
            try:
                num = float(num_str)
                if 1 <= num <= 168:
                    return num
            except ValueError:
                continue
        
        return None