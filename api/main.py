from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict
import os
import shutil
import logging
from utils.parser import parse_docx, parse_markdown

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DocuMind API",
    description="AI-Powered Document Search",
    version="0.1"
)

# Ensure data directories exist
os.makedirs("data/samples", exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Pre-load sample files on startup"""
    logger.info(f"Loaded {len(os.listdir('data/samples'))} sample files")

@app.get("/")
async def root():
    return {
        "message": "DocuMind API", 
        "endpoints": {
            "upload": "/upload (POST)",
            "search": "/search?q=query (GET)",
            "samples": "/samples (GET)",
            "docs": "/docs (Swagger UI)"
        }
    }

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """Handle file uploads (.docx, .md)"""
    try:
        file_location = f"data/{file.filename}"
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Parse based on file type
        if file.filename.endswith(".docx"):
            parsed = parse_docx(file_location)
        elif file.filename.endswith(".md"):
            parsed = parse_markdown(file_location)
        else:
            raise HTTPException(400, detail="Unsupported file type")

        return {
            "status": "success",
            "file_path": file_location,
            "metadata": {
                "title": parsed.get("title"),
                "author": parsed.get("author"),
                "last_modified": parsed.get("last_modified")
            },
            "content_preview": parsed.get("text", "")[:200] + "..."
        }

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(500, detail=str(e))

@app.get("/search")
async def search(
    q: str = Query(..., min_length=1, example="marketing strategy"),
    author: Optional[str] = None
):
    """Mock search - Member 2 will integrate FAISS"""
    logger.info(f"Search query: '{q}'")
    return {
        "query": q,
        "filters": {"author": author},
        "results": [
            {
                "id": 1,
                "title": "Sample Document",
                "score": 0.95,
                "snippet": "Relevant text snippet matching your query..."
            }
        ]
    }

@app.get("/samples")
async def list_samples():
    """List all sample files"""
    return {"samples": os.listdir("data/samples")}

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.1"}