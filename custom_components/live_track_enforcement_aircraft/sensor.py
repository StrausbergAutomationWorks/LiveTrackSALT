"""One status sensor: how many aircraft are drawn, and why the poll or the list is as it is.

! Every attribute is low-cardinality (it changes with the state of things, not with the clock), so the
recorder de-duplicates it.
"""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTRIBUTION, DOMAIN
from .coordinator import EnforcementCoordinator

_ATTRS = ("listed_shown", "outside_radius", "claimed_elsewhere", "federal_registrants", "circle_status", "hex_status",
          "source_backoff", "list", "radius_km", "max_aircraft", "nationwide")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    async_add_entities([EnforcementCount(hass.data[DOMAIN][entry.entry_id], entry)])


class EnforcementCount(SensorEntity):
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_name = "Aircraft shown"
    _attr_icon = "mdi:shield-airplane"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "aircraft"
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: EnforcementCoordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_aircraft_shown"

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success

    @property
    def native_value(self) -> int | None:
        data = self._coordinator.data or {}
        return len(data.get("aircraft") or {}) if data else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self._coordinator.data or {}
        return {k: data[k] for k in _ATTRS if k in data}

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self._coordinator.async_add_listener(self.async_write_ha_state))
