# Live Track Enforcement Aircraft

Immigration and federal law-enforcement aircraft on your Home Assistant map,
wherever they fly, published as `geo_location` entities.

## Status

**In development, not yet installable.** This repository holds the
integration's identity and licence while it is written.

## What it does

* **Draws every aircraft in the public EnforcementAircraft list** wherever ADS-B
  receivers see it: federal law-enforcement aircraft (DHS, CBP, ICE, DOJ, USMS)
  and state and local agencies with a sourced role in immigration enforcement.
  The list is published at
  [StrausbergAutomationWorks/EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)
  (ODbL), every entry with its sources.
* **Draws every aircraft in one focus area you choose**, so it is useful on its
  own.
* **Says how sure it is.** An entry is *sourced*, or *detected, unconfirmed* with
  what was seen. An aircraft whose address looks privacy-protected is labelled
  *Potential PIA*, never more.
* **Worldwide**, like every Live Track integration.

## Works best with Live Track Aircraft

[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft)
shows every aircraft around your home, with its owner, its route and smooth,
accurate motion. Install both and each keeps to what it does best:

* inside Live Track Aircraft's area, Live Track Aircraft draws every aircraft,
  the listed ones included;
* everywhere else, this integration draws the listed aircraft;
* one shared poll serves both, and no aircraft is drawn twice.

Both render on one map: the Live Track family shares one map vocabulary.

## Design

| | |
|---|---|
| Domain | `live_track_enforcement_aircraft` |
| Entities | one `geo_location` entity per aircraft, created and removed as aircraft come and go |
| Identity | ICAO hex, never a callsign |
| Positions | adsb.fi, one request for the whole list |

## Licence

Code: MIT, see `LICENSE`. The EnforcementAircraft list is under the Open
Database License (ODbL) v1.0. Aircraft icons by
[ADS-B Radar](https://adsb-radar.com) for macOS.
