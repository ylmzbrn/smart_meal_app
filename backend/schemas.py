from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


# =====================
# MENU ITEM
# =====================
class MenuItemBase(BaseModel):
    name: str
    price: Optional[Decimal] = None
    allergy: Optional[str] = None
    description: Optional[str] = None


class MenuItemCreate(MenuItemBase):
    restaurant_id: int


class MenuItemOut(MenuItemBase):
    food_id: int

    class Config:
        from_attributes = True


# =====================
# RESTAURANT
# =====================
class RestaurantBase(BaseModel):
    restaurant_name: str
    location: Optional[str] = None
    price_range: Optional[str] = None


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantOut(RestaurantBase):
    restaurant_id: int
    menu_items: List[MenuItemOut] = []

    class Config:
        from_attributes = True
