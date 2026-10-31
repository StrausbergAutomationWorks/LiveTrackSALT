"""Enforcement vessels (backlog 315): the tracker's records, the claims of other consumers, the picture, and the
coordinator's rule never to subscribe with an empty MMSI filter. Pure: no Home Assistant.
The EnforcementVessels READER is saw_livetrack.enforcement_vessels since saw-livetrack 0.2.20 (moved from vessels.py
with its tests, backlog 315 task 5a); its tests are the library's (tests/test_enforcement_vessels.py there).

Run from the repo root: python -m unittest discover -s tests
"""
import datetime as dt
import hashlib
import json
import os
import tempfile
import unittest
from types import SimpleNamespace

from _load import load, source
from saw_livetrack import enforcement_vessels as EV

V = load("vessels")
icons = load("icons")

UTC = dt.timezone.utc
T0 = dt.datetime(2026, 10, 30, 9, 0, 0, tzinfo=UTC)


def doc(**over):
    d = {
        "name": "EnforcementVessels", "schema": 1, "built": "2026-10-30T07:24:55Z", "license": "ODbL-1.0",
        "theatres": [{"id": "straits", "name": "Florida Straits", "box": [27.5, -79.0, 22.0, -83.5]},
                     {"id": "bad", "name": "bad", "box": [1, 2, 3]}],
        "entries": [{"id": "uscg-active", "short": "USCG"}],
        "vessels": [
            {"mmsi": "367269000", "name": "USCGC Active", "agency": "US Coast Guard", "hull": "WMEC 618",
             "entry": "uscg-active", "status": "sourced"},
            {"mmsi": "338926402", "name": "USCGC Richard Etheridge", "agency": "US Coast Guard", "hull": None,
             "entry": "uscg-re", "status": "sourced"},
            {"mmsi": "366999999", "name": "Cleared", "agency": "US Coast Guard", "entry": "x", "status": "cleared"},
            {"mmsi": "12345", "status": "sourced"},
            "junk",
        ],
    }
    d.update(over)
    return json.dumps(d).encode()


def reader():
    r = EV.VesselList(os.path.join(tempfile.mkdtemp(), EV.CACHE_NAME))
    r._install(doc())
    return r


def obs(mmsi="367269000", lat=24.5, lon=-81.8, at=T0, heading=None, course=None, speed=None, name="CGC ACTIVE"):
    return SimpleNamespace(identity=mmsi, latitude=lat, longitude=lon, observed_at=at, heading_deg=heading,
                           course_deg=course, speed_kmh=speed, name=name)


class Clock:
    def __init__(self, t=1_800_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


def pic(key, tone, weight, lights):
    return "pic:%s:%s:%s:%s" % (key, tone, weight, lights)


class TheLibrarysReader(unittest.TestCase):
    """0.2.20: the reader is the library's; this integration keeps no copy."""

    def test_no_reader_here(self):
        src = source("vessels.py")
        for gone in ("def parse(", "class VesselList", "def shared_list(", "BASE_URL", "SHA256SUMS first"):
            self.assertNotIn(gone, src)
        self.assertIs(V.VesselList, EV.VesselList)
        self.assertIs(V.CLEARED, EV.CLEARED)

    def test_setup_and_coordinator_take_it_from_the_library(self):
        init = source("__init__.py")
        self.assertIn("from saw_livetrack import enforcement_vessels as ev", init)
        self.assertIn('ev.shared_list(hass.data, hass.config.path(".storage", ev.CACHE_NAME))', init)
        self.assertIn("first_vessels = ev.STORE_KEY not in hass.data", init)   # the library's key: one cache load
        self.assertNotIn("from .vessels import CACHE_NAME", init)
        self.assertIn("from saw_livetrack.enforcement_vessels import VesselList", source("coordinator.py"))


class Tracker(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.t = V.VesselTracker(41.9, -87.6, clock=self.clock)
        self.r = reader()

    def test_inside_drawn_outside_counted_unlisted_and_cleared_ignored(self):
        self.t.deliver(obs("367269000", 24.5, -81.8))                 # listed, in the Straits
        self.t.deliver(obs("338926402", 30.4, -87.2))                 # listed, off Pensacola
        self.t.deliver(obs("366999999", 24.6, -81.7))                 # cleared, in the Straits
        self.t.deliver(obs("211000000", 24.7, -81.6))                 # not on the list
        recs, outside = self.t.build(self.r, pic)
        self.assertEqual(sorted(recs), ["367269000"])
        self.assertEqual(outside, 1)
        self.assertEqual(self.t.heard(), 4)
        self.assertEqual(self.t.claimed_elsewhere, 0)

    def test_a_vessel_another_consumer_claims_is_not_drawn(self):
        """Backlog 315 task 5: Live Track Ships draws a listed vessel itself; SALT steps aside, wherever it is."""
        self.t.deliver(obs("367269000", 24.5, -81.8))                 # listed, in the Straits, claimed
        self.t.deliver(obs("338926402", 30.4, -87.2))                 # listed, outside, claimed
        self.t.deliver(obs("366999999", 24.6, -81.7))                 # cleared, claimed: not a listed vessel
        self.t.deliver(obs("211000000", 24.7, -81.6))                 # unlisted, claimed: nothing to step aside from
        recs, outside = self.t.build(self.r, pic, frozenset({"367269000", "338926402", "366999999", "211000000"}))
        self.assertEqual((recs, outside, self.t.claimed_elsewhere), ({}, 0, 2))

    def test_a_claim_released_draws_it_again(self):
        self.t.deliver(obs())
        self.assertEqual(self.t.build(self.r, pic, frozenset({"367269000"}))[0], {})
        self.assertEqual(self.t.claimed_elsewhere, 1)
        self.assertEqual(sorted(self.t.build(self.r, pic, frozenset())[0]), ["367269000"])
        self.assertEqual(self.t.claimed_elsewhere, 0)                 # counted afresh each build

    def test_the_record(self):
        self.t.deliver(obs(heading=271.6, course=90.0, speed=20.0))
        rec = self.t.build(self.r, pic)[0]["367269000"]
        self.assertEqual(rec["map_layer"], "water")
        self.assertEqual(rec["object_ids"], {"mmsi": "367269000"})
        self.assertEqual((rec["enforcement_status"], rec["enforcement_agency"]), ("sourced", "US Coast Guard"))
        self.assertEqual(rec["theatre"], "Florida Straits")
        self.assertEqual((rec["vessel_name"], rec["list_name"], rec["hull"]), ("CGC ACTIVE", "USCGC Active", "WMEC 618"))
        self.assertEqual(rec["marker_label"], "USCG")
        # D4b rule 14: the hover reads "USCGC Active · USCG".
        self.assertEqual((rec["name"], rec["operator_short"]), ("USCGC Active", "USCG"))
        self.assertEqual((rec["icon_rotation_deg"], rec["icon_rotation_basis"], rec["icon_rotatable"]),
                         (272, "heading", True))
        self.assertEqual(rec["observed_at"], "2026-10-30T09:00:00Z")
        # ! The aircraft rules' sourced treatment: Coast Guard fill (mil) and the glow.
        self.assertEqual(rec["entity_picture"], "pic:vessel:mil:0.8:glow")
        self.assertNotIn("previous_latitude", rec)

    def test_label_falls_back_to_agency(self):
        self.t.deliver(obs("338926402", 24.5, -81.8))
        self.assertEqual(self.t.build(self.r, pic)[0]["338926402"]["marker_label"], "US Coast Guard")

    def test_hover_agency_falls_back_to_the_agency(self):
        self.t.deliver(obs("338926402", 24.5, -81.8, name="CG RICHARD ETHERIDGE"))
        rec = self.t.build(self.r, pic)[0]["338926402"]
        self.assertEqual((rec["name"], rec["operator_short"]), ("USCGC Richard Etheridge", "US Coast Guard"))

    def _one(self, row, name):
        r = EV.VesselList(os.path.join(tempfile.mkdtemp(), EV.CACHE_NAME))
        r._install(doc(vessels=[dict({"mmsi": "367000001", "status": "sourced"}, **row)]))
        self.t.deliver(obs("367000001", 24.5, -81.8, name=name))
        return self.t.build(r, pic)[0]["367000001"]

    def test_hover_name_is_the_ais_name_when_the_list_has_none(self):
        rec = self._one({"agency": "US Coast Guard", "entry": "uscg-active"}, "  CG NONAME ")
        self.assertEqual((rec["name"], rec["operator_short"]), ("CG NONAME", "USCG"))

    def test_hover_omits_what_is_unknown(self):
        rec = self._one({"name": "   "}, None)
        self.assertNotIn("name", rec)
        self.assertNotIn("operator_short", rec)
        self.assertEqual(rec["marker_label"], "Listed vessel")

    def test_hover_agency_at_most_22_characters(self):
        rec = self._one({"name": "X", "agency": "Customs and Border Protection Air and Marine"}, None)
        self.assertEqual(rec["operator_short"], "Customs and Border Pr…")
        self.assertEqual(len(rec["operator_short"]), 22)
        rec = self._one({"name": "X", "agency": "A" * 22}, None)
        self.assertEqual(rec["operator_short"], "A" * 22)

    def test_rotation(self):
        self.t.deliver(obs(course=90.0, speed=10.0))
        rec = self.t.build(self.r, pic)[0]["367269000"]
        self.assertEqual((rec["icon_rotation_deg"], rec["icon_rotation_basis"]), (90, "course"))
        self.t.deliver(obs(course=90.0, speed=3.0, lat=24.51))             # under 2 kn: a course is noise
        rec = self.t.build(self.r, pic)[0]["367269000"]
        self.assertNotIn("icon_rotation_deg", rec)
        self.assertFalse(rec["icon_rotatable"])

    def test_previous_fix(self):
        self.t.deliver(obs(lat=24.50, at=T0))
        self.t.deliver(obs(lat=24.50, at=T0 + dt.timedelta(seconds=10)))   # same place: no previous
        self.assertNotIn("previous_latitude", self.t.build(self.r, pic)[0]["367269000"])
        self.t.deliver(obs(lat=24.52, at=T0 + dt.timedelta(seconds=40)))
        rec = self.t.build(self.r, pic)[0]["367269000"]
        self.assertEqual((rec["previous_latitude"], rec["segment_duration_s"]), (24.50, 30.0))
        self.t.deliver(obs(lat=24.60, at=T0 + dt.timedelta(seconds=40 + V.MAX_SEGMENT_S + 1)))
        self.assertNotIn("previous_latitude", self.t.build(self.r, pic)[0]["367269000"])

    def test_stale_vessel_forgotten(self):
        self.t.deliver(obs())
        self.clock.t += V.STALE_S + 1
        self.assertEqual(self.t.build(self.r, pic), ({}, 0))
        self.assertEqual(self.t.heard(), 0)

    def test_a_bad_fix_is_ignored(self):
        self.t.deliver(obs(lat=None))
        self.t.deliver(SimpleNamespace(identity="nope", latitude=1, longitude=2))
        self.assertEqual(self.t.delivered, 0)


class Picture(unittest.TestCase):
    def test_vessel_is_a_local_key_drawn_by_the_library(self):
        url = icons.picture_url(V.VESSEL_KEY, "mil", V.WEIGHT, "glow")
        self.assertTrue(url.startswith(icons.URL_BASE + "/vessel/fixed.svg?"))
        self.assertIn("&l=g", url)
        svg = icons.render(V.VESSEL_KEY, "mil", V.WEIGHT, "glow")
        self.assertTrue(svg and svg.startswith("<svg") and "</svg>" in svg)
        self.assertNotEqual(svg, icons.render(V.VESSEL_KEY, "mil", V.WEIGHT, False))
        self.assertTrue(os.path.exists(icons.LOCAL_ICONS["vessel"]))

    def test_vessel_art_is_ships_generic_hull(self):
        with open(icons.LOCAL_ICONS["vessel"], "rb") as fh:
            self.assertEqual(hashlib.sha256(fh.read()).hexdigest()[:16], "7b5c429cb2384bb7")


class Wiring(unittest.TestCase):
    def test_never_an_empty_filter(self):
        co = source("coordinator.py")
        body = co[co.index("async def async_sync_vessels"):co.index("async def async_stop_vessels")]
        self.assertLess(body.index("if not want:"), body.index("client.add_vessels("))
        self.assertIn("self.aisstream_key and self.vessel_reader is not None", body)

    def test_others_claims_are_skipped_and_none_made(self):
        """Backlog 315 task 5: SALT skips what another consumer claims on the aisstream client and claims nothing."""
        co = source("coordinator.py")
        self.assertIn("ais_client.shared(self.hass.data).claimed_by_others(VESSEL_CONSUMER)", co)
        self.assertIn("self.vessels.build(self.vessel_reader, icons.picture_url, vessel_skip)", co)
        self.assertIn('"vessels_claimed_elsewhere": self.vessels.claimed_elsewhere', co)
        self.assertNotIn("claim(VESSEL_CONSUMER", co)
        self.assertIn('"vessels_claimed_elsewhere"', source("sensor.py"))

    def test_entity_name_and_unload(self):
        geo = source("geo_location.py")
        self.assertIn('self._attr_name = f"SALT vessel {mmsi}"', geo)
        passthrough = geo[geo.index("_VESSEL_PASSTHROUGH = ("):geo.index("async def async_setup_entry")]
        self.assertIn('"name", "operator_short"', passthrough)
        self.assertIn("await coordinator.async_stop_vessels()", source("__init__.py"))

    def test_key_is_optional(self):
        flow = source("config_flow.py")
        self.assertIn("vol.Optional(CONF_AISSTREAM_KEY", flow)


if __name__ == "__main__":
    unittest.main()
