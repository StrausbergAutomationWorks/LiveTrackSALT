"""Photos (2026-11-21): an aircraft's Planespotters photo looked up on hover through our own signed-in view
(06_MAP_CONTRACT.md D4i), and a listed vessel's Wikidata/Commons photo by IMO, else MMSI (D4g). The lookups and the
kept answers are the library's (saw_livetrack.aircraft_photos, saw_livetrack.vessel_photos, 0.2.43); their tests
are the library's. These check the wiring here. No real answer of either source is in this file.

Run from the repo root: python -m unittest discover -s tests
"""
import json
import re
import unittest

from _load import load, source
from saw_livetrack import aircraft_photos as AP
from saw_livetrack import vessel_photos as VP

const = load("const")


def _block(src, start, end="\n    def "):
    i = src.index(start)
    j = src.find(end, i + len(start))
    return src[i:j if j > 0 else len(src)]


class Paths(unittest.TestCase):
    def test_our_own_path_under_api(self):
        self.assertEqual(const.PHOTO_URL_BASE, "/api/live_track_salt/photo")
        p = AP.lookup_path(const.PHOTO_URL_BASE, "ABC123")
        self.assertEqual(p, "/api/live_track_salt/photo/abc123")
        # LiveTrackMapCard's D4h/D4i rule: /api/ then letters, digits, _ - / only, no empty segment, <= 200
        self.assertRegex(p, r"^/api/[A-Za-z0-9_\-/]+$")
        self.assertNotIn("//", p)
        self.assertLessEqual(len(p), 200)

    def test_never_a_siblings_path(self):
        self.assertNotIn("live_track_aircraft", const.PHOTO_URL_BASE)
        for name in ("web.py", "geo_location.py", "const.py", "__init__.py"):
            self.assertNotIn("live_track_aircraft_photos", source(name), name)
            self.assertNotIn("/api/live_track_aircraft/", source(name), name)

    def test_none_for_tis_b_or_a_privacy_address(self):
        self.assertIsNone(AP.lookup_path(const.PHOTO_URL_BASE, "~abc123"))
        self.assertIsNone(AP.lookup_path(const.PHOTO_URL_BASE, "abc123", True))


class View(unittest.TestCase):
    def test_signed_in_only_no_store_and_the_shared_store(self):
        web = source("web.py")
        view = _block(web, "class SaltPhotoView", "\n\n\n")
        self.assertNotIn("requires_auth", view.split('"""', 2)[2])     # Home Assistant's default: True
        self.assertIn('url = PHOTO_URL_BASE + "/{hexid}"', view)
        self.assertIn("photos.answer(hass.data, async_get_clientsession(hass), hexid)", view)
        self.assertIn('resp.headers["Cache-Control"] = "no-store"', view)
        self.assertIn("status_code=503", view)
        self.assertIn("status_code=400", view)

    def test_views_registered_once(self):
        web = source("web.py")
        reg = web[web.index("def register"):]
        self.assertIn("if hass.data.get(_VIEWS_KEY):", reg)
        self.assertIn("hass.http.register_view(SaltPhotoView())", reg)
        self.assertIn("hass.http.register_view(EnforcementIconView())", reg)

    def test_the_icon_view_stays_public_and_the_photo_view_does_not(self):
        web = source("web.py")
        self.assertEqual(web.count("requires_auth = False"), 1)
        self.assertLess(web.index("requires_auth = False"), web.index("class SaltPhotoView"))


class Entities(unittest.TestCase):
    def test_aircraft_carry_the_path_unrecorded(self):
        g = source("geo_location.py")
        cls = _block(g, "class EnforcementAircraft", "\nclass ")
        self.assertIn('_unrecorded_attributes = frozenset({"marker_photo_lookup"})', cls)
        self.assertIn('_photos.lookup_path(PHOTO_URL_BASE, self._identity, rec.get("identity_hidden"))', cls)
        self.assertNotIn("marker_photo_lookup", "".join(re.findall(r"_PASSTHROUGH = \((.*?)\)", g, re.S)))

    def test_vessels_carry_the_photo_unrecorded_by_imo_then_mmsi(self):
        g = source("geo_location.py")
        cls = g[g.index("class EnforcementVessel"):]
        self.assertIn('_unrecorded_attributes = frozenset({"marker_photo"})', cls)
        self.assertIn('book.photo(rec.get("imo"), self._mmsi, self._photo_arrived)', cls)
        self.assertIn("book.forget_waiter(self._photo_arrived)", cls)
        self.assertIn("self.hass.data.get(_vphotos.STORE_KEY)", cls)

    def test_the_vessel_record_keeps_a_broadcast_imo_unpublished(self):
        v = source("vessels.py")
        self.assertIn('rec["imo"] = str(imo)', v)
        self.assertIn("1000000 <= imo <= 9999999", v)
        g = source("geo_location.py")
        vessel_pass = re.search(r"_VESSEL_PASSTHROUGH = \((.*?)\)", g, re.S).group(1)
        self.assertNotIn('"imo"', vessel_pass)

    def test_the_book_is_started_once_and_never_blocks_setup(self):
        init = source("__init__.py")
        start = init.index("await vp.shared(")
        self.assertLess(init.rfind("try:", 0, start), start)
        self.assertIn("except Exception:", init[start:start + 600])
        self.assertIn('hass.config.path(".storage")', init[start:start + 300])

    def test_library_store_keys_are_saw_neutral(self):
        self.assertEqual(AP.STORE_KEY, "saw_aircraft_photos")
        self.assertEqual(VP.STORE_KEY, "saw_vessel_photo_book")


class Manifest(unittest.TestCase):
    def test_library_floor(self):
        req = json.loads(source("manifest.json"))["requirements"]
        self.assertIn("saw-livetrack>=0.2.43,<0.3", req)


if __name__ == "__main__":
    unittest.main()
