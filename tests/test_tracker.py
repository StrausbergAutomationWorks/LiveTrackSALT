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
from saw_livetrack import faa_registry as fr  # noqa: E402

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
    {"hex": "a0f500", "status": "sourced", "agency": "FSG", "entry": "us-fl-state-guard"},
])


def registry(rows):
    r = fr.FaaRegistry("unused")
    r.gov._table, r.gov._loaded = rows, True
    return r


# The FAA registry's rows (owner names as the FAA writes them; measured 2026-10-25: the list's 287 agree with it
# but for Florida State Guard's 12 and one FHP aircraft, whose owner is a plain state government).
REG = registry({"A00808": ["N1007G", "DEPARTMENT OF HOMELAND SECURITY", "DC"],
                "A1B2C3": ["N7DP", "TEXAS DEPARTMENT OF PUBLIC SAFETY", "TX"],
                "A0F500": ["N5FG", "STATE OF FLORIDA", "FL"],
                "ABC123": ["N9PD", "CITY OF EXAMPLE POLICE DEPT", "IL"],
                "A0EEEE": ["N808ZT", "DEPARTMENT OF HOMELAND SECURITY", "DC"]})


def obs(h, lat=39.822, lon=-84.045, t=1_800_000_000, **kw):
    base = dict(identity=h, latitude=lat, longitude=lon, observed_at=t, course_deg=90.0,
                speed_kmh=250.0, altitude_m=900.0, emitter_category="A1", type_code="C206")
    base.update(kw)
    return Observation(**base)


FAR = dict(lat=29.4, lon=-98.5)     # San Antonio, well outside a 56 km focus area


def build(circle, listed, skip=frozenset(), cap=250, t=None, reg=REG):
    t = t or tracker.Tracker(CENTRE[0], CENTRE[1], 56.0, reg)
    return t, t.build(circle, listed, LIST, skip, cap)


class TestTroySignal(unittest.TestCase):
    """Lee 2026-10-28: a DHS callsign (TROY...) on an aircraft the list does not know is a detection, watched at once."""

    def test_unlisted_troy_is_a_detection_with_the_ring(self):
        t, out = build([obs("aaa111", callsign="TROY305")], [])
        rec = out["aaa111"]
        self.assertEqual(rec["enforcement_status"], "detected_unconfirmed")
        self.assertEqual(rec["marker_label"], "Detected, unconfirmed")
        self.assertEqual(rec["detected_by"], "callsign TROY")
        self.assertIn("d=1", rec["entity_picture"])
        self.assertNotIn("l=g", rec["entity_picture"])
        self.assertEqual(set(t.detections), {"aaa111"})
        self.assertTrue(t.detections_added)
        self.assertEqual(t.detections["aaa111"]["callsign"], "TROY305")

    def test_watched_nationwide_after_it_leaves_the_focus_area(self):
        t, _ = build([obs("aaa111", callsign="TROY305")], [])
        _, out = build([], [obs("aaa111", t=1_800_000_060, **FAR)], t=t)
        self.assertIn("aaa111", out)
        self.assertTrue(out["aaa111"]["outside_radius"])
        self.assertEqual(out["aaa111"]["enforcement_status"], "detected_unconfirmed")

    def test_kept_when_the_aircraft_is_gone(self):
        t, _ = build([obs("aaa111", callsign="TROY305")], [])
        build([], [], t=t)
        self.assertIn("aaa111", t.detections)

    def test_a_bare_troy_and_four_digits_match_other_words_do_not(self):
        for cs, hit in (("TROY", True), ("TROY7012", True), ("troy71", True), ("TROYAIR1", False),
                        ("TROY12345", False), ("XTROY1", False), ("", False)):
            t, _ = build([obs("aaa112", callsign=cs)], [])
            self.assertEqual("aaa112" in t.detections, hit, cs)

    def test_listed_aircraft_keep_their_status(self):
        t, out = build([obs("a00808", callsign="TROY501"), obs("abc124", callsign="TROY502")], [])
        self.assertEqual(out["a00808"]["enforcement_status"], "sourced")
        self.assertNotIn("detected_by", out["a00808"])
        self.assertNotIn("detected_by", out["abc124"])
        self.assertEqual(t.detections, {})

    def test_cleared_is_never_detected(self):
        t, out = build([obs("def456", callsign="TROY503")], [])
        self.assertEqual(t.detections, {})
        self.assertNotIn("enforcement_status", out["def456"])

    def test_a_government_registrant_is_left_to_the_owner_rules(self):
        t, out = build([obs("a0eeee", callsign="TROY504")], [])
        self.assertEqual(t.detections, {})
        self.assertNotIn("enforcement_status", out["a0eeee"])

    def test_claimed_by_another_integration_still_recorded_not_drawn(self):
        t, out = build([obs("aaa113", callsign="TROY506")], [], skip=frozenset({"aaa113"}))
        self.assertNotIn("aaa113", out)
        self.assertIn("aaa113", t.detections)

    def test_coordinator_watches_and_persists_the_detections(self):
        src = open(os.path.join(COMP, "coordinator.py"), encoding="utf-8").read()
        self.assertIn("set(self.tracker.detections)", src)
        self.assertIn('Store(hass, 1, f"{DOMAIN}.detections")', src)
        self.assertIn("async_save(dict(self.tracker.detections))", src)


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
        self.assertEqual((dhs["operator_short"], dps["operator_short"]), ("DHS", "TX DPS"))
        self.assertEqual(dhs["identified_by"], "faa_government")

    def test_the_fill_is_the_owners_and_the_list_adds_the_glow(self):
        # Lee 2026-10-25: fill normally, the red/blue glow added when listed. The FAA names Florida State
        # Guard's owner a plain state government: orange, lit, its agency from the list.
        _, out = build([], [obs("a0f500", **FAR)])
        r = out["a0f500"]
        self.assertEqual(r["operator_category"], "Government")
        self.assertIn("t=gov", r["entity_picture"])
        self.assertIn("l=g", r["entity_picture"])
        self.assertEqual((r["operator_short"], r["marker_label"]), ("FSG", "FSG"))

    def test_without_a_registry_row_the_fill_is_ordinary_and_still_lit(self):
        _, out = build([], [obs("a00808", **FAR)], reg=None)
        r = out["a00808"]
        self.assertNotIn("operator_category", r)
        self.assertNotIn("t=law", r["entity_picture"])
        self.assertIn("l=g", r["entity_picture"])
        self.assertEqual((r["operator_short"], r["marker_label"]), ("DHS", "DHS"))

    def test_a_detection_is_ringed_over_its_owners_fill(self):
        _, out = build([], [obs("abc123", **FAR)])
        r = out["abc123"]
        self.assertIn("t=police", r["entity_picture"])
        self.assertIn("d=1", r["entity_picture"])
        self.assertNotIn("l=", r["entity_picture"])
        self.assertEqual(r["marker_label"], tracker.LABEL_DETECTED)

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


FED = {"a0ffff": {"registration": "N809EM", "operator": "Department of Homeland Security",
                  "operator_short": "DHS"},
        "def456": {"operator_short": "X"}}       # cleared on the list: stays cleared


class TestFederalRegistrants(unittest.TestCase):
    def test_a_registrant_off_the_list_is_drawn_lit_and_named(self):
        t = tracker.Tracker(CENTRE[0], CENTRE[1], 56.0)   # no registry here: the fields come from FED
        out = t.build([], [obs("a0ffff", **FAR), obs("def456", **FAR)], LIST, federal=FED)
        r = out["a0ffff"]
        self.assertEqual(r["marker_label"], "DHS")
        self.assertIn("l=g", r["entity_picture"])
        self.assertIn("t=law", r["entity_picture"])
        self.assertEqual(r["identified_by"], "faa_government")
        self.assertNotIn("enforcement_status", r)
        self.assertNotIn("def456", out)

    def test_without_the_table_it_is_not_drawn_outside(self):
        _, out = build([], [obs("a0ffff", **FAR)])
        self.assertNotIn("a0ffff", out)

    def test_a_registrant_from_this_registry_is_lit_and_named(self):
        # the coordinator passes this registry's federal hexes with no fields ({}); the row names it
        t = tracker.Tracker(CENTRE[0], CENTRE[1], 56.0, REG)
        out = t.build([], [obs("a0eeee", **FAR)], LIST, federal={"a0eeee": {}})
        r = out["a0eeee"]
        self.assertEqual((r["operator_short"], r["marker_label"]), ("DHS", "DHS"))
        self.assertIn("t=law", r["entity_picture"])
        self.assertIn("l=g", r["entity_picture"])
        self.assertEqual(r["list_registration"], "N808ZT")

    def test_the_registrys_short_name_before_the_lists(self):
        lst = reader([{"hex": "a0f501", "status": "sourced", "agency": "FHP", "entry": "us-fl-fhp"}])
        t = tracker.Tracker(CENTRE[0], CENTRE[1], 56.0, registry({"A0F501": ["N6HP", "FLORIDA HIGHWAY PATROL", "FL"]}))
        r = t.build([], [obs("a0f501", **FAR)], lst)["a0f501"]
        self.assertEqual(r["operator_short"], "FL Hwy Patrol")
        self.assertEqual(r["marker_label"], "FHP")              # the marker keeps the list's agency

    def test_a_federal_registrant_inside_glows_by_owner_class(self):
        # inside the focus area, not on the list, nothing published: the owner rules light it, as Live Track Aircraft
        _, out = build([obs("a0eeee")], [])
        pic = out["a0eeee"]["entity_picture"]
        self.assertIn("t=law", pic)
        self.assertIn("l=g", pic)

    def test_a_military_federal_owner_from_the_feed_alone(self):
        # no registry row, nothing published: the feed's flags and owner text decide, and nothing raises
        _, out = build([obs("aaaaab", db_flags=1, own_op="FEDERAL BUREAU OF INVESTIGATION")], [], reg=None)
        r = out["aaaaab"]
        self.assertEqual((r["operator_category"], r["operator_short"]), ("Federal law enforcement", "FBI"))
        self.assertIn("t=mil", r["entity_picture"])

    def test_an_unlisted_police_aircraft_inside_wigwags_as_in_live_track_aircraft(self):
        # Lee 2026-10-25 14:14: off the list is "drawn normally", meaning Live Track Aircraft's wig-wag
        _, out = build([obs("abc125", callsign="N9PD")], [], reg=registry({"ABC125": ["N9PD", "CITY OF EXAMPLE POLICE DEPT", "IL"]}))
        pic = out["abc125"]["entity_picture"]
        self.assertIn("t=police", pic)
        self.assertIn("l=w", pic)
        self.assertNotIn("l=g", pic)
        self.assertNotIn("d=1", pic)
        self.assertEqual(out["abc125"]["operator_short"], "Example Police")

    def test_the_cap_keeps_a_registrant(self):
        t = tracker.Tracker(CENTRE[0], CENTRE[1], 56.0)
        circle = [obs("%06x" % (0xc00000 + i), lat=39.822 + i * 0.001) for i in range(5)] + [obs("a0ffff", lat=39.872)]
        out = t.build(circle, [], LIST, max_aircraft=2, federal=FED)
        self.assertIn("a0ffff", out)


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

    def test_the_focus_area_is_asked_as_this_integration_and_credits_its_feed(self):
        # 0.2.14: a focus area inside another integration's circle costs no request; the feed is credited
        coord = dict(self._code())["coordinator.py"]
        self.assertIn("consumer=CONSUMER)", coord)
        self.assertIn("sources=ap.FI_ONLY", coord)
        self.assertIn('rec["feed"] = self.circle_source', coord)
        geo = dict(self._code())["geo_location.py"]
        self.assertIn('LOL_ATTRIBUTION if rec.get("feed") == "adsb.lol" else FEED_ATTRIBUTION', geo)
        self.assertIn('"saw-livetrack>=0.2.18,<0.3"', dict(self._code())["manifest.json"])

    def test_the_registry_is_loaded_refreshed_and_passed(self):
        init = dict(self._code())["__init__.py"]
        self.assertIn('registry = fr.shared(hass.data, hass.config.path(".storage"))', init)
        self.assertLess(init.index("await registry.load(hass.async_add_executor_job)"),
                        init.index("await coordinator.async_config_entry_first_refresh()"))
        self.assertIn("async_track_time_interval(hass, _check_registry, REGISTRY_TICK)", init)
        coord = dict(self._code())["coordinator.py"]
        self.assertIn("self.registry.gov.federal_law_enforcement_hexes()", coord)
        self.assertIn("Tracker(self.latitude, self.longitude, self.radius_km, registry)", coord)

    def test_never_imports_live_track_aircraft(self):
        for name, text in self._code():
            self.assertIsNone(re.search(r"^\s*(from|import)\s+[.\w]*live_track_aircraft\b", text, re.M), name)


CHARTER_LIST = reader([
    {"hex": "a00808", "status": "sourced", "agency": "DHS", "entry": "us-federal-law-enforcement"},
    {"hex": "a2c4e0", "status": "ice_air_charter", "agency": "ICE", "entry": "ice-air-charter-a2c4e0",
     "registration": "N278GX"},
])


class TestCharter(unittest.TestCase):
    """Backlog 313 (Lee 2026-10-29 00:37): an ICE Air charter airframe."""

    def run_(self, circle, listed, cap=250, t=None):
        t = t or tracker.Tracker(CENTRE[0], CENTRE[1], 56.0, REG)
        return t, t.build(circle, listed, CHARTER_LIST, frozenset(), cap)

    def airliner(self, h="a2c4e0", **kw):
        return obs(h, emitter_category="A3", type_code="A320", callsign="GXA301", **kw)

    def test_drawn_with_the_steady_glow_and_the_question(self):
        _, out = self.run_([self.airliner()], [])
        rec = out["a2c4e0"]
        self.assertEqual(rec["enforcement_status"], "ice_air_charter")
        self.assertEqual(rec["marker_label"], "ICE Air Charter?")
        self.assertIn("l=c", rec["entity_picture"])
        self.assertNotIn("l=g", rec["entity_picture"])
        self.assertNotIn("d=1", rec["entity_picture"])
        # the hover's " · ICE Air Charter?" (Lee 2026-10-29 13:45); the list's agency (ICE) is never put there
        self.assertEqual(rec["operator_short"], "ICE Air Charter?")

    def test_watched_nationwide(self):
        _, out = self.run_([], [self.airliner(**FAR)])
        self.assertIn("a2c4e0", out)
        self.assertTrue(out["a2c4e0"]["outside_radius"])
        self.assertEqual(out["a2c4e0"]["marker_label"], "ICE Air Charter?")

    def test_kept_past_the_cap(self):
        crowd = [obs("b%05x" % i, lat=39.818, lon=-84.050) for i in range(3)]
        _, out = self.run_(crowd + [self.airliner(lat=40.122, lon=-84.050)], [], cap=2)
        self.assertIn("a2c4e0", out)
        self.assertEqual(len(out), 3)

    def test_a_charter_on_its_own_designator_reads_by_name(self):
        _, out = self.run_([obs("a2c4e0", emitter_category="A3", type_code="A320", callsign="GXA6181")], [])
        self.assertEqual(out["a2c4e0"]["airline_short"], "GlobalX")
        self.assertEqual(out["a2c4e0"]["operator_short"], "ICE Air Charter?")
        _, out = self.run_([obs("a2c4e0", emitter_category="A3", type_code="A320", callsign="VELUX46")], [])  # a special callsign has no airline
        self.assertNotIn("airline_short", out["a2c4e0"])

    def test_a_detection_says_so_in_the_hover(self):
        t, out = self.run_([obs("ad0001", callsign="TROY505")], [])
        self.assertEqual(out["ad0001"]["enforcement_status"], el.DETECTED)
        self.assertEqual(out["ad0001"]["operator_short"], tracker.LABEL_DETECTED)

    def test_a_charter_is_never_a_troy_detection(self):
        t, out = self.run_([obs("a2c4e0", callsign="TROY505")], [])
        self.assertEqual(t.detections, {})
        self.assertEqual(out["a2c4e0"]["enforcement_status"], "ice_air_charter")

    def test_the_hex_round_takes_every_watched_status(self):
        with open(os.path.join(COMP, "coordinator.py"), encoding="utf-8") as fh:
            coord = fh.read()
        self.assertIn("self.reader.hexes(*el.WATCHED)", coord)
        self.assertEqual(CHARTER_LIST.hexes(*el.WATCHED), frozenset({"a00808", "a2c4e0"}))


class TestIceAirCallsign(unittest.TestCase):
    """Backlog 313 part 2 (Lee 2026-10-29 22:25-23:10): ICE Air's call signs mark THE FLIGHT."""

    def run_(self, circle, listed, t=None, lst=CHARTER_LIST, skip=frozenset()):
        t = t or tracker.Tracker(CENTRE[0], CENTRE[1], 56.0, REG)
        return t, t.build(circle, listed, lst, skip, 250)

    def jet(self, h, callsign, **kw):
        return obs(h, emitter_category="A3", type_code="A320", callsign=callsign, **kw)

    def test_listed_charter_flying_velux_loses_the_question(self):
        t, out = self.run_([self.jet("a2c4e0", "VELUX46")], [])
        rec = out["a2c4e0"]
        self.assertEqual(rec["marker_label"], "ICE Air Charter")
        self.assertEqual(rec["operator_short"], "ICE Air Charter")
        self.assertEqual(rec["ice_air_flight"], "VELUX")
        self.assertIn("l=c", rec["entity_picture"])
        self.assertEqual(t.detections, {})            # the list already knows it

    def test_a_carrier_designator_is_not_evidence(self):
        _, out = self.run_([self.jet("a2c4e0", "GXA6276")], [])
        self.assertEqual(out["a2c4e0"]["marker_label"], "ICE Air Charter?")
        self.assertNotIn("ice_air_flight", out["a2c4e0"])

    def test_dhs_own_aircraft_keeps_its_glow_and_agency(self):
        t, out = self.run_([self.jet("a00808", "VELUX35")], [])
        rec = out["a00808"]
        self.assertEqual(rec["marker_label"], "DHS")
        self.assertIn("l=g", rec["entity_picture"])
        self.assertEqual(rec["ice_air_flight"], "VELUX")
        self.assertEqual(t.detections, {})

    def test_unlisted_tail_is_a_charter_remembered_and_watched(self):
        t, out = self.run_([self.jet("aa1111", "VELUX32")], [])
        rec = out["aa1111"]
        self.assertEqual(rec["enforcement_status"], el.CHARTER)
        self.assertEqual(rec["marker_label"], "ICE Air Charter")
        self.assertEqual(rec["detected_by"], "callsign VELUX")
        self.assertIn("l=c", rec["entity_picture"])
        self.assertNotIn("d=1", rec["entity_picture"])
        det = t.detections["aa1111"]
        self.assertEqual((det["status"], det["entry"], det["callsign"]), (el.CHARTER, "callsign-velux", "VELUX32"))
        self.assertTrue(t.detections_added)
        # its next flight, on the carrier's own designator: still watched, the question mark back
        t, out = self.run_([self.jet("aa1111", "BBQ8252", t=1_800_000_060)], [], t=t)
        self.assertEqual(out["aa1111"]["marker_label"], "ICE Air Charter?")
        self.assertEqual(out["aa1111"]["operator_short"], "ICE Air Charter?")
        self.assertNotIn("ice_air_flight", out["aa1111"])
        # and nationwide, from the hex round, far outside the focus area
        t, out = self.run_([], [self.jet("aa1111", None, t=1_800_000_120, **FAR)], t=t)
        self.assertIn("aa1111", out)
        self.assertTrue(out["aa1111"]["outside_radius"])

    def test_tyson_and_tys_too(self):
        for h, cs, fam in (("aa2222", "TYSON43", "TYSON"), ("aa3333", "TYS44", "TYS")):
            t, out = self.run_([self.jet(h, cs)], [])
            self.assertEqual(out[h]["marker_label"], "ICE Air Charter", cs)
            self.assertEqual(t.detections[h]["detected_by"], "callsign " + fam)

    def test_never_trumps_757_nor_a_foreign_tys(self):
        for h, cs in (("aa3410", "TYSON1"), ("aa3410", "TYSON12"), ("e48a31", "TYS44")):
            t, out = self.run_([self.jet(h, cs)], [])
            self.assertEqual(t.detections, {}, cs)
            self.assertNotIn("ice_air_flight", out[h])
            self.assertNotIn("enforcement_status", out[h])

    def test_cleared_tail_marked_for_the_flight_only(self):
        # a US hex: LIST's cleared def456 is outside A00000-AFFFFF, so the rule ignores it (also right)
        cleared = reader([{"hex": "aaf29f", "status": "cleared", "entry": "avelo-ice-charter-aaf29f"}])
        t, out = self.run_([self.jet("aaf29f", "VELUX12")], [], lst=cleared)
        rec = out["aaf29f"]
        self.assertEqual(t.detections, {})            # the list decides whether to reopen it
        self.assertTrue(rec["ice_air_charter_flight"])
        self.assertEqual(rec["marker_label"], "ICE Air Charter")
        self.assertIn("l=c", rec["entity_picture"])
        self.assertNotIn("enforcement_status", rec)

    def test_an_ice_air_flight_is_kept_past_the_cap(self):
        cleared = reader([{"hex": "aaf29f", "status": "cleared", "entry": "avelo-ice-charter-aaf29f"}])
        crowd = [obs("b%05x" % i, lat=39.818, lon=-84.050) for i in range(3)]
        t = tracker.Tracker(CENTRE[0], CENTRE[1], 56.0, REG)
        out = t.build(crowd + [self.jet("aaf29f", "VELUX12", lat=40.122, lon=-84.050)], [], cleared, frozenset(), 2)
        self.assertIn("aaf29f", out)
        self.assertEqual(len(out), 3)

    def test_unlisted_dhs_registrant_keeps_the_owner_rules(self):
        t, out = self.run_([self.jet("a0eeee", "VELUX35")], [])      # REG: DEPARTMENT OF HOMELAND SECURITY
        self.assertEqual(t.detections, {})
        self.assertNotIn("ice_air_charter_flight", out["a0eeee"])
        self.assertEqual(out["a0eeee"]["ice_air_flight"], "VELUX")

    def test_troy_detection_later_seen_as_velux_becomes_a_charter(self):
        t, _ = self.run_([self.jet("aa4444", "TROY705")], [])
        self.assertNotIn("status", t.detections["aa4444"])
        t.detections_added = False
        t, out = self.run_([self.jet("aa4444", "VELUX40", t=1_800_000_060)], [], t=t)
        self.assertEqual(t.detections["aa4444"]["status"], el.CHARTER)
        self.assertTrue(t.detections_added)
        self.assertEqual(out["aa4444"]["marker_label"], "ICE Air Charter")

    def test_a_stored_troy_detection_without_status_stays_a_detection(self):
        t = tracker.Tracker(CENTRE[0], CENTRE[1], 56.0, REG)
        t.detections["aa5555"] = {"entry": "callsign-troy", "detected_by": "callsign TROY", "callsign": "TROY1",
                                  "first_seen": "x", "last_seen": "x"}       # as stored before 0.2.18
        _, out = self.run_([], [self.jet("aa5555", "TROY1", **FAR)], t=t)
        self.assertEqual(out["aa5555"]["enforcement_status"], el.DETECTED)

    def test_remembered_even_inside_another_integrations_circle(self):
        t, out = self.run_([self.jet("aa6666", "VELUX55")], [], skip=frozenset({"aa6666"}))
        self.assertNotIn("aa6666", out)
        self.assertEqual(t.detections["aa6666"]["status"], el.CHARTER)

    def test_the_sensor_lists_the_proposals(self):
        with open(os.path.join(COMP, "coordinator.py"), encoding="utf-8") as fh:
            coord = fh.read()
        with open(os.path.join(COMP, "sensor.py"), encoding="utf-8") as fh:
            sensor = fh.read()
        self.assertIn('"proposed_for_list"', coord)
        self.assertIn('"proposed_for_list"', sensor)


if __name__ == "__main__":
    unittest.main()
