import PyPDF2
from typing import Dict
from datetime import datetime

class DocumentService:
    @staticmethod
    async def read_pdf(file_path: str) -> Dict:
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                    
            return {
                'status': 'success',
                'content': text,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
