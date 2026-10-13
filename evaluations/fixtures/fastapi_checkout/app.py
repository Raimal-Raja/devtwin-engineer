"""Deliberately broken HTTP development fixture; repair only fresh copies."""
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()


class CheckoutRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    subtotal: int = Field(ge=0, strict=True)
    discount: int | None = Field(default=None, ge=0, strict=True)


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.post('/checkout')
def checkout(request: CheckoutRequest):
    return {'total': max(0, request.subtotal - request.discount)}
