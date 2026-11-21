"""Serves this integration's marker pictures from its own view (the library's aircraft, our ring).

! WHY ITS OWN VIEW: the library leaves the view and the URL to each consumer (picture_query), and this
integration cannot import Live Track Aircraft's. The URL base is ours, so the two caches never mix.
! An <img> cannot send a token, so the icon view is unauthenticated, as Live Track Aircraft's is: the
pictures are silhouettes with no user data in them.
! The photo view (06_MAP_CONTRACT.md D4i) is SIGNED IN ONLY: the card asks it with the viewer's own sign-in.
"""
from __future__ import annotations

import logging

from aiohttp import web

from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from saw_livetrack import aircraft_icons as lib
from saw_livetrack import aircraft_photos as photos

from . import icons
from .const import PHOTO_URL_BASE

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


class SaltPhotoView(HomeAssistantView):
    """A photo of one aircraft from Planespotters.net, asked by the map card the first time its hover box opens
    (06_MAP_CONTRACT.md D4i). Signed in only: requires_auth stays at Home Assistant's default, True.
    Answers `{"photo": <D4g marker_photo> | null}`; 400 for a bad id; 503 while lookups are paused or one
    failed, so the card asks again later. The kept answers and the 429/403 pause are the instance's one
    (saw_livetrack.aircraft_photos.shared): every consumer on the library shares them."""

    url = PHOTO_URL_BASE + "/{hexid}"
    name = "api:live_track_salt:photo"

    async def get(self, request: web.Request, hexid: str) -> web.Response:
        from homeassistant.helpers.aiohttp_client import async_get_clientsession  # noqa: PLC0415

        hass = request.app["hass"]
        status, body = await photos.answer(hass.data, async_get_clientsession(hass), hexid)
        if status == 200:
            resp = self.json(body)
        elif status == 400:
            resp = self.json_message("not an ICAO address", status_code=400)
        else:
            resp = self.json_message("photo lookup paused or failed", status_code=503)
        # The card keeps the answer itself (at most 12 h); no browser or proxy copy.
        resp.headers["Cache-Control"] = "no-store"
        return resp


_VIEWS_KEY = "live_track_salt_views"


def register(hass: HomeAssistant) -> None:
    """Register the views ONCE per run: every entry's setup calls this, and a second registration of a URL
    would add a second route."""
    if hass.data.get(_VIEWS_KEY):
        return
    hass.data[_VIEWS_KEY] = True
    hass.http.register_view(EnforcementIconView())
    hass.http.register_view(SaltPhotoView())
