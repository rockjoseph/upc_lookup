import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.excel import excel_service  # noqa: E402
from app.models import Product  # noqa: E402


def test_create_session_and_new_workbook_has_headers():
    session_id = excel_service.create_session()
    rows = excel_service.get_rows(session_id)
    assert rows == []


def test_upsert_appends_new_row_then_updates_in_place():
    session_id = excel_service.create_session()
    product = Product(
        sku="123456",
        name="Japanese Cherry Blossom Body Cream",
        original_price=16.50,
        sale_price=9.90,
        promo_deal="Buy 3, Get 1 Free",
        stock_status="InStock",
        url="https://www.bathandbodyworks.com/p/example",
    )

    rows = excel_service.upsert_product(session_id, product)
    assert len(rows) == 1
    assert rows[0].sku == "123456"
    assert rows[0].sale_price == 9.90

    # Update the same product (matched by SKU) -- should update in place,
    # not append a second row.
    product.sale_price = 7.50
    rows = excel_service.upsert_product(session_id, product)
    assert len(rows) == 1
    assert rows[0].sale_price == 7.50


def test_upsert_matches_by_name_when_sku_missing():
    session_id = excel_service.create_session()
    p1 = Product(
        sku=None,
        name="Vanilla Bean Noel Fine Fragrance Mist",
        original_price=14.50,
        sale_price=14.50,
        url="https://www.bathandbodyworks.com/p/example-2",
    )
    excel_service.upsert_product(session_id, p1)

    p2 = Product(
        sku=None,
        name="Vanilla Bean Noel Fine Fragrance Mist",
        original_price=14.50,
        sale_price=8.99,
        promo_deal="40% Off",
        url="https://www.bathandbodyworks.com/p/example-2",
    )
    rows = excel_service.upsert_product(session_id, p2)
    assert len(rows) == 1
    assert rows[0].sale_price == 8.99
    assert rows[0].promo_deal == "40% Off"
