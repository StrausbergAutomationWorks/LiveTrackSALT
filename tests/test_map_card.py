"""LiveTrackMapCard ships with this integration (backlog 291; card SSOT 67.7): the card is offered in
setup, nothing happens on unload, and only the domain's LAST entry withdraws it. __init__.py imports
Home Assistant, so setup and unload are read from its syntax tree and async_remove_entry is run on
its own against fakes. Also: the released bundle, the verbatim shared file, the manifest, the two
Repairs translations and the .gitattributes rule.

Run from the repo root: python -m unittest discover -s tests
"""
import ast
import asyncio
import hashlib
import json
import os
import re
import unittest

from _load import COMP, REPO

INIT = os.path.join(COMP, "__init__.py")
FRONTEND = os.path.join(COMP, "frontend")
CARD = os.path.join(FRONTEND, "live-track-map-card.js")
# LiveTrackCore reference/shared_map_card.py at 76ca971, SHA-256 of its LF text (bin\lt_reference_drift.py)
REFERENCE_SHA12 = "15251d6fcc54"
# LiveTrackMapCard release v0.1.0 (tools/vendor_card.py checks the asset's .sha256)
RELEASE_SHA12, RELEASE_VERSION, RELEASE_SIZE = "03ca81cd9ce1", "0.1.0+5a0bc01", 962822


def _tree():
    with open(INIT, encoding="utf-8") as fh:
        return ast.parse(fh.read())


def _func(name):
    for node in _tree().body:
        if isinstance(node, ast.AsyncFunctionDef) and node.name == name:
            return node
    raise AssertionError("no async def %s in __init__.py" % name)


def _names(node):
    """Every name and attribute named anywhere under node."""
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
    return out


def _calls(node, name):
    """Awaited calls to `name` under node, in source order."""
    return [n for n in ast.walk(node)
            if isinstance(n, ast.Await) and isinstance(n.value, ast.Call)
            and getattr(n.value.func, "id", getattr(n.value.func, "attr", None)) == name]


class Setup(unittest.TestCase):
    def test_offer_made_once_before_the_first_refresh(self):
        f = _func("async_setup_entry")
        offers = _calls(f, "async_offer_map_card")
        self.assertEqual(len(offers), 1)
        args = offers[0].value.args
        self.assertEqual([ast.unparse(a) for a in args], ["hass", "DOMAIN", "HERE / 'frontend'"])
        refresh = _calls(f, "async_config_entry_first_refresh")
        self.assertEqual(len(refresh), 1)
        self.assertLess(offers[0].lineno, refresh[0].lineno)

    def test_here_is_the_component_folder(self):
        src = ast.unparse(_tree())
        self.assertIn("HERE = Path(__file__).parent", src)
        self.assertIn("from .shared_map_card import async_offer_map_card, async_withdraw_map_card", src)


class Unload(unittest.TestCase):
    def test_unload_never_touches_the_card(self):
        used = _names(_func("async_unload_entry"))
        for name in ("async_offer_map_card", "async_withdraw_map_card", "async_reconcile"):
            self.assertNotIn(name, used)


class Remove(unittest.TestCase):
    """async_remove_entry compiled alone, with a fake withdraw and a fake hass."""

    def _run(self, entry_ids, removed):
        f = _func("async_remove_entry")
        mod = ast.Module(body=[f], type_ignores=[])
        calls = []

        async def withdraw(hass, domain):
            calls.append(domain)

        ns = {"DOMAIN": "live_track_enforcement_aircraft", "async_withdraw_map_card": withdraw,
              "HomeAssistant": object, "ConfigEntry": object}
        exec(compile(ast.fix_missing_locations(mod), INIT, "exec"), ns)

        class E:
            def __init__(self, i):
                self.entry_id = i

        class CE:
            def async_entries(self, domain):
                assert domain == "live_track_enforcement_aircraft"
                return [E(i) for i in entry_ids]

        class H:
            config_entries = CE()

        asyncio.run(ns["async_remove_entry"](H(), E(removed)))
        return calls

    def test_last_entry_withdraws(self):
        self.assertEqual(self._run(["a"], "a"), ["live_track_enforcement_aircraft"])

    def test_another_entry_left_does_not_withdraw(self):
        self.assertEqual(self._run(["a", "b"], "a"), [])

    def test_entry_already_gone_from_the_list_still_withdraws(self):
        self.assertEqual(self._run([], "a"), ["live_track_enforcement_aircraft"])


class Shipped(unittest.TestCase):
    def test_bundle_is_the_release(self):
        with open(CARD, "rb") as fh:
            data = fh.read()
        self.assertEqual(len(data), RELEASE_SIZE)
        self.assertEqual(hashlib.sha256(data).hexdigest()[:12], RELEASE_SHA12)
        first = data.split(b"\n", 1)[0].decode("utf-8")
        self.assertEqual(re.match(r"^/\*! live-track-map-card (\S+) \*/", first).group(1), RELEASE_VERSION)

    def test_nothing_precompressed_beside_it(self):
        # Home Assistant would serve a stale .gz or .br in preference (card SSOT 67.5).
        self.assertEqual(os.listdir(FRONTEND), ["live-track-map-card.js"])

    def test_shared_file_is_the_reference_verbatim(self):
        with open(os.path.join(COMP, "shared_map_card.py"), "rb") as fh:
            lf = fh.read().replace(b"\r\n", b"\n")
        self.assertEqual(hashlib.sha256(lf).hexdigest()[:12], REFERENCE_SHA12)

    def test_manifest(self):
        with open(os.path.join(COMP, "manifest.json"), encoding="utf-8") as fh:
            m = json.load(fh)
        self.assertIn("http", m["dependencies"])
        self.assertIn("lovelace", m["after_dependencies"])
        req = [r for r in m["requirements"] if r.startswith("saw-livetrack")]
        self.assertEqual(req, ["saw-livetrack>=0.2.15,<0.3"])   # 0.2.8 brought map_card
        keys = list(m)
        self.assertEqual(keys[:2], ["domain", "name"])
        self.assertEqual(keys[2:], sorted(keys[2:]))

    def test_repairs_translations(self):
        for name in ("strings.json", os.path.join("translations", "en.json")):
            with open(os.path.join(COMP, name), encoding="utf-8") as fh:
                issues = json.load(fh)["issues"]
            self.assertIn("{url}", issues["map_card_yaml_resource"]["description"], name)
            self.assertIn("{urls}", issues["map_card_duplicate_resources"]["description"], name)
            for key in ("map_card_yaml_resource", "map_card_duplicate_resources"):
                self.assertTrue(issues[key]["title"], name)

    def test_gitattributes_keeps_the_bundle_byte_for_byte(self):
        with open(os.path.join(REPO, ".gitattributes"), encoding="utf-8") as fh:
            rules = [l.strip() for l in fh if l.strip() and not l.startswith("#")]
        self.assertIn("custom_components/*/frontend/** -text -diff", rules)


if __name__ == "__main__":
    unittest.main()
