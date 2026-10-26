<center>
<div align="center">

# xiaomi-vacuum

A Home Assistant integration that keeps the full Dreame, MOVA, Mijia, and TROUVER support from [Tasshack/dreame-vacuum](https://github.com/Tasshack/dreame-vacuum), and is where further Xiaomi devices will be added.

Fork of [@Tasshack](https://github.com/Tasshack)'s upstream project. Not an official Dreame or Xiaomi product.

[![Version](https://img.shields.io/github/manifest-json/v/matteocelani/xiaomi-vacuum?filename=custom_components%2Fdreame_vacuum%2Fmanifest.json&color=18bcf2&label=Version&style=for-the-badge)](https://github.com/matteocelani/xiaomi-vacuum)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?logo=HomeAssistantCommunityStore&color=18bcf2&logoColor=white&style=for-the-badge)](https://github.com/hacs/integration)
[![Upstream](https://img.shields.io/badge/Upstream-Tasshack%2Fdreame--vacuum-18bcf2?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Tasshack/dreame-vacuum)
[![Community Forum](https://img.shields.io/static/v1.svg?label=Community&message=Forum&color=18bcf2&logo=HomeAssistant&logoColor=white&style=for-the-badge)](https://community.home-assistant.io/t/custom-component-dreame-vacuum/473026)

<hr>
<a href="https://github.com/Tasshack/dreame-vacuum"><img alt="Logo of the upstream Dreame Vacuum project" src="https://dreame-vacuum.tasshack.com/logo.svg" width=400></a>
<hr>

<a href="https://github.com/Tasshack/dreame-vacuum"><img alt="Map card from the upstream Dreame Vacuum project" src="https://dreame-vacuum.tasshack.com/dvc.png" width=480 /></a>

Images and the map card are from the upstream project by [@Tasshack](https://github.com/Tasshack).

</div>
</center>

<hr>

## What this repository is

[xiaomi-vacuum](https://github.com/matteocelani/xiaomi-vacuum) is both of these things:

- The Dreame-family integration. It continues to track and support **all** of [Tasshack/dreame-vacuum](https://github.com/Tasshack/dreame-vacuum): Dreame, MOVA, Mijia, and TROUVER robot vacuums and mops, including the accounts and local control that project already documents.
- The Xiaomi direction. Support for Xiaomi devices beyond that family is the work this fork adds on top. It is **in progress**. No second device family is in the tree yet.

## Repository name and Home Assistant domain

The GitHub repository is **xiaomi-vacuum**. Branding in this README uses that name. The Home Assistant integration domain stays **`dreame_vacuum`**.

| | |
| --- | --- |
| Repository | [matteocelani/xiaomi-vacuum](https://github.com/matteocelani/xiaomi-vacuum) |
| Home Assistant domain | `dreame_vacuum` |
| Installed folder | `custom_components/dreame_vacuum` |
| Name inside Home Assistant | Dreame Vacuum |

Installed users keep their config entries on `dreame_vacuum`. The previous name of this repository, `matteocelani/dreame-vacuum`, redirects to `matteocelani/xiaomi-vacuum`. [Tasshack/dreame-vacuum](https://github.com/Tasshack/dreame-vacuum) is still the upstream project and does not redirect here. There is no `xiaomi_vacuum` domain. A domain rename would need a new council decision, recorded against [0001](.agent/council/records/0001-xiaomi-wide-rename-and-expansion.md).

### Install and configuration

Add `https://github.com/matteocelani/xiaomi-vacuum` in HACS as a custom integration. The [HACS default listing](https://github.com/hacs/default) for this kind of vacuum is the upstream repository [Tasshack/dreame-vacuum](https://github.com/Tasshack/dreame-vacuum), which is a different install. After this fork is installed, Home Assistant still registers it as domain `dreame_vacuum`.

Minimum Home Assistant version for this repository is 2024.2.0.

Configure a Dreame, MOVA, Mijia, or TROUVER vacuum with the upstream guides. Those guides match the domain `dreame_vacuum` and the behavior this fork tracks:

- [Installation](https://dreame-vacuum.tasshack.com/installation), including [HACS](https://dreame-vacuum.tasshack.com/installation/hacs) and [manual](https://dreame-vacuum.tasshack.com/installation/manually) steps for the upstream project
- [Dreamehome](https://dreame-vacuum.tasshack.com/configuration/dreamehome)
- [Xiaomi Home](https://dreame-vacuum.tasshack.com/configuration/xiaomihome) (an account type for these vacuums, not a separate Xiaomi device)
- [MOVAhome](https://dreame-vacuum.tasshack.com/configuration/movahome)
- [TROUVER](https://dreame-vacuum.tasshack.com/configuration/trouver)
- [Local control](https://dreame-vacuum.tasshack.com/configuration/local) over the LAN
- [Configuration options](https://dreame-vacuum.tasshack.com/configuration-options)

## Features

What the integration does today, for the Dreame, MOVA, Mijia, and TROUVER vacuums inherited from upstream:

- Wide range of Dreame, MOVA, Mijia and Trouver robot vacuums and mops, configurable with a DreameHome, MovaHome, Xiaomi Home account or fully locally without the cloud
- Almost every setting and state exposed dynamically as auto generated entities
- Live and multi-floor map support with zone, spot and room cleaning
- Per-room suction, water volume and cleaning order for customized cleaning
- Persistent notifications and events for automations
- Cleaning/cruising history, obstacle photos, map backup & recovery and saved WiFi maps
- Backend translations for 40 languages
- Complete interactive map editor via embedded [Dreame Vacuum Card](https://dreame-vacuum-card.tasshack.com/)

### Xiaomi devices (in progress)

No models beyond the Dreame, MOVA, Mijia, and TROUVER family are supported yet. This README does not list any. A second device family is added as a sibling package under this integration only in the pull request that adds a concrete device.

## Documentation

These pages are the upstream documentation for the support this fork tracks. They describe the current Dreame-family integration.

- [Documentation](https://dreame-vacuum.tasshack.com/)
- [Supported devices](https://dreame-vacuum.tasshack.com/guide/more/supported-devices) for [Dreame](https://dreame-vacuum.tasshack.com/guide/more/supported-devices#dreame), [MOVA](https://dreame-vacuum.tasshack.com/guide/more/supported-devices#mova), [Mijia](https://dreame-vacuum.tasshack.com/guide/more/supported-devices#mijia), and [TROUVER](https://dreame-vacuum.tasshack.com/guide/more/supported-devices#trouver)
- [How to use](https://dreame-vacuum.tasshack.com/guide)
- [Dashboard](https://dreame-vacuum.tasshack.com/guide/dashboard), including the [Dreame Vacuum Card](https://dvc.tasshack.com/)
- [Entities](https://dreame-vacuum.tasshack.com/guide/entities), with [map](https://dreame-vacuum.tasshack.com/guide/entities/map-entities), [room](https://dreame-vacuum.tasshack.com/guide/entities/room-entities), and [consumable](https://dreame-vacuum.tasshack.com/guide/entities/consumable-entities) entities
- [Map support](https://dreame-vacuum.tasshack.com/guide/map-support), including [history](https://dreame-vacuum.tasshack.com/guide/map-support/history), [recovery](https://dreame-vacuum.tasshack.com/guide/map-support/recovery), [obstacle photos](https://dreame-vacuum.tasshack.com/guide/map-support/obstacles), and [Wi-Fi maps](https://dreame-vacuum.tasshack.com/guide/map-support/wifi-map)
- [Services](https://dreame-vacuum.tasshack.com/guide/services) for [device](https://dreame-vacuum.tasshack.com/guide/services/vacuum-services) and [map](https://dreame-vacuum.tasshack.com/guide/services/map-services) control
- [Notifications](https://dreame-vacuum.tasshack.com/guide/notifications)
- [Events](https://dreame-vacuum.tasshack.com/guide/events)
- [FAQ](https://dreame-vacuum.tasshack.com/guide/more/faq)

The [community thread](https://community.home-assistant.io/t/custom-component-dreame-vacuum/473026) is the upstream discussion.

## Credit and license

This repository is a fork of [dreame-vacuum](https://github.com/Tasshack/dreame-vacuum) by [@Tasshack](https://github.com/Tasshack). Copyright (c) 2022 Tasshack. The MIT license and that copyright notice live in [LICENSE](LICENSE) and stay with the project.

### Thanks

- [@Tasshack](https://github.com/Tasshack) for [dreame-vacuum](https://github.com/Tasshack/dreame-vacuum), the upstream integration this fork tracks
- [xiaomi_vacuum](https://github.com/pooyashahidi/xiaomi_vacuum) by [@pooyashahidi](https://github.com/pooyashahidi)
- [Xiaomi MIoT for Home Assistant](https://github.com/ha0y/xiaomi_miot_raw) by [@ha0y](https://github.com/ha0y)
- [Xiaomi Cloud Map Extractor](https://github.com/PiotrMachowski/Home-Assistant-custom-components-Xiaomi-Cloud-Map-Extractor) by [@PiotrMachowski](https://github.com/PiotrMachowski)
- Dreame cloud authentication by [@kuudori](https://github.com/kuudori)
- Mova cloud support by [@r1si](https://github.com/r1si)
