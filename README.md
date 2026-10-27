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

## Map card

Aircraft are drawn by [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
(`custom:live-track-map-card`), the one map every Live Track integration
renders on. It turns each aircraft's icon to its track, labels it with its
`marker_label` (a listed aircraft's agency), shows the glow and the ring, and
moves it between real fixes.

**The card is installed with the integration.** This integration carries a
released copy of the card, serves it, and registers it as a dashboard resource
when Home Assistant starts; there is nothing to download or copy into `www`.
Every Live Track integration does the same, and they keep exactly one resource
row between them: the highest card version any of them carries, never a
downgrade. A card you installed through HACS is left alone. Removing this
integration hands the row to another Live Track integration, or removes it if
none is left. See the card's README, section
[Live Track](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).

If your dashboards' resources are set in YAML (`lovelace: resource_mode: yaml`),
nothing can be registered for you. A Repairs issue then gives the exact line to
add; it looks like this, with the integration's own address in place of the
placeholders:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_enforcement_aircraft/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

If the integration's files are removed (through HACS, say) while it is still
set up, and no other Live Track integration is installed, nothing is left to
tidy the row: remove it in Settings > Dashboards > Resources. To install the
card by hand instead, follow the card's README; the resource row of a
hand-installed copy under `/local/` is pointed at an integration's copy only
when that copy is a newer release.

Give it the aircraft with
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities),
filtering on `domain: geo_location` and
`attributes: {source: live_track_enforcement_aircraft}`. With Live Track
Aircraft installed, add a second filter for `source: live_track_aircraft`: the
two never draw the same aircraft.

Any other map card that shows `geo_location` entities shows the aircraft too,
as plain markers.

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
