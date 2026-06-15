"""
Tests for suggest_outfit() in tools.py.

Run with: python3 -m pytest tests/test_suggest_outfit.py -v -s
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools import suggest_outfit
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe, load_listings


DENIM_JACKET = {
    "id": "lst_007",
    "title": "Denim Jacket — Light Wash, Cropped",
    "category": "outerwear",
    "style_tags": ["denim", "vintage", "classic", "streetwear"],
    "size": "S",
    "condition": "good",
    "price": 42.0,
    "colors": ["light blue", "white"],
    "brand": "Wrangler",
    "platform": "depop",
    "description": "A cropped light-wash denim jacket in great condition.",
}


def test_returns_nonempty_string_with_wardrobe():
    wardrobe = get_example_wardrobe()
    result = suggest_outfit(DENIM_JACKET, wardrobe)
    print(f"\n  suggest_outfit (with wardrobe):\n{result}\n")
    assert isinstance(result, str), "Expected a string return value"
    assert result.strip(), "Expected a non-empty string"


def test_returns_nonempty_string_with_empty_wardrobe():
    wardrobe = get_empty_wardrobe()
    result = suggest_outfit(DENIM_JACKET, wardrobe)
    print(f"\n  suggest_outfit (empty wardrobe):\n{result}\n")
    assert isinstance(result, str), "Expected a string return value"
    assert result.strip(), "Expected non-empty general styling advice, not an empty string"


def test_empty_wardrobe_does_not_raise():
    wardrobe = get_empty_wardrobe()
    try:
        result = suggest_outfit(DENIM_JACKET, wardrobe)
        print(f"\n  No exception raised. Response length: {len(result)} chars")
    except Exception as e:
        assert False, f"suggest_outfit raised an unexpected exception: {e}"


def test_wardrobe_response_references_item():
    wardrobe = get_example_wardrobe()
    result = suggest_outfit(DENIM_JACKET, wardrobe)
    print(f"\n  Checking response mentions item keywords...")
    item_keywords = ["denim", "jacket", "cropped", "wrangler", "light"]
    matched = [kw for kw in item_keywords if kw.lower() in result.lower()]
    print(f"  Matched keywords in response: {matched}")
    assert matched, (
        f"Expected response to reference the item in some way, "
        f"but none of {item_keywords} appeared in:\n{result}"
    )


def test_wardrobe_response_references_wardrobe_pieces():
    wardrobe = get_example_wardrobe()
    result = suggest_outfit(DENIM_JACKET, wardrobe)
    wardrobe_names = [item["name"].lower() for item in wardrobe["items"]]
    # Check at least one wardrobe item keyword appears in the response
    all_wardrobe_words = set(
        word for name in wardrobe_names for word in name.split()
        if len(word) > 3  # skip short filler words
    )
    matched = [w for w in all_wardrobe_words if w in result.lower()]
    print(f"\n  Wardrobe words found in response: {matched[:5]}")
    assert matched, (
        "Expected response to reference at least one piece from the wardrobe"
    )
