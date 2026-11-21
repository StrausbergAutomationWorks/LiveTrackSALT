# Live Track SALT

**English** · [Español](README.es.md) · [All languages](#languages)

**Immigration enforcement for Home Assistant, on one map.** Live Track SALT
puts the aircraft used in immigration enforcement on your Home Assistant map
wherever they fly: the aircraft of ICE, CBP and other federal agencies, the
airliners that fly ICE Air charters, and state and local agencies with a
sourced role in that work. It also draws every aircraft in one area you
choose, and, with a free key, the Coast Guard vessels used in immigration
work where that work happens.

> **Live Track SALT is one module of Live Track**, a family of Home Assistant
> integrations that draw everything that moves, and the weather it moves
> through, on one shared map: aircraft, ships, trains and weather. Install it
> on its own, or beside the other modules
> ([list below](#part-of-live-track-the-other-modules)).

> **Growing, and open to ideas.** Live Track SALT covers listed aircraft
> wherever volunteers' receivers hear them, and listed vessels in four areas
> of water, today, and we are adding more data sources. Is yours missing?
> [Suggest it](#help-it-grow), or add it yourself: we will help you do it.

**Status: 0.1.0, the first release.** Added to the Marketplace by link
([below](#install-it-step-by-step)); it is not in the Marketplace's catalog
yet.

Original work by StrausbergAutomationWorks. Not affiliated with, or endorsed
by, adsb.fi, adsb.lol, aisstream.io, the Federal Aviation Administration
(United States), ADS-B Radar, any government agency, any airline or any
aircraft operator.

> ⚠ **Not a warning system.** It shows public data, usually seconds old and
> sometimes a minute or more, and only aircraft that broadcast where
> volunteers' receivers hear them. An aircraft can fly with its transponder
> off or with its identity hidden, and many aircraft used in this work are not
> on the list yet. **An empty map does not mean that there is no enforcement
> activity near you.** An aircraft on the map says nothing about who is aboard
> or why it is flying.

---

## Contents

1. [Everything it does](#everything-it-does)
2. [Where it works](#where-it-works)
3. [Part of Live Track: the other modules](#part-of-live-track-the-other-modules)
4. [Before you start](#before-you-start)
5. [Install it, step by step](#install-it-step-by-step)
6. [Set it up, step by step](#set-it-up-step-by-step)
7. [Free keys that switch on more, step by step](#free-keys-that-switch-on-more-step-by-step)
8. [Put the map on a dashboard](#put-the-map-on-a-dashboard)
9. [Use it in automations](#use-it-in-automations)
10. [Everything on the map, in detail](#everything-on-the-map-in-detail)
11. [All the entities it creates](#all-the-entities-it-creates)
12. [What it sends and downloads](#what-it-sends-and-downloads)
13. [Help it grow](#help-it-grow)
14. [Languages](#languages)
15. [Credits and licences](#credits-and-licences)
16. [Keywords](#keywords)

---

## Everything it does

### On the map, with nothing to set up

You choose one **focus area** when you set it up: a centre on the map and a
radius around it. It starts at your home. The listed aircraft appear wherever
they fly; the focus area adds every other aircraft inside it.

| What | Where | From |
|---|---|---|
| **Listed aircraft**: every aircraft on the public EnforcementAircraft list, labelled with its agency and drawn with flashing red and blue lights | anywhere in the world where receivers hear them | adsb.fi, or adsb.lol when adsb.fi does not answer; the EnforcementAircraft list |
| **ICE Air charters**: airliners that fly ICE Air charters among other work, labelled "ICE Air Charter?" and drawn with a steady glow | anywhere in the world | the same |
| **ICE Air flights**: while an aircraft broadcasts an ICE Air call sign, its label loses the question mark. An aircraft not on the list that flies one is drawn as a charter and watched everywhere from then on | anywhere for listed aircraft; in your focus area for others | adsb.fi |
| **Federal law-enforcement aircraft in the FAA registry**: drawn in blue with lights, so an aircraft registered after the list was built still appears | anywhere in the world (aircraft registered in the United States) | the FAA aircraft registry (United States) |
| **Detections**: an aircraft not on the list that broadcasts a call sign used by DHS (`TROY` and digits) is labelled "Detected, unconfirmed", drawn without lights under a dashed white ring, and watched everywhere from then on | found in your focus area, then anywhere | adsb.fi |
| **Every aircraft in your focus area**: each drawn as its own type and turned to the direction it flies | your focus area | adsb.fi, or adsb.lol |

### Switched on by your own free key or account

| Free key or account | What it adds |
|---|---|
| **aisstream.io** key | the Coast Guard vessels on the public EnforcementVessels list, inside four areas of water where immigration work happens |
| **adsb.lol** key | more requests a day to adsb.lol, the second source, so the map keeps going during a long adsb.fi outage |

Each takes a few minutes to get: [step by step below](#free-keys-that-switch-on-more-step-by-step).

---

## Where it works

The lists are about immigration enforcement in the United States: every agency
on them is an agency of the United States. Their aircraft are drawn wherever
they fly, which includes flights to other countries.

| Region | What you get | From | Needs |
|---|---|---|---|
| **The whole world** | listed aircraft, and every aircraft in your focus area, wherever volunteers run receivers: dense over North America and Europe, thinner elsewhere, and little or nothing far out at sea | adsb.fi, adsb.lol | nothing |
| **North America**: the Caribbean | listed Coast Guard vessels around Puerto Rico (United States) and in the Mona Passage, in the Windward Passage between Cuba and Haiti, and in the Florida Straits, the Bahamas and the Yucatán Channel | aisstream.io, the EnforcementVessels list | a free key |
| **North America**: United States | federal law-enforcement aircraft from the FAA registry, and owner names for aircraft registered in the United States | the FAA aircraft registry | nothing |
| **North America**: United States | listed Coast Guard vessels off Southern California | aisstream.io, the EnforcementVessels list | a free key |

Not on the list? [Tell us](#help-it-grow). Where someone publishes the data
openly, we will look at adding it.

⚠ **Coverage is good where receivers are, and absent where they are not.** An
aircraft appears only when a volunteer's receiver hears it, or when several
receivers together can locate it.

⚠ **Vessels: aisstream.io heard no vessels at all in the Mona Passage or the
Windward Passage** when we measured in October 2026, so listed vessels there
may not appear. Outside the four areas a listed vessel is ordinary Coast Guard
work: it is counted, not drawn.

---

## Part of Live Track: the other modules

Live Track is a set of Home Assistant integrations, one per kind of moving
thing, all drawn on the same map card. Each works on its own; together they
make one live picture. They share the map card and a Python library
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
so installing another one adds no requests to a source another already reads.

| Module | What it puts on the map | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aircraft overhead from ADS-B, with routes and type icons | released |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | ships and boats from AIS, near you or anywhere | released |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | commuter trains in North America, Europe and Australia | released |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | intercity and long-distance trains in North America, Europe and Australia | released |
| **Live Track SALT** | immigration and federal law-enforcement aircraft and vessels, from public lists (this module) | released |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | weather, storms and natural hazards | released |
| Live Track Stations | departure boards and "time to leave" alerts for every station | planned |
| Live Track Satellites | satellites passing overhead | planned |
| Live Track Freight Trains | freight and work trains where railways publish them | planned |
| Live Track Transit | city buses, trams, ferries and metro | planned |
| Live Track Intercity Buses | intercity and regional coaches | planned |
| Live Track Commuter Buses | commuter buses | planned |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | the shared map card every module draws on | released, installed with each module |

Everything is free and open source. Nothing is held back for sponsors.

---

## Before you start

* **Home Assistant** 2026.11 or later.
* **The Marketplace** (HACS) in your Home Assistant, to install and update it
  the easy way. Without it you can copy the files by hand.
* **Internet access** for Home Assistant: everything comes from public
  sources.
* **Optional: auto-entities** from the Marketplace, to put the markers on the
  map (see [Put the map on a dashboard](#put-the-map-on-a-dashboard)).
* Nothing to pay and no account needed for the aircraft. The two free keys
  above are optional.
* Home Assistant installs the Python package it needs (`saw-livetrack`) by
  itself the first time the integration loads.

---

## Install it, step by step

### From the Marketplace (recommended)

Live Track SALT is not in the Marketplace's catalog yet. Add it by its link:

1. In Home Assistant, open **Settings → Marketplace** (HACS).
2. Choose **Add from link** (or the three-dot menu → **Custom repositories**).
3. Enter `StrausbergAutomationWorks/LiveTrackSALT`. If asked for the type,
   choose **Integration**.
4. Find **Live Track SALT** in the list and choose **Download** or
   **Install**.
5. **Restart Home Assistant**: **Settings → System → Repairs** offers the
   restart, or use **Settings → System → Restart Home Assistant**.

The Marketplace then offers each new release as an update.

### By hand

1. Download the source code of the
   [latest release](https://github.com/StrausbergAutomationWorks/LiveTrackSALT/releases/latest).
2. Copy its `custom_components/live_track_salt` folder into the
   `custom_components` folder of your Home Assistant configuration folder
   (create `custom_components` if it is not there).
3. Restart Home Assistant.

To update by hand, replace the folder with the new release's and restart.

---

## Set it up, step by step

The setup dialog is in English.

1. Open **Settings → Devices & services**.
2. Choose **Add integration** (bottom right) and search for **Live Track
   SALT**.
3. **Centre of the focus area**: drag the marker to the middle of the area
   where you want to see every aircraft. It starts at your home. To keep your
   home private, move it ([why](#what-it-sends-and-downloads)).
4. **Radius of the focus area (km)**: how far from the centre every aircraft
   is shown, from 1 to 463 km (0.6 to 288 miles). If unsure, keep 56 km
   (35 miles).
5. **Most aircraft shown in the focus area (listed aircraft are always shown)**: keep 250. It is a safety
   limit for the focus area only.
6. **Show listed aircraft outside the focus area**: keep it on. Off keeps the
   listed aircraft to the focus area too.
7. Leave the two key fields empty for now. Each is explained below.
8. Choose **Submit**.

That is all. Listed aircraft that are flying appear within a minute, and the
aircraft in your focus area within 15 seconds. The entry is titled with the
centre and radius, for example `39.817, -84.050 - 56 km`. There is one entry
only: the list is the same wherever the focus area is, so a second entry is
refused. Federal law-enforcement aircraft from the FAA registry appear after
the registry has downloaded, usually within the first minutes
([What it sends and downloads](#what-it-sends-and-downloads)).

### Change what it shows: the options

Open **Settings → Devices & services → Live Track SALT → Configure** (the
cog). Every option, in plain words:

| Option | What it does | Default |
|---|---|---|
| **Centre of the focus area** | moves the focus area; the entry's title follows | your home |
| **Radius of the focus area (km)** | how far from the centre every aircraft is shown, 1 to 463 km (0.6 to 288 miles) | 56 km (35 miles) |
| **Most aircraft shown in the focus area (listed aircraft are always shown)** | a safety limit, 1 to 1,000; when more aircraft are in the focus area, the nearest are kept. Listed aircraft and federal law-enforcement aircraft are always kept | 250 |
| **Show listed aircraft outside the focus area** | off keeps the listed aircraft to the focus area too | on |
| **aisstream.io API key, for listed vessels (optional; free at aisstream.io)** | your own key for aisstream.io; without it no vessels are shown ([how to get one](#free-keys-that-switch-on-more-step-by-step)) | empty |
| **adsb.lol API key (optional; your own, sent only to adsb.lol, which is asked while adsb.fi is failing)** | your own key for adsb.lol ([how to get one](#free-keys-that-switch-on-more-step-by-step)) | empty |

Clear a key field to stop using that key.

---

## Free keys that switch on more, step by step

Both are free and personal: each person who installs Live Track SALT gets
their own. Paste each into **Settings → Devices & services → Live Track
SALT → Configure**, and choose **Submit**.

### aisstream.io (listed Coast Guard vessels, four areas of water)

aisstream.io signs you in with a GitHub account, which is also free.

1. Open <https://aisstream.io/account> and choose **Continue with GitHub**.
2. Create a new API key there. The page behind the sign-in is not public, so
   its buttons are not named here; aisstream.io's documentation says that keys
   are made on this page and that a new key is shown only once.
3. Copy the key at once.
4. Paste it into **aisstream.io API key, for listed vessels (optional; free at aisstream.io)**.

⚠ aisstream.io allows three connections for each account and three for each
public internet address. Live Track SALT uses one, for the listed vessels; it
shares it with Live Track Ships when Ships is installed with the same key. If
other programs use the same key or the same internet connection, count them
too.

### adsb.lol (more requests to the second source, the whole world)

Live Track SALT asks adsb.fi first, and asks adsb.lol only while adsb.fi does
not answer. Without a key, adsb.lol allows 500 requests a day from one
internet address, which an adsb.fi outage can use up in about two hours. A key
raises that limit. You do not need one to start.

1. Open <https://www.adsb.lol/request>.
2. Fill in **email**, **What will you use it for?** and **How are you
   complying with the ODbL 1.0 licensing terms?** (name and company are
   optional), and choose **Send request**.
3. Confirm your email address within 24 hours: adsb.lol deletes a request
   that is not confirmed. adsb.lol says that it reads the ODbL answer before
   it sends a key, and that Outlook, Hotmail and Live addresses often reject
   its mail.
4. If you feed adsb.lol with a receiver of your own, use your feeder key
   instead. Your keys are under **My keys** on adsb.lol
   (<https://www.adsb.lol/mmb>).
5. Paste the key into **adsb.lol API key (optional; your own, sent only to adsb.lol, which is asked while adsb.fi is failing)**.

The key is sent only to adsb.lol. If adsb.lol refuses it (wrong or expired),
Live Track SALT carries on without it, and the sensor's `adsblol_key`
attribute shows `refused` until you change the key. Otherwise it shows `set`,
or `none` with no key. No password and no secret is needed.

---

## Put the map on a dashboard

The map is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
the card every Live Track module draws on. **It is installed with Live Track
SALT**: nothing to download, nothing to copy, no resource to add.

1. Open a dashboard, choose the pencil (**Edit dashboard**), then **Add card**.
2. Scroll to the bottom and choose **Manual**.
3. Paste this, and choose **Save**:

```yaml
type: custom:auto-entities
card:
  type: custom:live-track-map-card
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

This form needs [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)
from the Marketplace. With other Live Track modules installed, add one more
`- domain: geo_location` filter for each of their sources
(`live_track_aircraft`, `live_track_ships` and so on).

**Without auto-entities:** LiveTrackMapCard can choose what it shows by
itself, with `entity_filter`. Paste this instead; nothing more to install:

```yaml
type: custom:live-track-map-card
entity_filter:
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

Other Live Track modules go in `entity_filter` the same way: one more
`- domain: geo_location` rule for each source.

**On the map:**

* Each aircraft is drawn as its own type, turned to the direction it flies,
  and moves smoothly between the positions it reports. Each listed vessel is
  drawn as a hull, turned to its heading.
* A listed aircraft's label is its agency (`CBP`, `ICE`). An ICE Air charter
  reads `ICE Air Charter?`, a detection `Detected, unconfirmed`. Other
  aircraft show their call sign, their operator or their type.
* **Point at** a marker to see who operates it and what the list says about
  it. **Click** it for all its details.

The card keeps exactly one dashboard resource row for every Live Track module
together: the newest card version any of them carries, never an older one. A
card you installed yourself through the Marketplace is left alone. If your
dashboards' resources are set in YAML (`lovelace: resource_mode: yaml`),
nothing can be registered for you: a **Repairs** issue then gives the exact
line to add, which looks like this, with the integration's own address in
place of the placeholders:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_salt/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Deleting the Live Track SALT entry hands the row to another Live Track module,
or removes it when none is left. If the integration's files are removed while
its entry is still set up, and no other Live Track module is installed,
remove the card's row yourself in **Settings → Dashboards → Resources**. To
install the card by hand instead, follow the card's README; the row of a copy
you installed by hand under `/local/` is pointed at an integration's copy only
when that copy is a newer release. Any other map card that shows
`geo_location` entities shows the aircraft and vessels too, as plain markers.

---

## Use it in automations

Everything is an ordinary Home Assistant entity, so the automation editor
works with it, no code needed.

**A phone notification when a listed Coast Guard vessel is in one of the four
areas of water** (this needs the aisstream.io key):

1. **Settings → Automations & scenes → Create automation → Create new
   automation**.
2. **When**: **Add trigger**, type `numeric` in the search box, and choose
   **Numeric state crossed threshold**. Choose the **Entity** **Live Track
   SALT aircraft shown**, the **Attribute** **Vessels shown**
   (`vessels_shown`), and under **Above**, **Fixed number**, enter `0`.
3. **Then do**: **Add action**, search for your phone's notification action
   (it carries your phone's name), and enter a message, for example:

   ```text
   A listed Coast Guard vessel is on the map
   ```

4. **Save**.

**Other ideas:** a light that turns on while a listed aircraft is inside your
focus area over Puerto Rico, from the **Show listed aircraft outside the
focus area** option turned off and the `listed_shown` attribute above 0; a
dashboard count of listed aircraft in the air from `listed_shown`; a message
when Live Track SALT proposes a new ICE Air tail for the list, from the
`proposed_for_list` attribute changing; a notification when a vessel appears off Southern
California, from `vessels_shown`.

---

## Everything on the map, in detail

### Listed aircraft

[EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)
is a public list of aircraft used in immigration enforcement, published by
StrausbergAutomationWorks, each entry with its sources: federal
law-enforcement aircraft (DHS, CBP, ICE, DOJ, USMS), the charter airliners
that fly ICE Air, and state and local agencies with a sourced role in
immigration enforcement. On 19 November 2026 it held 416 aircraft, 344 of
them confirmed by their sources.

Live Track SALT asks for every aircraft on the list once a minute, wherever it
is. A listed aircraft is drawn with flashing red and blue lights and labelled
with its agency. Each one credits the list and the feed its position came
from.

Aircraft send their position by radio, a system called ADS-B. Volunteers
around the world run receivers and share what they hear through community
networks: Live Track SALT asks adsb.fi, and adsb.lol when adsb.fi does not
answer. Outside your focus area a listed aircraft moves once a minute.

On each aircraft: `enforcement_status` (`sourced`, `ice_air_charter` or
`detected_unconfirmed`), `enforcement_agency`, `enforcement_entry`,
`operator_short`, `outside_radius`, `identity` (the hex code), `callsign`,
`registration`, `aircraft_type`, `altitude_m`, `speed_kmh`, `course_deg`,
`last_seen`.

### ICE Air charters and ICE Air flights

Some airliners on the list fly ICE Air charters among other work. They are
labelled `ICE Air Charter?` and drawn with a steady glow: the question mark
says that the aircraft flies ICE Air charters, not that this flight is one.

While an aircraft registered in the United States broadcasts an ICE Air call
sign (`VELUX` or `TYSON` with two digits, `TYS` with one to four digits,
or `UX` with two digits, alone or after `VEL` or `GXA`), it is an ICE Air
flight: a charter's label loses its question mark, a listed government
aircraft keeps its own label, and `ice_air_flight` names the call sign family. An aircraft not on the list that flies one in your focus area is
drawn as a charter (`ice_air_charter_flight`), is remembered after a restart,
is watched everywhere from then on, and is listed in the sensor's
`proposed_for_list` attribute.

### Federal law-enforcement aircraft in the FAA registry

Every aircraft that the FAA registry (United States) lists as owned by a
federal law-enforcement agency is watched everywhere too, so an aircraft
registered after the list was built still appears. It is drawn in blue with
lights and named from the registry (`identified_by: faa_government`).

### Detections

An aircraft not on the list that broadcasts a call sign used by DHS (`TROY`
and digits) in your focus area is a detection. It is labelled `Detected,
unconfirmed`, drawn without lights under a dashed white ring, remembered after
a restart, and watched everywhere from then on. An aircraft whose address the
feed marks as privacy-protected is labelled `Potential PIA`, never more.

⚠ A detection is not a finding. Only the list's own review adds an aircraft
to the list.

### Your focus area

Every aircraft inside your focus area is drawn, as in
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
asked for every 15 seconds. When more aircraft are inside it than the option
**Most aircraft shown in the focus area (listed aircraft are always shown)** allows, the nearest are kept; listed aircraft are
always kept.

**With Live Track Aircraft installed**, each keeps to its own part: inside
Live Track Aircraft's area, Live Track Aircraft draws every aircraft, the
listed ones included; everywhere else Live Track SALT draws them. They share
one request to the sources, no aircraft is drawn twice, and a focus area that
lies wholly inside Live Track Aircraft's area costs no request of its own.

### Listed Coast Guard vessels

[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
is a public list of Coast Guard vessels named in immigration work, published
by StrausbergAutomationWorks, each with its source, together with the four
areas of water where that work happens. On 19 November 2026 it held 41
vessels.

With an aisstream.io key, Live Track SALT follows those vessels by their MMSI
numbers. A listed vessel is drawn only inside one of the four areas, in army
green with the red and blue glow, labelled with its agency. Pointing at it
shows its name, for example `USCGC Benjamin Bottoms (WPC 1132) · USCG`. A
vessel not heard for 30 minutes is removed.

**With Live Track Ships installed**, Live Track Ships draws a listed vessel
itself, with the same look, and Live Track SALT leaves it to Ships: one
vessel, one marker.

⚠ Vessels report their position by AIS only where a receiver hears them. When
we measured, at 01:25 Central Time (United States) on 19 November 2026, four
listed vessels were heard, all outside the four areas, and none was drawn.

---

## All the entities it creates

| Entity | What it is |
|---|---|
| `sensor.live_track_salt_aircraft_shown` | **Live Track SALT aircraft shown**: how many aircraft are on the map now, listed and in your focus area together |
| `geo_location.salt_aircraft_…` | one per aircraft, named from its hex code (`geo_location.salt_aircraft_a1b2c3`); it comes and goes with the aircraft |
| `geo_location.salt_vessel_…` | one per listed vessel inside one of the four areas, named from its MMSI (`geo_location.salt_vessel_338926432`); it comes and goes with the vessel |

Each marker carries `source: live_track_salt`, and its state is its distance
from the centre of your focus area in kilometres.

The sensor's attributes say what is happening: `listed_shown` (listed aircraft
on the map), `outside_radius` (aircraft drawn outside your focus area),
`claimed_elsewhere` (aircraft Live Track Aircraft draws instead),
`federal_registrants`, `detected_by_callsign`, `proposed_for_list`,
`vessels_shown`, `vessels_outside_theatres` (listed vessels heard outside the
four areas), `vessels_claimed_elsewhere` (listed vessels Live Track Ships
draws instead), `vessel_list`, `vessel_feed`, `circle_status` (the last
answer for your focus area: `ok`, or what went wrong), `hex_status`,
`source_backoff`, `adsblol_key`, `list`, `radius_km`, `max_aircraft` and
`nationwide`.

⚠ **The markers have no unique ID, on purpose.** Aircraft come and go by the
thousand, and a registry row for each would make Home Assistant slower to
start for nothing. So they cannot be renamed, hidden or given an area in the
interface. Their entity IDs still come from the hex code or the MMSI, so the
same aircraft or vessel always gets the same ID. The sensor has a unique ID
and can be renamed.

⚠ **Your database.** Home Assistant's recorder stores a new row each time an
entity changes, and a moving marker changes at every update: every 15 seconds
in your focus area, once a minute elsewhere. Live Track SALT does not keep
these attributes out of the recorder itself. Unless you want the history of
every marker, keep them out of the recorder. Add this to `configuration.yaml`,
then restart:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.salt_aircraft_*
      - geo_location.salt_vessel_*
```

If your `configuration.yaml` already has a `recorder:` section, add only the
two patterns to it, under `exclude:` and `entity_globs:`. A map card set to
draw history then has no trail to draw. The sensor is cheap to keep: its
attributes take few values, so the recorder stores them once.

---

## What it sends and downloads

**About your location.** The centre and radius of your focus area are sent to
adsb.fi at every update, every 15 seconds, and to adsb.lol while adsb.fi does
not answer. The centre is sent as you set it, and it starts at your home: to
stop sending your home, move the centre away from it (**Configure** →
**Centre of the focus area**) or delete the entry. When your focus area lies
wholly inside Live Track Aircraft's area, nothing is sent for it. The
once-a-minute request carries only the hex codes of the aircraft being
watched. aisstream.io receives your aisstream.io key and the MMSI numbers on
the vessel list, with an area covering the whole world: nothing about where
you are. Your adsb.lol key goes only to adsb.lol. Nothing else about you is
sent anywhere. Each service sees your internet address, as any website does.

**How much.** Sizes measured on 19 November 2026 at 01:25 Central Time
(United States). ⚠ That is night in North America, when far fewer aircraft
fly.

| Source | What and how often | Measured size | After an error |
|---|---|---|---|
| adsb.fi | every aircraft in your focus area, every 15 seconds; one request a minute for every watched aircraft together (the list's, the FAA registry's federal law-enforcement aircraft and the detections) | focus area of 56 km (35 miles): 0.7 KB (1 aircraft); of 463 km (288 miles) over Texas: 18.9 KB (37 aircraft), and 307 KB (535 aircraft) by day on 1 November 2026 at 14:01; the once-a-minute request for the list's 416 aircraft: 3.6 KB (6 in the air) | asks adsb.lol instead. A source that refuses with HTTP 429 is skipped for the time it asks, up to 15 minutes; after two other failures in a row, for 1 minute, doubling up to 10 minutes. A failed focus area keeps its last answer for three updates |
| adsb.lol | the same requests, only while adsb.fi does not answer; the focus area at most every 30 seconds | focus area of 463 km over Texas: 18.3 KB | the same |
| aisstream.io | one connection, kept open; listed vessels arrive as they report | 2 messages, 638 bytes, in 120 seconds | reconnects after a pause of 2 seconds, doubling up to 5 minutes |
| EnforcementAircraft, from GitHub | a checksum file every 6 hours; the list itself only when it has changed | checksum 91 bytes; list 292 KB | tried again at the next hourly check; the copy you have stays in use |
| EnforcementVessels, from GitHub | a checksum file every 6 hours; the list itself only when it has changed | checksum 90 bytes; list 90 KB | the same |
| FAA aircraft registry (United States) | checked once a day; downloaded from `registry.faa.gov` when your copy is 7 days old | 73.1 MB | tried again the next day; the copy you have stays in use |

The downloaded files are shared with other Live Track modules, so each is
downloaded once however many modules you install. They are kept in Home
Assistant's `.storage` folder under names beginning `saw_`. If you remove Live
Track SALT and no other Live Track module uses them, you can delete them by
hand.

---

## Help it grow

Live Track SALT is still growing. We add data sources as we find them, and we
want to know what you would like next.

### Suggest something

Is your area or data source missing? Is something wrong, or hard to
understand? Tell us whichever way is easier for you:

* [**Fill in a short form**](https://github.com/StrausbergAutomationWorks/LiveTrackSALT/issues/new?template=en.yml)
  in English. You need a free GitHub account.
* **Write an email** to
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  No account needed.

Either way, it helps to tell us:

* what you would like to see, and where in the world;
* a link to where the data is published, if you know one (an open-data page,
  a public feed, a service's website): not needed, but it helps;
* your Home Assistant language, if the problem is the wording or a
  translation.

Write in English or in your own language, whichever is easier for you.

An aircraft that belongs on the list goes to
[EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft),
which keeps the list, not to this form.

### Add it yourself, with our help

If you would like to add something yourself, we will help you do it, from
the first question to the finished release. You do not need to be a
developer to start:

* **A translation.** The words in the setup dialog are a short list of
  phrases in one text file. We will show you which file and which lines.
* **A new source.** Tell us where the data is published. We can write the
  code together, or look over yours.
* **Testing where you live.** Install it, look at your part of the map, and
  tell us what is right and what is not.
* **A fix to this README.** If a step did not match what you saw, tell us
  what you saw.

[**Tell us what you have in mind**](https://github.com/StrausbergAutomationWorks/LiveTrackSALT/issues/new?template=en.yml)
or write to
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
and we will reply with the next steps.

---

## Languages

This README: **English**, [Español](README.es.md). Each translated README is
complete. None has yet been read by a native speaker. If Spanish is your
language, please tell us whether its README reads well: see
[Help it grow](#help-it-grow).

The setup dialog and the options are in English only for now, whatever your
Home Assistant language. If you speak another language, you can translate
them yourself: it is a short list of phrases in one file, and [we will help
you do it](#add-it-yourself-with-our-help).

Found a mistake in a translation, or need another language? Tell us at
<https://github.com/StrausbergAutomationWorks/LiveTrackSALT/issues>, or
[translate it with our help](#add-it-yourself-with-our-help).

---

## Credits and licences

* **adsb.fi** (<https://adsb.fi>): aircraft positions, open data for personal,
  non-commercial use only, under the terms in its
  [open data README](https://github.com/adsbfi/opendata), which ask to cite
  adsb.fi and link to its home page. By installing this integration you use
  adsb.fi, and its terms apply to you.
* **adsb.lol** (<https://adsb.lol>): aircraft positions, under the
  [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/).
  By installing this integration you use adsb.lol, and its terms apply to you.
  Both networks are run by volunteers: if you can, support them by feeding a
  receiver.
* **aisstream.io** (<https://aisstream.io>): vessel positions, with your own
  account and key. aisstream.io publishes no terms of use; every vessel
  credits it.
* **EnforcementAircraft** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)):
  the list of aircraft used in immigration enforcement, under the
  [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
* **EnforcementVessels** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/EnforcementVessels)):
  the list of Coast Guard vessels named in immigration work, and the four
  areas of water, under the
  [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
* **The FAA aircraft registry** (Federal Aviation Administration, United
  States): owners of aircraft registered in the United States, and the
  federal law-enforcement aircraft, public data of the United States
  government, downloaded by each installation.
* **ADS-B Radar** (<https://adsb-radar.com>): the aircraft icons, used with
  permission and under its terms. The icons are not covered by this
  repository's MIT licence. Some icons, among them the Beechcraft King Air 350
  in the brand icon, were drawn by StrausbergAutomationWorks and donated to
  ADS-B Radar, so they are under its terms too. The dashed ring drawn over a
  detection is this integration's own. Details are in
  [ATTRIBUTION.md](ATTRIBUTION.md).
* **The vessel icon** is Live Track Ships' hull, drawn for
  StrausbergAutomationWorks, under the MIT licence.
* **The map card** is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, a copy of [ha-map-card](https://github.com/nathan-gs/ha-map-card) by
  nathan-gs, MIT. Its map tiles and their credits are in its README.

None of these organisations made or endorsed this integration.

**Code**: MIT, in [LICENSE](LICENSE).

**For developers:** the entities follow the shared Live Track map contract,
so every module renders on one map; the list readers, the aircraft icons, the
shared aircraft request and the shared aisstream.io connection are in the
[saw-livetrack](https://pypi.org/project/saw-livetrack/) library. The tests
run with `python -m unittest discover -s tests`, with `saw-livetrack`
installed.

---

## Keywords

Home Assistant immigration enforcement · ICE · ICE Air · deportation flights ·
CBP · DHS · Coast Guard · immigration aircraft · enforcement aircraft ·
ADS-B · ADS-B map · AIS · flight tracking · aircraft tracker ·
vuelos de deportación · aviones de ICE · inmigración · control migratorio ·
Guardia Costera · adsb.fi · adsb.lol · aisstream.io · EnforcementAircraft ·
EnforcementVessels · FAA registry · ADS-B Radar · geo_location · map card ·
Lovelace · HACS · Marketplace · Live Track · LiveTrack ·
StrausbergAutomationWorks

---

**Acknowledgement.** StrausbergAutomationWorks acknowledges the Indigenous
peoples of every land and water on this map, all over the world, and pays its
respect to their Elders, past and present.
