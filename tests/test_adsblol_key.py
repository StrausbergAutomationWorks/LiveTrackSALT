"""The user's own adsb.lol API key (backlog 336): one optional, masked field in both dialogs, stored stripped ("" so a
cleared key is not read back from entry.data), given to the shared poll in the coordinator, shown on the sensor as
none/set/refused, never the key. The library's tests cover the poll (saw-livetrack 0.2.36, tests/test_adsb_poll.py).
Source checks: the flow and coordinator import Home Assistant.

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


class AdsbLolKey(unittest.TestCase):
    def test_the_option_key(self):
        self.assertEqual(const.CONF_ADSBLOL_KEY, "adsblol_api_key")

    def test_one_masked_optional_field_cleared_by_emptying(self):
        f = src("config_flow.py")
        self.assertEqual(f.count("vol.Optional(CONF_ADSBLOL_KEY, description={\"suggested_value\""), 1)
        self.assertIn("TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))", f)
        self.assertNotIn("default=defaults.get(CONF_ADSBLOL_KEY", f)

    def test_both_flows_store_it_stripped(self):
        f = src("config_flow.py")
        self.assertEqual(f.count('values[CONF_ADSBLOL_KEY] = (values.get(CONF_ADSBLOL_KEY) or "").strip()'), 2)

    def test_the_poll_has_it_before_the_first_request_and_unload_drops_it(self):
        c = src("coordinator.py")
        init = c[c.index("def __init__"):c.index("async def async_sync_vessels")]
        self.assertIn('self.adsblol_key = str(opts.get(CONF_ADSBLOL_KEY) or "").strip()', init)
        self.assertIn("poll.set_key(CONSUMER, self.adsblol_key)", init)
        self.assertIn("poll.release(CONSUMER)", src("__init__.py"))

    def test_the_sensor_shows_the_status_never_the_key(self):
        self.assertIn('"adsblol_key": self.poll.key_status(),', src("coordinator.py"))
        self.assertIn('"adsblol_key"', src("sensor.py"))
        self.assertNotIn('"adsblol_key": self.adsblol_key', src("coordinator.py"))

    def test_labelled_in_both_steps_and_files(self):
        self.assertEqual(src("strings.json"), src(os.path.join("translations", "en.json")))
        d = json.loads(src("strings.json"))
        for step in (d["config"]["step"]["user"], d["options"]["step"]["init"]):
            self.assertTrue(step["data"]["adsblol_api_key"].startswith("adsb.lol API key (optional"))

    def test_requires_the_library_that_sends_it(self):
        self.assertIn("saw-livetrack>=0.2.36,<0.3", json.loads(src("manifest.json"))["requirements"])


if __name__ == "__main__":
    unittest.main()
