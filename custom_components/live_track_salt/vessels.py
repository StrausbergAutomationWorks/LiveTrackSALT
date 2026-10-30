"""Enforcement vessels: the EnforcementVessels list and the vessels it names, heard on aisstream.

The list is the public data repository StrausbergAutomationWorks/EnforcementVessels (ODbL v1.0), release
`data`: enforcementvessels.json and SHA256SUMS. Each row is a Coast Guard vessel a cited release names in
immigration work, by MMSI; the file also carries the THEATRES, boxes where that work happens (Lee 2026-10-30).
! A LISTED VESSEL IS DRAWN AS ENFORCEMENT ONLY INSIDE A THEATRE BOX: the file's own rule. Outside every
theatre it is an ordinary Coast Guard vessel and this integration does not draw it (it is counted).
! POSITIONS: the instance's ONE aisstream client (saw_livetrack.aisstream, saw-livetrack 0.2.19, backlog 315),
its VESSELS connection: the list's MMSIs, nationwide. Live Track Ships' areas are the other connection.
! NEVER AN EMPTY FILTER. aisstream reads an empty FiltersShipMMSI as no filter at all, the whole world
unfiltered; the coordinator subscribes only while the list names at least one MMSI (vessel_mmsis()).
! The reader follows saw_livetrack.enforcement_list (SHA256SUMS first, installed only when the bytes match, a
failure keeps the cached copy, which never expires). It lives HERE while SALT is its only consumer; Live Track
Ships applying the list's look is the second, and then it moves to saw-livetrack (rule 2).
! No Home Assistant import and no aiohttp import: the session and the executor come from the caller.
! The list stands alone: no data, code, token or task shared with any other SAW data service (Lee, 2026-10-23).
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
import re
import time
from dataclasses import dataclass
from typing import Any

BASE_URL = "https://github.com/StrausbergAutomationWorks/EnforcementVessels/releases/download/data/"
FILE_NAME = "enforcementvessels.json"
SUMS_NAME = "SHA256SUMS"
LIST_URL = BASE_URL + FILE_NAME
SUMS_URL = BASE_URL + SUMS_NAME
# In the consumer's .storage, SAW-neutral (never named after an integration).
CACHE_NAME = "saw_enforcementvessels.json"
STORE_KEY = "saw_enforcementvessels"
SCHEMA = 1

SOURCED = "sourced"
CLEARED = "cleared"

REFRESH_S = 6 * 3600
RETRY_S = 15 * 60
TIMEOUT_S = 60
MAX_BYTES = 16 * 1024 * 1024

# ! A VESSEL NOT HEARD FOR 30 MINUTES IS GONE from the map, Live Track Ships' window (its SSOT item 5).
STALE_S = 30 * 60
# A segment longer than this draws no previous_* (the card would slide it across the gap).
MAX_SEGMENT_S = 600
# Below 2 kn a course is noise; the hull's heading is used when the vessel sends one.
COURSE_MIN_KMH = 2 * 1.852
WEIGHT = 0.80               # aircraft_icons.DEFAULT_WEIGHT: every cutter one size, as an aircraft with no category
VESSEL_KEY = "vessel"       # the picture: icons.py
MAX_LABEL_CHARS = 22        # tracker.MAX_LABEL_CHARS: one label rule for aircraft and vessels

_MMSI = re.compile(r"^[0-9]{9}$")
_SUM_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(\S+)\s*$")


@dataclass(frozen=True)
class Vessel:
    mmsi: str
    status: str
    name: str | None = None
    agency: str | None = None
    short: str | None = None
    hull: str | None = None
    entry: str | None = None


@dataclass(frozen=True)
class Theatre:
    id: str
    name: str
    lat_min: float
    lon_min: float
    lat_max: float
    lon_max: float

    def holds(self, lat: float, lon: float) -> bool:
        return self.lat_min <= lat <= self.lat_max and self.lon_min <= lon <= self.lon_max


def norm_mmsi(value) -> str | None:
    s = str(value).strip() if value is not None and not isinstance(value, bool) else ""
    return s if _MMSI.match(s) else None


def parse(raw: bytes) -> tuple[dict[str, Vessel], list[Theatre], dict]:
    """The published file -> ({mmsi: Vessel}, [Theatre], header). Raises ValueError on a file not of this shape.
    A bad row or box is skipped, not fatal. A status this reader does not know is installed as given."""
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as err:
        raise ValueError("not JSON: %s" % err) from err
    if not isinstance(doc, dict) or doc.get("name") != "EnforcementVessels":
        raise ValueError("not the EnforcementVessels list")
    if doc.get("schema") != SCHEMA:
        raise ValueError("schema %r, this reader knows %d" % (doc.get("schema"), SCHEMA))
    rows = doc.get("vessels")
    if not isinstance(rows, list):
        raise ValueError("no vessels list")
    shorts = {}
    for e in doc.get("entries") or []:
        if isinstance(e, dict) and isinstance(e.get("id"), str):
            shorts[e["id"]] = e.get("short")
    vessels: dict[str, Vessel] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        m = norm_mmsi(row.get("mmsi"))
        status = row.get("status")
        if m is None or not isinstance(status, str) or not status:
            continue
        vessels[m] = Vessel(m, status, row.get("name"), row.get("agency"), shorts.get(row.get("entry")),
                            row.get("hull"), row.get("entry"))
    theatres: list[Theatre] = []
    for t in doc.get("theatres") or []:
        try:
            a, b, c, d = (float(x) for x in t["box"])
        except (KeyError, TypeError, ValueError):
            continue
        if not all(math.isfinite(x) for x in (a, b, c, d)):
            continue
        theatres.append(Theatre(str(t.get("id")), str(t.get("name") or t.get("id")),
                                min(a, c), min(b, d), max(a, c), max(b, d)))
    header = {k: doc.get(k) for k in ("built", "license", "attribution")}
    return vessels, theatres, header


def sha_from_sums(text: str, name: str = FILE_NAME) -> str | None:
    for line in text.splitlines():
        m = _SUM_LINE.match(line.strip())
        if m and m.group(2) == name:
            return m.group(1).lower()
    return None


def _read_file(path: str) -> bytes | None:
    try:
        with open(path, "rb") as fh:
            return fh.read(MAX_BYTES + 1)
    except FileNotFoundError:
        return None


def _write_file(path: str, raw: bytes) -> None:
    tmp = path + ".new"
    with open(tmp, "wb") as fh:
        fh.write(raw)
    os.replace(tmp, path)


async def _default_run_sync(func, *args):
    return await asyncio.get_running_loop().run_in_executor(None, func, *args)


class _Fault(Exception):
    pass


async def _get(session, url: str) -> bytes:
    async with asyncio.timeout(TIMEOUT_S):
        async with session.get(url) as resp:
            if resp.status != 200:
                raise _Fault("HTTP %d" % resp.status)
            raw = await resp.read()
    if len(raw) > MAX_BYTES:
        raise _Fault("over %d bytes" % MAX_BYTES)
    return raw


class VesselList:
    """The list in memory, its cache on disk, and its refresh."""

    def __init__(self, cache_path: str, clock=time.monotonic) -> None:
        self.cache_path = cache_path
        self._clock = clock
        self._lock = asyncio.Lock()
        self.vessels: dict[str, Vessel] = {}
        self.theatres: list[Theatre] = []
        self.header: dict = {}
        self.sha: str | None = None
        self.checked_at: float | None = None
        self.last_ok: bool | None = None
        self.last_result = "not checked"

    def vessel(self, mmsi) -> Vessel | None:
        m = norm_mmsi(mmsi)
        return self.vessels.get(m) if m else None

    def watched(self) -> frozenset[str]:
        """Every MMSI whose status is not cleared: what the VESSELS subscription asks for."""
        return frozenset(m for m, v in self.vessels.items() if v.status != CLEARED)

    def theatre(self, lat, lon) -> Theatre | None:
        if lat is None or lon is None:
            return None
        for t in self.theatres:
            if t.holds(lat, lon):
                return t
        return None

    @property
    def summary(self) -> str:
        if not self.vessels:
            return "no list" if self.last_ok is not False else "no list (%s)" % self.last_result
        n = sum(1 for v in self.vessels.values() if v.status == SOURCED)
        line = "%d sourced of %d, %d theatres, built %s" % (n, len(self.vessels), len(self.theatres),
                                                            self.header.get("built"))
        return line if self.last_ok is not False else line + " (%s)" % self.last_result

    def _install(self, raw: bytes) -> None:
        self.vessels, self.theatres, self.header = parse(raw)
        self.sha = hashlib.sha256(raw).hexdigest()

    def load_cache(self) -> bool:
        """SYNC (run it in an executor). True when a usable cached copy was installed."""
        raw = _read_file(self.cache_path)
        if raw is None or len(raw) > MAX_BYTES:
            return False
        try:
            self._install(raw)
        except ValueError:
            return False
        return True

    def due(self) -> bool:
        if self.checked_at is None:
            return True
        return self._clock() - self.checked_at >= (REFRESH_S if self.last_ok else RETRY_S)

    async def refresh(self, session, run_sync=None, force: bool = False) -> str:
        """"fresh", "unchanged", "updated" or "failed: <why>". Never raises for a network or file fault."""
        run_sync = run_sync or _default_run_sync
        async with self._lock:
            if not force and not self.due():
                return "fresh"
            try:
                result = await self._check(session, run_sync)
                self.last_ok = True
            except asyncio.CancelledError:
                raise
            except Exception as err:  # noqa: BLE001 - every fault keeps the cached list
                if isinstance(err, _Fault):
                    why = str(err)
                elif isinstance(err, (asyncio.TimeoutError, TimeoutError)):
                    why = "timeout"
                else:
                    why = type(err).__name__
                result = "failed: %s" % why
                self.last_ok = False
            self.checked_at = self._clock()
            self.last_result = result
            return result

    async def _check(self, session, run_sync) -> str:
        sums = await _get(session, SUMS_URL)
        want = sha_from_sums(sums.decode("utf-8", "replace"))
        if want is None:
            raise _Fault("SHA256SUMS names no %s" % FILE_NAME)
        if want == self.sha:
            return "unchanged"
        raw = await _get(session, LIST_URL)
        if hashlib.sha256(raw).hexdigest() != want:
            raise _Fault("checksum mismatch")
        try:
            parse(raw)
        except ValueError as err:
            raise _Fault("bad file: %s" % err) from err
        await run_sync(_write_file, self.cache_path, raw)
        self._install(raw)
        return "updated"


def shared_list(store: dict, cache_path: str) -> VesselList:
    """The instance's one reader, made on first use. store is hass.data."""
    reader = store.get(STORE_KEY)
    if reader is None:
        reader = store[STORE_KEY] = VesselList(cache_path)
    return reader


# --------------------------------------------------------------------------------------------------------------
def _km(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((p2 - p1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * 6371.0088 * math.asin(min(1.0, math.sqrt(a)))


def _iso(when) -> str | None:
    return when.isoformat().replace("+00:00", "Z") if when is not None else None


class VesselTracker:
    """What the shared client delivered (saw_livetrack.ais.Observation), kept per MMSI with its previous fix,
    and the records drawn from it: only listed vessels inside a theatre, heard within STALE_S."""

    def __init__(self, latitude: float, longitude: float, clock=time.time) -> None:
        self.latitude, self.longitude = latitude, longitude
        self._clock = clock
        self._last: dict[str, tuple[float, Any]] = {}     # mmsi -> (heard at, obs)
        self._prev: dict[str, Any] = {}                    # mmsi -> the fix before, at another position
        self.delivered = 0

    def deliver(self, obs) -> None:
        """The shared client's callback: in Home Assistant's loop, cheap, never raises on a bad fix."""
        m = norm_mmsi(getattr(obs, "identity", None))
        if m is None or obs.latitude is None or obs.longitude is None:
            return
        old = self._last.get(m)
        if old is not None and (old[1].latitude, old[1].longitude) != (obs.latitude, obs.longitude):
            self._prev[m] = old[1]
        self._last[m] = (self._clock(), obs)
        self.delivered += 1

    def heard(self) -> int:
        """MMSIs heard within STALE_S, anywhere."""
        cut = self._clock() - STALE_S
        return sum(1 for t, _o in self._last.values() if t >= cut)

    def build(self, reader: VesselList, picture_url) -> tuple[dict[str, dict], int]:
        """({mmsi: record} for listed vessels inside a theatre, how many listed vessels were heard outside every
        theatre). Stale vessels are forgotten here. picture_url(key, tone, weight, lights) -> str."""
        now = self._clock()
        out: dict[str, dict] = {}
        outside = 0
        for m in [m for m, (t, _o) in self._last.items() if t < now - STALE_S]:
            self._last.pop(m, None)
            self._prev.pop(m, None)
        for m, (_t, obs) in self._last.items():
            v = reader.vessel(m)
            if v is None or v.status == CLEARED:
                continue
            theatre = reader.theatre(obs.latitude, obs.longitude)
            if theatre is None:
                outside += 1
                continue
            out[m] = self.record(obs, v, theatre, picture_url)
        return out, outside

    def record(self, obs, v: Vessel, theatre: Theatre, picture_url) -> dict[str, Any]:
        rec: dict[str, Any] = {
            "identity": v.mmsi,
            "latitude": obs.latitude,
            "longitude": obs.longitude,
            "distance_km": round(_km(self.latitude, self.longitude, obs.latitude, obs.longitude), 1),
            # 10_SEED/06_MAP_CONTRACT.md D10 and D11: a vessel is on the water; its MMSI is its identity.
            "map_layer": "water",
            "object_ids": {"mmsi": v.mmsi},
            "enforcement_status": v.status,
            "enforcement_agency": v.agency,
            "enforcement_entry": v.entry,
            "theatre": theatre.name,
            "observed_at": _iso(obs.observed_at),
            "feed": "aisstream",
            "icon": "mdi:ferry",
        }
        if obs.name:
            rec["vessel_name"] = obs.name
        if v.name:
            rec["list_name"] = v.name
        if v.hull:
            rec["hull"] = v.hull
        for k in ("speed_kmh", "course_deg", "heading_deg"):
            val = getattr(obs, k, None)
            if val is not None:
                rec[k] = round(float(val), 1)
        # The picture points north; the card turns it. The hull's heading, else the course when moving.
        if obs.heading_deg is not None:
            rec["icon_rotation_deg"], rec["icon_rotation_basis"] = round(float(obs.heading_deg)) % 360, "heading"
        elif obs.course_deg is not None and (obs.speed_kmh or 0) >= COURSE_MIN_KMH:
            rec["icon_rotation_deg"], rec["icon_rotation_basis"] = round(float(obs.course_deg)) % 360, "course"
        rec["icon_rotatable"] = "icon_rotation_deg" in rec
        prev = self._prev.get(v.mmsi)
        if prev is not None and prev.observed_at is not None and obs.observed_at is not None:
            seg = (obs.observed_at - prev.observed_at).total_seconds()
            if 0 < seg <= MAX_SEGMENT_S:
                rec["previous_latitude"] = prev.latitude
                rec["previous_longitude"] = prev.longitude
                rec["previous_observed_at"] = _iso(prev.observed_at)
                rec["segment_duration_s"] = round(seg, 1)
        # ! THE AIRCRAFT RULES' SOURCED TREATMENT (Lee 2026-10-30: "use the same rules we already use for
        # aircraft"): the owner-class fill, which for the Coast Guard is army green ("mil", as
        # aircraft_icons.tone_for gives the Coast Guard), and the red/blue glow of a sourced entry.
        sourced = v.status == SOURCED
        rec["entity_picture"] = picture_url(VESSEL_KEY, "mil", WEIGHT, "glow" if sourced else False)
        # A listed vessel by its agency, as a sourced aircraft (tracker.marker_label): the entry's short form first.
        label = (v.short or v.agency or "Listed vessel").strip()
        rec["marker_label"] = (label if len(label) <= MAX_LABEL_CHARS
                               else label[: MAX_LABEL_CHARS - 1].rstrip() + "…")
        return rec
