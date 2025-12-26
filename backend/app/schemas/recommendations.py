from pydantic import BaseModel

class GiftResponse(BaseModel):
    title: str
    description: str
    url: str
    category: str

    class Config:
        from_attributes = True