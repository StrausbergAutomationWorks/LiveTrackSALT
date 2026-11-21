# Attribution

## Aircraft positions: adsb.fi and adsb.lol

Live positions are fetched at runtime. Nothing from either service is shipped in this repository.

**adsb.fi** - https://adsb.fi. Terms, as stated in https://github.com/adsbfi/opendata: the open data is
for personal, non-commercial use only; it may not be licensed, sold, rented or leased; it is provided
as-is; users must cite adsb.fi and link to its home page. This file, the Data sources section of
`README.md`, and the attribution shown on every entity are that citation.

**adsb.lol** - https://adsb.lol. Its data is under the
[Open Database License (ODbL) v1.0](https://opendatacommons.org/licenses/odbl/1-0/). This integration asks
adsb.lol while adsb.fi is failing. A focus area lying inside Live Track Aircraft's circle is answered from
that circle's last answer, which may also have come from adsb.lol. An aircraft drawn from such an answer
credits adsb.lol.

## Vessel positions: aisstream.io

Vessel positions are streamed at runtime from [aisstream.io](https://aisstream.io), with the user's own
account and API key. aisstream.io publishes no terms of use; every vessel's attribution names it. Nothing
from it is shipped in this repository.

## The lists: EnforcementAircraft and EnforcementVessels (ODbL v1.0)

Contains information from [EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft),
which is made available under the [Open Database License (ODbL) v1.0](https://opendatacommons.org/licenses/odbl/1-0/).

Contains information from [EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels),
which is made available under the [Open Database License (ODbL) v1.0](https://opendatacommons.org/licenses/odbl/1-0/).

## Aircraft owners: the FAA registry

Owners and agencies come from the Federal Aviation Administration's Releasable Aircraft Database
(https://registry.faa.gov/database/ReleasableAircraft.zip), downloaded at runtime by each installation. It
is a US government publication. Nothing from it is shipped in this repository.

## Aircraft icons: ADS-B Radar

The marker icons are drawn by the `saw-livetrack` library, which carries them with their own
attribution. Icons by [ADS-B Radar](https://adsb-radar.com), used with permission; the icons drawn for
StrausbergAutomationWorks were donated to ADS-B Radar and are under its terms. The ring this
integration draws over a detected aircraft is its own.

## The vessel icon and the brand icon

`custom_components/live_track_salt/icons/vessel.svg` is Live Track Ships' generic hull, drawn for
StrausbergAutomationWorks, under the MIT licence in `LICENSE`. The brand icon in
`custom_components/live_track_salt/brand/` is the StrausbergAutomationWorks logo with that hull and the
library's Beechcraft King Air 350 (`kingair350.svg`, drawn for StrausbergAutomationWorks to the type's
published dimensions and donated to ADS-B Radar, so it is under ADS-B Radar's terms, above).

## Aircraft photos: Planespotters.net

When a viewer points at an aircraft on the map, the integration asks the Planespotters.net photo API
(https://www.planespotters.net/photo/api) at runtime for a photo of that aircraft, by its hex code. Each Home
Assistant asks for its own users and answers for its own use; the requests carry a User-Agent naming the shared
`saw-livetrack` library and its repository. Nothing from Planespotters.net is shipped in this repository, and no
photo is copied into it.

Planespotters.net's terms are on that page (read 21 November 2026). What the code does to keep them, wherever a user
cannot change it:

* the photographer is named beside every photo, and the photo links to its page on Planespotters.net by the address
  the API returns, unchanged, in a plain link;
* an answer is kept for at most 24 hours: 12 hours in Home Assistant's memory, and at most 12 hours more in the page
  showing the map;
* the viewer's browser loads each image straight from the address the API returns; the integration does not
  download, store, proxy or re-host any image;
* a photo is asked for only when a viewer points at an aircraft, one request at a time for each aircraft; HTTP 429
  pauses every lookup, and HTTP 403 stops them for a day.

Each photo belongs to its photographer. The photos are not covered by the MIT licence in `LICENSE`, which applies to
the code in this repository. If you show the map to others, keep the photographer's name and the link with each
photo.

## Vessel photos: Wikidata and Wikimedia Commons

For each listed vessel the integration asks Wikidata (https://www.wikidata.org) at runtime which item carries the
vessel's IMO number or, when that finds nothing, its MMSI number, and asks Wikimedia Commons
(https://commons.wikimedia.org) for that item's image: a thumbnail address, the file's page, its author and its
licence. Wikidata's data is under CC0 1.0. Each image stays under its own licence, which is shown with it beside its
author's name, and links to its page on Commons; the viewer's browser loads it from Wikimedia. The requests carry a
User-Agent naming the shared `saw-livetrack` library and its repository, as Wikimedia's policy asks. Nothing from
either is shipped in this repository.

## The map card

`custom_components/live_track_salt/frontend/live-track-map-card.js` is a released build of
[LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) (MIT), committed byte for
byte. The notices for the packages bundled in it are in the file's first lines.

## The code

MIT, in `LICENSE`.
