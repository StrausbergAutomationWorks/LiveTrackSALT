"""From observations to the records the entities read. No Home Assistant import, so it tests alone.

What is drawn (Enforcement SSOT section 3.1, decisions A, G, K, O):
  * every `sourced` hex on the EnforcementAircraft list, anywhere the feed sees it: its agency's
    label, the red/blue glow over its owner-class fill;
  * every `detected_unconfirmed` hex, anywhere: "Detected, unconfirmed" ("Potential PIA" when the
    feed flags the address as a PIA), unlit, the dashed white ring over its owner-class fill;
  * ! every `ice_air_charter` hex, anywhere (backlog 313; Lee 2026-10-29 00:37): an airliner that flies ICE Air
    charters and other work too: "ICE Air Charter?", the library's STEADY charter glow (blue inside, red outside,
    no flash) over its owner-class fill, watched nationwide and past the cap like sourced and detected;
  * a `cleared` hex is not drawn nationwide; inside the focus area it is an ordinary aircraft;
  * every other aircraft inside the focus area, as an ordinary aircraft;
  * ! A CALLSIGN SIGNAL (Lee 2026-10-28 23:11): an aircraft the list does not know, broadcasting a DHS
    callsign (`TROY` and digits; NBC LA and TWZ report it as DHS's, CBP's scheme on RadioReference), is a
    detection: drawn as a `detected_unconfirmed` entry (the ring, "Detected, unconfirmed", unlit; decisions
    K, O) with `detected_by`, and WATCHED AT ONCE nationwide (its hex joins the hex round; the coordinator
    keeps the set in HA storage). Never for a listed hex, a cleared one (found not involved) or a government
    registrant (already drawn by the owner rules). Seen while another integration draws it, it is still
    recorded, so it stays watched when it leaves that circle;
  * ! NOT an aircraft another integration already draws (Live Track Aircraft inside its circle,
    decision A): the shared poll's claims, passed in as `skip`, so one aircraft is one marker.

! THE MOTION RULES ARE LIVE TRACK AIRCRAFT'S, copied from its coordinator at 62064b6: two DISTINCT
fixes per aircraft, never backwards, a stale observation re-publishes what was published, previous_*
for the card to interpolate across a segment up to MAX_SEGMENT_S, and a slow aircraft's course held.

! EVERY AIRCRAFT FILLS BY THE OWNER RULES, as in Live Track Aircraft (backlog 300; Lee 2026-10-25 01:42:
decision C answered, option 1, and the fill already decided): the FAA registry's owner class from
saw_livetrack.faa_registry, else the feed's flags (military green), else none; the list adds the glow
(sourced) or the ring (detected), never the fill. So Florida State Guard's 12 and one FHP aircraft fill
orange (the FAA names a plain government owner) with the glow. With no registry row an aircraft fills
as an ordinary one.
! operator_short, for the hover's first line (06_MAP_CONTRACT.md D4b rule 12): the registry's agency
code or force's short name, else the list's agency for a sourced aircraft.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

from saw_livetrack import aircraft_icons as lib
from saw_livetrack import airlines
from saw_livetrack import enforcement_list as el
from saw_livetrack import faa_registry as fr
from saw_livetrack.adsb_poll import Observation, km_between
from saw_livetrack.aircraft_icons import airframe

from . import icons
from .const import MAX_SEGMENT_S, SLOW_GROUND_SPEED_KMH

Fix = tuple[float, float, int]

LABEL_DETECTED = "Detected, unconfirmed"
LABEL_PIA = "Potential PIA"
# ! THE LIBRARY'S (saw-livetrack 0.2.16, Lee 2026-10-29): Live Track Aircraft prints the same label.
LABEL_CHARTER = el.CHARTER_LABEL
FLAG_MILITARY = 1
FLAG_PIA = 4
MAX_LABEL_CHARS = 22
_LOOKS_LIKE_REGISTRATION = re.compile(r"^(N\d[A-Z0-9]*|[A-Z]{1,2}-[A-Z0-9]{3,5})$")
# ! THE CALLSIGN SIGNALS: callsign pattern -> (entry name of the synthetic detection, detected_by text).
CALLSIGN_SIGNALS = ((re.compile(r"^TROY\d{0,4}$"), "callsign-troy", "callsign TROY"),)


def _iso(epoch_s: int) -> str:
    return datetime.fromtimestamp(epoch_s, UTC).isoformat()


def _shorten(text: str) -> str:
    out = text.strip()
    return out if len(out) <= MAX_LABEL_CHARS else out[: MAX_LABEL_CHARS - 1].rstrip() + "\u2026"


class Tracker:
    """Holds the fixes; build() turns one poll's observations into {hex: record}."""

    def __init__(self, latitude: float, longitude: float, radius_km: float, registry=None) -> None:
        """registry: anything with lookup_government(hex) (saw_livetrack.faa_registry.FaaRegistry), or None."""
        self.latitude, self.longitude, self.radius_km = latitude, longitude, radius_km
        self.registry = registry
        self._fix: dict[str, Fix] = {}
        self._prev_fix: dict[str, Fix] = {}
        self._angle: dict[str, float] = {}
        self._last_rec: dict[str, dict[str, Any]] = {}
        self._tilt_forward: dict[str, bool] = {}
        # hex -> {"entry", "detected_by", "callsign", "first_seen", "last_seen"}; never pruned with the fixes.
        self.detections: dict[str, dict[str, Any]] = {}
        self.detections_added = False      # set when a NEW hex is detected; the coordinator saves and clears it

    def build(self, circle: list[Observation], listed: list[Observation], reader,
              skip: frozenset[str] = frozenset(), max_aircraft: int = 250,
              federal: dict[str, dict[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
        """circle: the focus area's answer; listed: the hex round's answer for the watched hexes.

        federal: the FAA's federal law-enforcement registrants, when an installed integration holds the
        registry (enforcement_list.FEDERAL_KEY): watched nationwide too, so a registration newer than the
        list's build is not lost (Enforcement SSOT section 3.5 step 2).
        """
        federal = federal or {}
        out: dict[str, dict[str, Any]] = {}
        near = []
        for obs in circle:                  # skipped ones too: another integration draws it, we still watch it
            self._signal(reader, obs, federal)
        for obs in circle:
            if obs.identity in skip:
                continue
            rec = self.record(obs, self._entry(reader, obs.identity), federal.get(obs.identity))
            if rec is not None:
                near.append(rec)
        # ! The cap is a guard rail on the focus area only, nearest first; a listed aircraft is never dropped.
        near.sort(key=lambda r: r["distance_km"])
        for rec in near:
            if len(out) >= max_aircraft and not (rec.get("enforcement_status") or rec.get("identified_by")):
                continue
            out[rec["identity"]] = rec
        for obs in listed:
            if obs.identity in skip or obs.identity in out:
                continue
            entry = self._entry(reader, obs.identity)
            fed = federal.get(obs.identity)
            cleared = reader is not None and reader.status(obs.identity) == el.CLEARED
            if entry is None and (fed is None or cleared):
                continue
            rec = self.record(obs, entry, fed)
            if rec is not None:
                rec["outside_radius"] = rec["distance_km"] > self.radius_km
                out[obs.identity] = rec
        for gone in [k for k in self._fix if k not in out]:
            for store in (self._fix, self._prev_fix, self._angle, self._last_rec, self._tilt_forward):
                store.pop(gone, None)
        return out

    def _entry(self, reader, hex_id: str) -> el.Entry | None:
        """The list entry that changes how this aircraft is drawn, or None (a cleared one is ordinary).

        A callsign detection is a synthetic `detected_unconfirmed` entry, unless the list has since learned the hex."""
        entry = reader.entry(hex_id) if reader is not None else None
        if entry is not None:
            return entry if entry.status in el.WATCHED else None
        det = self.detections.get(hex_id)
        if det is not None:
            return el.Entry(hex=hex_id, status=el.DETECTED, entry=det["entry"])
        return None

    def _signal(self, reader, obs: Observation, federal: dict[str, dict[str, Any]]) -> None:
        """Record a callsign detection: not on the list in any status, not a government registrant."""
        callsign = (obs.callsign or "").strip().upper()
        for pattern, entry_name, by in CALLSIGN_SIGNALS:
            if not pattern.match(callsign):
                continue
            if reader is not None and reader.status(obs.identity) is not None:
                return                       # sourced, detected or cleared: the list already decides
            if obs.identity in federal or (self.registry is not None
                                           and self.registry.lookup_government(obs.identity)):
                return                       # a government registrant: the owner rules already draw it
            seen = _iso(obs.observed_at)
            det = self.detections.get(obs.identity)
            if det is None:
                self.detections[obs.identity] = {"entry": entry_name, "detected_by": by, "callsign": callsign,
                                                 "first_seen": seen, "last_seen": seen}
                self.detections_added = True
            else:
                det["last_seen"], det["callsign"] = seen, callsign
            return

    def record(self, obs: Observation, entry: el.Entry | None,
               fed: dict[str, Any] | None = None) -> dict[str, Any] | None:
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
        rec.update(self._describe(obs, entry, fed))
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

    def _describe(self, obs: Observation, entry: el.Entry | None,
                  fed: dict[str, Any] | None = None) -> dict[str, Any]:
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

        # ! The owner rules, as Live Track Aircraft's coordinator: the registry's row, then the feed's flags.
        gov = self.registry.lookup_government(obs.identity) if self.registry is not None else None
        military, category, extra = fr.from_feed_flags(obs.db_flags, obs.own_op, gov)
        if military:
            out["is_military"] = True
        if extra.get("identity_hidden"):
            out["identity_hidden"] = True
        # ! The hover's first line (Lee 2026-10-29 14:51, as Live Track Aircraft): "GlobalX 6181", not "GXA6181".
        short_name = airlines.airline_short(obs.callsign)
        if short_name:
            out["airline_short"] = short_name
        if obs.own_op:
            out["operator"] = obs.own_op
            out["operator_name_source"] = "feed"
        for name in ("identified_by", "operator_short"):
            if extra.get(name):
                out[name] = extra[name]
        if gov:
            if gov.get("operator"):
                out["operator"] = gov["operator"]
                out["operator_name_source"] = "government"
            for name in ("operator_state", "operator_short", "identified_by"):
                if gov.get(name):
                    out[name] = gov[name]
            if gov.get("registration") and "registration" not in out:
                out["list_registration"] = gov["registration"]
        # A federal law-enforcement registrant not on the list: from this registry, or published by another
        # integration's (fed) when this one has no row. Lit, as Live Track Aircraft's owner rules light it.
        registrant = entry is None and (category == "Federal law enforcement" or (fed is not None and gov is None))
        if registrant and gov is None and fed is not None:
            # ! A FEDERAL REGISTRANT NOT ON THE LIST is drawn as Live Track Aircraft's owner rules draw
            # it: the blue fill, lit (lights_for), named from the FAA registry.
            category = "Federal law enforcement"
            out["identified_by"] = "faa_government"
            for name in ("operator", "operator_short"):
                if fed.get(name):
                    out[name] = fed[name]
            if fed.get("operator"):
                out["operator_name_source"] = "government"
            if fed.get("registration") and "registration" not in out:
                out["list_registration"] = fed["registration"]
        if category:
            out["operator_category"] = category
        if entry is not None and entry.status == el.SOURCED and entry.agency and not out.get("operator_short"):
            out["operator_short"] = entry.agency
        detected = entry is not None and entry.status == el.DETECTED
        charter = entry is not None and entry.status == el.CHARTER
        # ! THE HOVER'S " · <status>" (Lee 2026-10-29 13:45; 06_MAP_CONTRACT.md D4b rule 12): what the list holds,
        # where no agency is named. A charter always says so; a detection only when nothing names an agency.
        if charter:
            out["operator_short"] = LABEL_CHARTER
        elif detected and not out.get("operator_short"):
            out["operator_short"] = LABEL_PIA if out.get("identity_hidden") else LABEL_DETECTED
        sourced = (entry is not None and entry.status == el.SOURCED) or registrant
        if entry is not None and entry.status == el.DETECTED and obs.identity in self.detections:
            out["detected_by"] = self.detections[obs.identity]["detected_by"]
        if entry is not None:
            out["enforcement_status"] = entry.status
            if entry.agency:
                out["enforcement_agency"] = entry.agency
            if entry.entry:
                out["enforcement_entry"] = entry.entry
            if entry.registration and "registration" not in out:
                out["list_registration"] = entry.registration
        tone = lib.tone_for(gov is not None or registrant, icon_category, category, military)
        # ! THE LIGHTS (Lee 2026-10-25 14:14: an aircraft off the list is "drawn normally", meaning
        # Live Track Aircraft's wig-wag): a detection stays unlit under its ring (decisions K, O);
        # a sourced aircraft or a federal registrant glows; anything else takes the owner rules,
        # as Live Track Aircraft's coordinator, so an unlisted police aircraft wig-wags.
        if detected:
            lights = False
        elif sourced:
            lights = lib.LIGHTS_GLOW
        elif charter:
            # ! An ICE Air charter: the steady glow, never the flash (Lee 2026-10-29 00:37, look C4).
            lights = lib.LIGHTS_CHARTER
        else:
            lights = lib.lights_for(category)
        out["entity_picture"] = icons.picture_url(
            key, tone, lib.weight_for(obs.emitter_category),
            lights=lights, detected=detected)
        return out


def marker_label(obs: Observation, rec: dict[str, Any]) -> str:
    """Never blank. A listed aircraft by its agency (section 3.1); a detection says so; else the callsign."""
    status = rec.get("enforcement_status")
    if status == el.DETECTED:
        return LABEL_PIA if rec.get("identity_hidden") else LABEL_DETECTED
    if status == el.CHARTER:
        return LABEL_CHARTER
    if status == el.SOURCED and rec.get("enforcement_agency"):
        return _shorten(rec["enforcement_agency"])
    callsign = (obs.callsign or "").strip()
    if callsign and not _LOOKS_LIKE_REGISTRATION.match(callsign.upper()):
        return callsign
    if rec.get("identity_hidden"):
        return "Identity hidden"
    if rec.get("operator_short"):
        return _shorten(rec["operator_short"])
    if rec.get("operator"):
        return _shorten(rec["operator"])
    return callsign or obs.type_code or obs.identity.upper()
