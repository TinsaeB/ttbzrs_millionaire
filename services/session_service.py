import json
from typing import Dict, List
from datetime import datetime
import os

class SessionService:
    def __init__(self, storage_dir: str = "sessions"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
    async def save_session(self, session_data: List[Dict], filename: str = None) -> Dict:
        try:
            if filename is None:
                filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
            filepath = os.path.join(self.storage_dir, filename)
            
            with open(filepath, 'w') as file:
                json.dump(session_data, file, indent=2)
                
            return {
                'status': 'success',
                'filepath': filepath,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    async def load_session(self, filepath: str) -> Dict:
        try:
            with open(filepath, 'r') as file:
                session_data = json.load(file)
                
            return {
                'status': 'success',
                'data': session_data,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
