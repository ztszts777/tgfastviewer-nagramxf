"""Build the NagramXF suite from its maintained plugin sources."""

import ast
from io import StringIO
import json
from pathlib import Path
import re
import tokenize

plugins = Path("plugins")
header = '''# SPDX-License-Identifier: GPL-3.0-only
# This combined release is distributed under GNU GPL version 3.
# The TGFastViewer component carries the upstream MIT copyright and permission notice.

from bisect import bisect_left, bisect_right
from collections import OrderedDict
from functools import lru_cache
import json
from time import monotonic
from uuid import uuid4

from android_utils import OnClickListener, OnLongClickListener, R, run_on_ui_thread
from base_plugin import BasePlugin
from client_utils import RequestCallback
from java import cast, dynamic_proxy, jarray, jbyte, jclass, jfloat, jint

__id__ = "nagramxf_media_suite"
__name__ = "NagramXF 增强 · Enhancer"
__description__ = "Media playback, filters and chat UI · 播放器、消息过滤与聊天界面"
__author__ = "ztszts777 / TGFastViewer by dunxuan"
__version__ = "1.7.0"
__app_version__ = ">=12.10.1"

LANGUAGE_AUTO, LANGUAGE_CHINESE, LANGUAGE_ENGLISH = range(3)
plugin_language = "zh"
ENGLISH_STRINGS = {}


def tr(text):
    return ENGLISH_STRINGS.get(text, text) if plugin_language == "en" else text


def choose_language(mode, system_language):
    if mode == LANGUAGE_CHINESE:
        return "zh"
    if mode == LANGUAGE_ENGLISH:
        return "en"
    code = str(system_language).lower().replace("_", "-").split("-")[0]
    return "zh" if code == "zh" else "en"


def system_language_code():
    if int(jclass("android.os.Build$VERSION").SDK_INT) >= 33:
        context = jclass("org.telegram.messenger.ApplicationLoader").applicationContext
        manager = context.getSystemService("locale")
        if manager is not None:
            locales = cast(jclass("android.app.LocaleManager"), manager).getSystemLocales()
            if not locales.isEmpty():
                return locales.get(0).getLanguage()
    locales = jclass("android.content.res.Resources").getSystem().getConfiguration().getLocales()
    return locales.get(0).getLanguage() if not locales.isEmpty() else "en"


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
def compact_count_by_ten_thousand(number):
    for unit, suffix in ((100_000_000, "亿"), (10_000, "W")):
        if number >= unit:
            whole, decimal = divmod(number // (unit // 10), 10)
            label = f"{whole}.{decimal}" if decimal else str(whole)
            return label + suffix, (whole * 10 + decimal) * (unit // 10)
    return str(number), number


class TenThousandCounts(PluginFeature):
    def on_plugin_load(self):
        locale = jclass("org.telegram.messenger.LocaleController").getClass()
        self.hook = self.hook_method(method(locale, "formatShortNumber", 2), after=self.after_format)

    def after_format(self, param):
        number = int(param.args[0])
        if number < 1_000 or str(param.getResult()) == str(number):
            return  # Preserve the client's full-number preference.
        label, rounded = compact_count_by_ten_thousand(number)
        if param.args[1] is not None:
            param.args[1][0] = rounded
        param.setResult(label)

    def on_plugin_unload(self):
        if hasattr(self, "hook"):
            self.unhook_method(self.hook)


class MainTabsGlass(PluginFeature):
    HEIGHT = 48
    NATIVE_HEIGHT = 56
    GLASS_TINT_ALPHA = 158

    def on_plugin_load(self):
        self.hooks = []
        self.fragments = []
        self.active = True
        self.tabs_type = jclass("org.telegram.ui.MainTabsActivity")
        self.dialogs_type = jclass("org.telegram.ui.DialogsActivity").getClass()
        self.launch = jclass("org.telegram.ui.LaunchActivity")
        self.weak = jclass("java.lang.ref.WeakReference")
        self.integer = jclass("java.lang.Integer")
        self.dp = jclass("org.telegram.messenger.AndroidUtilities").dp
        self.refresh_dialogs = method(self.dialogs_type, "refreshSearchSettingsUi", 0)
        self.no_args = jarray(jclass("java.lang.Object"))([])
        owner = self.tabs_type.getClass()
        self.refresh_tab_source = method(owner, "blur3_invalidateBlur", 0)
        self.refresh_dialog_source = method(self.dialogs_type, "blur3_InvalidateBlur", 0)
        self.views = tuple(field(owner, name) for name in ("tabsView", "tabsBarContainer", "searchTabButton"))
        self.margin = jclass("tw.nekomimi.nekogram.helpers.MainTabsHelper").getMainTabsMargin()
        self.render_node = None
        self.blurred_drawable = jclass("org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawable")
        self.enabled_effects = []
        if jclass("android.os.Build$VERSION").SDK_INT >= 33:
            self.render_node = jclass("org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawableRenderNode")
            render_type = self.render_node.getClass()
            self.effect = field(render_type, "liquidGlassEffect")
            self.fill = field(render_type, "renderNodeFill")
            self.glass_tint = field(self.blurred_drawable.getClass(), "backgroundColor")
            self.glass_provider = field(self.blurred_drawable.getClass(), "colorProvider")
            self.chat_glass = jclass("org.telegram.ui.Components.blur3.drawable.color.impl.BlurredBackgroundProviderImpl")
            self.hooks.append(self.hook_method(method(render_type, "updateColors", 0), after=self.after_glass_colors))
        helper = jclass("tw.nekomimi.nekogram.helpers.MainTabsHelper").getClass()
        for name, height in (("getMainTabsHeight", self.HEIGHT),
                             ("getMainTabsHeightWithMargins", self.HEIGHT + 2 * self.margin)):
            self.hooks.append(self.hook_method(method(helper, name, 0),
                before=lambda param, value=height: param.setResult(self.integer(value))))
        for name, arity in (("createView", 1), ("onResume", 0)):
            self.hooks.append(self.hook_method(method(owner, name, arity), after=self.after_tabs))
        activity = self.launch.instance
        if activity is not None and activity.getActionBarLayout() is not None:
            stack = activity.getActionBarLayout().getFragmentStack()
            for index in range(stack.size()):
                fragment = stack.get(index)
                if owner.isInstance(fragment):
                    self.style_tabs(fragment)

    def after_tabs(self, param):
        self.style_tabs(param.thisObject)

    def style_tabs(self, fragment, enabled=True):
        tabs, bar, search = (part.get(fragment) for part in self.views)
        if tabs is None or bar is None or search is None:
            return
        self.fragments = [ref for ref in self.fragments if ref.get() is not None]
        if enabled and not any(ref.get() == fragment for ref in self.fragments):
            self.fragments.append(self.weak(fragment))
        height = self.HEIGHT if enabled else self.NATIVE_HEIGHT
        changed = False
        for view, size in ((tabs, height + 2 * self.margin), (bar, height + 2 * self.margin),
                           (search, height)):
            params = view.getLayoutParams()
            if params.height != self.dp(size) or (view == search and params.width != self.dp(size)):
                params.height = self.dp(size)
                if view == search:
                    params.width = self.dp(size)
                view.setLayoutParams(params)
                changed = True
        icon = search.getChildAt(0)
        padding = self.dp(12 if enabled else 14)
        if icon is not None and icon.getPaddingTop() != padding:
            icon.setPadding(padding, padding, padding, padding)
        background_changed = False
        for view in (tabs, search):
            background = view.getBackground()
            if background is not None:
                provider = fragment.getResourceProvider() if self.render_node is not None else None
                if self.style_background(background, height, enabled, provider):
                    background_changed = True
        if changed or background_changed:
            fragment = cast(self.tabs_type, fragment)
            dialogs = fragment.getCurrentVisibleFragment()
            is_dialogs = dialogs is not None and self.dialogs_type.isInstance(dialogs)
            if changed and is_dialogs:
                self.refresh_dialogs.invoke(dialogs, self.no_args)
            root = fragment.getFragmentView()
            if root is not None:
                if changed:
                    root.requestApplyInsets()
                if self.render_node is not None:
                    # Rebuild native capture from the compact bounds after the next layout.
                    def refresh():
                        if self.active != enabled or fragment.getFragmentView() != root or not root.isAttachedToWindow():
                            return
                        try:
                            if is_dialogs and dialogs == fragment.getCurrentVisibleFragment():
                                self.refresh_dialog_source.invoke(dialogs, self.no_args)
                            self.refresh_tab_source.invoke(fragment, self.no_args)
                            tabs.invalidate()
                            search.invalidate()
                        except Exception as error:
                            self.log(f"Could not refresh main-tabs glass: {type(error).__name__}: {error}")

                    run_on_ui_thread(refresh, 32)

    def after_glass_colors(self, param):
        node = param.thisObject
        if any(state[0].get() == node for state in self.enabled_effects):
            self.apply_glass_tint(node)

    def apply_glass_tint(self, node):
        color = self.glass_tint.getInt(node)
        if ((color >> 24) & 255) > self.GLASS_TINT_ALPHA:
            tinted = (self.GLASS_TINT_ALPHA << 24) | (color & 0xFFFFFF)
            self.glass_tint.setInt(node, jint(tinted - (1 << 32)))

    def style_background(self, drawable, height, enabled, provider=None):
        if not self.blurred_drawable.getClass().isInstance(drawable):
            return False
        drawable = cast(self.blurred_drawable, drawable)
        if self.render_node is not None and self.render_node.getClass().isInstance(drawable):
            node = cast(self.render_node, drawable)
            self.enabled_effects = [state for state in self.enabled_effects if state[0].get() is not None]
            state = next((state for state in self.enabled_effects if state[0].get() == node), None)
            if enabled == (state is not None):
                return False
            if enabled and state is None:
                added = self.effect.get(node) is None
                if added:
                    node.setLiquidGlassEffectAllowed()
                original = self.glass_provider.get(node)
                self.enabled_effects.append((self.weak(node), added, original))
                node.setColorProvider(self.chat_glass.bottomPanelChatActivity(provider))
                self.apply_glass_tint(node)
            elif not enabled and state is not None:
                self.enabled_effects.remove(state)
                if state[1]:
                    self.effect.set(node, None)
                    self.fill.get(node).setRenderEffect(None)
                node.setColorProvider(state[2])
            node.invalidateDisplayList()
        drawable.setRadius(jfloat(self.dp(height / 2)))
        drawable.invalidateSelf()
        return self.render_node is not None

    def on_plugin_unload(self):
        self.active = False
        for hook in self.hooks:
            self.unhook_method(hook)
        for ref in self.fragments:
            fragment = ref.get()
            if fragment is not None:
                self.style_tabs(fragment, enabled=False)


def settings_groups():
    return (
        ("媒体浏览", (
            ("fast_viewer", "快速浏览", "预载相邻媒体，保留完整相册"),
            ("album_thumbnails", "缩略图侧栏", "点小白条展开或收起，左右拖动调宽"),
            ("filter_display", "同步 AyuGram 过滤", "应用到聊天预览、置顶和媒体库"),
        )),
        ("播放器界面", (
            ("video_toolbar", "视频工具栏", None),
            ("photo_shadows", "媒体说明与阴影", "说明显示在顶部"),
            ("video_autoplay", "显示视频播放模式", "可从视频设置开启，后台听视频也适用"),
        )),
        ("聊天界面", (
            ("main_tabs_glass", "紧凑玻璃底栏", "聊天列表底部的标签和搜索"),
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

SETTINGS = tuple(setting for _, settings in settings_groups() for setting in settings)
DEFAULTS = {"auto_fullscreen_on_switch": False}
SUITE_DEFAULTS = {"thumbnail_portrait_position": THUMBNAIL_POSITION_BOTTOM,
                  "adjustment_tick_strength": 60, "adjustment_tick_rate": 30}
SWITCH_KEYS = frozenset(key for key, _, _ in SETTINGS)


class ChatFolderReturn(PluginFeature):
    def on_plugin_load(self):
        dialogs = jclass("org.telegram.ui.DialogsActivity").getClass()
        self.chat = jclass("org.telegram.ui.ChatActivity").getClass()
        page = jclass("org.telegram.ui.DialogsActivity$ViewPage").getClass()
        self.tabs = field(dialogs, "filterTabsView")
        self.pages = field(dialogs, "viewPages")
        self.selected = field(page, "selectedType")
        self.dialogs_type = dialogs
        self.main_tabs_type = jclass("org.telegram.ui.MainTabsActivity").getClass()
        self.weak = jclass("java.lang.ref.WeakReference")
        self.origins = []
        self.hooks = []
        self.hooks.append(self.hook_method(method(self.chat, "onResume", 0), after=self.remember_folder))
        self.hooks.append(self.hook_method(method(dialogs, "onResume", 0), after=self.restore_folder))
        self.hooks.append(self.hook_method(method(dialogs, "onBecomeFullyVisible", 0),
                                           after=lambda param: self.restore_folder(param, committed=True)))

    def visible_fragment(self, fragment):
        return fragment.getCurrentVisibleFragment() if self.main_tabs_type.isInstance(fragment) else fragment

    def remember_folder(self, param):
        chat = param.thisObject
        navigation = chat.getParentLayout()
        if navigation is None or chat.isInPreviewMode():
            return
        stack = navigation.getFragmentStack()
        count = stack.size()
        if count < 2 or stack.get(count - 1) != chat:
            return
        dialogs = self.visible_fragment(stack.get(count - 2))
        if not self.dialogs_type.isInstance(dialogs) or dialogs.getCurrentAccount() != chat.getCurrentAccount():
            return
        self.origins = [entry for entry in self.origins if entry[0].get() is not None]
        if any(entry[0].get() == dialogs and entry[1].get() == chat for entry in self.origins):
            return
        self.origins = [entry for entry in self.origins if entry[0].get() != dialogs]
        tabs = self.tabs.get(dialogs)
        if tabs is not None and tabs.getTabsCount() > 1 and not tabs.isFirstTabSelected():
            stable_id = tabs.getCurrentTabStableId()
            if stable_id >= 0:
                self.origins.append((self.weak(dialogs), self.weak(chat), dialogs.getCurrentAccount(), stable_id))

    def restore_folder(self, param, committed=False):
        dialogs = param.thisObject
        entry = next((entry for entry in self.origins if entry[0].get() == dialogs), None)
        if entry is None:
            return
        if dialogs.getCurrentAccount() != entry[2]:
            self.origins.remove(entry)
            return
        navigation = dialogs.getParentLayout()
        if navigation is None:
            return
        top = navigation.getLastFragment()
        if self.visible_fragment(top) != dialogs and (committed or top != entry[1].get()):
            return
        if committed:
            self.origins.remove(entry)
        tabs, pages = self.tabs.get(dialogs), self.pages.get(dialogs)
        if tabs is None or tabs.getVisibility() != 0 or pages is None or not len(pages) or pages[0] is None:
            return
        self.select_folder(dialogs, tabs, pages[0], entry[3])

    def select_folder(self, dialogs, tabs, page, stable_id):
        for position in range(tabs.getTabsCount()):
            if tabs.getStableId(position) != stable_id:
                continue
            tab = tabs.getTab(position)
            filters = dialogs.getMessagesController().getDialogFilters()
            if tab.isLocked or not 0 <= tab.id < filters.size():
                return
            current = filters.get(tab.id)
            if (0 if current.isDefault() else current.localId) != stable_id:
                return
            if self.selected.getInt(page) == tab.id and tabs.getCurrentTabStableId() == stable_id:
                return
            if tabs.selectTabWithStableId(stable_id):
                self.selected.setInt(page, tab.id)
                dialogs.switchToCurrentSelectedMode(False)
                tabs.finishAddingTabs(False)
                tabs.getTabsContainer().scrollToPosition(position)
            return

    def on_plugin_unload(self):
        self.origins.clear()
        for hook in self.hooks:
            self.unhook_method(hook)


class PluginSettingRows(PluginFeature):
    def on_plugin_load(self):
        screen = jclass("com.exteragram.messenger.plugins.ui.PluginSettingsActivity").getClass()
        cell = jclass("org.telegram.ui.Cells.TextCheckCell").getClass()
        controller = jclass("com.exteragram.messenger.plugins.PluginsController").getClass()
        self.settings_engine_type = jclass("com.exteragram.messenger.plugins.PluginsController$PluginsEngine")
        self.screen_plugin = field(screen, "plugin")
        self.screen_list = field(screen, "listView")
        self.screen_reset = field(screen, "resetItem")
        self.row_title = field(cell, "textView")
        self.row_detail = field(cell, "valueTextView")
        self.measure_spec = jclass("android.view.View$MeasureSpec")
        self.dp = jclass("org.telegram.messenger.AndroidUtilities").dp
        self.weak_reference = jclass("java.lang.ref.WeakReference")
        self.lists = []
        self.settings_reset = None
        self.hooks = [
            self.hook_method(method(screen, "createView", 1), after=self.track_settings_list),
            self.hook_method(method(cell, "onMeasure", 2), before=self.measure_text_rows),
            self.hook_method(method(controller, "setPluginSetting", 3), before=self.save_switch_without_rebind),
        ]

    def track_settings_list(self, param):
        screen = param.thisObject
        plugin = self.screen_plugin.get(screen)
        listing = self.screen_list.get(screen)
        if plugin is not None and plugin.getId() == __id__ and listing is not None:
            self.lists = [ref for ref in self.lists if ref.get() not in (None, listing)]
            self.lists.append(self.weak_reference(listing))
            reset = self.screen_reset.get(screen)
            self.settings_reset = self.weak_reference(reset) if reset is not None else None

    def save_switch_without_rebind(self, param):
        plugin_id, key, value = param.args
        if plugin_id != __id__ or key not in SWITCH_KEYS:
            return
        engine = param.thisObject.getPluginEngine(plugin_id)
        if engine is None:
            return
        # The native row and its UItem have already toggled; the caller still runs its on-change callback.
        cast(self.settings_engine_type, engine).setPluginSetting(plugin_id, key, value)
        param.setResult(None)
        reset = self.settings_reset
        if reset is not None:
            def show_reset():
                item = reset.get()
                if item is not None and item.getVisibility() != 0:
                    item.setVisibility(0)

            run_on_ui_thread(show_reset)

    def measure_text_rows(self, param):
        cell = param.thisObject
        parent = cell.getParent()
        if parent is None or not any(ref.get() == parent for ref in self.lists):
            return
        detail = self.row_detail.get(cell)
        if detail.getVisibility() != 0:
            return
        title = self.row_title.get(cell)
        title_params, detail_params = title.getLayoutParams(), detail.getLayoutParams()
        for label in (title, detail):
            if label.getMaxLines() != 2147483647 or label.getEllipsize() is not None:
                label.setSingleLine(False)
                label.setMaxLines(2147483647)
                label.setEllipsize(None)
        spec = self.measure_spec
        width = spec.getSize(int(param.args[0])) - cell.getPaddingLeft() - cell.getPaddingRight()
        title_width = max(1, width - title_params.leftMargin - title_params.rightMargin)
        title.measure(spec.makeMeasureSpec(title_width, spec.EXACTLY), spec.makeMeasureSpec(0, spec.UNSPECIFIED))
        detail_params.topMargin = title_params.topMargin + title.getMeasuredHeight() + self.dp(3)

    def on_plugin_unload(self):
        for hook in getattr(self, "hooks", ()):
            self.unhook_method(hook)


FEATURES = (
    (PluginSettingRows, ()),
    (FastViewerPlugin, ("fast_viewer",)),
    (AyuFilterDisplayFix, ("filter_display",)),
    (MainTabsGlass, ("main_tabs_glass",)),
    (ChatFolderReturn, ()),
    (TenThousandCounts, ()),
    (VideoSeekbarGestureInsets, ("video_toolbar", "photo_shadows", "album_thumbnails",
                               "double_tap", "double_tap_seek", "hold_speed",
                               "pinch", "fullscreen_swipe", "orientation",
                               "brightness_swipe", "volume_swipe", "auto_fullscreen", "auto_fullscreen_on_switch")),
    (MediaSleepTimer, ("timer", "audio_toolbar", "hide_audio_profile_button")),
    (SystemVideoPip, ("system_pip", "media_controls", "background_audio", "video_autoplay")),
)


class NagramXFMediaSuite(BasePlugin):
    def select_language(self, mode):
        global plugin_language
        language = system_language_code() if mode == LANGUAGE_AUTO and jclass is not None else "zh"
        selected = choose_language(mode, language)
        if plugin_language != selected:
            plugin_language = selected
            if hasattr(self, "slider_factories"):
                self.slider_factories.clear()

    def change_language(self, mode):
        mode = int(mode)
        self.select_language(mode)
        self.set_setting("plugin_language", mode, reload_settings=True)
        player = self.components.get(SystemVideoPip)
        if player is not None:
            run_on_ui_thread(player[1].refresh_language)

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
        return SUITE_DEFAULTS.get(key, default)

    def set_setting(self, key, value, reload_settings=False):
        self.settings_backup().edit().putString(key, json.dumps(value, ensure_ascii=False)).apply()
        return super().set_setting(key, value, reload_settings)

    def on_plugin_load(self):
        self.select_language(self.get_setting("plugin_language", LANGUAGE_AUTO))
        self.flags = {key: bool(self.get_setting(key, DEFAULTS.get(key, True))) for key, _, _ in SETTINGS}
        self.components = {}
        self.running = True
        run_on_ui_thread(lambda: self.apply_settings(stagger=True), 24)

    def create_settings(self):
        from ui.settings import Header, Input, Selector, Switch

        self.select_language(self.get_setting("plugin_language", LANGUAGE_AUTO))
        rows = [Selector(key="plugin_language", text="插件语言", default=LANGUAGE_AUTO,
                         items=["跟随系统语言", "简体中文", "English"],
                         on_change=self.change_language)]
        for title, group in settings_groups():
            rows.append(Header(text=title))
            for key, label, detail in group:
                rows.append(Switch(key=key, text=label, subtext=detail, default=DEFAULTS.get(key, True),
                                   on_change=lambda enabled, name=key: self.change_feature(name, enabled)))
                if key == "hold_speed":
                    speeds = (*[f"{speed:g}×" for speed in HOLD_SPEED_PRESETS], "自定义")
                    rows.append(self.slider_setting("hold_speed_preset", "倍速预设", 0, len(speeds) - 1,
                                                    DEFAULT_HOLD_SPEED_INDEX, speeds.__getitem__, speeds))
                    rows.append(Input(key="hold_speed_custom", text="自定义倍速", default="2.5",
                                      subtext="预设选「自定义」后使用",
                                      on_change=lambda value: self.change_video_value("hold_speed_custom", value)))
                elif key == "album_thumbnails":
                    rows.append(thumbnail_default_state_setting(
                        lambda value: self.change_video_value("thumbnail_default_state", value)))
                    rows.append(thumbnail_state_scope_setting(
                        lambda value: self.change_video_value("thumbnail_state_scope", value)))
                    rows.append(thumbnail_position_setting(
                        lambda value: self.change_video_value("thumbnail_portrait_position", value),
                        SUITE_DEFAULTS["thumbnail_portrait_position"]))
            if title == "手势振动":
                rows.extend([
                    self.slider_setting("adjustment_tick_strength", "振动强度", 0, 100,
                                        SUITE_DEFAULTS["adjustment_tick_strength"], lambda n: f"{n}%" if n else "关闭"),
                    self.slider_setting("adjustment_tick_rate", "频率上限", 0, 30,
                                        SUITE_DEFAULTS["adjustment_tick_rate"], lambda n: f"{n} 次/秒" if n else "关闭"),
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
        affected = tuple((feature, keys) for feature, keys in FEATURES if key in keys)
        run_on_ui_thread(lambda: self.apply_settings(affected), 32)

    def change_video_value(self, key, value):
        self.set_setting(key, value)
        entry = self.components.get(VideoSeekbarGestureInsets)
        if entry is not None:
            run_on_ui_thread(lambda: self.configure_video_values(entry[1]))

    def configure_video_values(self, component):
        component.hold_speed = selected_hold_speed(
            self.get_setting("hold_speed_preset", DEFAULT_HOLD_SPEED_INDEX), self.get_setting("hold_speed_custom", "2.5"))
        component.configure_adjustment_ticks(self.get_setting("adjustment_tick_rate", "12"),
                                             self.get_setting("adjustment_tick_percent", "1"),
                                             self.get_setting("adjustment_tick_strength", "42"))
        component.load_thumbnail_width()
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
                if previous[0][1] and not values[1]:
                    component.restore_mini_audio_speed()
                for audio_ref, _, _ in component.audio_rows:
                    audio = audio_ref.get()
                    if audio is not None:
                        component.update_audio_footer(audio, restore=any(
                            before and not after for before, after in zip(previous[0][1:], values[1:])))
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
            if not keys or any(values[:-1] if feature is VideoSeekbarGestureInsets else values):
                component = feature(self, dict(zip(keys, values)))
                if feature is VideoSeekbarGestureInsets:
                    self.configure_video_values(component)
                    component.on_thumbnail_edge = self.prefetch_thumbnail_edge
                    component.caption_source_hidden = self.album_caption_hidden
                if feature is SystemVideoPip:
                    component.on_background_handoff = self.keep_video_timer
                    component.autoplay_timer_due = self.video_timer_due
                    component.make_playback_mode_capsule = self.make_playback_mode_capsule
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

    def make_playback_mode_capsule(self, context, selected, select):
        modes, labels = zip(
            (VIDEO_PLAY_STOP, "播完停止"),
            (VIDEO_PLAY_CONTINUOUS, "连续播放"),
            (VIDEO_PLAY_LOOP, "循环播放"),
        )
        positions = (0.0, 0.5, 1.0)

        def apply(final, _, point):
            if final:
                select(modes[point])

        return self.get_capsule_ui().make_gear_capsule(context, "播放模式", positions, labels,
            positions[modes.index(selected)], None, apply, discrete=True)

    def keep_video_timer(self, viewer):
        timer = self.components.get(MediaSleepTimer)
        if timer is not None:
            timer[1].follow_background_audio(viewer)

    def video_timer_due(self, player):
        timer = self.components.get(MediaSleepTimer)
        return timer is not None and timer[1].reached_deadline_for(player) is not None

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


def localize(source, catalog):
    """Route plugin UI literals through the shared catalog while preserving SDK metadata."""
    lines = source.splitlines(keepends=True)
    edits = []
    fstrings = []
    cjk = re.compile(r"[\u3400-\u9fff]")
    used = set()
    for token in tokenize.generate_tokens(StringIO(source).readline):
        kind, value, start, end, line = token
        if kind == tokenize.FSTRING_START:
            fstrings.append(value)
        elif kind == tokenize.FSTRING_END:
            fstrings.pop()
        elif kind in (tokenize.STRING, tokenize.FSTRING_MIDDLE) and cjk.search(value):
            if line.lstrip().startswith(("__name__ =", "__description__ =")) or "# bilingual" in line:
                continue
            if start[0] != end[0]:
                raise ValueError(f"Multiline translation at line {start[0]}")
            key = value if kind == tokenize.FSTRING_MIDDLE else ast.literal_eval(value)
            if key not in catalog:
                raise ValueError(f"Missing English translation for {key!r} at line {start[0]}")
            used.add(key)
            if kind == tokenize.FSTRING_MIDDLE:
                quote = "'" if fstrings[-1].endswith('"') else '"'
                if quote in key or "\\" in key:
                    raise ValueError(f"Unsupported translated f-string segment: {key!r}")
                replacement = "{tr(" + quote + key + quote + ")}"
            else:
                replacement = "tr(" + value + ")"
            edits.append((start[0] - 1, start[1], end[1], replacement))
    if catalog.keys() - used:
        raise ValueError(f"Unused translations: {sorted(catalog.keys() - used)}")
    for index, start, end, value in reversed(edits):
        lines[index] = lines[index][:start] + value + lines[index][end:]
    english = json.dumps(catalog, ensure_ascii=False, indent=4)
    return "".join(lines).replace("ENGLISH_STRINGS = {}", "ENGLISH_STRINGS = " + english, 1)


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
catalog = json.loads((plugins / "i18n" / "en.json").read_text(encoding="utf-8"))
source = localize(source, catalog)
filename = plugins / "nagramxf_media_suite.plugin"
compile(source, str(filename), "exec")
ast.parse(source, filename=str(filename), feature_version=(3, 11))
filename.write_text(source, encoding="utf-8", newline="\n")
print(f"Built {filename} ({len(source.encode('utf-8'))} bytes)")
