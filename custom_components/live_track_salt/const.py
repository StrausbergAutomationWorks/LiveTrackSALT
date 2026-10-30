"""Constants for Live Track SALT.

Identity is PERMANENT: the domain is fixed at first install and no rename recovers it
(10_SEED/00_START_HERE.md, damage item 2). Reserved by Lee 2026-10-24 01:29.
"""
from __future__ import annotations

DOMAIN = "live_track_salt"

# ! THE TERMS REQUIRE THIS. adsb.fi: "You must cite adsb.fi and include a link to our home page"
# (05_SHARED_LESSONS.md B16a). The EnforcementAircraft list is ODbL v1.0. This integration never asks
# adsb.lol itself; but a focus area inside Live Track Aircraft's circle is answered from that circle's
# answer (saw-livetrack 0.2.14), which may be adsb.lol's, whose data is ODbL 1.0: such an aircraft
# credits adsb.lol (LOL_ATTRIBUTION).
FEED_ATTRIBUTION = "Data from adsb.fi (https://adsb.fi)"
LOL_ATTRIBUTION = "Data from adsb.lol (https://adsb.lol, ODbL 1.0)"
LIST_ATTRIBUTION = ("Contains information from EnforcementAircraft "
                    "(https://github.com/StrausbergAutomationWorks/EnforcementAircraft), "
                    "which is made available under the Open Database License (ODbL) v1.0")
ATTRIBUTION = FEED_ATTRIBUTION + "; " + LIST_ATTRIBUTION
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
VESSEL_LIST_ATTRIBUTION = ("Contains information from EnforcementVessels "
                           "(https://github.com/StrausbergAutomationWorks/EnforcementVessels), "
                           "which is made available under the Open Database License (ODbL) v1.0")

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
