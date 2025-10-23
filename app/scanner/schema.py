from pydantic import BaseModel


class ScannerResponse(BaseModel):
    file_name: str
    scan_status: str
    category: str
    malicious_count: int
    harmless_count: int
    suspicious_count: int
    undetected_count: int
    link: str