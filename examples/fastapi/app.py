"""FastAPI mini-shop example."""

from __future__ import annotations

import json
import os
import secrets
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from client import get_client
from db import Order, Product, SessionLocal, Transfer, ensure_working_db, seed_products
from proxy import handle_proxy
from sessions import create_session, get_session

load_dotenv()
ensure_working_db()

app = FastAPI(title="MainMoney FastAPI example")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.environ.get(
            "CORS_ORIGINS",
            "http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175,http://127.0.0.1:4200",
        ).split(",")
        if origin.strip()
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _product_payload(product: Product) -> dict[str, Any]:
    return {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "currency": product.currency,
    }


def _order_payload(order: Order) -> dict[str, Any]:
    return {
        "id": order.id,
        "reference": order.reference,
        "product_id": order.product_id,
        "amount": order.amount,
        "currency": order.currency,
        "status": order.status,
    }


def _transfer_payload(transfer: Transfer) -> dict[str, Any]:
    return {
        "id": transfer.id,
        "reference": transfer.reference,
        "amount": transfer.amount,
        "currency": transfer.currency,
        "destination": transfer.destination,
        "status": transfer.status,
    }


def _bearer_token(request: Request) -> str:
    header = request.headers.get("authorization") or ""
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    return ""


def _public_base(request: Request) -> str:
    return str(request.base_url).rstrip("/")


@app.get("/products")
def product_list() -> list[dict[str, Any]]:
    with SessionLocal() as db:
        return [_product_payload(item) for item in db.query(Product).order_by(Product.id)]


@app.get("/products/{product_id}")
def product_detail(product_id: int) -> dict[str, Any]:
    with SessionLocal() as db:
        product = db.get(Product, product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return _product_payload(product)


@app.post("/session")
async def create_checkout_session(request: Request) -> dict[str, Any]:
    body = await request.json()
    operation = str(body.get("operation") or "deposit")
    product_id = body.get("product_id")
    amount = body.get("amount")
    currency = body.get("currency")
    lock_amount = True
    order_id = None
    transfer_id = None
    reference = f"EX-{secrets.token_hex(6).upper()}"

    with SessionLocal() as db:
        if product_id is not None:
            product = db.get(Product, int(product_id))
            if product is None:
                raise HTTPException(status_code=404, detail="Product not found")
            amount = product.price
            currency = product.currency
            order = Order(
                reference=reference,
                product_id=product.id,
                amount=product.price,
                currency=product.currency,
                status="pending",
            )
            db.add(order)
            db.commit()
            db.refresh(order)
            order_id = order.id
            operation = "deposit"
        elif operation == "payout":
            if not amount or not currency:
                raise HTTPException(status_code=400, detail="amount and currency are required for payouts")
            transfer = Transfer(reference=reference, amount=str(amount), currency=str(currency), status="pending")
            db.add(transfer)
            db.commit()
            db.refresh(transfer)
            transfer_id = transfer.id
        elif amount and currency:
            lock_amount = bool(body.get("lockAmount", True))
        else:
            raise HTTPException(status_code=400, detail="product_id or amount and currency are required")

    session = create_session(
        reference=reference,
        amount=str(amount) if amount is not None else None,
        currency=str(currency) if currency is not None else None,
        lock_amount=lock_amount,
        operation=operation,
        order_id=order_id,
        transfer_id=transfer_id,
    )
    base = _public_base(request)
    return {
        "merchantBackendUrl": f"{base}/payments",
        "clientToken": session.token,
        "pollUrl": f"{base}/payments/status",
        "pollHeaders": {"Authorization": f"Bearer {session.token}"},
        "locale": "en",
        "amount": session.amount,
        "currency": session.currency,
        "lockAmount": session.lock_amount,
        "reference": session.reference,
        "operation": session.operation,
    }


@app.get("/orders")
def order_list() -> list[dict[str, Any]]:
    with SessionLocal() as db:
        return [_order_payload(item) for item in db.query(Order).order_by(Order.id.desc())]


@app.post("/orders/{order_id}/refund")
def refund_order(order_id: int) -> dict[str, Any]:
    with SessionLocal() as db:
        order = db.get(Order, order_id)
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status != "paid":
            raise HTTPException(status_code=400, detail="Only paid orders can be refunded")
        client = get_client()
        refund_reference = f"RF-{secrets.token_hex(6).upper()}"
        result = client.refunds.create(
            {
                "reference": refund_reference,
                "original_transaction_id": order.reference,
                "amount": order.amount,
                "currency": order.currency,
                "reason": "Example shop refund",
            },
            refund_reference,
        )
        order.status = "refunded"
        db.commit()
        db.refresh(order)
        return {"order": _order_payload(order), "refund": result}


@app.get("/transfers")
def transfer_list() -> list[dict[str, Any]]:
    with SessionLocal() as db:
        return [_transfer_payload(item) for item in db.query(Transfer).order_by(Transfer.id.desc())]


@app.post("/transfers")
async def create_transfer(request: Request) -> dict[str, Any]:
    body = await request.json()
    amount = body.get("amount")
    currency = body.get("currency")
    destination = str(body.get("destination") or body.get("customer_phone") or "")
    if not amount or not currency:
        raise HTTPException(status_code=400, detail="amount and currency are required")
    reference = f"PO-{secrets.token_hex(6).upper()}"
    client = get_client()
    result = client.payouts.create(
        {
            "provider_code": body.get("provider_code"),
            "reference": reference,
            "amount": str(amount),
            "currency": str(currency),
            "customer_phone": destination,
        },
        reference,
    )
    with SessionLocal() as db:
        transfer = Transfer(
            reference=reference,
            amount=str(amount),
            currency=str(currency),
            destination=destination,
            status="pending",
        )
        db.add(transfer)
        db.commit()
        db.refresh(transfer)
        return {"transfer": _transfer_payload(transfer), "payout": result}


@app.api_route("/payments", methods=["GET", "POST"])
@app.api_route("/payments/{route:path}", methods=["GET", "POST"])
async def payments(request: Request, route: str = "") -> JSONResponse:
    token = _bearer_token(request)
    session = get_session(token)
    if session is None:
        return JSONResponse({"message": "Invalid checkout session"}, status_code=401)
    query = dict(request.query_params)
    body: dict[str, Any] = {}
    if request.method == "POST":
        try:
            payload = await request.json()
            if isinstance(payload, dict):
                body = payload
        except Exception:
            body = {}
    status, payload = handle_proxy(request.method, route, query, body, session)
    return JSONResponse(payload, status_code=status)


@app.post("/webhooks")
async def webhooks(request: Request) -> dict[str, bool]:
    raw = (await request.body()).decode("utf-8")
    signature = request.headers.get("x-webhook-signature") or ""
    client = get_client()
    if not client.webhooks.verify(raw, signature, os.environ.get("MM_WEBHOOK_SECRET", "")):
        raise HTTPException(status_code=400, detail="Invalid signature")
    try:
        payload = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        payload = {}
    if isinstance(payload, dict):
        reference = str(payload.get("reference") or payload.get("merchant_reference") or "")
        status = str(payload.get("status") or "pending").lower()
        mapped = "paid" if status in {"success", "successful", "paid", "completed"} else (
            "failed" if status in {"failed", "error"} else status
        )
        if reference:
            with SessionLocal() as db:
                for model in (Order, Transfer):
                    row = db.query(model).filter_by(reference=reference).first()
                    if row is not None:
                        row.status = mapped
                db.commit()
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=int(os.environ.get("PORT", "8001")), reload=True)
