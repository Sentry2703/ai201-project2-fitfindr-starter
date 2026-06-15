"""
Tests for search_listings() in tools.py.

Covers the three verification cases from planning.md:
  1. Broad query with no filters returns multiple results
  2. Size + price filters narrow results
  3. Query with no matching keywords returns an empty list

Run with: python3 -m pytest tests/test_tools.py -v -s
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools import search_listings


def test_broad_query_returns_multiple_results():
    results = search_listings("vintage jeans")
    print(f"\n  query='vintage jeans' → {len(results)} results")
    for r in results[:3]:
        print(f"    [{r['id']}] {r['title']} — ${r['price']}")
    assert len(results) > 1, "Expected multiple results for a broad query"


def test_returns_list_of_dicts_with_expected_fields():
    results = search_listings("jacket")
    print(f"\n  query='jacket' → {len(results)} results")
    required_fields = {"id", "title", "description", "category", "style_tags",
                       "size", "condition", "price", "colors", "brand", "platform"}
    for listing in results:
        missing = required_fields - listing.keys()
        print(f"    [{listing['id']}] fields present={sorted(listing.keys())}")
        assert not missing, f"Listing {listing['id']} missing fields: {missing}"
    assert len(results) > 0


def test_price_filter_excludes_expensive_items():
    max_price = 20.0
    results = search_listings("shirt", max_price=max_price)
    print(f"\n  query='shirt' max_price=${max_price} → {len(results)} results")
    for r in results:
        print(f"    [{r['id']}] {r['title']} — ${r['price']} ({'OK' if r['price'] <= max_price else 'FAIL'})")
        assert r["price"] <= max_price, (
            f"Listing ${r['price']} exceeds max_price ${max_price}"
        )


def test_size_filter_narrows_results():
    results_all = search_listings("jeans")
    results_sized = search_listings("jeans", size="S")
    print(f"\n  query='jeans' unfiltered={len(results_all)}, size='S' filtered={len(results_sized)}")
    for r in results_sized:
        print(f"    [{r['id']}] size='{r['size']}' — {r['title']}")
        assert "s" in r["size"].lower(), (
            f"Listing size '{r['size']}' does not match filter 'S'"
        )
    assert len(results_sized) <= len(results_all)


def test_size_filter_is_case_insensitive():
    results_upper = search_listings("jeans", size="M")
    results_lower = search_listings("jeans", size="m")
    ids_upper = [l["id"] for l in results_upper]
    ids_lower = [l["id"] for l in results_lower]
    print(f"\n  size='M' ids: {ids_upper}")
    print(f"  size='m' ids: {ids_lower}")
    assert ids_upper == ids_lower, "Case-insensitive size filter returned different results"


def test_combined_size_and_price_filter():
    results = search_listings("top", size="M", max_price=30.0)
    print(f"\n  query='top' size='M' max_price=$30 → {len(results)} results")
    for r in results:
        price_ok = r["price"] <= 30.0
        size_ok = "m" in r["size"].lower()
        print(f"    [{r['id']}] size='{r['size']}' price=${r['price']} price_ok={price_ok} size_ok={size_ok}")
        assert price_ok, f"Price ${r['price']} exceeds $30"
        assert size_ok, f"Size '{r['size']}' does not match 'M'"


def test_no_matching_keywords_returns_empty_list():
    query = "xyznonexistentkeyword12345"
    results = search_listings(query)
    print(f"\n  query='{query}' → {len(results)} results (expected 0)")
    assert results == [], f"Expected empty list, got {len(results)} results"


def test_results_sorted_by_relevance():
    results = search_listings("vintage denim jacket")
    print(f"\n  query='vintage denim jacket' → {len(results)} results")
    for r in results[:5]:
        tags = ", ".join(r.get("style_tags", []))
        print(f"    [{r['id']}] {r['title']} | tags: {tags}")
    if len(results) < 2:
        print("  (fewer than 2 results — skipping sort check)")
        return
    first_text = " ".join([
        results[0]["title"],
        results[0]["description"],
        results[0]["category"],
        " ".join(results[0].get("style_tags", [])),
    ]).lower()
    matched = [kw for kw in ["vintage", "denim", "jacket"] if kw in first_text]
    print(f"  top result matched keywords: {matched}")
    assert matched, f"Top result '{results[0]['title']}' matched none of the query keywords"
