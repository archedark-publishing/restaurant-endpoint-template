# Restaurant Endpoint Capabilities

This endpoint exposes the restaurant's core public information for AI agents and tools.

## Available capabilities

- **Menu lookup** (`GET /menu`)
  - Returns the current menu from `data/menu.json`
  - Includes sections, item descriptions, pricing, and dietary tags

- **Hours lookup** (`GET /hours`)
  - Returns weekly business hours and special closures from `data/hours.json`

- **Natural language Q&A** (`POST /ask`)
  - Handles basic menu and hours questions with keyword matching
  - Supports dietary filters (`vegan`, `vegetarian`, `gluten`)
  - Supports hours questions (`open`, `close`, `when`)
  - Supports price questions (`price`, `cost`, `how much`)
  - Falls back to menu item name search

- **A2A discovery**
  - `GET /agent.json`
  - `GET /.well-known/agent.json`

- **MCP discovery**
  - `GET /.well-known/mcp/server-card.json` (SEP-1649)
  - `GET /.well-known/mcp.json` (SEP-1960)
