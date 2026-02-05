import pandas as pd
import re

class ExcelService:
    def __init__(self):
        pass
    
    def extract_hours(self, file_path):
        try:
            file_extension = file_path.split('.')[-1].lower()
            
            if file_extension == 'xlsx':
                df = pd.read_excel(file_path, engine='openpyxl')
            elif file_extension == 'xls':
                df = pd.read_excel(file_path, engine='xlrd')
            else:
                raise ValueError(f"Unsupported Excel file type: {file_extension}")
            
            return self._extract_hours_from_dataframe(df)
        except Exception as e:
            print(f"Error processing Excel file: {e}")
            return None
    
    def _extract_hours_from_dataframe(self, df):
        if df.empty:
            return None
        
        hours_columns = [
            'hours', 'total hours', 'hours worked', 'time', 'total time',
            'hrs', 'total hrs', 'duration', 'total', 'hours_worked',
            'total_hours', 'work_hours', 'logged_hours'
        ]
        
        for col_name in hours_columns:
            for column in df.columns:
                if isinstance(column, str) and col_name.lower() in column.lower():
                    hours_value = self._extract_numeric_from_column(df[column])
                    if hours_value is not None:
                        return hours_value
        
        for column in df.columns:
            if df[column].dtype in ['float64', 'int64']:
                hours_value = self._extract_numeric_from_column(df[column])
                if hours_value is not None and 0 <= hours_value <= 168:
                    return hours_value
        
        for column in df.columns:
            hours_value = self._extract_hours_from_text_column(df[column])
            if hours_value is not None:
                return hours_value
        
        return None
    
    def _extract_numeric_from_column(self, column):
        try:
            numeric_values = pd.to_numeric(column, errors='coerce').dropna()
            
            if not numeric_values.empty:
                for value in numeric_values:
                    if 0 <= value <= 168:
                        return float(value)
                
                total_value = numeric_values.sum()
                if 0 <= total_value <= 168:
                    return float(total_value)
        except:
            pass
        return None
    
    def _extract_hours_from_text_column(self, column):
        for value in column.dropna():
            if isinstance(value, str):
                hours = self._extract_hours_from_text(value)
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