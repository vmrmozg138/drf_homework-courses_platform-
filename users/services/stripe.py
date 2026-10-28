import requests
from django.conf import settings

STRIPE_API_URL = "https://api.stripe.com/v1"

success_url = "http://localhost:8000/?session_id={CHECKOUT_SESSION_ID}"
cancel_url = "http://localhost:8000/"


def _stripe_post(endpoint, data):
    """Отправляет POST-запрос к Stripe REST API."""
    if not settings.STRIPE_SECRET_KEY:
        raise ValueError("Не настроен STRIPE_SECRET_KEY")

    response = requests.post(
        f"{STRIPE_API_URL}/{endpoint}",
        data=data,
        auth=(settings.STRIPE_SECRET_KEY, ""),
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def create_stripe_product(course_or_lesson):
    """Создаёт продукт Stripe для курса или урока."""
    product = _stripe_post(
        "products",
        {
            "name": course_or_lesson.title,
            "description": course_or_lesson.description or "",
        },
    )
    return product["id"]


def create_stripe_price(product_id, amount):
    """Создаёт одноразовую цену Stripe для продукта."""
    amount_in_kopecks = int(amount * 100)

    price = _stripe_post(
        "prices",
        {
            "product": product_id,
            "currency": "rub",
            "unit_amount": amount_in_kopecks,
        },
    )
    return price["id"]


def get_or_create_stripe_price(item):
    """Возвращает Stripe Price ID, создавая продукт и цену при необходимости."""

    if item.stripe_price_id:
        return item.stripe_price_id

    product_id = item.stripe_product_id

    if not product_id:
        product_id = create_stripe_product(item)
        item.stripe_product_id = product_id

    price_id = create_stripe_price(product_id, item.price)

    item.stripe_price_id = price_id
    item.save(update_fields=["stripe_product_id", "stripe_price_id"])

    return price_id


def create_checkout_session(payment, item, success_url, cancel_url):
    """Создаёт Stripe Checkout Session для оплаты курса или урока."""

    price_id = get_or_create_stripe_price(item)

    session = _stripe_post(
        "checkout/sessions",
        {
            "mode": "payment",
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": 1,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "client_reference_id": str(payment.pk),
            "metadata[payment_id]": str(payment.pk),
        },
    )

    payment.session_id = session["id"]
    payment.link = session["url"]
    payment.save(update_fields=["session_id", "link"])

    return session


def retrieve_checkout_session(session_id):
    """Получает актуальную Checkout Session из Stripe."""

    if not settings.STRIPE_SECRET_KEY:
        raise ValueError("Не настроен STRIPE_SECRET_KEY")

    response = requests.get(
        f"{STRIPE_API_URL}/checkout/sessions/{session_id}",
        auth=(settings.STRIPE_SECRET_KEY, ""),
        timeout=15,
    )
    response.raise_for_status()

    return response.json()
