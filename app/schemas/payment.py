from pydantic import BaseModel


class PaymentSessionCreate(BaseModel):
    order_id: int
    success_url: str
    cancel_url: str


class PaymentSessionOut(BaseModel):
    url: str
    session_id: str