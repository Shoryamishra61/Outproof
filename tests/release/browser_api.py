"""Controlled E2E server. Never deploy this synthetic client/provider wrapper."""

import json

from app.main import create_app


class ControlledRanker:
    async def generate(self, request: dict) -> str:
        plan_id = request["format"]["properties"]["selected_plan_id"]["enum"][0]
        return json.dumps(
            {"selected_plan_id": plan_id, "reason": "Selected for your soft preferences."}
        )


application = create_app(fixture_enabled=True, model=ControlledRanker())


async def app(scope: dict, receive: object, send: object) -> None:
    if scope["type"] == "http":
        # Distinct synthetic users; production uses the socket peer, never this header.
        header = dict(scope["headers"]).get(b"x-test-client", b"one")
        scope = {**scope, "client": ("fixture-" + header.decode(), 1)}
    await application(scope, receive, send)
