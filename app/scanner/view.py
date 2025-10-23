from fastapi import (
    APIRouter, 
    Depends,
    File, 
    UploadFile, 
    status, 
    Request
)
from app.rate_limiting import limiter
from app.scanner.controller import scan_file
from app.scanner.schema import ScannerResponse
from app.utils import get_api_key

router = APIRouter(prefix="/scanner", tags=["Scanner"])


@router.post("/", response_model=ScannerResponse, status_code=status.HTTP_200_OK)
@limiter.limit("4/minute")
async def scan_file_view(
    request: Request, 
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    return await scan_file(file)