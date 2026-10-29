"""Marker pictures: the library's aircraft, and this integration's ring for a detection.

! THE AIRCRAFT IS saw_livetrack.aircraft_icons, drawn exactly as Live Track Aircraft draws it (backlog
298): the type table, the artwork, render(), the tones and the lights. Icons by ADS-B Radar,
https://adsb-radar.com; the library carries ATTRIBUTION.md beside them.

! THE RING IS THIS INTEGRATION'S OWN (2026-10-24). Decision O (Lee 18:38): a detected_unconfirmed
aircraft is drawn D2, a static dashed white ring over its owner-class fill, unlit, so an unconfirmed
loiterer never looks like a confirmed enforcement aircraft (decision K). Live Track Aircraft leaves a
detection to its owner rules (decision N), so this is the only consumer: it lives here, not in the
library (rule 2: hoist on the second consumer), and its revision is LOCAL_ART_REV.

! IT IS LAID ON render()'s OUTPUT and so depends on two facts of it: the root
viewBox="0 0 <w> <h>" and the closing </svg>. tests/test_icons.py asserts both against the installed
library and pins the ringed pictures by digest.
"""
from __future__ import annotations

import re

from saw_livetrack import aircraft_icons as lib

URL_BASE = "/api/live_track_salt/icon"

# ! THE a= REVISION IS THE LIBRARY'S PLUS OURS. The library bumps ART_REV with any change to its
# pictures; LOCAL_ART_REV bumps with any change to the ring. Both only go up, so the sum does too,
# and a cached picture is never served under a new look.
LOCAL_ART_REV = 0
ART_REV = lib.ART_REV + LOCAL_ART_REV

# The ring, in pixels of the 64 px picture (scaled by the viewBox): a dark band under a white dash,
# so it reads on light tiles and on water. As rendered and chosen, ltea_detected_look.py ring().
RING_INSET_PX = 2.2
RING_DARK = "#1F2327"
RING_DARK_PX = 3.0
RING_WHITE = "#FFFFFF"
RING_WHITE_PX = 1.6
RING_DASH_PX = (4.0, 3.0)

_VIEWBOX = re.compile(r'<svg[^>]*\sviewBox="0 0 ([\d.]+) ([\d.]+)"')


def ring(svg: str) -> str:
    """The picture with the detection ring on top. Raises ValueError if render()'s shape changed."""
    m = _VIEWBOX.search(svg)
    end = svg.rfind("</svg>")
    if not m or end < 0:
        raise ValueError("not render()'s picture: no root viewBox or no </svg>")
    w, h = float(m.group(1)), float(m.group(2))
    px = max(w, h) / 64.0
    cx, cy = w / 2.0, h / 2.0
    r = min(w, h) / 2.0 - RING_INSET_PX * px
    dash = " ".join("%.3f" % (d * px) for d in RING_DASH_PX)
    mark = ('<circle cx="%.3f" cy="%.3f" r="%.3f" fill="none" stroke="%s" stroke-width="%.3f"/>'
            '<circle cx="%.3f" cy="%.3f" r="%.3f" fill="none" stroke="%s" stroke-width="%.3f" '
            'stroke-dasharray="%s"/>'
            % (cx, cy, r, RING_DARK, RING_DARK_PX * px, cx, cy, r, RING_WHITE, RING_WHITE_PX * px, dash))
    return svg[:end] + mark + svg[end:]


def render(key: str, tone: str = "default", weight: float = lib.DEFAULT_WEIGHT,
           lights=False, detected: bool = False) -> str | None:
    """One unrotated, disc-less picture (the card turns the marker); None for an unknown key.

    ! A DETECTION IS NEVER LIT: the ring replaces the lights, whatever is asked.
    """
    path = lib.icon_path(key)
    if path is None:
        return None
    svg = lib.render(path, None, 64, tone, weight, False, False if detected else lights)
    return ring(svg) if detected else svg


def picture_url(key: str, tone: str = "default", weight: float | None = None,
                lights=False, detected: bool = False) -> str:
    """The entity_picture. d=1 asks for the ring and drops the lights; the query is the cache key."""
    query = lib.picture_query(tone, weight, False if detected else lights, ART_REV)
    if detected:
        query = query.replace("&b=0", "&d=1&b=0", 1)
    return "%s/%s/fixed.svg?%s" % (URL_BASE, key, query)
