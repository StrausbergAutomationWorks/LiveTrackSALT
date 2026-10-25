# Live Track Enforcement Aircraft

Immigration and federal law-enforcement aircraft on your Home Assistant map,
wherever they fly, published as `geo_location` entities.

## Status

**Working, not yet released.** The integration runs, but it is not in HACS
yet and its repository stays private until the first release.

## What it does

* **Draws every aircraft in the public EnforcementAircraft list** wherever ADS-B
  receivers see it: federal law-enforcement aircraft (DHS, CBP, ICE, DOJ, USMS)
  and state and local agencies with a sourced role in immigration enforcement.
  The list is published at
  [StrausbergAutomationWorks/EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)
  (ODbL), every entry with its sources. A listed aircraft is labelled with its
  agency and glows red and blue.
* **Draws every aircraft in one focus area you choose**: a centre anywhere on the
  map and a radius, so it is useful on its own.
* **Says how sure it is.** A *sourced* entry glows. A *detected, unconfirmed*
  entry is never lit: it is labelled so and drawn under a dashed white ring. An
  aircraft whose address looks privacy-protected is labelled *Potential PIA*,
  never more.
* **Worldwide**, like every Live Track integration.

## Works best with Live Track Aircraft

[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft)
shows every aircraft in a circle you choose, with its owner, its route and
smooth, accurate motion. Install both and each keeps to what it does best:

* inside Live Track Aircraft's circle, Live Track Aircraft draws every aircraft,
  the listed ones included;
* everywhere else, this integration draws the listed aircraft, and every aircraft
  in its own focus area;
* with Live Track Aircraft installed, this integration also watches every federal
  law-enforcement aircraft in the FAA registry, including registrations newer
  than the list;
* one shared poll serves both: no aircraft is drawn twice, and a focus area that
  lies inside Live Track Aircraft's circle costs no request of its own.

Live Track Aircraft on its own shows listed aircraft only inside its circle.
Both render on one map: the Live Track family shares one map vocabulary.

## Setup

One entry: the focus area's centre (a marker on a map), its radius in
kilometres, and whether to show listed aircraft outside it.

## Design

| | |
|---|---|
| Domain | `live_track_enforcement_aircraft` |
| Entities | one `geo_location` entity per aircraft, named `Enforcement aircraft <hex>`, created and removed as aircraft come and go; one sensor counting the aircraft shown |
| Identity | ICAO hex, never a callsign |
| Positions | [adsb.fi](https://adsb.fi): one request a minute for the whole list, and the focus area every 15 seconds |
| Shared code | [`saw-livetrack`](https://pypi.org/project/saw-livetrack/): the list reader, the aircraft icons and the shared poll |

## Licence

Code: MIT, see `LICENSE`. The EnforcementAircraft list is under the Open
Database License (ODbL) v1.0. Aircraft positions are from adsb.fi; a focus area
inside Live Track Aircraft's circle uses that circle's answer, which may come
from adsb.lol (ODbL v1.0), and each aircraft credits the feed it came from. Aircraft
icons by [ADS-B Radar](https://adsb-radar.com); the icons drawn for this project
were donated to ADS-B Radar and are under its terms. See `ATTRIBUTION.md`.
