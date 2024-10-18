from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class MessageRead(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    content: str
    date_time: datetime

    model_config = ConfigDict(from_attributes=True)



class MessageCreate(BaseModel):
    recipient_id: int
    content: str
    date_time: datetime | None = None