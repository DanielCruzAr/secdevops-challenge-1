from fastapi import File, UploadFile, HTTPException
from app.config.vt_client import client
from app.config.boto3_client import s3_client
from dotenv import load_dotenv
from .schema import ScannerResponse
import logging
import os

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "my-default-bucket")
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def scan_file(file: UploadFile = File(...)) -> ScannerResponse:
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
        logging.info("Beginning VirusTotal scan...")
        with open(filepath, "rb") as f:
            vt_file = await client.scan_file_async(f, wait_for_completion=True)
            logging.info(f"File scanned. VT Analysis ID: {vt_file.id}, Status: {vt_file.status}")

        analysis = await client.get_object_async(f"/analyses/{vt_file.id}")
        safe = analysis.stats.get("malicious", 0) == 0
        category = "safe" if safe else "malicious"
        logging.info(f"Scan complete. File categorized as: {category}")

        object_url = None
        if safe:
            # Upload to S3 if the file is safe
            s3_key = f"safe_files/{file.filename}"
            s3_client.upload_file(filepath, S3_BUCKET_NAME, s3_key)
            object_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
            logging.info(f"Safe file uploaded to S3 bucket '{S3_BUCKET_NAME}' with key '{s3_key}'")

        return ScannerResponse(
            file_name=file.filename,
            scan_status=vt_file.status,
            category=category,
            malicious_count=analysis.stats.get("malicious", 0),
            harmless_count=analysis.stats.get("harmless", 0),
            suspicious_count=analysis.stats.get("suspicious", 0),
            undetected_count=analysis.stats.get("undetected", 0),
            link=object_url
        )
    except Exception as e:
        logging.error(f"Error scanning file: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    finally:
        # Clean up the saved file
        if os.path.exists(filepath):
            os.remove(filepath)
            logging.info(f"Cleaned up file: {filepath}")