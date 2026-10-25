"""Coordinator: the focus area and the list's hexes, through the instance's shared adsb.fi poll.

! ONE POLL PER INSTANCE (saw_livetrack.adsb_poll, backlog 297): the list's hexes join the union hex
round once a minute; the focus area is a circle request every SCAN_INTERVAL_S, asked once if another
consumer asks the same circle; one 429 backoff for the house's IP. adsb.fi only, never adsb.lol.
! A FAILED CIRCLE NEVER BLANKS THE LIST: the hex round's answer stands on its own, and the last good
circle is served for MAX_TRANSIENT_FAILURES polls before the focus area empties (its status says why).
"""
from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from saw_livetrack import adsb_poll as ap
from saw_livetrack import enforcement_list as el

from .const import (
    CONF_LATITUDE, CONF_LONGITUDE, CONF_NATIONWIDE, CONF_RADIUS_KM, CONSUMER, DEFAULT_NATIONWIDE,
    DEFAULT_RADIUS_KM, MAX_AIRCRAFT, MAX_TRANSIENT_FAILURES, SCAN_INTERVAL_S, USER_AGENT,
)
from .tracker import Tracker

_LOGGER = logging.getLogger(__name__)


class EnforcementCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, poll: ap.Poll,
                 reader: el.EnforcementList) -> None:
        opts = {**entry.data, **entry.options}
        self.latitude = float(opts.get(CONF_LATITUDE, hass.config.latitude))
        self.longitude = float(opts.get(CONF_LONGITUDE, hass.config.longitude))
        self.radius_km = float(opts.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM))
        self.nationwide = bool(opts.get(CONF_NATIONWIDE, DEFAULT_NATIONWIDE))
        super().__init__(hass, _LOGGER, name="Live Track Enforcement Aircraft",
                         update_interval=timedelta(seconds=SCAN_INTERVAL_S))
        self._session = async_get_clientsession(hass)
        self.poll = poll
        self.reader = reader
        self.tracker = Tracker(self.latitude, self.longitude, self.radius_km)
        self._circle: list[ap.Observation] = []
        self._circle_failures = 0
        self._last_count: int | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        now = time.time()
        # The list's sourced and detected hexes, and the FAA's federal law-enforcement registrants when an
        # installed integration publishes them (enforcement_list.FEDERAL_KEY; Live Track Aircraft does).
        federal = self.hass.data.get(el.FEDERAL_KEY) or {}
        self.poll.set_hexes(CONSUMER, (self.reader.hexes(el.SOURCED, el.DETECTED) | set(federal))
                            if self.nationwide else None)
        hex_status = await self.poll.hex_round(self._session, now)
        circle_status = "ok"
        try:
            _source, self._circle = await self.poll.circle(
                self._session, self.latitude, self.longitude, self.radius_km, now,
                sources=ap.FI_ONLY, min_expected=ap.short_floor(self._last_count), user_agent=USER_AGENT)
            self._circle_failures = 0
            self._last_count = len(self._circle)
        except ap.SourceError as err:
            self._circle_failures += 1
            circle_status = str(err)
            if self._circle_failures > MAX_TRANSIENT_FAILURES:
                self._circle = []
                self._last_count = None
            _LOGGER.debug("Focus area: %s (%s in a row)", err, self._circle_failures)
        listed = self.poll.hex_observations(CONSUMER) if self.nationwide else []
        skip = self.poll.claimed_by_others(CONSUMER)
        aircraft = self.tracker.build(self._circle, listed, self.reader, skip, MAX_AIRCRAFT, federal)
        self.poll.claim(CONSUMER, aircraft.keys())
        return {
            "aircraft": aircraft,
            "listed_shown": sum(1 for r in aircraft.values() if r.get("enforcement_status")),
            "outside_radius": sum(1 for r in aircraft.values() if r.get("outside_radius")),
            # hexes another integration draws (Live Track Aircraft inside its circle), left to it
            "claimed_elsewhere": len(skip),
            # federal registrants found in hass.data (0 when no installed integration holds the registry)
            "federal_registrants": len(federal),
            "circle_status": circle_status,
            "hex_status": hex_status,
            "source_backoff": self.poll.backoff.status(),
            "list": self.reader.summary,
            "radius_km": self.radius_km,
            "nationwide": self.nationwide,
        }
