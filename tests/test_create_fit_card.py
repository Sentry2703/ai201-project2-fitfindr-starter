"""
Tests for create_fit_card() in tools.py.

Run with: python3 -m pytest tests/test_create_fit_card.py -v -s
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools import create_fit_card


GRAPHIC_TEE = {
    "id": "lst_002",
    "title": "Vintage Band Tee — Faded Black",
    "category": "tops",
    "style_tags": ["vintage", "grunge", "graphic"],
    "size": "M",
    "condition": "good",
    "price": 18.0,
    "colors": ["black", "white"],
    "brand": None,
    "platform": "depop",
    "description": "Faded black band tee with a worn-in feel.",
}

OUTFIT = (
    "Pair the vintage band tee with baggy straight-leg jeans and white chunky sneakers "
    "for an effortless 90s grunge look."
)


def test_returns_nonempty_string():
    result = create_fit_card(OUTFIT, GRAPHIC_TEE)
    print(f"\n  create_fit_card output:\n{result}\n")
    assert isinstance(result, str), "Expected a string return value"
    assert result.strip(), "Expected a non-empty caption"


def test_caption_length_is_2_to_4_sentences():
    result = create_fit_card(OUTFIT, GRAPHIC_TEE)
    # Split on sentence-ending punctuation as a rough sentence count
    import re
    sentences = [s.strip() for s in re.split(r'[.!?]+', result) if s.strip()]
    print(f"\n  Sentence count: {len(sentences)}")
    for i, s in enumerate(sentences, 1):
        print(f"    {i}. {s}")
    assert 2 <= len(sentences) <= 5, (
        f"Expected 2–4 sentences, got {len(sentences)}: {sentences}"
    )


def test_caption_mentions_item_title():
    result = create_fit_card(OUTFIT, GRAPHIC_TEE)
    title_words = [w.lower() for w in GRAPHIC_TEE["title"].split() if len(w) > 3]
    matched = [w for w in title_words if w in result.lower()]
    print(f"\n  Title words found in caption: {matched}")
    assert matched, (
        f"Expected caption to mention the item title. "
        f"None of {title_words} found in:\n{result}"
    )


def test_caption_mentions_price():
    result = create_fit_card(OUTFIT, GRAPHIC_TEE)
    price_str = str(int(GRAPHIC_TEE["price"]))  # "18"
    print(f"\n  Checking caption mentions price '{price_str}': {'yes' if price_str in result else 'no'}")
    assert price_str in result, (
        f"Expected caption to mention the price ${GRAPHIC_TEE['price']}, got:\n{result}"
    )


def test_caption_mentions_platform():
    result = create_fit_card(OUTFIT, GRAPHIC_TEE)
    platform = GRAPHIC_TEE["platform"]
    print(f"\n  Checking caption mentions platform '{platform}': {'yes' if platform.lower() in result.lower() else 'no'}")
    assert platform.lower() in result.lower(), (
        f"Expected caption to mention '{platform}', got:\n{result}"
    )


def test_empty_outfit_returns_error_string_not_exception():
    try:
        result = create_fit_card("", GRAPHIC_TEE)
        print(f"\n  Empty outfit result: '{result}'")
        assert result.strip(), "Expected a non-empty error message string"
        assert "error" in result.lower(), (
            f"Expected an error message for empty outfit, got: '{result}'"
        )
    except Exception as e:
        assert False, f"create_fit_card raised an exception on empty outfit: {e}"


def test_whitespace_only_outfit_returns_error_string():
    try:
        result = create_fit_card("   ", GRAPHIC_TEE)
        print(f"\n  Whitespace outfit result: '{result}'")
        assert "error" in result.lower(), (
            f"Expected an error message for whitespace outfit, got: '{result}'"
        )
    except Exception as e:
        assert False, f"create_fit_card raised an exception on whitespace outfit: {e}"
