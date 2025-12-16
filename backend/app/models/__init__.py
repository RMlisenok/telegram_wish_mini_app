from .user import User, ThemeEnum, TextSizeEnum
from .wish import Wish, CurrencyEnum
from .wishlist import Wishlist, TypePrivacyEnum
from .wish_wishlist import WishWishlist
from .wish_reservation import WishReservation

# Список всех моделей для удобного импорта
__all__ = [
    "User",
    "ThemeEnum",
    "TextSizeEnum",
    "Wish",
    "CurrencyEnum",
    "Wishlist", 
    "PrivacyEnum",
    "WishWishlist",
    "WishReservation",
]