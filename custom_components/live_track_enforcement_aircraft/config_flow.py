"""Config flow: the focus area (a map marker and a radius) and the nationwide list on or off.

One entry (manifest single_config_entry): the list is nationwide whatever the focus area, and a
second entry would draw every listed aircraft twice. NOT final (Enforcement SSOT section 1).
"""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import LocationSelector, LocationSelectorConfig

from .centre import from_form, to_form
from .const import (
    CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NATIONWIDE, CONF_RADIUS_KM,
    DEFAULT_NATIONWIDE, DEFAULT_RADIUS_KM, DOMAIN, MAX_RADIUS_KM, MIN_RADIUS_KM,
)


def _title(cfg: dict[str, Any]) -> str:
    return "%.3f, %.3f - %.0f km" % (float(cfg[CONF_LATITUDE]), float(cfg[CONF_LONGITUDE]),
                                     float(cfg[CONF_RADIUS_KM]))


def _schema(defaults: dict[str, Any], hass) -> vol.Schema:
    return vol.Schema({
        vol.Required(CONF_LOCATION, default=to_form(defaults, hass.config.latitude,
                                                    hass.config.longitude)):
            LocationSelector(LocationSelectorConfig(radius=False, icon="mdi:shield-airplane")),
        vol.Required(CONF_RADIUS_KM, default=defaults.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM)):
            vol.All(vol.Coerce(float), vol.Range(min=MIN_RADIUS_KM, max=MAX_RADIUS_KM)),
        vol.Required(CONF_NATIONWIDE, default=defaults.get(CONF_NATIONWIDE, DEFAULT_NATIONWIDE)): bool,
    })


class EnforcementConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            values, error = from_form(user_input)
            if error is None:
                return self.async_create_entry(title=_title(values), data=values)
            errors[CONF_LOCATION] = error
        return self.async_show_form(step_id="user", data_schema=_schema({}, self.hass), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        return EnforcementOptionsFlow(entry)


class EnforcementOptionsFlow(OptionsFlow):
    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            values, error = from_form(user_input)
            if error is None:
                # ! TITLE AND OPTIONS IN ONE CALL, as Live Track Aircraft learned (2026-09-19): a
                # title-only update reloads the entry before the new options are stored.
                self.hass.config_entries.async_update_entry(self._entry, title=_title(values), options=values)
                return self.async_create_entry(title="", data=values)
            errors[CONF_LOCATION] = error
        return self.async_show_form(
            step_id="init", data_schema=_schema({**self._entry.data, **self._entry.options}, self.hass),
            errors=errors)
