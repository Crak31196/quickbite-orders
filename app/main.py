from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="QuickBite Orders API")


# --- Mock data (in-memory, resets when app restarts) ---
MENU = [
    {"id": 1, "name": "Margherita Pizza", "price": 249},
    {"id": 2, "name": "Veg Biryani", "price": 199},
    {"id": 3, "name": "Butter Chicken", "price": 279},
]

ORDERS = {}
next_order_id = 1


class OrderRequest(BaseModel):
    item_id: int
    quantity: int


@app.get("/health")
def health():
    return {"status": "ok", "service": "quickbite-orders"}


@app.get("/menu")
def get_menu():
    return MENU


@app.post("/orders")
def create_order(order: OrderRequest):
    global next_order_id

    item = next((m for m in MENU if m["id"] == order.item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    order_id = next_order_id
    next_order_id += 1

    ORDERS[order_id] = {
        "order_id": order_id,
        "item": item["name"],
        "quantity": order.quantity,
        "total": item["price"] * order.quantity,
        "status": "placed",
    }
    return ORDERS[order_id]


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    if order_id not in ORDERS:
        raise HTTPException(status_code=404, detail="Order not found")
    return ORDERS[order_id]
# Mount static files LAST, after every route above
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
