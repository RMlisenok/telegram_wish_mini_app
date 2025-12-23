from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class TagBase(BaseModel):
    tag_value: str
    type_tags: bool = True

class TagResponse(TagBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserFormItem(BaseModel):
    tag_id: int
    detail: Optional[str] = None

class QuestionnaireCreate(BaseModel):
    interests: List[UserFormItem]
    avoid_gifts: List[UserFormItem]

class QuestionnaireResponse(BaseModel):
    user_id: int
    interests: List[TagResponse]
    avoid_gifts: List[TagResponse]