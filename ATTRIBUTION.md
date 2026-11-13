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

## The map card

`custom_components/live_track_salt/frontend/live-track-map-card.js` is a released build of
[LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) (MIT), committed byte for
byte. The notices for the packages bundled in it are in the file's first lines.

## The code

MIT, in `LICENSE`.
