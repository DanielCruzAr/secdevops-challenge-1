from fastapi import APIRouter, File, UploadFile, status, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from app.config.vt_client import client
from dotenv import load_dotenv
import os

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/scanner", tags=["Scanner"])


@router.post("/", status_code=status.HTTP_200_OK)
async def scan_file(
    request: Request, 
    file: UploadFile = File(...),
):
    """
    Endpoint to scan a file for malware.
    """
    try:
        content = await file.read()
        filepath = os.path.join(UPLOAD_DIR, file.filename)
        logging.info(f"Received file: {file.filename} of type {file.content_type} with size {len(content)} bytes")

        # Save the uploaded file to disk
        with open(filepath, "wb") as f:
            f.write(content)
            logging.info(f"File saved to {filepath}")

        # Scan the file using VT client
        with open(filepath, "rb") as f:
            vt_file = await client.scan_file_async(f, wait_for_completion=True)
            logging.info(f"File scanned. VT Analysis ID: {vt_file.id}, Status: {vt_file.status}")

        analysis = await client.get_object_async(f"/analyses/{vt_file.id}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "filename": file.filename, 
                "scan_status": analysis.status,
                "malicious_count": analysis.stats.get("malicious"),
                "harmless_count": analysis.stats.get("harmless"),
                "suspicious_count": analysis.stats.get("suspicious"),
                "undetected_count": analysis.stats.get("undetected"),
                "link": f"https://www.virustotal.com/gui/file/{analysis.id}"
            }
        )
    except Exception as e:
        logging.error(f"Error scanning file: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    finally:
        # Clean up the saved file
        if os.path.exists(filepath):
            os.remove(filepath)
            logging.info(f"Cleaned up file: {filepath}")