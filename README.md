# restaurant-endpoint-template

A clean, forkable FastAPI template for making a local business queryable by AI agents.

This template is intentionally simple:
- JSON files for business data (`data/*.json`)
- no database required
- deployable in ~15 minutes

## What this provides

### A2A discovery
- `GET /agent.json`
- `GET /.well-known/agent.json`

### Human-readable capability doc
- `GET /skill.md`

### Business data endpoints
- `GET /menu`
- `GET /hours`

### Natural-language query endpoint (no LLM)
- `POST /ask`

### MCP discovery (both proposals)
- `GET /.well-known/mcp/server-card.json` (SEP-1649)
- `GET /.well-known/mcp.json` (SEP-1960)

> MCP `.well-known` discovery is pre-standard as of March 2026 (two competing proposals). This template supports both paths and can be updated once a final standard is published.

## Project structure

```text
restaurant-endpoint-template/
├── README.md
├── LICENSE
├── app.py
├── requirements.txt
├── data/
│   ├── restaurant.json
│   ├── menu.json
│   └── hours.json
├── Dockerfile
├── .env.example
└── tests/
    └── test_endpoints.py
```

## Quick start (local)

```bash
git clone https://github.com/archedark-publishing/restaurant-endpoint-template.git
cd restaurant-endpoint-template
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Server runs at `http://127.0.0.1:8000`.

## Configure your business data

Edit these files:
- `data/restaurant.json` — name, description, location, URL, contact
- `data/menu.json` — sections, items, prices, tags (`vegan`, `vegetarian`, `gluten-free`, etc.)
- `data/hours.json` — weekly hours, closures, notes

Default sample data uses **The Corner Café**.

## `/ask` behavior

`POST /ask` accepts:

```json
{
  "question": "do you have vegan options?"
}
```

Routing logic (keyword-based, zero API cost):
- `vegan / vegetarian / gluten` → dietary-tag filtering
- `hours / open / close / when` → hours response
- `price / cost / how much` → priced item list
- otherwise → menu item name search
- no matches → fallback guidance

## Run tests

```bash
pytest
```

## Docker

```bash
docker build -t restaurant-endpoint-template .
docker run --rm -p 8000:8000 restaurant-endpoint-template
```
