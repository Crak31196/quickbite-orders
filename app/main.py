from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("quickbite")

app = FastAPI(title="QuickBite Orders API")

# --- Chaos mode toggle (instructor use only, for live troubleshooting demo) ---
CHAOS_MODE = {"db_down": False}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000)
    logger.info(f"{request.method} {request.url.path} {response.status_code} ({duration}ms)")
    return response


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

    # --- Chaos check: simulates a database outage when toggled on ---
    if CHAOS_MODE["db_down"]:
        logger.error(f"Database connection timed out — order for item_id={order.item_id} failed")
        raise HTTPException(status_code=500, detail="Internal server error: database unavailable")

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
    logger.info(f"Order placed: order_id={order_id} item={item['name']} qty={order.quantity}")
    return ORDERS[order_id]


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    if order_id not in ORDERS:
        raise HTTPException(status_code=404, detail="Order not found")
    return ORDERS[order_id]


@app.get("/admin/chaos/{toggle}")
def toggle_chaos(toggle: str):
    """Instructor-only: flip this to simulate a database outage live."""
    CHAOS_MODE["db_down"] = (toggle == "on")
    logger.warning(f"CHAOS MODE {'ENABLED' if CHAOS_MODE['db_down'] else 'DISABLED'} — database failures simulated")
    return {"chaos_db_down": CHAOS_MODE["db_down"]}


# Mount static files LAST, after every route above
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
