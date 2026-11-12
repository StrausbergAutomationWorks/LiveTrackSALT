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
from homeassistant.helpers.selector import (
    LocationSelector, LocationSelectorConfig, TextSelector, TextSelectorConfig, TextSelectorType,
)

from .centre import from_form, to_form
from .const import (
    CONF_ADSBLOL_KEY, CONF_AISSTREAM_KEY, CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_MAX_AIRCRAFT, CONF_NATIONWIDE,
    CONF_RADIUS_KM,
    DEFAULT_MAX_AIRCRAFT, DEFAULT_NATIONWIDE, DEFAULT_RADIUS_KM, DOMAIN, MAX_MAX_AIRCRAFT, MAX_RADIUS_KM,
    MIN_MAX_AIRCRAFT, MIN_RADIUS_KM,
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
        # ! As Live Track Aircraft's: a guard rail on the focus area, the user's (Lee 2026-10-25).
        vol.Required(CONF_MAX_AIRCRAFT, default=defaults.get(CONF_MAX_AIRCRAFT, DEFAULT_MAX_AIRCRAFT)):
            vol.All(vol.Coerce(int), vol.Range(min=MIN_MAX_AIRCRAFT, max=MAX_MAX_AIRCRAFT)),
        vol.Required(CONF_NATIONWIDE, default=defaults.get(CONF_NATIONWIDE, DEFAULT_NATIONWIDE)): bool,
        # ! OPTIONAL (backlog 315): the user's own aisstream.io key; without it SALT draws no vessels.
        vol.Optional(CONF_AISSTREAM_KEY, default=defaults.get(CONF_AISSTREAM_KEY, "")): str,
        # ! OPTIONAL (backlog 336): the user's own adsb.lol API key, masked. suggested_value, not default: with a
        # default, a cleared field sends nothing and the old key would come back.
        vol.Optional(CONF_ADSBLOL_KEY, description={"suggested_value": defaults.get(CONF_ADSBLOL_KEY, "")}):
            TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
    })


class EnforcementConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            values, error = from_form(user_input)
            # Stored without surrounding spaces, "" meaning none, so a cleared key is not read back from entry.data.
            values[CONF_ADSBLOL_KEY] = (values.get(CONF_ADSBLOL_KEY) or "").strip()
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
            # Stored without surrounding spaces, "" meaning none, so a cleared key is not read back from entry.data.
            values[CONF_ADSBLOL_KEY] = (values.get(CONF_ADSBLOL_KEY) or "").strip()
            if error is None:
                # ! TITLE AND OPTIONS IN ONE CALL, as Live Track Aircraft learned (2026-09-19): a
                # title-only update reloads the entry before the new options are stored.
                self.hass.config_entries.async_update_entry(self._entry, title=_title(values), options=values)
                return self.async_create_entry(title="", data=values)
            errors[CONF_LOCATION] = error
        return self.async_show_form(
            step_id="init", data_schema=_schema({**self._entry.data, **self._entry.options}, self.hass),
            errors=errors)
