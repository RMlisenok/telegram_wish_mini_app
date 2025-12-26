# from pydantic import BaseModel, ConfigDict
# from typing import Optional, List
#
# class TagItem(BaseModel):
#     tag: str # Текст тега
#     details: Optional[str] = None
#
# class QuestionnaireCreate(BaseModel):
#     interests: List[TagItem]
#     avoid_gifts: List[TagItem]
#
# class QuestionnaireResponse(BaseModel):
#     interests: List[TagItem]
#     avoid_gifts: List[TagItem]
#
# class TagBase(BaseModel):
#     tag_value: str
#     type_tags: bool = True
#
# class TagResponse(TagBase):
#     id: int
#     model_config = ConfigDict(from_attributes=True)
#
# class UserFormItem(BaseModel):
#     tag_id: int
#     detail: Optional[str] = None
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List

class TagItem(BaseModel):
    tag: str = Field(..., description="Например 'Спорт')")
    details: Optional[str] = Field(None, description="Дополнительные детали")

class QuestionnaireCreate(BaseModel):
    interests: List[TagItem] = Field(..., min_length=3)  # Валидация из api.yaml
    avoid_gifts: List[TagItem] = Field(..., min_length=1)

class QuestionnaireResponse(BaseModel):
    interests: List[TagItem]
    avoid_gifts: List[TagItem]

class TagBase(BaseModel):
    tag_value: str
    type_tags: bool = True  # True - интересы, False - ограничения

class TagResponse(TagBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserFormItem(BaseModel):
    tag_id: int
    detail: Optional[str] = None