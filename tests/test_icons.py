"""icons.py: the library's aircraft, unchanged, and this integration's ring for a detection.

! ring_golden.json pins the ringed pictures by digest. A changed ring breaks it ON PURPOSE: bump
LOCAL_ART_REV and regenerate it (ltea_ring_golden.py). A library picture change
breaks it too, through lib.ART_REV, so the a= sum always moves with what is drawn.
"""
import hashlib
import json
import os
import re
import unittest

from _load import HERE, load

icons = load("icons")
from saw_livetrack import aircraft_icons as lib  # noqa: E402

KEYS = sorted(n[:-4] for n in os.listdir(lib.icon_dir()) if n.endswith(".svg"))
GOLDEN = os.path.join(HERE, "ring_golden.json")
CASES = [("a7", "default", 0.78), ("kingair350", "default", 0.8), ("cessna", "gov", 0.66),
         ("pc12", "police", 0.8), ("b0", "default", 0.62), ("tiltrotor", "mil", 0.78)]


def digest(svg):
    return hashlib.sha256(svg.encode("utf-8")).hexdigest()


class TestTheFactsTheRingRestsOn(unittest.TestCase):
    def test_every_library_picture_has_a_root_viewbox_and_ends_in_svg(self):
        self.assertGreaterEqual(len(KEYS), 64)
        for key in KEYS:
            for lights in (False, lib.LIGHTS_GLOW, lib.LIGHTS_WIGWAG):
                svg = lib.render(lib.icon_path(key), None, 64, "default", 0.8, False, lights)
                self.assertRegex(svg, r'^<svg [^>]*viewBox="0 0 [\d.]+ [\d.]+"', key)
                self.assertTrue(svg.endswith("</svg>"), key)

    def test_ring_adds_two_circles_on_top_and_changes_nothing_else(self):
        for key in KEYS:
            plain = icons.render(key, "gov", 0.8)
            ringed = icons.render(key, "gov", 0.8, detected=True)
            end = plain.rfind("</svg>")
            self.assertTrue(ringed.startswith(plain[:end]), key)
            added = ringed[end:-len("</svg>")]
            self.assertEqual(added.count("<circle"), 2, key)
            self.assertIn('stroke-dasharray="', added)
            self.assertIn('fill="none"', added)
            self.assertNotIn("<animate", added)      # static (decision O)

    def test_the_ring_sits_inside_the_marker_circle(self):
        svg = icons.render("a7", detected=True)
        w = float(re.search(r'viewBox="0 0 ([\d.]+)', svg).group(1))
        r = float(re.findall(r'<circle cx="[\d.]+" cy="[\d.]+" r="([\d.]+)"', svg)[-1])
        dark = float(re.findall(r'stroke-width="([\d.]+)"', svg)[-2])
        self.assertLessEqual(r + dark / 2, w / 2)

    def test_a_detection_is_never_lit(self):
        for key in ("a7", "pc12", "kingair350"):
            for lights in (True, lib.LIGHTS_GLOW, lib.LIGHTS_WIGWAG):
                self.assertEqual(icons.render(key, "police", 0.8, lights, detected=True),
                                 icons.render(key, "police", 0.8, False, detected=True))
        self.assertNotIn("l=", icons.picture_url("a7", "law", 0.8, lib.LIGHTS_GLOW, detected=True))

    def test_without_detection_it_is_the_library_picture_byte_for_byte(self):
        for key in KEYS:
            self.assertEqual(icons.render(key, "law", 0.7, lib.LIGHTS_GLOW),
                             lib.render(lib.icon_path(key), None, 64, "law", 0.7, False, lib.LIGHTS_GLOW))

    def test_not_a_render_raises(self):
        with self.assertRaises(ValueError):
            icons.ring("<svg width='64'></svg>")
        self.assertIsNone(icons.render("../etc"))
        self.assertIsNone(icons.render("nosuchicon"))


class TestUrl(unittest.TestCase):
    def test_query(self):
        u = icons.picture_url("a7", "law", 0.8, lib.LIGHTS_GLOW)
        self.assertEqual(u, "%s/a7/fixed.svg?t=law&w=0.80&l=g&b=0&a=%d" % (icons.URL_BASE, icons.ART_REV))
        d = icons.picture_url("a7", "law", 0.8, lib.LIGHTS_GLOW, detected=True)
        self.assertEqual(d, "%s/a7/fixed.svg?t=law&w=0.80&d=1&b=0&a=%d" % (icons.URL_BASE, icons.ART_REV))
        self.assertEqual(icons.ART_REV, lib.ART_REV + icons.LOCAL_ART_REV)
        self.assertTrue(icons.URL_BASE.startswith("/api/live_track_salt/"))


class TestGolden(unittest.TestCase):
    def test_ringed_pictures_are_pinned(self):
        with open(GOLDEN, encoding="utf-8") as fh:
            gold = json.load(fh)
        self.assertEqual(gold["art_rev"], icons.ART_REV,
                         "a picture changed: bump LOCAL_ART_REV (the ring) and regenerate ring_golden.json")
        for key, tone, weight in CASES:
            name = "%s|%s|%.2f" % (key, tone, weight)
            self.assertEqual(digest(icons.render(key, tone, weight, detected=True)), gold["digests"][name], name)


if __name__ == "__main__":
    unittest.main()
