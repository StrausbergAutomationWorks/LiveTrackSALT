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
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from saw_livetrack import adsb_poll as ap
from saw_livetrack import aisstream as ais_client
from saw_livetrack import enforcement_list as el
from saw_livetrack import faa_registry as fr
from saw_livetrack.enforcement_vessels import VesselList

from . import icons
from .const import (
    CONF_AISSTREAM_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_MAX_AIRCRAFT, CONF_NATIONWIDE, CONF_RADIUS_KM, CONSUMER, DOMAIN,
    DEFAULT_MAX_AIRCRAFT, DEFAULT_NATIONWIDE, DEFAULT_RADIUS_KM, MAX_TRANSIENT_FAILURES, SCAN_INTERVAL_S,
    USER_AGENT, VESSEL_CONSUMER,
)
from .tracker import Tracker
from .vessels import VesselTracker

_LOGGER = logging.getLogger(__name__)


class EnforcementCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, poll: ap.Poll,
                 reader: el.EnforcementList, registry: fr.FaaRegistry | None = None,
                 vessel_reader: VesselList | None = None) -> None:
        opts = {**entry.data, **entry.options}
        self.latitude = float(opts.get(CONF_LATITUDE, hass.config.latitude))
        self.longitude = float(opts.get(CONF_LONGITUDE, hass.config.longitude))
        self.radius_km = float(opts.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM))
        self.nationwide = bool(opts.get(CONF_NATIONWIDE, DEFAULT_NATIONWIDE))
        self.max_aircraft = int(opts.get(CONF_MAX_AIRCRAFT, DEFAULT_MAX_AIRCRAFT))
        super().__init__(hass, _LOGGER, name="Live Track SALT",
                         update_interval=timedelta(seconds=SCAN_INTERVAL_S))
        self._session = async_get_clientsession(hass)
        self.poll = poll
        self.reader = reader
        self.registry = registry
        self.tracker = Tracker(self.latitude, self.longitude, self.radius_km, registry)
        self._circle: list[ap.Observation] = []
        self.circle_source = ap.FI
        self._circle_failures = 0
        self._last_count: int | None = None
        # ! CALLSIGN DETECTIONS SURVIVE A RESTART (Lee 2026-10-28: "a detection is watched at once"): the tracker's
        # set, in HA storage under this domain; loaded before the first poll, saved when a new hex is detected.
        self._detections_store = Store(hass, 1, f"{DOMAIN}.detections")
        self._detections_loaded = False
        # ! ENFORCEMENT VESSELS (backlog 315): the list's MMSIs on the shared aisstream client's VESSELS
        # connection; positions arrive pushed into self.vessels, and each poll draws what is inside a theatre.
        self.aisstream_key = str(opts.get(CONF_AISSTREAM_KEY) or "").strip()
        self.vessel_reader = vessel_reader
        self.vessels = VesselTracker(self.latitude, self.longitude)
        self._vessel_mmsis: frozenset | None = None     # what the client was last given; None = not added
        self.vessel_status = "no API key" if not self.aisstream_key else "no list"

    async def async_sync_vessels(self) -> None:
        """The VESSELS subscription follows the list. ! NEVER AN EMPTY FILTER: aisstream reads an empty
        FiltersShipMMSI as the whole world unfiltered, so with no key or no MMSI there is no subscription."""
        client = ais_client.shared(self.hass.data)
        want = (self.vessel_reader.watched() if self.aisstream_key and self.vessel_reader is not None
                else frozenset())
        try:
            if not want:
                if self._vessel_mmsis is not None:
                    self._vessel_mmsis = None
                    await client.remove(VESSEL_CONSUMER)
                self.vessel_status = "no API key" if not self.aisstream_key else "no list"
                return
            if self._vessel_mmsis is None:
                client.add_vessels(VESSEL_CONSUMER, async_get_clientsession(self.hass), self.aisstream_key,
                                   sorted(want), self.vessels.deliver, DOMAIN,
                                   create_task=lambda coro, name: self.hass.async_create_background_task(coro, name))
            elif want != self._vessel_mmsis:
                client.update(VESSEL_CONSUMER, mmsis=sorted(want))
            self._vessel_mmsis = want
        except ValueError as err:          # past aisstream's 200 MMSIs per subscription
            self.vessel_status = str(err)
            _LOGGER.warning("Enforcement vessels not subscribed: %s", err)

    async def async_stop_vessels(self) -> None:
        if self._vessel_mmsis is not None:
            self._vessel_mmsis = None
            await ais_client.shared(self.hass.data).remove(VESSEL_CONSUMER)

    def _vessel_connection(self) -> str:
        if self._vessel_mmsis is None:
            return self.vessel_status
        status = ais_client.shared(self.hass.data).status()
        return next((c["status"] for c in status["connections"] if c["kind"] == ais_client.VESSELS), "starting")

    async def _async_update_data(self) -> dict[str, Any]:
        now = time.time()
        if not self._detections_loaded:
            saved = await self._detections_store.async_load()
            if isinstance(saved, dict):
                self.tracker.detections.update({k: v for k, v in saved.items() if isinstance(v, dict)})
            self._detections_loaded = True
        # The list's watched hexes (sourced, detected and, since backlog 313, ICE Air charter), and the FAA's federal law-enforcement registrants when an
        # installed integration publishes them (enforcement_list.FEDERAL_KEY; Live Track Aircraft does).
        # ! The registrants from the instance's own FAA registry (backlog 300), so this integration keeps the
        # nationwide scope alone; what Live Track Aircraft publishes is kept for its fields.
        federal = {h: {} for h in (self.registry.gov.federal_law_enforcement_hexes() if self.registry else ())}
        federal.update(self.hass.data.get(el.FEDERAL_KEY) or {})
        self.poll.set_hexes(CONSUMER, (self.reader.hexes(*el.WATCHED) | set(federal)
                                       | set(self.tracker.detections))
                            if self.nationwide else None)
        hex_status = await self.poll.hex_round(self._session, now)
        circle_status = "ok"
        try:
            # ! A FOCUS AREA INSIDE ANOTHER INTEGRATION'S CIRCLE COSTS NO REQUEST (saw-livetrack 0.2.14,
            # Lee 2026-10-24 23:58): it is answered from that circle's last answer, whatever feed
            # answered it; the source is kept so the entities credit the feed the data came from.
            self.circle_source, self._circle = await self.poll.circle(
                self._session, self.latitude, self.longitude, self.radius_km, now,
                sources=ap.FI_ONLY, min_expected=ap.short_floor(self._last_count), user_agent=USER_AGENT,
                consumer=CONSUMER)
            if self.poll.circle_how.get(CONSUMER) == "covered":
                circle_status = "ok, covered by another integration's circle"
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
        aircraft = self.tracker.build(self._circle, listed, self.reader, skip, self.max_aircraft, federal)
        self.poll.claim(CONSUMER, aircraft.keys())
        if self.tracker.detections_added:
            self.tracker.detections_added = False
            await self._detections_store.async_save(dict(self.tracker.detections))
        # Which feed each aircraft came from, for its attribution: the focus area's answer may be another
        # integration's, from adsb.lol; the hex round is always adsb.fi.
        in_circle = {o.identity for o in self._circle}
        for hex_id, rec in aircraft.items():
            rec["feed"] = self.circle_source if hex_id in in_circle and not rec.get("outside_radius") else ap.FI
        # ! ONE VESSEL, ONE MARKER (backlog 315 task 5): what another consumer claims on the shared aisstream client
        # (Live Track Ships, which draws a listed vessel itself) is left to it. SALT claims nothing for vessels.
        vessel_skip = (ais_client.shared(self.hass.data).claimed_by_others(VESSEL_CONSUMER)
                       if self.vessel_reader is not None else frozenset())
        vessels, vessels_outside = (self.vessels.build(self.vessel_reader, icons.picture_url, vessel_skip)
                                    if self.vessel_reader is not None else ({}, 0))
        return {
            "aircraft": aircraft,
            "vessels": vessels,
            "vessels_shown": len(vessels),
            # listed vessels heard outside every theatre: ordinary Coast Guard work there, not drawn
            "vessels_outside_theatres": vessels_outside,
            # listed vessels another integration draws (Live Track Ships), left to it
            "vessels_claimed_elsewhere": self.vessels.claimed_elsewhere,
            "vessel_list": self.vessel_reader.summary if self.vessel_reader is not None else "no list",
            "vessel_feed": self._vessel_connection(),
            "listed_shown": sum(1 for r in aircraft.values() if r.get("enforcement_status")),
            "outside_radius": sum(1 for r in aircraft.values() if r.get("outside_radius")),
            # hexes another integration draws (Live Track Aircraft inside its circle), left to it
            "claimed_elsewhere": len(skip),
            # federal registrants found in hass.data (0 when no installed integration holds the registry)
            "federal_registrants": len(federal),
            # hexes watched because they broadcast a DHS callsign (TROY...) or ICE Air's (VELUX...) while off the list
            "detected_by_callsign": len(self.tracker.detections),
            # ! those seen flying ICE Air's call sign: proposed for the list (Lee 2026-10-29 22:25), for its review
            "proposed_for_list": sorted("%s %s" % (h.upper(), d.get("callsign", ""))
                                        for h, d in self.tracker.detections.items() if d.get("status") == el.CHARTER),
            "circle_status": circle_status,
            "hex_status": hex_status,
            "source_backoff": self.poll.backoff.status(),
            "list": self.reader.summary,
            "radius_km": self.radius_km,
            "max_aircraft": self.max_aircraft,
            "nationwide": self.nationwide,
        }
