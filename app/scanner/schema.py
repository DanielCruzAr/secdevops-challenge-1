from pydantic import BaseModel
from typing import Optional


class ScannerResponse(BaseModel):
    file_name: str
    scan_status: str
    category: str
    malicious_count: int
    harmless_count: int
    suspicious_count: int
    undetected_count: int
    link: Optional[str] = None