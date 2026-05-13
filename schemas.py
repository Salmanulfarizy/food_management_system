from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class FoodCreate(BaseModel):
    donor: str
    food: str
    quantity: int
    location: str
    phone: str
