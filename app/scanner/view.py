from fastapi import (
    APIRouter, 
    File, 
    UploadFile, 
    status, 
    Request
)
from app.rate_limiting import limiter
from app.scanner.controller import scan_file
from app.scanner.schema import ScannerResponse

router = APIRouter(prefix="/scanner", tags=["Scanner"])


@router.post("/", response_model=ScannerResponse, status_code=status.HTTP_200_OK)
@limiter.limit("4/minute")
async def scan_file_view(
    request: Request, 
    file: UploadFile = File(...),
):
    return await scan_file(file)