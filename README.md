# QuickBite Orders API

A small food-ordering API built during the **InsideIT by Rakesh** seminar.
Follow along: run it, test it, containerize it, and ship it with CI/CD.

## What's in this app

- A REST API (FastAPI) with menu, orders, and health endpoints
- A simple web UI (`app/static/index.html`) — browse the menu, add items to cart, place an order, view past orders
- Live request logging to `logs/server.log`
- An instructor "chaos panel" on the web page, to simulate a database outage live during the troubleshooting lab

## Run locally (inside your Codespace)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0
```

Then open the forwarded port (Codespaces will show a popup), or test the API directly:

```bash
curl localhost:8000/health
curl localhost:8000/menu
curl -X POST localhost:8000/orders -H "Content-Type: application/json" -d '{"item_id": 1, "quantity": 2}'
```

## Using the web UI

Open the forwarded port in your browser. You can:
- **Menu tab** — browse items, use `+`/`−` to adjust quantity, add to cart
- **View Cart tab** — see items, line totals, remove items, place the order
- **My Orders tab** — see confirmed orders after checkout
- **Instructor panel** (bottom of page) — toggle "System: Healthy" / "System: DOWN" to simulate a database failure live, for the troubleshooting lab

## Watching live logs

In a second terminal, run:

```bash
tail -f logs/server.log
```

Every request (successful or failed) appears here in real time as you use the app — this is what you'll use in the Linux/`grep` debugging lab.

## Run tests

```bash
pytest
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/menu` | List menu items |
| POST | `/orders` | Place an order |
| GET | `/orders/{id}` | Get order by ID |
| GET | `/admin/chaos/{on\|off}` | Instructor use: simulate a database outage |

## Notes

- Data is stored in memory only — orders reset if the server restarts.
- Each item in a cart currently creates a separate order record (simplified for the seminar's API lab).
