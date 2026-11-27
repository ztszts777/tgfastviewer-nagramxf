"""Build the NagramXF suite from its maintained plugin sources."""

import ast
from pathlib import Path

plugins = Path("plugins")
header = '''# SPDX-License-Identifier: GPL-3.0-only
# This combined release is distributed under GNU GPL version 3.
# The TGFastViewer component carries the upstream MIT copyright and permission notice.

from bisect import bisect_left, bisect_right
from collections import OrderedDict
import json
from time import monotonic
from uuid import uuid4

from android_utils import OnClickListener, R, run_on_ui_thread
from base_plugin import BasePlugin
from client_utils import RequestCallback
from java import cast, dynamic_proxy, jarray, jbyte, jclass, jfloat, jint

__id__ = "nagramxf_media_suite"
__name__ = "NagramXF 媒体增强"
__description__ = "改善播放器、媒体浏览和消息过滤，功能可单独设置。"
__author__ = "ztszts777 / TGFastViewer by dunxuan"
__version__ = "1.2.4"
__app_version__ = ">=12.10.1"


class PluginFeature:
    def __init__(self, owner, flags):
        self.flags = flags
        self.log = owner.log
        self.hook_method = owner.hook_method
        self.hook_all_constructors = owner.hook_all_constructors
        self.unhook_method = owner.unhook_method
        self.get_setting = owner.get_setting
        self.set_setting = owner.set_setting
'''


def component(filename, drop=()):
    path = plugins / filename
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    for node in reversed(ast.parse(source).body):
        removable = isinstance(node, (ast.Import, ast.ImportFrom))
        if isinstance(node, ast.Assign):
            removable = all(isinstance(target, ast.Name) and (
                target.id.startswith("__") or target.id in drop) for target in node.targets)
        if isinstance(node, ast.FunctionDef):
            removable = node.name in drop
        if removable:
            del lines[node.lineno - 1:node.end_lineno]
    return ("\n".join(lines).strip().replace("(BasePlugin):", "(PluginFeature):")
            .replace("(MediaCapsule, BasePlugin):", "(MediaCapsule, PluginFeature):"))


wrapper = '''
SETTINGS_GROUPS = (
    ("媒体浏览", (
        ("fast_viewer", "快速浏览", "预载相邻媒体，保留完整相册"),
        ("album_thumbnails", "缩略图侧栏", "横竖屏均可收起和调宽"),
        ("filter_display", "同步 AyuGram 过滤", "应用到聊天预览、置顶和媒体库"),
    )),
    ("播放器界面", (
        ("video_toolbar", "视频工具栏", None),
        ("photo_shadows", "媒体说明与阴影", "说明显示在顶部"),
    )),
    ("播放手势", (
        ("double_tap", "双击播放或暂停", "双击屏幕中央"),
        ("double_tap_seek", "双击跳转", "双击屏幕两侧"),
        ("hold_speed", "长按倍速", "松手恢复原速"),
        ("pinch", "双指缩放", None),
        ("brightness_swipe", "左侧滑动调亮度", "退出播放器后恢复"),
        ("volume_swipe", "右侧滑动调音量", "退出播放器后恢复"),
    )),
    ("手势振动", ()),
    ("全屏与旋转", (
        ("fullscreen_swipe", "滑动切换全屏", "中央下滑进入，上滑退出"),
        ("orientation", "按比例锁定方向", "转到媒体对应的横向或竖向后锁定"),
        ("auto_fullscreen", "宽视频自动横屏", None),
        ("auto_fullscreen_on_switch", "切换媒体时自动旋转", "随自动横屏生效"),
    )),
    ("音频与播控", (
        ("audio_toolbar", "音乐工具栏", None),
        ("hide_audio_profile_button", "隐藏添加到个人资料", None),
        ("timer", "睡眠定时", "适用于音乐和视频"),
        ("system_pip", "系统画中画", None),
        ("media_controls", "系统播控", None),
        ("background_audio", "视频后台播放", "退出视频页后继续播放音频"),
    )),
)

SETTINGS = tuple(setting for _, settings in SETTINGS_GROUPS for setting in settings)
DEFAULTS = {"auto_fullscreen_on_switch": False}
THUMBNAIL_LABELS = ("小", "较小", "标准", "大", "特大")

FEATURES = (
    (FastViewerPlugin, ("fast_viewer",)),
    (AyuFilterDisplayFix, ("filter_display",)),
    (VideoSeekbarGestureInsets, ("video_toolbar", "photo_shadows", "album_thumbnails",
                               "double_tap", "double_tap_seek", "hold_speed",
                               "pinch", "fullscreen_swipe", "orientation",
                               "brightness_swipe", "volume_swipe", "auto_fullscreen", "auto_fullscreen_on_switch")),
    (MediaSleepTimer, ("timer", "audio_toolbar", "hide_audio_profile_button")),
    (SystemVideoPip, ("system_pip", "media_controls", "background_audio")),
)


class NagramXFMediaSuite(BasePlugin):
    def settings_backup(self):
        if not hasattr(self, "settings_preferences"):
            context = jclass("org.telegram.messenger.ApplicationLoader").applicationContext
            self.settings_preferences = context.getSharedPreferences("nagramxf_media_suite_settings", 0)
        return self.settings_preferences

    def get_setting(self, key, default=None):
        saved = super().get_setting(key, None)
        backup = self.settings_backup()
        cached = backup.getString(key, None)
        if saved is not None:
            encoded = json.dumps(saved, ensure_ascii=False)
            if cached != encoded:
                backup.edit().putString(key, encoded).apply()
            return saved
        if cached is not None:
            try:
                return json.loads(str(cached))
            except ValueError:
                pass
        return default

    def set_setting(self, key, value, reload_settings=False):
        self.settings_backup().edit().putString(key, json.dumps(value, ensure_ascii=False)).apply()
        return super().set_setting(key, value, reload_settings)

    def on_plugin_load(self):
        self.flags = {key: bool(self.get_setting(key, DEFAULTS.get(key, True))) for key, _, _ in SETTINGS}
        self.components = {}
        self.running = True
        run_on_ui_thread(lambda: self.apply_settings(stagger=True), 24)

    def create_settings(self):
        from ui.settings import Header, Input, Switch

        rows = []
        for title, group in SETTINGS_GROUPS:
            rows.append(Header(text=title))
            for key, label, detail in group:
                rows.append(Switch(key=key, text=label, subtext=detail, default=DEFAULTS.get(key, True),
                                   on_change=lambda enabled, name=key: self.change_feature(name, enabled)))
                if key == "double_tap_seek":
                    rows.append(Input(key="double_tap_seconds", text="跳转时长（秒）", default="15",
                                      on_change=lambda value: self.change_video_value("double_tap_seconds", value)))
                elif key == "hold_speed":
                    speeds = (*[f"{speed:g}×" for speed in HOLD_SPEED_PRESETS], "自定义")
                    rows.append(self.slider_setting("hold_speed_preset", "倍速预设", 0, len(speeds) - 1,
                                                    DEFAULT_HOLD_SPEED_INDEX, speeds.__getitem__, speeds))
                    rows.append(Input(key="hold_speed_custom", text="自定义倍速", default="2.5",
                                      subtext="预设选「自定义」后使用",
                                      on_change=lambda value: self.change_video_value("hold_speed_custom", value)))
                elif key == "album_thumbnails":
                    rows.append(self.slider_setting("thumbnail_size", "缩略图大小", 0, len(THUMBNAIL_LABELS) - 1,
                                                    DEFAULT_THUMBNAIL_SIZE, THUMBNAIL_LABELS.__getitem__,
                                                    THUMBNAIL_LABELS))
                    rows.append(thumbnail_default_state_setting(
                        lambda value: self.change_video_value("thumbnail_default_state", value)))
                    rows.append(thumbnail_state_scope_setting(
                        lambda value: self.change_video_value("thumbnail_state_scope", value)))
            if title == "手势振动":
                rows.extend([
                    self.slider_setting("adjustment_tick_strength", "振动强度", 0, 100,
                                        DEFAULT_ADJUSTMENT_TICK_STRENGTH, lambda n: f"{n}%" if n else "关闭"),
                    self.slider_setting("adjustment_tick_rate", "频率上限", 0, 30,
                                        DEFAULT_ADJUSTMENT_TICK_RATE, lambda n: f"{n} 次/秒" if n else "关闭"),
                    self.slider_setting("adjustment_tick_percent", "振动刻度", 1, 100,
                                        DEFAULT_ADJUSTMENT_TICK_PERCENT, lambda n: f"{n}%"),
                ])
        return rows

    def slider_setting(self, key, title, minimum, maximum, default, format_value, choices=None):
        from ui.settings import Input, Selector, SimpleSettingFactory

        if not hasattr(self, "slider_factories"):
            self.slider_factories = {}
        factory = self.slider_factories.get(key)
        if factory is None:
            steps = maximum - minimum
            positions = tuple(i / steps for i in range(steps + 1)) if choices else (0.0, 1.0)
            labels = choices or (format_value(minimum), format_value(maximum))

            def create(context, _list_view, _account, _guid, _provider):
                return jclass("android.widget.FrameLayout")(context)

            def bind(view, _item, _divider, _adapter, _list_view):
                capsule = self.get_capsule_ui()
                host = cast(capsule.frame_layout, view)
                theme = jclass("org.telegram.ui.ActionBar.Theme")
                primary = theme.getColor(theme.key_windowBackgroundWhiteBlackText)
                secondary = theme.getColor(theme.key_dialogTextGray2)
                accent = theme.getColor(theme.key_windowBackgroundWhiteBlueText)
                palette = (primary, secondary, accent, (primary & 0xFFFFFF) | 0x24000000, WHITE)
                value = adjustment_tick_value(self.get_setting(key, default), default, minimum, maximum)
                initial = (value - minimum) / steps

                def from_progress(progress):
                    return minimum + round(progress * steps)

                def apply(final, progress, _point):
                    if final:
                        self.change_video_value(key, from_progress(progress))

                slider = capsule.make_gear_capsule(host.getContext(), title, positions, labels, initial,
                    lambda progress: format_value(from_progress(progress)), apply, palette=palette, steps=steps)
                host.setBackgroundColor(jint(theme.getColor(theme.key_windowBackgroundWhite)))
                host.removeAllViews()
                host.addView(slider, capsule.frame_params(-1, -2))

            factory = SimpleSettingFactory(create, bind)
            self.slider_factories[key] = factory
        setting = factory()
        if setting.factory is not None:
            return setting
        def change(value):
            self.change_video_value(key, value)

        if choices:
            return Selector(key=key, text=title, default=default, items=list(choices), on_change=change)
        return Input(key=key, text=title, default=str(default), on_change=change)

    def change_feature(self, key, enabled):
        enabled = bool(enabled)
        self.flags[key] = enabled
        self.set_setting(key, enabled)
        run_on_ui_thread(self.apply_settings)

    def change_video_value(self, key, value):
        self.set_setting(key, value)
        entry = self.components.get(VideoSeekbarGestureInsets)
        if entry is not None:
            run_on_ui_thread(lambda: self.configure_video_values(entry[1]))

    def configure_video_values(self, component):
        component.double_tap_seconds = selected_double_tap_seconds(self.get_setting("double_tap_seconds", "15"))
        component.hold_speed = selected_hold_speed(
            self.get_setting("hold_speed_preset", DEFAULT_HOLD_SPEED_INDEX), self.get_setting("hold_speed_custom", "2.5"))
        component.configure_adjustment_ticks(self.get_setting("adjustment_tick_rate", "12"),
                                             self.get_setting("adjustment_tick_percent", "1"),
                                             self.get_setting("adjustment_tick_strength", "42"))
        component.thumbnail_size_changed(self.get_setting("thumbnail_size", DEFAULT_THUMBNAIL_SIZE))
        component.configure_thumbnail_state()

    def apply_settings(self, features=FEATURES, stagger=False):
        if not self.running:
            return
        if stagger and len(features) > 1:
            remaining = features[1:]
            features = features[:1]
            run_on_ui_thread(lambda: self.apply_settings(remaining, stagger=True), 24)
        for feature, keys in features:
            values = tuple(self.flags[key] for key in keys)
            previous = self.components.get(feature)
            if previous is not None and previous[0] == values:
                continue
            if (feature is VideoSeekbarGestureInsets and previous is not None
                    and previous[0][:-1] == values[:-1]):
                component = previous[1]
                component.flags["auto_fullscreen_on_switch"] = values[-1]
                self.components[feature] = (values, component)
                continue
            if feature is MediaSleepTimer and previous is not None and previous[0][0] == values[0] and any(values):
                component = previous[1]
                component.flags.update(zip(keys, values))
                self.components[feature] = (values, component)
                for audio_ref, _, _ in component.audio_rows:
                    audio = audio_ref.get()
                    if audio is not None:
                        component.update_audio_footer(audio, restore=previous[0][2] and not values[2])
                        component.audio_layout.get(audio).requestLayout()
                continue
            if feature is SystemVideoPip and previous is not None and any(values):
                component = previous[1]
                component.flags.update(zip(keys, values))
                self.components[feature] = (values, component)
                component.refresh_features(previous[0][:2] != values[:2])
                continue
            if previous is not None:
                self.components.pop(feature)
                previous[1].on_plugin_unload()
            if any(values[:-1] if feature is VideoSeekbarGestureInsets else values):
                component = feature(self, dict(zip(keys, values)))
                if feature is VideoSeekbarGestureInsets:
                    self.configure_video_values(component)
                    component.on_thumbnail_edge = self.prefetch_thumbnail_edge
                    component.caption_source_hidden = self.album_caption_hidden
                if feature is SystemVideoPip:
                    component.on_background_handoff = self.keep_video_timer
                if feature is MediaSleepTimer:
                    component.make_timer_capsule = self.make_timer_capsule
                self.components[feature] = (values, component)
                try:
                    component.on_plugin_load()
                except Exception as error:
                    self.log(f"{feature.__name__}: {type(error).__name__}: {error}")
                    try:
                        component.on_plugin_unload()
                    except Exception:
                        pass
                    self.components.pop(feature, None)

    def get_capsule_ui(self):
        if not hasattr(self, "capsule_ui"):
            capsule = MediaCapsule()
            capsule.initialize_capsule_ui()
            self.capsule_ui = capsule
        return self.capsule_ui

    def make_timer_capsule(self, *args, **kwargs):
        return self.get_capsule_ui().make_gear_capsule(*args, **kwargs)

    def keep_video_timer(self, viewer):
        timer = self.components.get(MediaSleepTimer)
        if timer is not None:
            timer[1].follow_background_audio(viewer)

    def prefetch_thumbnail_edge(self, viewer, index, direction):
        fast = self.components.get(FastViewerPlugin)
        gallery = getattr(fast[1], "gallery", None) if fast is not None else None
        if gallery is not None and gallery.viewer == viewer:
            gallery.prefetch(index, direction)

    def album_caption_hidden(self, message, chat, group):
        filtering = self.components.get(AyuFilterDisplayFix)
        return filtering is not None and filtering[1].media_hidden(message, chat, group)

    def on_plugin_unload(self):
        self.running = False
        components, self.components = self.components, {}
        for _, component in reversed(tuple(components.values())):
            component.on_plugin_unload()
'''

parts = [
    header.strip(),
    component("video_seekbar_gesture_insets.plugin"),
    component("media_sleep_timer.plugin", {"VIDEO_TIMER_CONTROL_TAG", "WHITE"}),
    component("system_video_pip.plugin", {"field", "method", "STATE_ENDED"}),
    component("tgfastviewer_nagramxf.plugin"),
    component("ayufilter_display_fix.plugin", {"field", "method"}),
    wrapper.strip(),
]
license_text = (plugins / "COPYING").read_text(encoding="utf-8").splitlines()
parts.append("\n".join("# " + line if line else "#" for line in license_text))
source = "\n\n\n".join(parts) + "\n"
filename = plugins / "nagramxf_media_suite.plugin"
compile(source, str(filename), "exec")
filename.write_text(source, encoding="utf-8", newline="\n")
print(f"Built {filename} ({len(source.encode('utf-8'))} bytes)")
