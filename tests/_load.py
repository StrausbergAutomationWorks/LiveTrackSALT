"""Load the component's PURE modules without Home Assistant (const, centre, icons, tracker).

A package shell stands in for custom_components.live_track_enforcement_aircraft so the relative
imports resolve without running __init__.py. saw_livetrack comes from SAW_LIVETRACK_SRC when set (the
library clone's src, for a version not yet on PyPI), else from what is installed.
"""
import importlib
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
COMP = os.path.join(REPO, "custom_components", "live_track_enforcement_aircraft")

_src = os.environ.get("SAW_LIVETRACK_SRC")
if _src and _src not in sys.path:
    sys.path.insert(0, _src)

if "ltea" not in sys.modules:
    _m = types.ModuleType("ltea")
    _m.__path__ = [COMP]
    sys.modules["ltea"] = _m


def load(name: str):
    return importlib.import_module("ltea." + name)


def source(relpath: str) -> str:
    with open(os.path.join(COMP, relpath), encoding="utf-8") as fh:
        return fh.read()
