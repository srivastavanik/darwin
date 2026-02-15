# DARWIN Runbook

## Services
- API service: `python -m scripts.run_api` (FastAPI + websocket host lifecycle)
- Dashboard: `cd dashboard && npm run dev`

## Local Production-Like Start
- Copy env template: `cp .env.example .env`
- Fill provider keys and optional Supabase credentials.
- Start stack:
  - `docker compose up --build`
- Endpoints:
  - API health: `http://localhost:8000/health`
  - Dashboard: `http://localhost:3000`
  - WebSocket: `ws://localhost:8765/ws/<game_id>`

## Operational Checks
- Health check returns status `ok`.
- Start game from dashboard control bar.
- Confirm round streaming and final game state.
- Open replay link by game id.

## Common Failures
- `401` websocket close: check `MARKOV_WS_TOKEN` and `NEXT_PUBLIC_WS_TOKEN`.
- No live rounds: ensure API service is running and websocket port `8765` is reachable.
- LLM fallback spam: verify provider model IDs and API keys.
- Replay missing: verify `data/games/<game_id>/game.json` exists.

## Safe Restart
- API restart does not delete artifacts in `data/games`.
- If cancelling a run, use `POST /api/games/{id}/cancel` or dashboard cancel button.

## Rollback
- Use previous container image tag or previous git commit.
- Keep `data/` volume mounted so historical runs persist across rollback.
