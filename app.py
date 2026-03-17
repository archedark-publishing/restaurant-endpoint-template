from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse, PlainTextResponse

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SKILL_FILE = BASE_DIR / "skill.md"

app = FastAPI(
    title="Restaurant Endpoint Template",
    description="Self-hosted A2A + MCP endpoint template for local businesses.",
    version="0.1.0",
)


class AskRequest(BaseModel):
    question: str


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_restaurant() -> dict[str, Any]:
    return _load_json(DATA_DIR / "restaurant.json")


def load_menu() -> dict[str, Any]:
    return _load_json(DATA_DIR / "menu.json")


def load_hours() -> dict[str, Any]:
    return _load_json(DATA_DIR / "hours.json")


def flatten_menu_items(menu: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for section in menu.get("sections", []):
        section_name = section.get("name")
        for item in section.get("items", []):
            normalized = dict(item)
            normalized["section"] = section_name
            normalized.setdefault("tags", [])
            items.append(normalized)
    return items


def build_agent_card(restaurant: dict[str, Any]) -> dict[str, Any]:
    base_url = restaurant.get("url", "")
    return {
        "name": restaurant.get("name", "Restaurant"),
        "description": restaurant.get("description", ""),
        "url": base_url,
        "version": "1.0.0",
        "tags": restaurant.get("tags", []),
        "contact": restaurant.get("contact", {}),
        "skills": [
            {
                "id": "menu",
                "name": "Menu Lookup",
                "description": "Returns menu sections and items, including dietary tags.",
                "input": {"type": "none"},
                "output": {"type": "application/json", "path": "/menu"},
            },
            {
                "id": "hours",
                "name": "Hours Lookup",
                "description": "Returns weekly hours and special closures.",
                "input": {"type": "none"},
                "output": {"type": "application/json", "path": "/hours"},
            },
        ],
    }


def build_mcp_server_card(restaurant: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": restaurant.get("name", "Restaurant MCP"),
        "description": "MCP discovery card for restaurant menu and hours endpoints.",
        "version": "1.0.0",
        "protocol": "mcp",
        "capabilities": {
            "tools": [
                {
                    "name": "menu",
                    "description": "Retrieve current menu with dietary tags.",
                    "endpoint": "/menu",
                },
                {
                    "name": "hours",
                    "description": "Retrieve opening hours and special closures.",
                    "endpoint": "/hours",
                },
                {
                    "name": "ask",
                    "description": "Ask natural-language questions about menu and hours.",
                    "endpoint": "/ask",
                },
            ]
        },
    }


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def _search_items_by_name(items: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    tokens = [token for token in query.split() if token]
    if not tokens:
        return []

    results = []
    for item in items:
        name = item.get("name", "").lower()
        if any(token in name for token in tokens):
            results.append(item)
    return results


def answer_question(question: str) -> dict[str, Any]:
    menu = load_menu()
    hours = load_hours()
    items = flatten_menu_items(menu)

    normalized_question = question.lower().strip()

    dietary_map = {
        "vegan": ["vegan"],
        "vegetarian": ["vegetarian"],
        "gluten": ["gluten-free", "gluten_friendly", "gluten"],
    }

    for keyword, tag_candidates in dietary_map.items():
        if keyword in normalized_question:
            matches = [
                item
                for item in items
                if any(tag in [t.lower() for t in item.get("tags", [])] for tag in tag_candidates)
            ]
            if matches:
                return {
                    "intent": "dietary",
                    "query": keyword,
                    "matches": matches,
                    "message": f"Found {len(matches)} {keyword} option(s).",
                }

    if _contains_any(normalized_question, ["hours", "open", "close", "when"]):
        return {
            "intent": "hours",
            "message": "Here are our current opening hours and special closures.",
            "hours": hours,
        }

    if _contains_any(normalized_question, ["price", "cost", "how much"]):
        matched_items = _search_items_by_name(items, normalized_question)
        if not matched_items:
            matched_items = items

        return {
            "intent": "price",
            "message": "Here are menu items with prices.",
            "matches": [
                {
                    "name": item.get("name"),
                    "price": item.get("price"),
                    "section": item.get("section"),
                }
                for item in matched_items
            ],
        }

    name_matches = _search_items_by_name(items, normalized_question)
    if name_matches:
        return {
            "intent": "menu_search",
            "message": "Here are matching menu items.",
            "matches": name_matches,
        }

    return {
        "intent": "fallback",
        "message": "I can help with menu items, hours, and dietary options.",
    }


@app.get("/agent.json")
def get_agent_card() -> dict[str, Any]:
    return build_agent_card(load_restaurant())


@app.get("/.well-known/agent.json")
def get_agent_card_well_known() -> dict[str, Any]:
    return build_agent_card(load_restaurant())


@app.get("/skill.md")
def get_skill_md() -> PlainTextResponse:
    content = SKILL_FILE.read_text(encoding="utf-8")
    return PlainTextResponse(content, media_type="text/markdown")


@app.get("/menu")
def get_menu() -> dict[str, Any]:
    return load_menu()


@app.get("/hours")
def get_hours() -> dict[str, Any]:
    return load_hours()


@app.post("/ask")
def ask(request: AskRequest) -> JSONResponse:
    response = answer_question(request.question)
    return JSONResponse(response)


@app.get("/.well-known/mcp/server-card.json")
def get_mcp_server_card() -> dict[str, Any]:
    return build_mcp_server_card(load_restaurant())


@app.get("/.well-known/mcp.json")
def get_mcp_legacy_card() -> dict[str, Any]:
    return build_mcp_server_card(load_restaurant())
