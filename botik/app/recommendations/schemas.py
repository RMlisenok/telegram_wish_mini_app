from dataclasses import dataclass

@dataclass
class GiftItem:
    title: str
    price: int
    url: str
    source: str  # ozon / wb
