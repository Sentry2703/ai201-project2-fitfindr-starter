# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.

---

## Tool Inventory

### `search_listings(description: str, size: str | None, max_price: float | None) -> list[dict]`
Loads the full listings dataset and returns items that match the query. Filters first by `max_price` (inclusive) and `size` (case-insensitive substring match, so `"M"` matches `"S/M"`), then scores each remaining item by counting how many words from `description` appear anywhere in its title, description, category, style tags, colors, and brand. Items with a score of zero are dropped. The remaining items are returned sorted by score, highest first. Returns an empty list if nothing matches — never raises.

### `suggest_outfit(new_item: dict, wardrobe: dict) -> str`
Given a listing dict and a wardrobe dict (with an `items` key), calls the Groq LLM to suggest 1–2 outfit combinations. If `wardrobe["items"]` is empty, the prompt asks for general styling advice for the item. If it is populated, the prompt lists every wardrobe piece by name and color and asks the LLM to suggest specific combinations using named pieces. Returns the LLM response as a non-empty string in both cases.

### `create_fit_card(outfit: str, new_item: dict) -> str`
Generates a 2–4 sentence OOTD-style caption. Guards against an empty or whitespace-only `outfit` string — returns a descriptive error message immediately without calling the LLM. Otherwise, builds a prompt with the item's title, price, and platform alongside the outfit description, and instructs the LLM to write a casual, authentic caption that mentions the item name, price, and platform each exactly once. Uses `temperature=1.0` for varied output. Returns the LLM response as a string.

---

## How the Planning Loop Works

`run_agent()` in `agent.py` executes a fixed, linear pipeline with one conditional exit:

1. **Parse** — The raw query is sent to the LLM via `_parse_query()`, which returns a JSON object with `description` (str), `size` (str or null), and `max_price` (float or null). Using the LLM here handles freeform phrasing — a user can say "under $30" or "nothing over thirty bucks" and both resolve correctly.

2. **Search** — `search_listings()` is called with the parsed parameters. If the result list is empty, `session["error"]` is set to a helpful message and the function returns immediately. No further tools are called. This is the only conditional branch in the loop.

3. **Select** — The first item in the results list (highest relevance score) is chosen as `session["selected_item"]`.

4. **Suggest** — `suggest_outfit()` is called unconditionally with the selected item and the user's wardrobe.

5. **Card** — `create_fit_card()` is called unconditionally with the outfit suggestion and selected item.

6. **Return** — The completed session dict is returned to the caller.

---

## State Management

All state for a single interaction lives in a session dict initialized by `_new_session()`:

| Key | Type | Set in step | Passed to |
|-----|------|-------------|-----------|
| `query` | str | init | `_parse_query` |
| `parsed` | dict | Step 1 | `search_listings` |
| `search_results` | list[dict] | Step 2 | early-exit check |
| `selected_item` | dict | Step 3 | `suggest_outfit`, `create_fit_card` |
| `wardrobe` | dict | init | `suggest_outfit` |
| `outfit_suggestion` | str | Step 4 | `create_fit_card` |
| `fit_card` | str | Step 5 | UI / caller |
| `error` | str \| None | Step 2 (on failure) | caller |

Each tool receives only what it needs — no tool reads from the session dict directly. The agent passes values explicitly as function arguments and writes results back into the session after each call.

---

## Error Handling

**`search_listings`** — Returns an empty list when no listings match the filters or keywords. The agent treats this as the terminal failure case: `session["error"]` is set to `"No listings matched your search. Try broadening your description, adjusting the size, or raising the price limit."` and the agent returns without calling the remaining tools. Confirmed in testing: the query `"designer ballgown size XXS under $5"` returns an empty list and triggers this path correctly.

**`suggest_outfit`** — An empty wardrobe is not treated as an error; the tool branches on `wardrobe["items"]` being empty and switches to a general-styling prompt instead. No exception is raised and the return value is always a non-empty string. Confirmed in testing: calling with `get_empty_wardrobe()` returns styling advice rather than an empty string or exception.

**`create_fit_card`** — An empty or whitespace-only `outfit` string returns the message `"Error: outfit description is missing — cannot generate a fit card."` without calling the LLM. In practice this should not happen in a normal pipeline run (since `suggest_outfit` always returns a non-empty string), but the guard ensures the tool is safe to call in isolation during testing.

---

## Spec Reflection

**One way the spec helped:** The planning.md spec required documenting the failure mode for each tool before writing any code. This directly shaped the `search_listings` implementation — because the spec explicitly said "return an empty list, do NOT raise", the scoring and filtering logic was written to swallow zero-match cases naturally rather than relying on the caller to catch exceptions.

**One way implementation diverged from the spec:** The planning.md spec described a more dynamic planning loop where the LLM "decides which tool to call next" at each step. In practice, the tool call order is always the same (search → suggest → card) and the only real decision is whether to exit early after an empty search. A fully dynamic loop would add complexity without any benefit for a three-tool linear pipeline, so the implementation uses a fixed sequence with a single conditional exit instead.

---

## AI Usage

**Instance 1 — Implementing `search_listings`:** Claude was directed to implement `search_listings()` using the Tool 1 spec from planning.md and the `load_listings()` signature. The initial output scored keywords against title and description only. This was revised to also score against `style_tags`, `colors`, and `brand` — without those fields, a query like `"vintage denim"` would miss items whose titles were generic but whose style tags explicitly said `"vintage"` or `"denim"`.

**Instance 2 — Query parsing approach:** Claude was directed to use the LLM for query parsing in `_parse_query()`. The first generated version returned the parsed result as plain text and used string splitting to extract values. This was overridden to instead prompt the LLM for raw JSON and parse it with `json.loads()`, with a strip for accidental markdown fences. The structured output approach is more reliable with freeform input — natural language price expressions like "nothing over fifty" or "cheap, under $25" parse correctly into `max_price` without custom regex.
