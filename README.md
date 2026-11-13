# Live Track SALT

Immigration enforcement on your Home Assistant map: the aircraft of ICE, CBP
and the other federal, state and local agencies that take part in it, wherever
they fly, and the Coast Guard vessels used in immigration work where that work
happens, published as `geo_location` entities.

Live Track SALT continues Live Track Enforcement Aircraft under a new name.

## Status

**0.1.0**, the first release. It runs live on its development instance.

## Requirements

- Home Assistant 2026.11 or later.
- No account and no API key needed for aircraft. Two keys of your own are
  optional: an [aisstream.io](https://aisstream.io) key, without which no
  vessels are shown, and an [adsb.lol](https://adsb.lol) key (see
  [Data sources](#data-sources)).
- Home Assistant installs the Python package it needs (`saw-livetrack`) the
  first time the integration loads.

## Installation

### From the Marketplace

Live Track SALT is not in the Marketplace catalog yet. Add it by its link:

1. Go to **Settings > Marketplace** and select **Add from link**.
2. Enter `StrausbergAutomationWorks/LiveTrackSALT`. If asked for the type,
   choose **Integration**.
3. Install **Live Track SALT**.
4. Restart Home Assistant. The Marketplace offers the restart as a repair under
   **Settings > System > Repairs**.

The Marketplace then offers each new release as an update.

### By hand

1. Download the source code of the
   [latest release](https://github.com/StrausbergAutomationWorks/LiveTrackSALT/releases/latest).
2. Copy its `custom_components/live_track_salt` folder into the
   `custom_components` folder of your Home Assistant configuration directory
   (create that folder if it is not there), so the path ends in
   `custom_components/live_track_salt/manifest.json`.
3. Restart Home Assistant.

To update by hand, replace the folder with the new release's and restart.

## What it does

* **Draws every aircraft in the public EnforcementAircraft list** wherever ADS-B
  receivers see it: federal law-enforcement aircraft (DHS, CBP, ICE, DOJ, USMS),
  the charter airliners that fly ICE Air, and state and local agencies with a
  sourced role in immigration enforcement. The list is published at
  [StrausbergAutomationWorks/EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)
  (ODbL), every entry with its sources. A listed aircraft is labelled with its
  agency and glows red and blue.
* **Watches every federal law-enforcement aircraft in the FAA registry** too,
  so a registration newer than the list is still drawn.
* **Marks ICE Air flights.** While an aircraft broadcasts an ICE Air call sign
  it is drawn as an ICE Air charter, whether or not its tail is on the list.
* **Draws every aircraft in one focus area you choose**: a centre anywhere on the
  map and a radius, so it is useful on its own.
* **Draws the Coast Guard vessels used in immigration work**, from the public
  [EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
  list (ODbL), when you give it an aisstream.io key. A listed vessel is drawn
  only inside the list's theatres, the waters where that work happens (around
  Puerto Rico and the Mona Passage, the Windward Passage, the Florida Straits,
  the Bahamas and the Yucatan Channel, and off Southern California); elsewhere it
  is an ordinary Coast Guard vessel and is only counted.
* **Says how sure it is.** A *sourced* entry glows. A *detected, unconfirmed*
  entry is never lit: it is labelled so and drawn under a dashed white ring. An
  aircraft whose address looks privacy-protected is labelled *Potential PIA*,
  never more.
* **Worldwide**, like every Live Track integration.

## Setup

1. Go to **Settings > Devices & services**, select **Add integration**, and
   search for **Live Track SALT**.
2. Fill in the dialog:

   | Field | Default | Limits | What it does |
   |---|---|---|---|
   | Centre of the focus area | your Home Assistant location | anywhere on earth | the middle of the focus area; drag the marker |
   | Radius of the focus area (km) | 56 | 1 to 463 | how far from the centre every aircraft is drawn |
   | Most aircraft shown in the focus area | 250 | 1 to 1000 | a safety ceiling on the focus area; listed aircraft are always shown |
   | Show listed aircraft outside the focus area | on | on or off | off keeps the list to the focus area too |
   | aisstream.io API key, for listed vessels | empty | your own key | optional; without it no vessels are shown. Free at [aisstream.io](https://aisstream.io) |
   | adsb.lol API key | empty | your own key | optional; see [Data sources](#data-sources) |

3. Select **Submit**. The integration's card is titled with the focus area's
   centre and radius, for example `39.817, -84.050 - 56 km`.

Every field can be changed later under **Configure** on that card. One entry
only: the list is the same wherever the focus area is, and a second entry would
draw every listed aircraft twice.

### What it creates

- a sensor, **Live Track SALT aircraft shown**
  (`sensor.live_track_salt_aircraft_shown`): how many aircraft are drawn. Its
  attributes include how many are listed, how many vessels are shown, the state
  of the list and of each feed, and the `adsblol_key` status.
- one `geo_location` entity per aircraft, named `SALT aircraft <hex>`
  (`geo_location.salt_aircraft_<hex>`), created when the aircraft is seen and
  removed when it goes.
- one `geo_location` entity per listed vessel inside a theatre, named
  `SALT vessel <MMSI>` (`geo_location.salt_vessel_<mmsi>`).

Each carries `source: live_track_salt`.

### Putting it on a map

The map card comes with the integration (see [Map card](#map-card)). It needs
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities), which
you can install from the Marketplace. Then add this card to a dashboard, with
your own centre in `x` and `y`:

```yaml
type: custom:auto-entities
card_param: entities
card:
  type: custom:live-track-map-card
  x: 39.82       # latitude
  y: -84.05      # longitude
  zoom: 5
filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_salt
      options:
        display: attribute
        attribute: marker_label
        position_transition: auto
  exclude:
    - state: unavailable
```

With Live Track Aircraft installed, add a second `include` for
`source: live_track_aircraft`: the two never draw the same aircraft.

### What it downloads

Besides the positions (see [Data sources](#data-sources)), each installation
fetches three public files on its own and keeps a copy in Home Assistant's
storage: the [EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)
and [EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
lists, both from GitHub and asked every hour, and the FAA aircraft registry
(about 73 MB, fetched when the copy is a week old), which names the owners of
US-registered aircraft. With Live Track Aircraft installed, both use one copy
of the registry and of the list.

### Removing

1. Delete the entry under **Settings > Devices & services > Live Track SALT**.
   Deleting it withdraws the map card's resource row, or hands it to another
   Live Track integration.
2. Remove Live Track SALT in the Marketplace, or delete the
   `custom_components/live_track_salt` folder if you installed it by hand.
3. Restart Home Assistant.

The downloaded files stay in Home Assistant's `.storage` folder, under names
beginning `saw_`, because other Live Track integrations share them. Delete them
by hand if nothing else uses them.

## Works best with Live Track Aircraft

[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft)
shows every aircraft in a circle you choose, with its owner, its route and
smooth, accurate motion. Install both and each keeps to what it does best:

* inside Live Track Aircraft's circle, Live Track Aircraft draws every aircraft,
  the listed ones included;
* everywhere else, this integration draws the listed aircraft, and every aircraft
  in its own focus area;
* one shared poll serves both: no aircraft is drawn twice, and a focus area that
  lies inside Live Track Aircraft's circle costs no request of its own.

Live Track Aircraft on its own shows listed aircraft only inside its circle.
With Live Track Ships installed, a listed vessel it draws is not drawn here a
second time.

## Map card

Aircraft and vessels are drawn by
[LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
(`custom:live-track-map-card`), the one map every Live Track integration
renders on. It turns each icon to its track, labels it with its
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
    - url: /live_track_salt/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

If the integration's files are removed (through HACS, say) while it is still
set up, and no other Live Track integration is installed, nothing is left to
tidy the row: remove it in Settings > Dashboards > Resources. To install the
card by hand instead, follow the card's README; the resource row of a
hand-installed copy under `/local/` is pointed at an integration's copy only
when that copy is a newer release.

Any other map card that shows `geo_location` entities shows the aircraft and
vessels too, as plain markers.

## Data sources

Aircraft positions come from two free community networks, tried in order:

- **[adsb.fi](https://adsb.fi)** - open data for **personal, non-commercial
  use only**, under the terms in its
  [open data README](https://github.com/adsbfi/opendata). Asked first: one
  request a minute for every listed aircraft at once, and the focus area every
  15 seconds.
- **[adsb.lol](https://adsb.lol)** - data under the
  [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/).
  Asked while adsb.fi is failing, the focus area at most every 30 seconds.

adsb.lol allows 500 requests a day from one address without a key, which an
adsb.fi outage can use up in about two hours. A key of your own raises that: a
free one from [adsb.lol](https://www.adsb.lol/docs/open-data/api), or a feeder's
key if you feed it a receiver. Enter it as **adsb.lol API key** in the dialog. It
is sent only to adsb.lol. If adsb.lol refuses it (wrong or expired), the
integration carries on without it and the sensor's `adsblol_key` attribute reads
`refused` until you change it; otherwise it reads `set`, or `none` with no key.

Vessel positions come from **[aisstream.io](https://aisstream.io)**, a free
service with your own account and key. aisstream.io publishes no terms of use.
The key stays in Home Assistant; nothing in your browser talks to aisstream.io.

The lists are public data repositories of StrausbergAutomationWorks, both under
the [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/):
[EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)
and [EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels).
Owners and agencies come from the FAA's
[Releasable Aircraft Database](https://registry.faa.gov/database/ReleasableAircraft.zip),
a US government publication.

By installing this integration you use these services, and their terms apply to
you. adsb.fi and adsb.lol are volunteer-run; if you can, support them by feeding
a receiver. The integration backs off when a service answers HTTP 429. Each
aircraft credits the feed it came from. See [`ATTRIBUTION.md`](ATTRIBUTION.md).

## Design

| | |
|---|---|
| Domain | `live_track_salt` |
| Identity | an aircraft's ICAO hex, never a call sign; a vessel's MMSI |
| Shared code | [`saw-livetrack`](https://pypi.org/project/saw-livetrack/): the list readers, the aircraft icons, the shared aircraft poll and the shared aisstream client |

## Licence

Code: MIT, see `LICENSE`. The EnforcementAircraft and EnforcementVessels lists
and adsb.lol's data are under the Open Database License (ODbL) v1.0. Aircraft
icons by [ADS-B Radar](https://adsb-radar.com); the icons drawn for this project
were donated to ADS-B Radar and are under its terms. See `ATTRIBUTION.md`.
