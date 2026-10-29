"""The entity names, and the ids Home Assistant derives from them (no unique_id on aircraft; the sensor
has no device), so they never collide with a sibling's: Live Track Aircraft's geo_location.aircraft_<hex>,
Live Track Enforcement Aircraft's geo_location.enforcement_aircraft_<hex> and sensor.aircraft_shown.
geo_location.py and sensor.py import Home Assistant, so both are read from their syntax trees.

Run from the repo root: python -m unittest discover -s tests
"""
import ast
import os
import re
import unittest

from _load import COMP


def _tree(name):
    with open(os.path.join(COMP, name), encoding="utf-8") as fh:
        return ast.parse(fh.read())


def _slug(text):
    """The entity-id part Home Assistant's slugify gives for these ASCII names."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _aircraft_name_parts():
    for node in ast.walk(_tree("geo_location.py")):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Attribute) and node.targets[0].attr == "_attr_name"
                and isinstance(node.value, ast.JoinedStr)):
            return node.value.values
    raise AssertionError("no f-string self._attr_name in geo_location.py")


class AircraftName(unittest.TestCase):
    def test_prefix_is_salt_aircraft(self):
        parts = _aircraft_name_parts()
        self.assertIsInstance(parts[0], ast.Constant)
        self.assertEqual(parts[0].value, "SALT aircraft ")

    def test_hex_is_upper_case_identity(self):
        parts = _aircraft_name_parts()
        self.assertEqual(len(parts), 2)
        self.assertEqual(ast.unparse(parts[1].value), "identity.upper()")

    def test_id_is_salt_aircraft_hex_and_collides_with_no_sibling(self):
        slug = _slug(_aircraft_name_parts()[0].value + "A1B2C3")
        self.assertEqual(slug, "salt_aircraft_a1b2c3")
        self.assertFalse(slug.startswith(("aircraft_", "enforcement_aircraft_")))

    def test_docstring_names_the_id(self):
        doc = ast.get_docstring(_tree("geo_location.py"))
        self.assertIn('"SALT aircraft <HEX>"', doc)
        self.assertIn("geo_location.salt_aircraft_<hex>", doc)


class SensorName(unittest.TestCase):
    def test_status_sensor_id(self):
        names = [n.value.value for n in ast.walk(_tree("sensor.py"))
                 if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                 and n.targets[0].id == "_attr_name" and isinstance(n.value, ast.Constant)]
        self.assertEqual(names, ["Live Track SALT aircraft shown"])
        self.assertEqual(_slug(names[0]), "live_track_salt_aircraft_shown")


if __name__ == "__main__":
    unittest.main()
