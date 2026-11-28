# NagramXF Media Enhancements

**English** · [简体中文](README.zh-CN.md)

A plugin for faster media browsing, better AyuGram filter integration, and more controls for the photo, video, and music players in NagramXF.

**[Download the latest plugin](https://github.com/ztszts777/tgfastviewer-nagramxf/releases/latest/download/nagramxf_media_suite.plugin)** · [Release notes](https://github.com/ztszts777/tgfastviewer-nagramxf/releases/latest) · [Version history (简体中文)](CHANGELOG.md) · [Report an issue](https://github.com/ztszts777/tgfastviewer-nagramxf/issues)

## Install or update

1. In NagramXF, open **N Settings → Plugins** and enable the plugin engine.
2. Download `nagramxf_media_suite.plugin`, tap **+** in the Plugins screen, and import the file. Enable **NagramXF Media Enhancements**.
3. If you already use the suite, choose **Update** when importing to keep your settings. Disable overlapping standalone plugins if you see duplicate controls.

Requires **NagramXF 12.10.1 or newer** with the plugin engine. Version 1.7.0 passed regression tests and interface checks against **NagramXF 12.10.1.1251** (build `30dcd6c`, `arm64-v8a`). Settings switches were also tested on a phone. [Tested client build](https://github.com/Keeperorowner/NagramXF/releases/tag/1251)

## Features

| Feature | What it does |
| --- | --- |
| **TGFastViewer media loading** | Prioritizes media around the photo or video you open. Loads more as you swipe and keeps albums together when loading pages. |
| **AyuGram filtering** | Uses each chat’s active filter rules, including exclusions. Applies them to pinned messages, shared media, files, and fullscreen navigation. Hides empty date headers and uses the latest visible message for the chat preview when available. |
| **Unread state in filtered chats** | Updates the unread badge through NagramXF’s read flow when you jump to the latest position and the newest loaded message is filtered out. |
| **Photo and video viewer** | Adds expandable captions, playback gestures, and layout controls for portrait and landscape. The video settings menu offers speed, available quality levels, playback mode, and background audio. |
| **Thumbnail strip** | Browse across messages, including single-media posts. Tap the handle to toggle the strip and drag it to resize. The strip preloads nearby thumbnails as you scroll. |
| **Shared media** | Opens near the current item and marks it. Back returns to playback, then to the chat and message position. |
| **Music controls and sleep timer** | Adds a two-row music toolbar. Open the timer in either player, choose a preset from 15 to 120 minutes or a custom duration, and optionally finish the current item when time runs out. The timer icon shows the remaining time. |
| **Android picture-in-picture and media controls** | Use Android’s floating player or media controls for playback and 15-second skips. The media session can show the video title and available artwork. |
| **Listen to videos in the background** | Turn on background audio in the video settings menu. NagramXF’s top playback bar controls it after you leave the viewer. This preference is saved per chat. |

## Gestures and defaults

- **Double-tap** the middle to play or pause. Double-tap either side to seek by the interval configured in NagramXF.
- **Press and hold** the video or an empty part of the viewer to temporarily play at **2.5×**. You can set a different speed.
- **Pinch and drag** to zoom and pan. The reset button appears while the image is zoomed.
- **Swipe vertically in the middle** of a wide video to enter fullscreen on a downward swipe or leave it on an upward swipe.
- **Swipe vertically on either side** to change brightness on the left or media volume on the right. Adjustments persist while switching within the viewer and reset when you close it. Haptics default to a tick per 1% change, 60% intensity, and a cap of 30 ticks per second.

The interface follows the Android system language by default. Select **English** or **简体中文** in the plugin settings to override it. Portrait thumbnails start collapsed at the bottom and remember their state per chat. Opening a video wider than it is tall can switch to landscape. Automatic rotation when swiping between media items is off by default.

## Troubleshooting

- **Plugins menu missing** — Check that your NagramXF build includes the plugin engine and that the engine is enabled.
- **Picture-in-picture unavailable** — Allow picture-in-picture for NagramXF in Android settings and enable **Android picture-in-picture** in the plugin.
- **Duplicate controls** — Disable any standalone plugin that provides the same feature.
- **Something else** — Include your NagramXF build, Android version, plugin version, affected settings, and steps to reproduce. [Report an issue](https://github.com/ztszts777/tgfastviewer-nagramxf/issues)

## Source and license

The release asset is a readable Python `.plugin` file. The suite is generated from [the component sources](plugins/) and [the English translation catalog](plugins/i18n/en.json). Run `python tools/build_media_suite.py` from the repository root to rebuild `plugins/nagramxf_media_suite.plugin`.

The suite is licensed under [GNU GPLv3](LICENSE) (`GPL-3.0-only`). TGFastViewer was created by **dunxuan**. The suite includes the original copyright and [full MIT notice](LICENSES/TGFastViewer-MIT.txt). The standalone [v1.0.1 adaptation](https://github.com/ztszts777/tgfastviewer-nagramxf/releases/tag/v1.0.1) remains MIT-licensed. [Upstream TGFastViewer](https://github.com/dunxuan/tgfastviewer)
