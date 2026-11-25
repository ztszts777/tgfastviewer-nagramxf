"""Build the NagramXF suite from its maintained plugin sources."""

import ast
from pathlib import Path

plugins = Path("plugins")
header = '''# SPDX-License-Identifier: GPL-3.0-only
# This combined release is distributed under GNU GPL version 3.
# The TGFastViewer component carries the upstream MIT copyright and permission notice.

from collections import OrderedDict
from threading import local
from time import monotonic
from uuid import uuid4

from android_utils import OnClickListener, R, run_on_ui_thread
from base_plugin import BasePlugin
from client_utils import RequestCallback
from java import cast, dynamic_proxy, jarray, jclass, jfloat, jint

__id__ = "nagramxf_media_suite"
__name__ = "NagramXF 插件合集"
__description__ = "快速媒体浏览、AyuGram 过滤显示修复、视频和音乐播放工具，功能可分别开关。"
__author__ = "ztszts777 / TGFastViewer by dunxuan"
__version__ = "1.1.0"
__app_version__ = ">=12.10.1"


class PluginFeature:
    def __init__(self, owner, flags):
        self.flags = flags
        self.log = owner.log
        self.hook_method = owner.hook_method
        self.hook_all_constructors = owner.hook_all_constructors
        self.unhook_method = owner.unhook_method
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
    return "\n".join(lines).strip().replace("(BasePlugin):", "(PluginFeature):")


wrapper = '''
SETTINGS = (
    ("fast_viewer", "TG 快点滑", "从点开的媒体附近加载，保留完整相册并继续补页"),
    ("filter_display", "AyuGram 过滤显示修复", "沿用各聊天的过滤设置，应用到日期、预览、置顶和共享媒体"),
    ("video_toolbar", "视频双行工具栏", "进度条、播放按钮和底部功能键"),
    ("photo_shadows", "照片渐变阴影", "底部阴影跟随可见的缩略图或说明"),
    ("album_thumbnails", "放大相册缩略图", "放大照片与视频共用的底部缩略图条"),
    ("double_tap", "中央双击播放或暂停", "左右双击使用 NagramXF 的跳转动画"),
    ("double_tap_seek", "自定义左右双击跳转时长", "同时更新实际跳转和动画上的秒数"),
    ("hold_speed", "长按视频临时倍速", "在未被控件遮挡的视频画面长按，松手恢复"),
    ("pinch", "双指缩放和还原", "缩放后显示还原按钮"),
    ("fullscreen_swipe", "横向视频中央滑动切全屏", "下拉进入，上拉退出"),
    ("brightness_swipe", "左侧上下滑调亮度", "同一播放器内切换视频时保留，退出后恢复"),
    ("volume_swipe", "右侧上下滑调媒体音量", "调整系统媒体音量，退出播放页时恢复"),
    ("orientation", "按媒体比例锁定旋转方向", "切到不同方向的照片或视频后，转动手机到该方向再锁定"),
    ("auto_fullscreen", "宽照片和视频自动横屏", "打开宽度大于高度的照片或视频时进入横屏"),
    ("auto_fullscreen_on_switch", "切换媒体时立即调整方向", "开启自动横屏后生效。关闭时等你把手机转到对应方向"),
    ("audio_toolbar", "音乐双行工具栏", "播放键和功能键分行，倍速放在功能行"),
    ("hide_audio_profile_button", "隐藏音乐资料页按钮", "取消底部资料页按钮占用的空间"),
    ("timer", "睡眠定时", "音乐和视频定时、时长滑块和到点播完"),
    ("system_pip", "Android 系统小窗", "在「更多」中进入，提供前后 15 秒"),
    ("media_controls", "系统播控卡片", "标题、封面、播放和前后 15 秒"),
    ("background_audio", "视频后台音频", "点亮耳机后，离开播放页仍可从顶部播放栏继续听"),
)

DEFAULTS = {"auto_fullscreen_on_switch": False}

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
    def on_plugin_load(self):
        self.flags = {key: bool(self.get_setting(key, DEFAULTS.get(key, True))) for key, _, _ in SETTINGS}
        self.components = {}
        self.running = True
        run_on_ui_thread(self.apply_settings)

    def create_settings(self):
        from ui.settings import Input, Selector, Switch

        rows = []
        for key, label, detail in SETTINGS:
            rows.append(Switch(key=key, text=label, subtext=detail, default=DEFAULTS.get(key, True),
                               on_change=lambda enabled, name=key: self.change_feature(name, enabled)))
            if key == "double_tap_seek":
                rows.append(Input(key="double_tap_seconds", text="左右双击跳转秒数", default="15",
                                  subtext="输入正整数，默认 15 秒",
                                  on_change=lambda value: self.change_video_value("double_tap_seconds", value)))
            elif key == "hold_speed":
                rows.append(Selector(key="hold_speed_preset", text="长按倍速", default=DEFAULT_HOLD_SPEED_INDEX,
                                     items=[f"{speed:g}×" for speed in HOLD_SPEED_PRESETS] + ["自定义"],
                                     on_change=lambda value: self.change_video_value("hold_speed_preset", value)))
                rows.append(Input(key="hold_speed_custom", text="自定义长按倍速", default="2.5",
                                  subtext="选择「自定义」后使用，输入大于等于 1 的数字",
                                  on_change=lambda value: self.change_video_value("hold_speed_custom", value)))
        return rows

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

    def apply_settings(self):
        if not self.running:
            return
        for feature, keys in FEATURES:
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
                if feature is SystemVideoPip:
                    component.on_background_handoff = self.keep_video_timer
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

    def keep_video_timer(self, viewer):
        timer = self.components.get(MediaSleepTimer)
        if timer is not None:
            timer[1].follow_background_audio(viewer)

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
