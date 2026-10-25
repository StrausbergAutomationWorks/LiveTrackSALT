"""From observations to the records the entities read. No Home Assistant import, so it tests alone.

What is drawn (Enforcement SSOT section 3.1, decisions A, G, K, O):
  * every `sourced` hex on the EnforcementAircraft list, anywhere the feed sees it: its agency's
    label, the red/blue glow over its owner-class fill;
  * every `detected_unconfirmed` hex, anywhere: "Detected, unconfirmed" ("Potential PIA" when the
    feed flags the address as a PIA), unlit, the dashed white ring over its owner-class fill;
  * a `cleared` hex is not drawn nationwide; inside the focus area it is an ordinary aircraft;
  * every other aircraft inside the focus area, as an ordinary aircraft;
  * ! NOT an aircraft another integration already draws (Live Track Aircraft inside its circle,
    decision A): the shared poll's claims, passed in as `skip`, so one aircraft is one marker.

! THE MOTION RULES ARE LIVE TRACK AIRCRAFT'S, copied from its coordinator at 62064b6: two DISTINCT
fixes per aircraft, never backwards, a stale observation re-publishes what was published, previous_*
for the card to interpolate across a segment up to MAX_SEGMENT_S, and a slow aircraft's course held.

! OWNER CLASS WITHOUT THE FAA REGISTRY (decision C, open). The list's federal rule entry is
"Federal law enforcement" (the blue fill), any other listed agency "Law enforcement" (the police
white); a detection or an unlisted aircraft has only the feed's flags (military green) or none.
Live Track Aircraft fills from the FAA registry, so 13 of today's 287 differ: Florida State Guard (12)
and one FLHSMV aircraft are orange there.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

from saw_livetrack import aircraft_icons as lib
from saw_livetrack import enforcement_list as el
from saw_livetrack.adsb_poll import Observation, km_between
from saw_livetrack.aircraft_icons import airframe

from . import icons
from .const import FEDERAL_RULE, MAX_SEGMENT_S, SLOW_GROUND_SPEED_KMH

Fix = tuple[float, float, int]

LABEL_DETECTED = "Detected, unconfirmed"
LABEL_PIA = "Potential PIA"
FLAG_MILITARY = 1
FLAG_PIA = 4
MAX_LABEL_CHARS = 22
_LOOKS_LIKE_REGISTRATION = re.compile(r"^(N\d[A-Z0-9]*|[A-Z]{1,2}-[A-Z0-9]{3,5})$")


def _iso(epoch_s: int) -> str:
    return datetime.fromtimestamp(epoch_s, UTC).isoformat()


def _shorten(text: str) -> str:
    out = text.strip()
    return out if len(out) <= MAX_LABEL_CHARS else out[: MAX_LABEL_CHARS - 1].rstrip() + "\u2026"


def owner_category(entry: el.Entry | None) -> str | None:
    """The owner class the fill is drawn in, from the list alone (decision C open; see the docstring)."""
    if entry is None or entry.status not in (el.SOURCED, el.DETECTED) or entry.entry is None:
        return None
    return "Federal law enforcement" if entry.entry == FEDERAL_RULE else "Law enforcement"


class Tracker:
    """Holds the fixes; build() turns one poll's observations into {hex: record}."""

    def __init__(self, latitude: float, longitude: float, radius_km: float) -> None:
        self.latitude, self.longitude, self.radius_km = latitude, longitude, radius_km
        self._fix: dict[str, Fix] = {}
        self._prev_fix: dict[str, Fix] = {}
        self._angle: dict[str, float] = {}
        self._last_rec: dict[str, dict[str, Any]] = {}
        self._tilt_forward: dict[str, bool] = {}

    def build(self, circle: list[Observation], listed: list[Observation], reader,
              skip: frozenset[str] = frozenset(), max_aircraft: int = 250) -> dict[str, dict[str, Any]]:
        """circle: the focus area's answer; listed: the hex round's answer for the list's hexes."""
        out: dict[str, dict[str, Any]] = {}
        near = []
        for obs in circle:
            if obs.identity in skip:
                continue
            rec = self.record(obs, self._entry(reader, obs.identity))
            if rec is not None:
                near.append(rec)
        # ! The cap is a guard rail on the focus area only, nearest first; a listed aircraft is never dropped.
        near.sort(key=lambda r: r["distance_km"])
        for rec in near:
            if len(out) >= max_aircraft and rec.get("enforcement_status") is None:
                continue
            out[rec["identity"]] = rec
        for obs in listed:
            if obs.identity in skip or obs.identity in out:
                continue
            entry = self._entry(reader, obs.identity)
            if entry is None:
                continue
            rec = self.record(obs, entry)
            if rec is not None:
                rec["outside_radius"] = rec["distance_km"] > self.radius_km
                out[obs.identity] = rec
        for gone in [k for k in self._fix if k not in out]:
            for store in (self._fix, self._prev_fix, self._angle, self._last_rec, self._tilt_forward):
                store.pop(gone, None)
        return out

    @staticmethod
    def _entry(reader, hex_id: str) -> el.Entry | None:
        """The list entry that changes how this aircraft is drawn, or None (a cleared one is ordinary)."""
        entry = reader.entry(hex_id) if reader is not None else None
        if entry is None or entry.status not in (el.SOURCED, el.DETECTED):
            return None
        return entry

    def record(self, obs: Observation, entry: el.Entry | None) -> dict[str, Any] | None:
        here = (round(obs.latitude, 6), round(obs.longitude, 6))
        cur = self._fix.get(obs.identity)
        # ! A STALE OR REPEATED OBSERVATION re-publishes what was published (Live Track Aircraft,
        # "2026-09-22 EVENING - THE STALE BOUNCE").
        if cur is not None and obs.observed_at <= cur[2]:
            held = self._last_rec.get(obs.identity)
            if held is not None:
                return held
        is_new = cur is None or obs.observed_at > cur[2] or (
            obs.observed_at == cur[2] and (cur[0], cur[1]) != here)
        if is_new:
            if cur is not None:
                self._prev_fix[obs.identity] = cur
            self._fix[obs.identity] = (here[0], here[1], obs.observed_at)
        latest = self._fix[obs.identity]
        prev = self._prev_fix.get(obs.identity)
        rec: dict[str, Any] = {
            "identity": obs.identity,
            "latitude": here[0],
            "longitude": here[1],
            "observed_at": _iso(latest[2]),
            "last_seen": _iso(latest[2]),
            "distance_km": km_between(self.latitude, self.longitude, here[0], here[1]),
        }
        for key, value in (("callsign", obs.callsign), ("registration", obs.registration),
                           ("emitter_category", obs.emitter_category), ("squawk", obs.squawk),
                           ("altitude_m", obs.altitude_m), ("speed_kmh", obs.speed_kmh),
                           ("vertical_rate_ms", obs.vertical_rate_ms), ("heading_deg", obs.heading_deg),
                           ("course_deg", obs.course_deg), ("aircraft_type", obs.type_code)):
            if value is not None:
                rec[key] = value
        rec.update(self._describe(obs, entry))
        rec["marker_label"] = marker_label(obs, rec)
        if prev is not None:
            segment = latest[2] - prev[2]
            if 0 < segment <= MAX_SEGMENT_S:
                rec["previous_latitude"] = prev[0]
                rec["previous_longitude"] = prev[1]
                rec["previous_observed_at"] = _iso(prev[2])
                rec["segment_duration_s"] = segment
        self._last_rec[obs.identity] = rec
        return rec

    def _describe(self, obs: Observation, entry: el.Entry | None) -> dict[str, Any]:
        out: dict[str, Any] = {}
        rotor = airframe.is_rotorcraft(obs.emitter_category, obs.type_code)
        icon_category = "rotorcraft" if rotor else None
        out["icon"] = "mdi:helicopter" if rotor else "mdi:airplane"
        out["map_layer"] = airframe.map_layer(obs.emitter_category, obs.type_code)
        key = lib.pick(obs.emitter_category, obs.type_code, icon_category)
        if key == "tiltrotor":
            fwd = lib.tiltrotor_forward(self._tilt_forward.get(obs.identity), obs.speed_kmh)
            self._tilt_forward[obs.identity] = fwd
            if fwd:
                key = "tiltrotorfwd"
        bearing = obs.heading_deg if obs.heading_deg is not None else obs.course_deg
        basis = "heading" if obs.heading_deg is not None else "course"
        if basis == "course" and obs.speed_kmh is not None and obs.speed_kmh < SLOW_GROUND_SPEED_KMH:
            held = self._angle.get(obs.identity)
            if held is not None:
                bearing, basis = held, "held"
        rotatable = lib.is_rotatable(key)
        angle = lib.quantise(bearing) if rotatable else None
        if bearing is not None and basis != "held":
            self._angle[obs.identity] = bearing
        out["icon_rotatable"] = rotatable
        if angle is not None:
            out["icon_rotation_deg"] = angle
            out["icon_rotation_basis"] = basis

        flags = obs.db_flags or 0
        military = bool(flags & FLAG_MILITARY)
        if military:
            out["is_military"] = True
        if flags & FLAG_PIA:
            out["identity_hidden"] = True
        if obs.own_op:
            out["operator"] = obs.own_op
            out["operator_name_source"] = "feed"
        category = owner_category(entry)
        if category:
            out["operator_category"] = category
        detected = entry is not None and entry.status == el.DETECTED
        sourced = entry is not None and entry.status == el.SOURCED
        if entry is not None:
            out["enforcement_status"] = entry.status
            if entry.agency:
                out["enforcement_agency"] = entry.agency
            if entry.entry:
                out["enforcement_entry"] = entry.entry
            if entry.registration and "registration" not in out:
                out["list_registration"] = entry.registration
        tone = lib.tone_for(category is not None, icon_category, category, military)
        out["entity_picture"] = icons.picture_url(
            key, tone, lib.weight_for(obs.emitter_category),
            lights=lib.LIGHTS_GLOW if sourced else False, detected=detected)
        return out


def marker_label(obs: Observation, rec: dict[str, Any]) -> str:
    """Never blank. A listed aircraft by its agency (section 3.1); a detection says so; else the callsign."""
    status = rec.get("enforcement_status")
    if status == el.DETECTED:
        return LABEL_PIA if rec.get("identity_hidden") else LABEL_DETECTED
    if status == el.SOURCED and rec.get("enforcement_agency"):
        return _shorten(rec["enforcement_agency"])
    callsign = (obs.callsign or "").strip()
    if callsign and not _LOOKS_LIKE_REGISTRATION.match(callsign.upper()):
        return callsign
    if rec.get("identity_hidden"):
        return "Identity hidden"
    if rec.get("operator"):
        return _shorten(rec["operator"])
    return callsign or obs.type_code or obs.identity.upper()
