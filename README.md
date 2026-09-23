# QuickBite Orders API

A small food-ordering API built during the **InsideIT by Rakesh** seminar.
Follow along: run it, test it, containerize it, and ship it with CI/CD.

## Run locally (inside your Codespace)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0
```

Then open the forwarded port, or in a second terminal:

```bash
curl localhost:8000/health
curl localhost:8000/menu
curl -X POST localhost:8000/orders -H "Content-Type: application/json" -d '{"item_id": 1, "quantity": 2}'
```

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
