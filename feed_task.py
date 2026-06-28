from datetime import datetime
from decimal import Decimal
import xml.etree.ElementTree as ET


CATEGORIES = [
    {
        "id": 1,
        "name": "Чай",
        "is_active": True,
    },
    {
        "id": 2,
        "name": "Посуда",
        "is_active": True,
    },
    {
        "id": 3,
        "name": "Подарочные наборы",
        "is_active": False,
    },
]


PRODUCTS = [
    {
        "id": 101,
        "name": 'Чай "Лес & травы" <сбор №1>',
        "slug": "les-i-travy",
        "category_id": 1,
        "price": "490.00",
        "old_price": "590.00",
        "stock": 12,
        "description": "Вкус: мята & чабрец > классический чай",
        "image_url": "https://example.test/media/tea-101.jpg",
        "is_active": True,
    },
    {
        "id": 102,
        "name": "Чайник стеклянный",
        "slug": "glass-teapot",
        "category_id": 2,
        "price": "1500.00",
        "old_price": "1400.00",
        "stock": 0,
        "description": "Стеклянный чайник объёмом 800 мл",
        "image_url": "https://example.test/media/teapot-102.jpg",
        "is_active": True,
    },
    {
        "id": 103,
        "name": "Скрытый товар",
        "slug": "hidden-product",
        "category_id": 1,
        "price": "350.00",
        "old_price": None,
        "stock": 5,
        "description": "Товар отключён администратором",
        "image_url": "https://example.test/media/product-103.jpg",
        "is_active": False,
    },
    {
        "id": 104,
        "name": "Пробник чая",
        "slug": "tea-sample",
        "category_id": 1,
        "price": "0.00",
        "old_price": None,
        "stock": 30,
        "description": "Бесплатный пробник",
        "image_url": "https://example.test/media/product-104.jpg",
        "is_active": True,
    },
    {
        "id": 105,
        "name": "Чашка фарфоровая",
        "slug": "porcelain-cup",
        "category_id": 2,
        "price": "700.00",
        "old_price": "900.00",
        "stock": 4,
        "description": "Фарфоровая чашка",
        "image_url": None,
        "is_active": True,
    },
    {
        "id": 106,
        "name": "Подарочный набор",
        "slug": "gift-set",
        "category_id": 3,
        "price": "2500.00",
        "old_price": "3000.00",
        "stock": 2,
        "description": "Товар находится в неактивной категории",
        "image_url": "https://example.test/media/product-106.jpg",
        "is_active": True,
    },
    {
        "id": 107,
        "name": "Чай улун молочный",
        "slug": "milk-oolong",
        "category_id": 1,
        "price": "700.50",
        "old_price": None,
        "stock": 3,
        "description": "",
        "image_url": "https://example.test/media/product-107.jpg",
        "is_active": True,
    },
]


def valid_image(url):
    return bool(url) and url.startswith(("http://", "https://"))


def valid_product(product, categories_map):
    category = categories_map.get(product["category_id"])

    return (
        product["is_active"]
        and category
        and category["is_active"]
        and product["name"]
        and Decimal(product["price"]) > 0
        and valid_image(product["image_url"])
    )


def build_yml(products, categories, generated_at):
    categories_map = {c["id"]: c for c in categories}

    valid_products = [p for p in products if valid_product(p, categories_map)]

    valid_products.sort(key=lambda x: x["id"])

    used_categories = sorted({p["category_id"] for p in valid_products})

    root = ET.Element(
        "yml_catalog",
        {"date": generated_at.strftime("%Y-%m-%d %H:%M")},
    )

    shop = ET.SubElement(root, "shop")

    ET.SubElement(shop, "name").text = "Test Shop"
    ET.SubElement(shop, "company").text = "Test Company"
    ET.SubElement(shop, "url").text = "https://example.test"

    currencies = ET.SubElement(shop, "currencies")
    ET.SubElement(currencies, "currency", {"id": "RUB", "rate": "1"})

    cats = ET.SubElement(shop, "categories")
    for cid in used_categories:
        c = categories_map[cid]
        el = ET.SubElement(cats, "category", {"id": str(c["id"])})
        el.text = c["name"]

    offers = ET.SubElement(shop, "offers")

    for p in valid_products:
        offer = ET.SubElement(
            offers,
            "offer",
            {
                "id": str(p["id"]),
                "available": "true" if p["stock"] > 0 else "false",
            },
        )

        ET.SubElement(
            offer,
            "url",
        ).text = f"https://example.test/products/{p['slug']}/"

        ET.SubElement(
            offer,
            "price",
        ).text = f'{Decimal(p["price"]):.2f}'

        if p["old_price"] and Decimal(p["old_price"]) > Decimal(p["price"]):
            ET.SubElement(
                offer,
                "oldprice",
            ).text = f'{Decimal(p["old_price"]):.2f}'

        ET.SubElement(offer, "currencyId").text = "RUB"
        ET.SubElement(offer, "categoryId").text = str(p["category_id"])
        ET.SubElement(offer, "picture").text = p["image_url"]
        ET.SubElement(offer, "name").text = p["name"]

        if p["description"]:
            ET.SubElement(offer, "description").text = p["description"]

    ET.indent(root, space="    ")

    return ET.tostring(
        root,
        encoding="utf-8",
        xml_declaration=True,
    ).decode("utf-8")


if __name__ == "__main__":
    result = build_yml(
        PRODUCTS,
        CATEGORIES,
        datetime(2026, 6, 18, 12, 0),
    )

    print(result)