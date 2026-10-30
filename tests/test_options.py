"""The focus area is the user's, as Live Track Aircraft's (Lee 2026-10-25 14:14: "adjustable and
moveable just like LTA's"): a map marker, a radius and max_aircraft in both dialogs, read by the
coordinator from the entry, shown on the sensor. Source checks: the flow imports Home Assistant.

Run from the repo root: python -m unittest discover -s tests
"""
import json
import os
import unittest

from _load import COMP, load

const = load("const")


def src(name):
    with open(os.path.join(COMP, name), encoding="utf-8") as fh:
        return fh.read()


class FocusArea(unittest.TestCase):
    def test_limits_match_live_track_aircraft(self):
        self.assertEqual((const.MIN_RADIUS_KM, const.MAX_RADIUS_KM), (1.0, 463.0))
        self.assertEqual((const.MIN_MAX_AIRCRAFT, const.DEFAULT_MAX_AIRCRAFT, const.MAX_MAX_AIRCRAFT),
                         (1, 250, 1000))
        self.assertEqual(const.CONF_MAX_AIRCRAFT, "max_aircraft")
        self.assertFalse(hasattr(const, "MAX_AIRCRAFT"))   # no fixed cap left

    def test_dialog_carries_every_field(self):
        flow = src("config_flow.py")
        for key in ("CONF_LOCATION", "CONF_RADIUS_KM", "CONF_MAX_AIRCRAFT", "CONF_NATIONWIDE"):
            self.assertIn("vol.Required(%s" % key, flow)
        self.assertIn("vol.Range(min=MIN_MAX_AIRCRAFT, max=MAX_MAX_AIRCRAFT)", flow)
        self.assertIn("class EnforcementOptionsFlow(OptionsFlow)", flow)
        self.assertIn("{**self._entry.data, **self._entry.options}", flow)

    def test_coordinator_reads_it_and_a_change_reloads(self):
        co = src("coordinator.py")
        self.assertIn("int(opts.get(CONF_MAX_AIRCRAFT, DEFAULT_MAX_AIRCRAFT))", co)
        self.assertIn("skip, self.max_aircraft, federal)", co)
        self.assertIn("opts = {**entry.data, **entry.options}", co)
        self.assertIn("entry.add_update_listener(_reload)", src("__init__.py"))
        self.assertIn('"max_aircraft"', src("sensor.py"))

    def test_strings_label_it_in_both_steps(self):
        for name in ("strings.json", os.path.join("translations", "en.json")):
            s = json.loads(src(name))
            for step in (s["config"]["step"]["user"], s["options"]["step"]["init"]):
                self.assertEqual(set(step["data"]), {"location", "radius_km", "max_aircraft", "nationwide",
                                                      "aisstream_api_key"}, name)
        self.assertEqual(src("strings.json"), src(os.path.join("translations", "en.json")))


if __name__ == "__main__":
    unittest.main()
