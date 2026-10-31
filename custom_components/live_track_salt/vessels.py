"""Enforcement vessels: the EnforcementVessels list and the vessels it names, heard on aisstream.

The list is the public data repository StrausbergAutomationWorks/EnforcementVessels (ODbL v1.0), release
`data`: enforcementvessels.json and SHA256SUMS. Each row is a Coast Guard vessel a cited release names in
immigration work, by MMSI; the file also carries the THEATRES, boxes where that work happens (Lee 2026-10-30).
! A LISTED VESSEL IS DRAWN AS ENFORCEMENT ONLY INSIDE A THEATRE BOX: the file's own rule. Outside every
theatre it is an ordinary Coast Guard vessel and this integration does not draw it (it is counted).
! POSITIONS: the instance's ONE aisstream client (saw_livetrack.aisstream, saw-livetrack 0.2.19, backlog 315),
its VESSELS connection: the list's MMSIs, nationwide. Live Track Ships' areas are the other connection.
! NEVER AN EMPTY FILTER. aisstream reads an empty FiltersShipMMSI as no filter at all, the whole world
unfiltered; the coordinator subscribes only while the list names at least one MMSI (and saw-livetrack 0.2.20
refuses an empty list itself).
! THE READER IS THE LIBRARY'S since saw-livetrack 0.2.20: saw_livetrack.enforcement_vessels, moved from here by span
(backlog 315 task 5a), because Live Track Ships is its second reader (rule 2). One reader per instance, the same
store key and cache file as before. This module keeps the tracker.
! ONE VESSEL, ONE MARKER (Lee 2026-10-30 22:15, backlog 315 task 5): a vessel another consumer CLAIMS on the shared
aisstream client is not drawn here, only counted (claimed_elsewhere). Live Track Ships claims every vessel it
draws and draws a listed one itself, with the list's look, anywhere. SALT claims nothing: Ships does not skip, so
SALT is the one that steps aside.
! No Home Assistant import and no aiohttp import: the session and the executor come from the caller.
! The list stands alone: no data, code, token or task shared with any other SAW data service (Lee, 2026-10-23).
"""
from __future__ import annotations

import math
import time
from typing import Any

from saw_livetrack.enforcement_vessels import (
    CLEARED, LIST_TONE, Theatre, Vessel, VesselList, attributes, label, lights, norm_mmsi,
)

# ! A VESSEL NOT HEARD FOR 30 MINUTES IS GONE from the map, Live Track Ships' window (its SSOT item 5).
STALE_S = 30 * 60
# A segment longer than this draws no previous_* (the card would slide it across the gap).
MAX_SEGMENT_S = 600
# Below 2 kn a course is noise; the hull's heading is used when the vessel sends one.
COURSE_MIN_KMH = 2 * 1.852
WEIGHT = 0.80               # aircraft_icons.DEFAULT_WEIGHT: every cutter one size, as an aircraft with no category
VESSEL_KEY = "vessel"       # the picture: icons.py


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
        self.claimed_elsewhere = 0                         # listed vessels heard that another consumer draws

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

    def build(self, reader: VesselList, picture_url, skip=frozenset()) -> tuple[dict[str, dict], int]:
        """({mmsi: record} for listed vessels inside a theatre, how many listed vessels were heard outside every
        theatre). Stale vessels are forgotten here. picture_url(key, tone, weight, lights) -> str. skip: the MMSIs
        another consumer claims (saw_livetrack.aisstream claimed_by_others), not drawn wherever they are and
        counted in self.claimed_elsewhere."""
        now = self._clock()
        out: dict[str, dict] = {}
        outside = 0
        self.claimed_elsewhere = 0
        for m in [m for m, (t, _o) in self._last.items() if t < now - STALE_S]:
            self._last.pop(m, None)
            self._prev.pop(m, None)
        for m, (_t, obs) in self._last.items():
            v = reader.vessel(m)
            if v is None or v.status == CLEARED:
                continue
            if m in skip:                  # another integration draws it: one vessel, one marker
                self.claimed_elsewhere += 1
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
            "theatre": theatre.name,
            "observed_at": _iso(obs.observed_at),
            "feed": "aisstream",
            "icon": "mdi:ferry",
        }
        if obs.name:
            rec["vessel_name"] = obs.name
        # ! THE LOOK OF A LISTED VESSEL IS THE LIBRARY'S (saw-livetrack 0.2.21, saw_livetrack.enforcement_vessels; Live
        # Track Ships draws by the same rules): status, agency, entry, hull and list name, and the hover's first line
        # (06_MAP_CONTRACT.md D4b rule 14: "USCGC Benjamin Bottoms (WPC 1132) · USCG"), the list's name else what the
        # vessel broadcasts, the agency at most 22 characters. Unknown values omitted (D0).
        rec.update(attributes(v, obs.name))
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
        # aircraft"): the owner-class fill, which for the Coast Guard is army green (LIST_TONE, "mil", as
        # aircraft_icons.tone_for gives the Coast Guard), and the red/blue glow of a sourced entry.
        rec["entity_picture"] = picture_url(VESSEL_KEY, LIST_TONE, WEIGHT, lights(v) or False)
        # A listed vessel by its agency, as a sourced aircraft (tracker.marker_label): the entry's short form first.
        rec["marker_label"] = label(v)
        return rec
