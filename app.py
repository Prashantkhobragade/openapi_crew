from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# Pydantic model for our item
class Item(BaseModel):
    item_number: int
    item_name: str
    value: int

# In-memory storage using a dictionary for faster lookup
items = []

@app.get("/items/", response_model=List[Item])
async def read_items():
    return items


@app.post("/items/")
async def create_item(item: Item):
    items.append(item)
    return {"message": "Item created successfully"}


@app.get("/items/{item_number}", response_model=Item)
async def read_item_by_item_number(item_number: int):
    for item in items:
        if item.item_number == item_number:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{item_number}")
async def delete_item(item_number: int):
    for index, item in enumerate(items):
        if item.item_number == item_number:
            items.pop(index)
            return {"message": f"Item with number {item_number} deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
