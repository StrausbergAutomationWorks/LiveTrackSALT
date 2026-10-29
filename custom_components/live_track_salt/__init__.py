"""Live Track SALT: listed enforcement aircraft wherever they are, plus one focus area.

The list is the public EnforcementAircraft data repository (ODbL v1.0), read through
saw_livetrack.enforcement_list; positions come through saw_livetrack.adsb_poll, the instance's one
adsb.fi poll. Both are per instance in hass.data under SAW-neutral keys, so whichever integration
starts first builds them and Live Track Aircraft, when installed, finds the same ones.
! The list stands alone: no data, code, token or task shared with any other SAW data service
(Lee, 2026-10-23; tests/test_tracker.py checks the code for it).
"""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession, async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval

from saw_livetrack import adsb_poll as ap
from saw_livetrack import enforcement_list as el
from saw_livetrack import faa_registry as fr

from .const import CONSUMER, DOMAIN
from .coordinator import EnforcementCoordinator
from .shared_map_card import async_offer_map_card, async_withdraw_map_card
from .web import register as register_views

HERE = Path(__file__).parent
PLATFORMS: list[Platform] = [Platform.GEO_LOCATION, Platform.SENSOR]
# The reader holds a good check for 6 h and a failed one for 15 min; asked every hour.
LIST_TICK = timedelta(hours=1)
# The FAA registry's cache is checked daily; it is downloaded when a week old (saw_livetrack.faa_registry).
REGISTRY_TICK = timedelta(days=1)


def _list_session(hass: HomeAssistant):
    """The list's own session with the raised header limits (05_SHARED_LESSONS.md B17), shared."""
    session = hass.data.get(el.SESSION_KEY)
    if session is None or session.closed:
        session = async_create_clientsession(hass, **el.SESSION_KWARGS)
        hass.data[el.SESSION_KEY] = session
    return session


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    register_views(hass)
    # LiveTrackMapCard, shipped in frontend/: served once per run, offered, and the one dashboard
    # resource row reconciled (backlog 291). Never raises.
    await async_offer_map_card(hass, DOMAIN, HERE / "frontend")
    first = el.STORE_KEY not in hass.data
    reader = el.shared(hass.data, hass.config.path(".storage", el.CACHE_NAME))
    if first:
        await hass.async_add_executor_job(reader.load_cache)
    poll = ap.shared(hass.data)
    # ! THE FAA REGISTRY, ONE PER INSTANCE (saw-livetrack 0.2.15, backlog 300; Lee 2026-10-25: decision C,
    # option 1): shared with Live Track Aircraft when it is installed, loaded and refreshed here when it is
    # not. Every aircraft fills by the owner rules; the list adds the glow.
    registry = fr.shared(hass.data, hass.config.path(".storage"))
    await registry.load(hass.async_add_executor_job)
    coordinator = EnforcementCoordinator(hass, entry, poll, reader, registry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    async def _check_list(_now=None) -> None:
        await reader.refresh(_list_session(hass), hass.async_add_executor_job)

    hass.async_create_background_task(_check_list(), "live_track_salt_list")
    entry.async_on_unload(async_track_time_interval(hass, _check_list, LIST_TICK))

    async def _check_registry(_now=None) -> None:
        await registry.refresh(async_get_clientsession(hass), hass.async_add_executor_job)

    hass.async_create_background_task(_check_registry(), "live_track_salt_registry")
    entry.async_on_unload(async_track_time_interval(hass, _check_registry, REGISTRY_TICK))
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_reload))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload. The map card is NOT withdrawn here: every restart and reload unloads, and that is
    not an uninstall (card SSOT 67.6); async_remove_entry does it."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        # Its hexes leave the union round and its claims go, so Live Track Aircraft stops skipping them.
        poll = hass.data.get(ap.STORE_KEY)
        if poll is not None:
            poll.release(CONSUMER)
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """The entry was deleted. The domain's LAST entry withdraws the map card."""
    if not [e for e in hass.config_entries.async_entries(DOMAIN)
            if e.entry_id != entry.entry_id]:
        await async_withdraw_map_card(hass, DOMAIN)


async def _reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Options changed. ! A reload does not re-import modules: changed code needs a full restart."""
    await hass.config_entries.async_reload(entry.entry_id)
