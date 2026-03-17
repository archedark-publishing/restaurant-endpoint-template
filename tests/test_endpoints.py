from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app

client = TestClient(app)


def test_agent_card_paths_work():
    direct = client.get("/agent.json")
    well_known = client.get("/.well-known/agent.json")

    assert direct.status_code == 200
    assert well_known.status_code == 200
    assert direct.json() == well_known.json()
    assert "skills" in direct.json()


def test_agent_card_uses_base_url_from_env(monkeypatch):
    monkeypatch.setenv("BASE_URL", "https://restaurant.example")

    direct = client.get("/agent.json")
    well_known = client.get("/.well-known/agent.json")

    assert direct.status_code == 200
    assert well_known.status_code == 200
    assert direct.json()["url"] == "https://restaurant.example"
    assert well_known.json()["url"] == "https://restaurant.example"


def test_skill_md_returns_markdown():
    response = client.get("/skill.md")

    assert response.status_code == 200
    assert "text/markdown" in response.headers["content-type"]
    assert "Restaurant Endpoint Capabilities" in response.text


def test_menu_endpoint_reads_json_file():
    response = client.get("/menu")

    assert response.status_code == 200
    body = response.json()
    assert "sections" in body
    assert body["sections"]


def test_hours_endpoint_reads_json_file():
    response = client.get("/hours")

    assert response.status_code == 200
    body = response.json()
    assert "weekly" in body
    assert "special_closures" in body


def test_ask_vegan_returns_matches():
    response = client.post("/ask", json={"question": "do you have vegan options?"})

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "dietary"
    assert body["matches"]


def test_ask_open_returns_hours_data():
    response = client.post("/ask", json={"question": "what time do you open?"})

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "hours"
    assert "hours" in body
    assert "weekly" in body["hours"]


def test_mcp_paths_return_same_content():
    first = client.get("/.well-known/mcp/server-card.json")
    second = client.get("/.well-known/mcp.json")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
