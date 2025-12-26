

class RecommendationItem(BaseModel):
    title: str
    description: str
    price: Optional[float] = None
    url: str
    category: str