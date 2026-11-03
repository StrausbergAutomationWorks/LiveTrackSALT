"""Constants for Live Track SALT.

Identity is PERMANENT: the domain is fixed at first install and no rename recovers it
(10_SEED/00_START_HERE.md, damage item 2). Reserved by Lee 2026-10-24 01:29.
"""
from __future__ import annotations

DOMAIN = "live_track_salt"

# ! THE TERMS REQUIRE THIS. adsb.fi: "You must cite adsb.fi and include a link to our home page"
# (05_SHARED_LESSONS.md B16a). The EnforcementAircraft list is ODbL v1.0. adsb.lol's data is ODbL 1.0, and an
# aircraft from it credits it (LOL_ATTRIBUTION): this integration asks adsb.lol only while adsb.fi is failing (Lee
# 2026-11-02 22:11), and a focus area inside Live Track Aircraft's circle is answered from that circle's answer
# (saw-livetrack 0.2.14), which may be adsb.lol's.
FEED_ATTRIBUTION = "Data from adsb.fi (https://adsb.fi)"
LOL_ATTRIBUTION = "Data from adsb.lol (https://adsb.lol, ODbL 1.0)"
LIST_ATTRIBUTION = ("Contains information from EnforcementAircraft "
                    "(https://github.com/StrausbergAutomationWorks/EnforcementAircraft), "
                    "which is made available under the Open Database License (ODbL) v1.0")
ATTRIBUTION = FEED_ATTRIBUTION + "; " + LOL_ATTRIBUTION + "; " + LIST_ATTRIBUTION
USER_AGENT = ("LiveTrackSALT/0.1 "
              "(+https://github.com/StrausbergAutomationWorks/LiveTrackSALT)")

# The consumer name this integration registers in the shared poll (saw_livetrack.adsb_poll).
CONSUMER = DOMAIN
# ! ENFORCEMENT VESSELS (backlog 315, 2026-10-30): the consumer on the instance's shared aisstream client
# (saw_livetrack.aisstream), its VESSELS connection, and the user's own aisstream.io API key (optional: no key,
# no vessels). aisstream publishes no terms (Live Track Ships SSOT item 250); credited anyway.
VESSEL_CONSUMER = DOMAIN + ":vessels"
CONF_AISSTREAM_KEY = "aisstream_api_key"
AIS_ATTRIBUTION = "Data: aisstream.io (https://aisstream.io)"
# The list's ODbL line is the library's since saw-livetrack 0.2.21 (the same text; Live Track Ships credits by it).
from saw_livetrack.enforcement_vessels import LIST_ATTRIBUTION as VESSEL_LIST_ATTRIBUTION  # noqa: E402

# --- configuration keys (the focus area is stored as two numbers, as Live Track Aircraft's centre) ---
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_RADIUS_KM = "radius_km"
CONF_NATIONWIDE = "nationwide"
# ! A DIALOG FIELD, NEVER STORED: centre.py turns it into CONF_LATITUDE and CONF_LONGITUDE.
CONF_LOCATION = "location"

DEFAULT_RADIUS_KM = 56.0
MIN_RADIUS_KM = 1.0
MAX_RADIUS_KM = 463.0           # adsb.fi's own ceiling is 250 nm
DEFAULT_NATIONWIDE = True

# ! 15 s, Live Track Aircraft's measured floor: at 5 s, 196 of 360 requests returned HTTP 429.
SCAN_INTERVAL_S = 15
# ! While adsb.fi is out the focus area asks adsb.lol at most this often, half the cadence: two consumers polling adsb.lol
# every 15 s from one IP had half their requests refused (05_SHARED_LESSONS.md B16, measured 2026-09-22), and a refusal
# backs off the feed Live Track Aircraft is then living on.
LOL_CIRCLE_EVERY_S = 30.0
MAX_TRANSIENT_FAILURES = 3
# ! THE FOCUS AREA'S CAP IS THE USER'S, as Live Track Aircraft's max_aircraft (Lee 2026-10-25 14:14:
# the focus area "adjustable and moveable just like LTA's"). A guard rail on the focus area, not a
# display control; listed aircraft and registrants are never dropped (tracker.build).
CONF_MAX_AIRCRAFT = "max_aircraft"
DEFAULT_MAX_AIRCRAFT = 250
MIN_MAX_AIRCRAFT = 1
MAX_MAX_AIRCRAFT = 1000
MAX_SEGMENT_S = 300
SLOW_GROUND_SPEED_KMH = 30.0

# The list's rule entry for every federal law-enforcement registrant (EnforcementAircraft entries).
FEDERAL_RULE = "us-federal-law-enforcement"
