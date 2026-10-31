"""geo_location entities: one per aircraft, keyed on the ICAO 24-bit address.

Contract: 10_SEED/06_MAP_CONTRACT.md. `state` is the distance (from the focus centre); `source` is the
domain, which the shared map filters on.
! NO unique_id, as Live Track Aircraft (its SSOT, "2026-09-11 EVENING"): aircraft recur by the
thousand and a registry row each would cost tens of MB; the entity_id comes from the name instead.
! THE NAME IS "SALT aircraft <HEX>", so the id is geo_location.salt_aircraft_<hex>.
"Aircraft <HEX>" would collide with Live Track Aircraft's geo_location.aircraft_<hex>, and
"Enforcement aircraft <HEX>" with Live Track Enforcement Aircraft's, which SALT succeeds (renamed
2026-10-28, Lee). tests/test_entity_name.py checks both.
"""
from __future__ import annotations

from typing import Any

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    AIS_ATTRIBUTION, DOMAIN, FEED_ATTRIBUTION, LIST_ATTRIBUTION, LOL_ATTRIBUTION, VESSEL_LIST_ATTRIBUTION,
)
from .coordinator import EnforcementCoordinator

_PASSTHROUGH = (
    "map_layer", "identity", "marker_label", "callsign", "aircraft_type", "registration",
    "list_registration", "operator", "operator_short", "airline_short", "operator_name_source", "operator_category", "operator_state",
    "identified_by",
    # Backlog 313 part 2: the ICE Air call-sign family while the flight broadcasts it (VELUX, TYSON, TYS), and True on an
    # unknown tail drawn as a charter for that flight (tracker.py). Published only while the record holds them.
    "ice_air_flight", "ice_air_charter_flight",
    "enforcement_status", "enforcement_agency", "enforcement_entry",
    "is_military", "identity_hidden", "outside_radius", "emitter_category",
    "icon_rotatable", "icon_rotation_deg", "icon_rotation_basis", "squawk",
    "altitude_m", "speed_kmh", "vertical_rate_ms", "heading_deg", "course_deg",
    "last_seen", "observed_at", "previous_latitude", "previous_longitude",
    "previous_observed_at", "segment_duration_s",
)

# ! A VESSEL (backlog 315): what the card needs (06_MAP_CONTRACT.md D10 map_layer water, D11 object_ids.mmsi),
# what the list says, and the AIS fix.
_VESSEL_PASSTHROUGH = (
    "map_layer", "object_ids", "identity", "marker_label", "vessel_name", "list_name", "hull",
    # D4b rule 14: the hover's "USCGC Benjamin Bottoms · USCG" (vessels.py).
    "name", "operator_short",
    "enforcement_status", "enforcement_agency", "enforcement_entry", "theatre",
    "icon_rotatable", "icon_rotation_deg", "icon_rotation_basis", "speed_kmh", "course_deg", "heading_deg",
    "observed_at", "previous_latitude", "previous_longitude", "previous_observed_at", "segment_duration_s",
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    coordinator: EnforcementCoordinator = hass.data[DOMAIN][entry.entry_id]
    live: dict[str, EnforcementAircraft] = {}

    @callback
    def _sync() -> None:
        current = set((coordinator.data or {}).get("aircraft") or {})
        new = [i for i in current if i not in live]
        if new:
            entities = [EnforcementAircraft(coordinator, i) for i in new]
            live.update(zip(new, entities))
            async_add_entities(entities)
        # ! Departed aircraft are REMOVED: with no registry row there is nothing to keep.
        for gone in [i for i in live if i not in current]:
            entity = live.pop(gone)
            entity.hass.async_create_task(entity.async_remove(force_remove=True))

    _sync()
    entry.async_on_unload(coordinator.async_add_listener(_sync))

    live_vessels: dict[str, EnforcementVessel] = {}

    @callback
    def _sync_vessels() -> None:
        current = set((coordinator.data or {}).get("vessels") or {})
        new = [m for m in current if m not in live_vessels]
        if new:
            entities = [EnforcementVessel(coordinator, m) for m in new]
            live_vessels.update(zip(new, entities))
            async_add_entities(entities)
        # ! A vessel that leaves its theatre, or is not heard for 30 min, is REMOVED: nothing to keep.
        for gone in [m for m in live_vessels if m not in current]:
            entity = live_vessels.pop(gone)
            entity.hass.async_create_task(entity.async_remove(force_remove=True))

    _sync_vessels()
    entry.async_on_unload(coordinator.async_add_listener(_sync_vessels))


class EnforcementAircraft(GeolocationEvent):
    _attr_should_poll = False
    _attr_unit_of_measurement = "km"
    _attr_source = DOMAIN

    def __init__(self, coordinator: EnforcementCoordinator, identity: str) -> None:
        self._coordinator = coordinator
        self._identity = identity
        self._attr_name = f"SALT aircraft {identity.upper()}"

    def _rec(self) -> dict[str, Any] | None:
        return ((self._coordinator.data or {}).get("aircraft") or {}).get(self._identity)

    @property
    def attribution(self) -> str:
        # The feed the position came from (adsb.lol only through another integration's circle, 0.2.14),
        # and the list's ODbL notice on what the list decided.
        rec = self._rec() or {}
        feed = LOL_ATTRIBUTION if rec.get("feed") == "adsb.lol" else FEED_ATTRIBUTION
        return feed + "; " + LIST_ATTRIBUTION if rec.get("enforcement_status") else feed

    @property
    def icon(self) -> str:
        return (self._rec() or {}).get("icon") or "mdi:airplane"

    @property
    def entity_picture(self) -> str | None:
        return (self._rec() or {}).get("entity_picture")

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success and self._rec() is not None

    @property
    def latitude(self) -> float | None:
        rec = self._rec()
        return rec["latitude"] if rec else None

    @property
    def longitude(self) -> float | None:
        rec = self._rec()
        return rec["longitude"] if rec else None

    @property
    def distance(self) -> float | None:
        rec = self._rec()
        return rec["distance_km"] if rec else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        rec = self._rec()
        if not rec:
            return {}
        return {k: rec[k] for k in _PASSTHROUGH if k in rec}

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self._coordinator.async_add_listener(self.async_write_ha_state))


class EnforcementVessel(GeolocationEvent):
    """A vessel on the EnforcementVessels list, inside a theatre (vessels.py). No unique_id, as the aircraft."""
    _attr_should_poll = False
    _attr_unit_of_measurement = "km"
    _attr_source = DOMAIN

    def __init__(self, coordinator: EnforcementCoordinator, mmsi: str) -> None:
        self._coordinator = coordinator
        self._mmsi = mmsi
        # ! "SALT vessel <MMSI>", so the id is geo_location.salt_vessel_<mmsi>: never Live Track Ships' ids.
        self._attr_name = f"SALT vessel {mmsi}"

    def _rec(self) -> dict[str, Any] | None:
        return ((self._coordinator.data or {}).get("vessels") or {}).get(self._mmsi)

    @property
    def attribution(self) -> str:
        return AIS_ATTRIBUTION + "; " + VESSEL_LIST_ATTRIBUTION

    @property
    def icon(self) -> str:
        return (self._rec() or {}).get("icon") or "mdi:ferry"

    @property
    def entity_picture(self) -> str | None:
        return (self._rec() or {}).get("entity_picture")

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success and self._rec() is not None

    @property
    def latitude(self) -> float | None:
        rec = self._rec()
        return rec["latitude"] if rec else None

    @property
    def longitude(self) -> float | None:
        rec = self._rec()
        return rec["longitude"] if rec else None

    @property
    def distance(self) -> float | None:
        rec = self._rec()
        return rec["distance_km"] if rec else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        rec = self._rec()
        if not rec:
            return {}
        return {k: rec[k] for k in _VESSEL_PASSTHROUGH if k in rec}

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self._coordinator.async_add_listener(self.async_write_ha_state))
