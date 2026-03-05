# bmsydney-order-loading

MVP backend scaffold for BMSYDNEY Order Loading Bridge (Phase 1), implemented in Python.

## Included in this MVP
- Manual order submission API
- Validation for pickup/delivery and item master
- Queue number generation per queue/day
- Minimal Accrivia-compatible XLS generation
- Staff queue listing

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`.

## Endpoints

- `GET /health`
- `POST /api/orders/submit`
- `GET /api/staff/queue?orderType=Pickup&store=Cabramatta`

## Notes
- Customer XLS uploads are not implemented.
- XLS output is single `Sheet1` and never writes price cells.
