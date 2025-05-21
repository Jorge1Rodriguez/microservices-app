from pydantic import BaseModel
from typing import List, Optional

class ProductItem(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
    quantity: int

class OrderBase(BaseModel):
    products: List[ProductItem]
    total_amount: float
    status: str = "pending"

class OrderCreate(OrderBase):
    user_id: int

class OrderInDB(OrderBase):
    id: int
    user_id: int
    created_at: str

class OrderResponse(OrderInDB):
    pass
