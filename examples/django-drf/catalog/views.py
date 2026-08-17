"""Mini-shop and merchant-proxy API."""

from __future__ import annotations

import json
import secrets
from typing import Any, cast

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.client import get_client
from catalog.models import Order, Product, Transfer
from catalog.proxy import handle_proxy
from catalog.sessions import create_session, get_session

DEMO_PRODUCTS = [
    {"sku": "DEMO-SHIRT", "name": "Demo T-shirt", "description": "Cotton demo shirt", "price": "25.00", "currency": "USD"},
    {"sku": "DEMO-COFFEE", "name": "Demo coffee", "description": "A cup of demo coffee", "price": "5.00", "currency": "USD"},
    {"sku": "DEMO-BUNDLE", "name": "Demo bundle", "description": "Shirt plus coffee", "price": "10.00", "currency": "USD"},
]


def _product_payload(product: Product) -> dict[str, Any]:
    return {
        "id": product.pk,
        "sku": product.sku,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "currency": product.currency,
    }


def _order_payload(order: Order) -> dict[str, Any]:
    return {
        "id": order.pk,
        "reference": order.reference,
        "product_id": order.product_id,
        "amount": order.amount,
        "currency": order.currency,
        "status": order.status,
    }


def _transfer_payload(transfer: Transfer) -> dict[str, Any]:
    return {
        "id": transfer.pk,
        "reference": transfer.reference,
        "amount": transfer.amount,
        "currency": transfer.currency,
        "destination": transfer.destination,
        "status": transfer.status,
    }


def _bearer_token(request: Request | HttpRequest) -> str:
    header = request.headers.get("Authorization") or request.META.get("HTTP_AUTHORIZATION") or ""
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    return ""


def _public_base(request: Request | HttpRequest) -> str:
    return request.build_absolute_uri("/").rstrip("/")


@api_view(["GET"])
def product_list(_request: Request) -> Response:
    return Response([_product_payload(product) for product in Product.objects.order_by("id")])


@api_view(["GET"])
def product_detail(_request: Request, product_id: int) -> Response:
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response({"message": "Product not found"}, status=404)
    return Response(_product_payload(product))


@api_view(["POST"])
def create_checkout_session(request: Request) -> Response:
    body = request.data if isinstance(request.data, dict) else {}
    operation = str(body.get("operation") or "deposit")
    product_id = body.get("product_id")
    amount = body.get("amount")
    currency = body.get("currency")
    lock_amount = True
    order_id = None
    transfer_id = None
    reference = f"EX-{secrets.token_hex(6).upper()}"

    if product_id is not None:
        try:
            product = Product.objects.get(pk=int(product_id))
        except (Product.DoesNotExist, TypeError, ValueError):
            return Response({"message": "Product not found"}, status=404)
        amount = product.price
        currency = product.currency
        lock_amount = True
        order = Order.objects.create(
            reference=reference,
            product=product,
            amount=product.price,
            currency=product.currency,
            status="pending",
        )
        order_id = order.pk
        operation = "deposit"
    elif operation == "payout":
        if not amount or not currency:
            return Response({"message": "amount and currency are required for payouts"}, status=400)
        transfer = Transfer.objects.create(
            reference=reference,
            amount=str(amount),
            currency=str(currency),
            status="pending",
        )
        transfer_id = transfer.pk
        lock_amount = True
    elif amount and currency:
        lock_amount = bool(body.get("lockAmount", True))
    else:
        return Response({"message": "product_id or amount and currency are required"}, status=400)

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
    return Response(
        {
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
    )


@api_view(["GET"])
def order_list(_request: Request) -> Response:
    return Response([_order_payload(order) for order in Order.objects.select_related("product").order_by("-id")])


@api_view(["POST"])
def refund_order(_request: Request, order_id: int) -> Response:
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response({"message": "Order not found"}, status=404)
    if order.status != "paid":
        return Response({"message": "Only paid orders can be refunded"}, status=400)
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
    order.save(update_fields=["status"])
    return Response({"order": _order_payload(order), "refund": result})


@api_view(["GET", "POST"])
def transfers(request: Request) -> Response:
    if request.method == "GET":
        return Response([_transfer_payload(item) for item in Transfer.objects.order_by("-id")])
    return _create_transfer(request)


def _create_transfer(request: Request) -> Response:
    body = request.data if isinstance(request.data, dict) else {}
    amount = body.get("amount")
    currency = body.get("currency")
    destination = str(body.get("destination") or body.get("customer_phone") or "")
    if not amount or not currency:
        return Response({"message": "amount and currency are required"}, status=400)
    reference = f"PO-{secrets.token_hex(6).upper()}"
    client = get_client()
    payload = {
        "provider_code": body.get("provider_code"),
        "reference": reference,
        "amount": str(amount),
        "currency": str(currency),
        "customer_phone": destination,
    }
    result = client.payouts.create(payload, reference)
    transfer = Transfer.objects.create(
        reference=reference,
        amount=str(amount),
        currency=str(currency),
        destination=destination,
        status="pending",
    )
    return Response({"transfer": _transfer_payload(transfer), "payout": result}, status=201)


@api_view(["GET", "POST"])
def payments(request: Request, route: str = "") -> Response:
    token = _bearer_token(request)
    session = get_session(token)
    if session is None:
        return Response({"message": "Invalid checkout session"}, status=401)
    query = {key: value for key, value in request.query_params.items()}
    body = request.data if isinstance(request.data, dict) else {}
    status, payload = handle_proxy(request.method or "GET", route, query, cast(dict[str, Any], body), session)
    return Response(payload, status=status)


@csrf_exempt
def webhooks(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return JsonResponse({"message": "Method not allowed"}, status=405)
    raw = request.body.decode("utf-8")
    signature = request.headers.get("X-Webhook-Signature") or ""
    client = get_client()
    if not client.webhooks.verify(raw, signature, settings.MM_WEBHOOK_SECRET):
        return JsonResponse({"message": "Invalid signature"}, status=400)
    try:
        payload = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        payload = {}
    reference = ""
    status = "pending"
    if isinstance(payload, dict):
        reference = str(payload.get("reference") or payload.get("merchant_reference") or "")
        status = str(payload.get("status") or "pending").lower()
        mapped = "paid" if status in {"success", "successful", "paid", "completed"} else (
            "failed" if status in {"failed", "error"} else status
        )
        if reference:
            Order.objects.filter(reference=reference).update(status=mapped)
            Transfer.objects.filter(reference=reference).update(status=mapped)
    return JsonResponse({"ok": True})
