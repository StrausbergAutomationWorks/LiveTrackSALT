"""tracker.py: what is drawn, how it is labelled and lit, and the motion rules. No Home Assistant.

Run from the repo root: python -m unittest discover -s tests
"""
import json
import os
import re
import unittest

from _load import COMP, load

tracker = load("tracker")
icons = load("icons")
from saw_livetrack import enforcement_list as el  # noqa: E402
from saw_livetrack.adsb_poll import Observation  # noqa: E402

CENTRE = (39.817, -84.050)


def reader(rows):
    r = el.EnforcementList("unused")
    r._install(json.dumps({"name": "EnforcementAircraft", "schema": 1, "built": "x",
                           "aircraft": rows}).encode())
    return r


LIST = reader([
    {"hex": "a00808", "status": "sourced", "agency": "DHS", "entry": "us-federal-law-enforcement",
     "registration": "N1007G"},
    {"hex": "a1b2c3", "status": "sourced", "agency": "TX DPS", "entry": "us-tx-dps"},
    {"hex": "abc123", "status": "detected_unconfirmed"},
    {"hex": "abc124", "status": "detected_unconfirmed"},
    {"hex": "def456", "status": "cleared", "agency": "HOMELAND AVIATION LLC"},
])


def obs(h, lat=39.822, lon=-84.045, t=1_800_000_000, **kw):
    base = dict(identity=h, latitude=lat, longitude=lon, observed_at=t, course_deg=90.0,
                speed_kmh=250.0, altitude_m=900.0, emitter_category="A1", type_code="C206")
    base.update(kw)
    return Observation(**base)


FAR = dict(lat=29.4, lon=-98.5)     # San Antonio, well outside a 56 km focus area


def build(circle, listed, skip=frozenset(), cap=250, t=None):
    t = t or tracker.Tracker(CENTRE[0], CENTRE[1], 56.0)
    return t, t.build(circle, listed, LIST, skip, cap)


class TestWhatIsDrawn(unittest.TestCase):
    def test_sourced_anywhere_with_its_agency_and_the_glow(self):
        _, out = build([], [obs("a00808", **FAR), obs("a1b2c3", **FAR)])
        dhs, dps = out["a00808"], out["a1b2c3"]
        self.assertTrue(dhs["outside_radius"])
        self.assertEqual(dhs["marker_label"], "DHS")
        self.assertEqual(dps["marker_label"], "TX DPS")
        self.assertIn("l=g", dhs["entity_picture"])
        self.assertNotIn("d=1", dhs["entity_picture"])
        self.assertEqual(dhs["operator_category"], "Federal law enforcement")
        self.assertIn("t=law", dhs["entity_picture"])
        self.assertEqual(dps["operator_category"], "Law enforcement")
        self.assertIn("t=police", dps["entity_picture"])
        self.assertEqual(dhs["enforcement_status"], "sourced")
        self.assertEqual(dhs["list_registration"], "N1007G")

    def test_detected_is_ringed_unlit_and_says_so(self):
        _, out = build([], [obs("abc123", **FAR), obs("abc124", db_flags=4, **FAR)])
        d = out["abc123"]
        self.assertEqual(d["marker_label"], tracker.LABEL_DETECTED)
        self.assertIn("d=1", d["entity_picture"])
        self.assertNotIn("l=", d["entity_picture"])
        self.assertEqual(out["abc124"]["marker_label"], tracker.LABEL_PIA)
        self.assertEqual(d["enforcement_status"], "detected_unconfirmed")

    def test_cleared_not_nationwide_but_ordinary_inside(self):
        _, out = build([], [obs("def456", **FAR)])
        self.assertNotIn("def456", out)
        _, out = build([obs("def456", callsign="N462WC")], [])
        rec = out["def456"]
        self.assertNotIn("enforcement_status", rec)
        self.assertNotIn("l=", rec["entity_picture"])
        self.assertNotIn("d=1", rec["entity_picture"])

    def test_unlisted_only_inside(self):
        _, out = build([obs("aaaaaa", callsign="UAL12")], [obs("bbbbbb", **FAR)])
        self.assertEqual(list(out), ["aaaaaa"])
        self.assertEqual(out["aaaaaa"]["marker_label"], "UAL12")

    def test_listed_inside_focus_is_still_lit(self):
        _, out = build([obs("a00808")], [])
        self.assertIn("l=g", out["a00808"]["entity_picture"])
        self.assertEqual(out["a00808"]["marker_label"], "DHS")

    def test_claimed_hexes_are_skipped_in_both_paths(self):
        _, out = build([obs("a00808"), obs("aaaaaa")], [obs("a1b2c3", **FAR)],
                       skip=frozenset({"a00808", "a1b2c3"}))
        self.assertEqual(list(out), ["aaaaaa"])

    def test_cap_drops_ordinary_never_listed(self):
        circle = [obs("%06x" % (0xc00000 + i), lat=39.822 + i * 0.001) for i in range(5)] + [
            obs("a00808", lat=39.872)]
        _, out = build(circle, [], cap=2)
        self.assertIn("a00808", out)
        self.assertEqual(len(out), 3)

    def test_military_flag_fills_green(self):
        _, out = build([obs("aaaaaa", db_flags=1)], [])
        self.assertIn("t=mil", out["aaaaaa"]["entity_picture"])
        self.assertTrue(out["aaaaaa"]["is_military"])

    def test_rotorcraft_layer(self):
        _, out = build([obs("aaaaaa", emitter_category="A7", type_code="AS50")], [])
        self.assertEqual(out["aaaaaa"]["map_layer"], "air_low")
        self.assertEqual(out["aaaaaa"]["icon"], "mdi:helicopter")


class TestMotion(unittest.TestCase):
    def test_previous_fix_and_the_stale_bounce(self):
        t, out = build([obs("aaaaaa", t=1000)], [])
        self.assertNotIn("previous_latitude", out["aaaaaa"])
        _, out = build([obs("aaaaaa", lat=39.832, t=1015)], [], t=t)
        r = out["aaaaaa"]
        self.assertEqual((r["previous_latitude"], r["segment_duration_s"]), (39.822, 15))
        _, out = build([obs("aaaaaa", lat=39.827, t=1010)], [], t=t)   # older: re-publish
        self.assertEqual(out["aaaaaa"]["latitude"], 39.832)

    def test_slow_course_is_held(self):
        t, _ = build([obs("aaaaaa", t=1000, course_deg=90.0)], [])
        _, out = build([obs("aaaaaa", t=1015, lat=39.823, course_deg=200.0, speed_kmh=10.0)], [], t=t)
        self.assertEqual(out["aaaaaa"]["icon_rotation_basis"], "held")
        self.assertEqual(out["aaaaaa"]["icon_rotation_deg"], lib_q(90.0))

    def test_gone_aircraft_forgotten(self):
        t, _ = build([obs("aaaaaa", t=1000)], [])
        build([], [], t=t)
        _, out = build([obs("aaaaaa", t=1015, lat=39.832)], [], t=t)
        self.assertNotIn("previous_latitude", out["aaaaaa"])


def lib_q(b):
    from saw_livetrack import aircraft_icons
    return aircraft_icons.quantise(b)


class TestBoundaries(unittest.TestCase):
    def _code(self):
        out = []
        for name in sorted(os.listdir(COMP)):
            if name.endswith((".py", ".json")):
                with open(os.path.join(COMP, name), encoding="utf-8") as fh:
                    out.append((name, fh.read()))
        return out

    def test_never_filedroutesdb(self):
        for name, text in self._code():
            for word in ("filedroutes", "release_session", "github_frdb", "saw_routes", "ladd"):
                self.assertNotIn(word, text.lower(), "%s names %s" % (name, word))

    def test_never_adsb_lol(self):
        for name, text in self._code():
            code = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
            code = re.sub(r'"""[\s\S]*?"""', "", code)
            self.assertNotIn("FI_THEN_LOL", code, name)
            self.assertNotIn("api.adsb.lol", code, name)

    def test_never_imports_live_track_aircraft(self):
        for name, text in self._code():
            self.assertIsNone(re.search(r"^\s*(from|import)\s+[.\w]*live_track_aircraft\b", text, re.M), name)


if __name__ == "__main__":
    unittest.main()
