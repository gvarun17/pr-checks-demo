"""Tiny example service used to demonstrate the PR check pipeline."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="pr-checks-demo", version="0.1.0")

_ITEMS: dict[int, "Item"] = {}


class Item(BaseModel):
    id: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/items", status_code=201)
def create_item(item: Item) -> Item:
    if item.id in _ITEMS:
        raise HTTPException(status_code=409, detail="item already exists")
    _ITEMS[item.id] = item
    return item


@app.get("/items/{item_id}")
def get_item(item_id: int) -> Item:
    item = _ITEMS.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="item not found")
    return item
