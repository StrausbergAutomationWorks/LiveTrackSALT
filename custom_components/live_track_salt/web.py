"""Serves this integration's marker pictures from its own view (the library's aircraft, our ring).

! WHY ITS OWN VIEW: the library leaves the view and the URL to each consumer (picture_query), and this
integration cannot import Live Track Aircraft's. The URL base is ours, so the two caches never mix.
! An <img> cannot send a token, so the view is unauthenticated, as Live Track Aircraft's is: the
pictures are silhouettes with no user data in them.
"""
from __future__ import annotations

import logging

from aiohttp import web

from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from saw_livetrack import aircraft_icons as lib

from . import icons

_LOGGER = logging.getLogger(__name__)


class EnforcementIconView(HomeAssistantView):
    """One aircraft silhouette, unrotated; ?d=1 adds the detection ring."""

    url = icons.URL_BASE + "/{key}/fixed.svg"
    name = "api:live_track_salt:icon"
    requires_auth = False

    async def get(self, request: web.Request, key: str) -> web.Response:
        # ! UNTRUSTED input: valid_key() keeps the key to [a-z0-9]; tone falls back to default;
        # weight is clamped in render(); a mangled l= or d= draws nothing extra.
        tone = request.query.get("t", "default")
        try:
            weight = float(request.query.get("w", lib.DEFAULT_WEIGHT))
        except (TypeError, ValueError):
            weight = lib.DEFAULT_WEIGHT
        lights = lib.lights_from_query(request.query.get("l"))
        detected = request.query.get("d") == "1"
        try:
            svg = await request.app["hass"].async_add_executor_job(
                icons.render, key, tone, weight, lights, detected)
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Could not render %s", key)
            return web.Response(status=500, text="render failed")
        if svg is None:
            return web.Response(status=404, text="unknown icon")
        return web.Response(body=svg.encode("utf-8"), content_type="image/svg+xml",
                            headers={"Cache-Control": "public, max-age=86400, immutable"})


def register(hass: HomeAssistant) -> None:
    hass.http.register_view(EnforcementIconView())
