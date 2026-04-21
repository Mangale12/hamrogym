from django.db import migrations


PAYMENT_METHODS = [
    {
        "code": "CASH",
        "name": "Cash",
        "category": "cash",
        "provider": "",
        "sequence": 1,
        "is_digital": False,
        "supports_online": False,
        "supports_qr": False,
        "requires_reference": False,
        "is_default": True,
        "is_active": True,
        "remarks": "Physical cash settlement.",
    },
    {
        "code": "CHEQUE",
        "name": "Cheque",
        "category": "cheque",
        "provider": "Bank Cheque",
        "sequence": 2,
        "is_digital": False,
        "supports_online": False,
        "supports_qr": False,
        "requires_reference": True,
        "is_default": False,
        "is_active": True,
        "remarks": "Cheque-based payment cleared through bank.",
    },
    {
        "code": "BANK_DEPOSIT",
        "name": "Bank Deposit",
        "category": "bank",
        "provider": "Any Bank / BFI",
        "sequence": 3,
        "is_digital": False,
        "supports_online": False,
        "supports_qr": False,
        "requires_reference": True,
        "is_default": False,
        "is_active": True,
        "remarks": "Direct over-the-counter bank deposit.",
    },
    {
        "code": "BANK_TRANSFER",
        "name": "Bank Transfer",
        "category": "bank",
        "provider": "Any Bank / BFI",
        "sequence": 4,
        "is_digital": True,
        "supports_online": True,
        "supports_qr": False,
        "requires_reference": True,
        "is_default": False,
        "is_active": True,
        "remarks": "Standard inter-bank or intra-bank transfer.",
    },
    {
        "code": "MOBILE_BANKING",
        "name": "Mobile Banking",
        "category": "bank",
        "provider": "Bank Mobile Banking",
        "sequence": 5,
        "is_digital": True,
        "supports_online": True,
        "supports_qr": False,
        "requires_reference": True,
        "is_default": False,
        "is_active": True,
        "remarks": "Payment initiated from a bank mobile banking app.",
    },
    {
        "code": "INTERNET_BANKING",
        "name": "Internet Banking",
        "category": "bank",
        "provider": "Bank Internet Banking",
        "sequence": 6,
        "is_digital": True,
        "supports_online": True,
        "supports_qr": False,
        "requires_reference": True,
        "is_default": False,
        "is_active": True,
        "remarks": "Payment initiated from a bank web portal.",
    },
    {
        "code": "CONNECT_IPS",
        "name": "connectIPS",
        "category": "bank",
        "provider": "NCHL",
        "sequence": 7,
        "is_digital": True,
        "supports_online": True,
        "supports_qr": True,
        "requires_reference": True,
        "is_default": False,
        "is_active": True,
        "remarks": "Bank-account based transfers and bill payments via connectIPS.",
    },
    {
        "code": "FONEPAY_QR",
        "name": "Fonepay QR",
        "category": "qr",
        "provider": "Fonepay",
        "sequence": 8,
        "is_digital": True,
        "supports_online": True,
        "supports_qr": True,
        "requires_reference": False,
        "is_default": False,
        "is_active": True,
        "remarks": "Interoperable QR payment through the Fonepay network.",
    },
    {
        "code": "NEPALPAY_QR",
        "name": "NEPALPAY QR",
        "category": "qr",
        "provider": "NCHL / NepalPay",
        "sequence": 9,
        "is_digital": True,
        "supports_online": True,
        "supports_qr": True,
        "requires_reference": False,
        "is_default": False,
        "is_active": True,
        "remarks": "National interoperable QR standard used by banks, wallets, and connectIPS.",
    },
    {
        "code": "ESEWA",
        "name": "eSewa",
        "category": "wallet",
        "provider": "eSewa",
        "sequence": 10,
        "is_digital": True,
        "supports_online": True,
        "supports_qr": True,
        "requires_reference": False,
        "is_default": False,
        "is_active": True,
        "remarks": "Popular digital wallet in Nepal.",
    },
    {
        "code": "KHALTI",
        "name": "Khalti",
        "category": "wallet",
        "provider": "Khalti by IME",
        "sequence": 11,
        "is_digital": True,
        "supports_online": True,
        "supports_qr": True,
        "requires_reference": False,
        "is_default": False,
        "is_active": True,
        "remarks": "Digital wallet and payment platform.",
    },
    {
        "code": "IME_PAY",
        "name": "IME Pay",
        "category": "wallet",
        "provider": "IME Pay",
        "sequence": 12,
        "is_digital": True,
        "supports_online": True,
        "supports_qr": True,
        "requires_reference": False,
        "is_default": False,
        "is_active": True,
        "remarks": "Digital wallet and payment service in Nepal.",
    },
    {
        "code": "DEBIT_CARD",
        "name": "Debit Card",
        "category": "card",
        "provider": "Visa / Mastercard / NepalPay",
        "sequence": 13,
        "is_digital": True,
        "supports_online": True,
        "supports_qr": False,
        "requires_reference": True,
        "is_default": False,
        "is_active": True,
        "remarks": "Debit card payment via POS or online gateway.",
    },
    {
        "code": "CREDIT_CARD",
        "name": "Credit Card",
        "category": "card",
        "provider": "Visa / Mastercard",
        "sequence": 14,
        "is_digital": True,
        "supports_online": True,
        "supports_qr": False,
        "requires_reference": True,
        "is_default": False,
        "is_active": True,
        "remarks": "Credit card payment via POS or online gateway.",
    },
]


def seed_payment_methods(apps, schema_editor):
    PaymentMethod = apps.get_model("finance", "PaymentMethod")
    db_alias = schema_editor.connection.alias

    for item in PAYMENT_METHODS:
        code = item["code"]
        defaults = dict(item)
        defaults.pop("code", None)
        PaymentMethod.objects.using(db_alias).update_or_create(
            code=code,
            defaults=defaults,
        )


def unseed_payment_methods(apps, schema_editor):
    PaymentMethod = apps.get_model("finance", "PaymentMethod")
    db_alias = schema_editor.connection.alias
    codes = [item["code"] for item in PAYMENT_METHODS]
    PaymentMethod.objects.using(db_alias).filter(code__in=codes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("finance", "0004_paymentmethod"),
    ]

    operations = [
        migrations.RunPython(seed_payment_methods, unseed_payment_methods),
    ]
