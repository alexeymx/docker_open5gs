from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuthData(BaseModel):
    amf: str
    lpa: Optional[str] = None
    adm1: Optional[str] = None
    sqn: int
    pin1: Optional[str] = None
    misc1: Optional[str] = None
    iccid: Optional[str] = None
    pin2: Optional[str] = None
    misc2: Optional[str] = None
    imsi: str
    puk1: Optional[str] = None
    misc3: Optional[str] = None
    batch_name: Optional[str] = None
    puk2: Optional[str] = None
    misc4: Optional[str] = None
    auc_id: int
    sim_vendor: Optional[str] = None
    kid: Optional[str] = None
    last_modified: datetime
    ki: str
    esim: bool
    psk: Optional[str] = None
    opc: str
    des: Optional[str] = None

class HLRResponse(BaseModel):
    success: bool
    data: Optional[AuthData] = None
    error: Optional[str] = None 