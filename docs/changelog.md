# Changelog

This page summarizes major changes. The [full development history](/zh-cn/changelog) includes intermediate versions. Downloadable packages and individual release notes are listed on [GitHub Releases](https://github.com/ztszts777/tgfastviewer-nagramxf/releases).

## v1.7.0 · Language and settings {#v170}

- The plugin follows the Android system language by default, with a manual choice of English or Simplified Chinese.
- Settings switches save in place and preserve the current scroll position.
- Portrait thumbnails default to the bottom edge. Gesture haptics default to 60% strength and a cap of 30 pulses per second.
- Includes fixes for disappearing seek bars after rotation and clipped lines in folded captions.

[Read the v1.7.0 release notes](https://github.com/ztszts777/tgfastviewer-nagramxf/releases/tag/v1.7.0)

## v1.6.x · Filter previews and playback modes {#v16}

- Start preparing filtered chat previews in batches and prioritize the first screen of each chat folder.
- Switch between stop after current, continuous playback, and loop in the video settings.
- Improve fullscreen transitions, keep the bottom controls synchronized with the thumbnails, and fix caption and seek-bar rendering.

## v1.5.x · Portrait thumbnails and chat navigation {#v15}

- Add a bottom thumbnail strip in portrait, with an adjustable height.
- Restore the previous chat position when returning from landscape playback in a linked chat.
- Reuse pinned-message filter results to reduce work while scrolling through chats.

## v1.3.x–v1.4.x · Bookmarks, rotation, and music controls {#v13-v14}

- Add per-chat background audio and continuous video playback, and preserve the playback state on exit.
- Recognize saved messages and support bookmark controls in the viewer and in chats.
- Improve landscape and portrait layouts, thumbnail preloading, rotation, and navigation back to the chat or folder.
- Add a two-row music toolbar with speed, sleep timer, and a shortcut back to the chat.

## v1.2.x · Viewer and shared media {#v12}

- Add playback gestures, thumbnail browsing across messages, and separate landscape and portrait layouts.
- Open shared media near the current item and return through the viewer to the chat.
- Refine AyuGram filter handling and keep plugin settings on upgrade.

## v1.1.0–v1.1.1 · The combined plugin {#v11}

- Combine fast media browsing, AyuGram filter fixes, and audio/video controls into one plugin under GPLv3, while preserving the original MIT notice.
- Fix the unread badge when jumping to the latest position and the latest loaded message is filtered out.

## v1.0.1 · TGFastViewer for NagramXF {#v101}

- Release the standalone NagramXF adaptation with the original author’s credit and the full MIT license.
