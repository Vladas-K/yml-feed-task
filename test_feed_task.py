import xml.etree.ElementTree as ET
from datetime import datetime

import pytest

from feed_task import (
    build_yml,
    PRODUCTS,
    CATEGORIES,
)


@pytest.fixture
def root():
    xml = build_yml(
        PRODUCTS,
        CATEGORIES,
        datetime(2026, 6, 18, 12, 0),
    )

    return ET.fromstring(xml)


def test_build_yml_returns_valid_xml():
    xml = build_yml(
        PRODUCTS,
        CATEGORIES,
        datetime(2026, 6, 18, 12, 0),
    )

    root = ET.fromstring(xml)

    assert root.tag == "yml_catalog"


def test_xml_is_valid(root):
    assert root.tag == "yml_catalog"
    assert root.attrib["date"] == "2026-06-18 12:00"


def test_only_valid_products_are_exported(root):
    offer_ids = [
        int(offer.attrib["id"])
        for offer in root.findall(".//offer")
    ]

    assert offer_ids == [101, 102, 107]


def test_categories_are_unique_and_sorted(root):
    category_ids = [
        int(category.attrib["id"])
        for category in root.findall(".//category")
    ]

    assert category_ids == [1, 2]


def test_available_attribute(root):
    offers = {
        offer.attrib["id"]: offer.attrib["available"]
        for offer in root.findall(".//offer")
    }

    assert offers == {
        "101": "true",
        "102": "false",
        "107": "true",
    }


def test_prices_are_formatted_correctly(root):
    prices = {
        offer.attrib["id"]: offer.find("price").text
        for offer in root.findall(".//offer")
    }

    assert prices == {
        "101": "490.00",
        "102": "1500.00",
        "107": "700.50",
    }


def test_oldprice_is_added_only_when_valid(root):
    offer_101 = root.find(".//offer[@id='101']")
    offer_102 = root.find(".//offer[@id='102']")
    offer_107 = root.find(".//offer[@id='107']")

    assert offer_101.find("oldprice").text == "590.00"
    assert offer_102.find("oldprice") is None
    assert offer_107.find("oldprice") is None


def test_empty_description_is_not_exported(root):
    offer_107 = root.find(".//offer[@id='107']")

    assert offer_107.find("description") is None


def test_special_characters_are_preserved(root):
    name = root.find(".//offer[@id='101']/name")
    description = root.find(".//offer[@id='101']/description")

    assert name.text == 'Чай "Лес & травы" <сбор №1>'
    assert description.text == "Вкус: мята & чабрец > классический чай"
    

def test_description_is_exported(root):
    offer_101 = root.find(".//offer[@id='101']")

    assert (
        offer_101.find("description").text
        == "Вкус: мята & чабрец > классический чай"
    )
