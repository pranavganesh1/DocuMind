from docx import Document
import markdown
from typing import Dict, Optional
import os
from datetime import datetime

def parse_docx(file_path: str) -> Optional[Dict]:
    """Extract text and metadata from .docx"""
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        
        return {
            "text": text,
            "title": os.path.splitext(os.path.basename(file_path))[0],
            "author": "Unknown",
            "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        }
    except Exception as e:
        print(f"[ERROR] Failed to parse {file_path}: {e}")
        return None

def parse_markdown(file_path: str) -> Optional[Dict]:
    """Extract text and metadata from .md"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        return {
            "text": text,
            "title": os.path.splitext(os.path.basename(file_path))[0],
            "author": "Notion User",
            "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        }
    except Exception as e:
        print(f"[ERROR] Failed to parse {file_path}: {e}")
        return None