
import datetime
from pydantic import BaseModel

class MetaClient(BaseModel):
    access_token: str
    expires_at: datetime.datetime

