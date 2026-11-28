from pathlib import Path
from types import ModuleType, SimpleNamespace as Obj
import sys


def native_list(items):
    # Chaquopy exposes size and get for the target app's ArrayList.
    return Obj(get=items.__getitem__, size=lambda: len(items))


for name, attrs in {
    "android_utils": {"run_on_ui_thread": lambda fn, delay=0: None,
                      "OnClickListener": lambda fn: fn, "OnLongClickListener": lambda fn: fn, "R": lambda fn: fn},
    "base_plugin": {"BasePlugin": object},
    "client_utils": {"RequestCallback": object},
    "java": {"jarray": None, "jbyte": int, "jclass": None, "dynamic_proxy": None, "jfloat": float, "jint": int,
             "cast": lambda type_, value: value},
}.items():
    sys.modules[name] = ModuleType(name)
    vars(sys.modules[name]).update(attrs)


def load(name):
    merged_component = "--merged" in sys.argv and name != "nagramxf_media_suite"
    path = Path("plugins") / (("nagramxf_media_suite" if merged_component else name) + ".plugin")
    namespace = {"__name__": name}
    code = compile(path.read_text(encoding="utf-8"), str(path), "exec")
    exec(code, namespace)
    if merged_component:
        # Component tests supply fake Java state and do not need the real plugin owner.
        namespace["PluginFeature"].__init__ = lambda self: None
    return Obj(**namespace)


class JavaList(list):
    size = list.__len__
    get = list.__getitem__


def message(mid, day, *, is_date=False, kind=0):
    return Obj(messageOwner=object(), isDateObject=is_date, contentType=kind,
               dateKeyInt=day, getId=lambda: mid)


ayu = load("ayufilter_display_fix")


class PinnedList(JavaList):
    add, equals = list.append, list.__eq__

    def isEmpty(self):
        return not self

    def contains(self, value):
        return value in self

    def indexOf(self, value):
        return self.index(value) if value in self else -1


def member(name):
    get = lambda obj: getattr(obj, name)
    set_value = lambda obj, value: setattr(obj, name, value)
    return Obj(get=get, set=set_value, getInt=get, setInt=set_value, getBoolean=get, setBoolean=set_value)


read_updates = []
read_dialog = Obj(top_message=601, unread_count=3)
read_controller = Obj(ignoreSetOnline=False, dialogs_dict={10: read_dialog},
                      markDialogAsRead=lambda *args: read_updates.append(args))
hidden_latest = Obj(messageOwner=Obj(date=1234))
read_rows = PinnedList([hidden_latest])
read_adapter = Obj(start=2, end=3, isFiltered=False, isFrozen=False, getMessages=lambda: read_rows)
read_chat = Obj(getChatMode=lambda: 0, isFeedSearch=lambda: False, isSecretChat=lambda: False,
                isTopic=False, isThreadChat=lambda: False, isInPreviewMode=lambda: False,
                paused=False, loading=False, hiding=True, at_end=[True],
                query=0, canceled=False, jump_id=0, history=[{601: hidden_latest}], adapter=read_adapter,
                getDialogId=lambda: 10, getCurrentAccount=lambda: 1, getClassGuid=lambda: 533,
                getChatListView=lambda: Obj(isFastScrollAnimationRunning=lambda: False))
read_fix = ayu.AyuFilterDisplayFix()
read_fix.active, read_fix.page_down_context, read_fix.latest_read_request = True, None, None
read_fix.forward_end, read_fix.chat_paused, read_fix.chat_first_loading = (
    member("at_end"), member("paused"), member("loading"))
read_fix.latest_query, read_fix.latest_query_canceled, read_fix.postponed_message = (
    member("query"), member("canceled"), member("jump_id"))
read_fix.hide_mode, read_fix.message_dict, read_fix.adapter = member("hiding"), member("history"), member("adapter")
read_fix.start, read_fix.end = member("start"), member("end")
read_fix.weak = lambda chat: Obj(get=lambda: chat)
read_fix.ayu = Obj(isDialogExcluded=lambda dialog: False)
read_fix.mc = Obj(getInstance=lambda account: read_controller if account == 1 else None)
read_fix.position_type = lambda adapter, position: ayu.HIDDEN_ROW if position == 2 else 0
read_param = Obj(thisObject=read_chat)
read_fix.after_scroll_to_latest(read_param)
assert not read_updates, "Programmatic scrolls must not use the jump-to-latest read fallback"
read_fix.before_page_down(read_param)
read_fix.after_page_down(read_param)
assert not read_updates, "Navigating to an unread divider or a reply is not a jump to the latest message"
read_fix.before_page_down(read_param)
read_fix.after_scroll_to_latest(read_param)
read_fix.after_page_down(read_param)
assert read_updates == [(10, 601, 601, 1234, False, 0, 3, True, 0)]
read_updates.clear()

for owner, key, value in (
        (read_chat, "at_end", [False]), (read_chat, "paused", True), (read_chat, "hiding", False),
        (read_chat, "isTopic", True), (read_adapter, "isFiltered", True),
        (read_controller, "ignoreSetOnline", True), (read_dialog, "top_message", 602),
        (read_fix.ayu, "isDialogExcluded", lambda dialog: True),
        (read_fix, "position_type", lambda adapter, position: 0)):
    previous = getattr(owner, key)
    setattr(owner, key, value)
    read_fix.read_hidden_latest(read_chat)
    assert not read_updates, key
    setattr(owner, key, previous)

read_fix.before_page_down(read_param)
read_chat.query = 21
read_fix.after_scroll_to_latest(read_param)
read_fix.after_page_down(read_param)
assert not read_updates
loaded = [10] + [None] * 9 + [532, 21] + [None] * 3
read_fix.after_latest_load(read_chat, loaded)
assert read_fix.latest_read_request[1] == 21 and not read_updates
loaded[10], read_chat.query = 533, 22
read_fix.after_latest_load(read_chat, loaded)
assert read_fix.latest_read_request[1] == 22 and not read_updates
loaded[11], read_chat.query = 22, 0
read_fix.after_latest_load(read_chat, loaded)
assert len(read_updates) == 1 and read_fix.latest_read_request is None
read_updates.clear()
read_fix.latest_read_request = read_fix.weak(read_chat), 22
read_chat.canceled = True
read_fix.after_latest_load(read_chat, loaded)
assert not read_updates and read_fix.latest_read_request is None
print("Passed filtered latest-message read receipts, cache retry, and canceled navigation")


previews = ayu.AyuFilterDisplayFix()
previews.active, previews.layouts = True, []
previews.cache, previews.queued, previews.running = ayu.OrderedDict(), ayu.OrderedDict(), {}
previews.preview_warm_accounts, previews.preview_warm_at = {}, {}
previews.preview_warm_dirty, previews.preview_warm_checked = set(), ayu.OrderedDict()
previews.preview_account = Obj(selectedAccount=0)
previews.schedule_preview_warm = lambda *args, **kwargs: None
previews.preview_drain_pending = False
previews.account, previews.cell_message, previews.cell_group, previews.cell_date = (
    member("account"), member("message"), member("group"), member("date"))
dummy = object()
previews.dummies = [dummy, dummy]
scope = (0, -55)
preview_dialog = Obj(top_message=70, last_message_date=100)
previews.mc = Obj(getInstance=lambda _: Obj(dialogs_dict={-55: preview_dialog}, dialogMessage={},
                                             getChat=lambda _: object()))
previews.chat_object = Obj(isChannel=lambda _: True)
previews.ayu = Obj(shouldHideFilteredMessages=lambda: True)
previews.dialog_object = Obj(isEncryptedDialog=lambda _: False)
previews.allowed = lambda message, group, key: not getattr(message, "hidden", False)


def preview_message(mid, date):
    return Obj(getId=lambda: mid, getDialogId=lambda: -55, getGroupId=lambda: 0,
               messageOwner=Obj(date=date, edit_date=0))


old_preview, newer_preview = preview_message(66, 90), preview_message(68, 97)
preview_cell = Obj(account=0, message=old_preview, group=None, date=90, isDialogCell=True,
                   insideCommunityListNoDialog=False, isDialogFolder=lambda: False,
                   isDialogCommunity=lambda: False, getDialogId=lambda: -55)
preview_param = Obj(thisObject=preview_cell)
requested, rebuilt = [], []
previews.schedule = lambda _, key: requested.append(key)
previews.track_cell = lambda *_: None
previews.matching_cells = lambda key=None: [preview_cell] if key is None or key == previews.preview_key(preview_cell) else []
previews.rebuild_cell = rebuilt.append
previews.before_layout(preview_param)
previews.after_layout(preview_param)
assert previews.cache[scope][2] == (old_preview, None)
preview_cell.message = dummy


def render_preview():
    previews.before_layout(preview_param)
    visible = preview_cell.message
    previews.after_layout(preview_param)
    assert preview_cell.message is dummy
    return visible


def finish_preview(candidate=None, retry=False):
    lookup = ayu.PreviewSearch.__new__(ayu.PreviewSearch)
    lookup.plugin, lookup.key = previews, requested[-1]
    lookup.prefetch = False
    previews.running[lookup.key] = lookup
    lookup.finish(candidate, retry=retry)


assert render_preview() is old_preview and len(requested) == 1
finish_preview()
assert render_preview() is old_preview and len(requested) == 1  # A checked head has no expiry.
preview_dialog.top_message = 71
assert render_preview() is old_preview and len(requested) == 2
finish_preview(retry=True)
assert render_preview() is old_preview and len(requested) == 2 and not rebuilt
preview_dialog.top_message = 72
assert render_preview() is old_preview
finish_preview((newer_preview, None))
assert render_preview() is newer_preview and rebuilt == [preview_cell]
preview_dialog.top_message = 73
assert render_preview() is newer_preview
finish_preview((old_preview, None))
assert render_preview() is newer_preview and len(rebuilt) == 1
previews.delete_previews(0, {68}, 56)  # Same ID belongs to a different channel.
assert render_preview() is newer_preview
previews.refresh_previews()
assert render_preview() is newer_preview
previews.delete_previews(0, {68}, 55)
assert render_preview() is dummy
previews.matching_cells = lambda *_: iter(())
warm_key = previews.dialog_preview_key(0, -55, preview_dialog, previews.mc.getInstance(0))
warm_request = ayu.PreviewSearch.__new__(ayu.PreviewSearch)
warm_request.plugin, warm_request.key, warm_request.prefetch = previews, warm_key, True
warm_request.active_scope = lambda: True
previews.running[warm_key] = warm_request
warm_request.finish((newer_preview, None))
assert previews.cache[scope] == (warm_key, None, (newer_preview, None))
assert warm_key not in previews.running

# Each folder's initial entries are considered before the unbounded loaded-chat sweep.
warm_dialogs = [Obj(id=mid, top_message=mid) for mid in range(1, 231)]
preview_folder = Obj(isDefault=lambda: False, includesDialog=lambda _, dialog_id, __: dialog_id >= 210)
all_dialogs = native_list(warm_dialogs)
first_dialogs = (native_list(warm_dialogs[:18]), native_list(warm_dialogs[190:205]))
warm_controller = Obj(getDialogs=first_dialogs.__getitem__, getDialogFilters=lambda: native_list([preview_folder]),
                      getAllDialogs=lambda: all_dialogs)
previews.preview_dialog_type = Obj(isInstance=lambda value: value is not None)
previews.account_instance = Obj(getInstance=lambda _: object())
ordered_warm = [dialog.id for dialog in previews.preview_warm_dialogs(0, warm_controller) if dialog is not None]
assert ordered_warm[:4] == [1, 191, 2, 192]
assert ordered_warm.index(210) < ordered_warm.index(100)
assert set(ordered_warm) == set(range(1, 231))
pending_scan = []
background_namespace = previews.warm_preview_rows.__globals__
background_scheduler = background_namespace["run_on_ui_thread"]
original_mc = previews.mc
try:
    background_namespace["run_on_ui_thread"] = lambda fn, delay=0: pending_scan.append((fn, delay))
    previews.mc = Obj(getInstance=lambda _: warm_controller)
    previews.ayu.shouldHideIgnoredBlockedMessages = lambda: False
    ticket = previews.preview_warm_accounts[0] = object()
    touched = []
    previews.warm_dialog_preview = lambda _, dialog_id, *args: touched.append(dialog_id)
    previews.warm_preview_rows(0, ticket)
    assert 0 < len(touched) <= 8
    while pending_scan:
        scan, delay = pending_scan.pop(0)
        before = len(touched)
        scan()
        assert len(touched) - before <= 8 and delay == ayu.PREVIEW_WARM_STEP_MS
    assert len(touched) == len(set(touched)) == 230 and not previews.preview_warm_accounts
finally:
    previews.mc = original_mc
    background_namespace["run_on_ui_thread"] = background_scheduler

# A local preview appears immediately but doesn't mark the head as checked by the server.
previews.cache.clear()
previews.rebuild_cell = rebuilt.append
warm_request.keep_preview((old_preview, None), [], provisional=True)
assert previews.cache[scope] == (None, None, (old_preview, None))
warm_request.keep_preview((newer_preview, None), [])
assert previews.cache[scope] == (warm_key, None, (newer_preview, None))
print("Passed startup preview priority, sliced scanning, local fallback and durable preview updates")


pins = ayu.AyuFilterDisplayFix()
pins.pinned_chats, pins.pinned_frames = [], []
pins.pin_projections = {}
pins.pin_projection_events = {70}
pins.weak = lambda chat: Obj(get=lambda: chat)
pins.integer, pins.java_boolean, pins.java_list, pins.object_array = int, bool, PinnedList, list
pins.pinned_ids, pins.pinned_objects, pins.message_dict = member("ids"), member("objects"), member("history")
pins.current_pin, pins.pin_index = member("current"), member("index")
pins.loaded_pin_count, pins.total_pin_count, pins.hide_mode = member("loaded"), member("total"), member("hiding")
pins.find_pin, pins.hide_pin_view, pins.check_pin_paddings = "select", "hide", "paddings"
native_updates = []


def native_pin(method, chat, args):
    if method != "select":
        native_updates.append((method, args))
        return True
    candidates, target, index = args
    if not candidates:
        return 0
    selected = min(candidates, key=lambda mid: abs(target - mid))
    index[0] = candidates.index(selected)
    return selected


pins.original = native_pin
pin_preferences = {}


def notifications_settings(account):
    assert account == 1
    return Obj(getInt=lambda key, default: pin_preferences.get(key, default))


pins.mc = Obj(getNotificationsSettings=notifications_settings)
pins.media_hidden = lambda msg, chat, group: (
    chat.hiding and not chat.excluded and msg.hidden
    and not (group.findPrimaryMessageObject() if group is not None else msg).skipAyuFiltering)


def pinned_message(hidden=False, skip=False):
    return Obj(messageOwner=object(), hidden=hidden, skipAyuFiltering=skip, getGroupId=lambda: 0)


filtered = pinned_message(hidden=True, skip=True)
allowed_pin = pinned_message()
pin_chat = Obj(ids=PinnedList([40, 30, 20, 10]), objects={40: filtered, 10: filtered},
               history=[{30: allowed_pin}], current=40, index=[0], loaded=4, total=6, hiding=True,
               excluded=False, mode=0, isThreadChat=lambda: False, isTopic=False)
pin_chat.getChatMode = lambda: pin_chat.mode
pin_chat.getCurrentAccount = lambda: 1
pin_chat.getClassGuid = lambda: 45
pin_chat.getDialogId = lambda: -100
original_pin_ids = pin_chat.ids
pin_results = []
banner = Obj(thisObject=pin_chat, args=[True, 1], setResult=pin_results.append)
pins.before_pinned_ui(banner, "banner")
assert pin_chat.ids == [30, 20] and pin_chat.current == 30 and pin_chat.index == [0]
assert (pin_chat.loaded, pin_chat.total) == (2, 2) and banner.args == [False, 0]
assert filtered.skipAyuFiltering
pins.after_pinned_ui(banner)
assert pin_chat.ids is original_pin_ids and pin_chat.index == [1] and (pin_chat.loaded, pin_chat.total) == (4, 6)
selection = Obj(thisObject=pin_chat, args=[pin_chat.ids, 40, pin_chat.index],
                getResult=lambda: 40, setResult=pin_results.append)
pins.after_choose_pin(selection)
assert pin_results == [30] and pin_chat.index == [1]

pin_chat.current, pin_chat.ids = 40, PinnedList([40, 10])
pins.before_pinned_ui(banner, "banner")
assert not pin_chat.ids and pin_chat.current == 0
pins.after_pinned_ui(banner)
assert pin_chat.ids == [40, 10]
pin_chat.excluded = True
pins.forget_pin_projection(Obj(thisObject=pin_chat))
pin_chat.current = 40
pins.before_pinned_ui(banner, "banner")
assert pin_chat.ids == [40, 10] and pin_chat.current == 40
pins.after_pinned_ui(banner)

pin_chat.excluded = False
pins.forget_pin_projection(Obj(thisObject=pin_chat))
pin_chat.hiding = False
open_list = Obj(thisObject=pin_chat, args=[False])
pins.before_pinned_ui(open_list, "open")
child = Obj(hiding=True)
pins.inherit_pinned_filter(Obj(thisObject=child, args=[Obj(getInt=lambda _: ayu.PINNED_CHAT_MODE)]))
assert not child.hiding and pin_chat.ids == [40, 10]
pins.after_pinned_ui(open_list)
pin_chat.hiding = True
pin_chat.ids = original_pin_ids
pins.before_pinned_ui(open_list, "open")
assert pin_chat.ids == [30, 20]
pins.after_pinned_ui(open_list)
assert pin_chat.ids is original_pin_ids

# The stock hide button records the newest server pin, even when the banner shows an older one.
pin_preferences["pin_-100"] = 40
dismissed_banner = Obj(thisObject=pin_chat, args=[True, 1], setResult=pin_results.append)
pins.before_pinned_ui(dismissed_banner, "banner")
assert pin_chat.ids is original_pin_ids and pin_chat.ids[0] == pin_preferences["pin_-100"]
assert dismissed_banner.args == [True, 1]
pins.after_pinned_ui(dismissed_banner)

pin_chat.ids = PinnedList([50, *original_pin_ids])
pin_chat.objects[50] = allowed_pin
pin_chat.current = 50
pins.before_pinned_ui(dismissed_banner, "banner")
assert pin_chat.ids == [50, 30, 20] and pin_chat.current == 50
pins.after_pinned_ui(dismissed_banner)
assert pin_chat.ids == [50, 40, 30, 20, 10]

pin_preferences.clear()
pin_chat.ids, pin_chat.current = original_pin_ids, 40
pins.before_pinned_ui(dismissed_banner, "banner")
assert pin_chat.ids == [30, 20] and pin_chat.current == 30
pins.after_pinned_ui(dismissed_banner)
pin_chat.mode = ayu.PINNED_CHAT_MODE
pins.after_pinned_count(Obj(thisObject=pin_chat, setResult=pin_results.append))
assert pin_results[-1] == 2
pin_chat.mode = 0
observed_pins = []
hide_pin = pins.pinned_hidden
pins.pinned_hidden = lambda chat, message: (observed_pins.append(message), hide_pin(chat, message))[1]
pins.forget_pin_projection(Obj(thisObject=pin_chat))
for _ in range(3):
    visible, loaded = pins.visible_pins(pin_chat, pin_chat.ids)
    assert visible == [30, 20] and loaded == [30]
assert len(observed_pins) == 4
# A message can finish loading or be edited with the pin IDs unchanged.
pin_chat.objects[40] = allowed_pin
pins.before_pin_change(Obj(thisObject=pin_chat, args=[70]))
assert pins.visible_pins(pin_chat, pin_chat.ids)[0] == [40, 30, 20]
assert len(observed_pins) == 8
pin_chat.ids[0] = 50
assert pins.visible_pins(pin_chat, pin_chat.ids)[0] == [50, 30, 20]
assert len(observed_pins) == 12
pin_chat.ids[0], pin_chat.objects[40] = 40, filtered
pins.forget_pin_projection(Obj(thisObject=pin_chat))
pins.pinned_hidden = hide_pin
pin_chat.isThreadChat = lambda: True
pin_chat.getThreadMessage = lambda: filtered
pins.before_pinned_ui(banner, "banner")
assert pin_results[-1] is None and native_updates == [("hide", [False]), ("paddings", [])]
pins.after_pinned_ui(banner)

rows = JavaList([message(42, 25), message(41, 25),
                 message(0, 25, kind=2), message(0, 25, is_date=True),
                 message(40, 24)])
assert not ayu.day_has_visible_message(rows, 3, 25, lambda index: index in (2, 4))
assert ayu.day_has_visible_message(rows, 3, 25, lambda index: index == 0)
assert ayu.day_has_visible_message(rows, 3, 24, lambda index: index == 4)
assert not ayu.day_has_visible_message(JavaList([rows[3]]), 0, 25, lambda _: True)
assert ayu.day_has_visible_message(JavaList([rows[3], message(-3, 25)]), 0, 25, lambda _: True)


def raw(mid, group=0):
    return Obj(id=mid, grouped_id=group)


seen = []


def choose(messages):
    ids = tuple(raw.id for raw in messages)
    seen.append(ids)
    return ids if ids == (44,) else None


pages = ayu.AlbumPages()
assert pages.consume([raw(50, 5), raw(49, 5)], choose) is None
assert not seen
assert pages.consume([raw(48, 5), raw(47), raw(46, 6)], choose) is None
assert seen == [(50, 49, 48), (47,)]
assert pages.consume([raw(45, 6), raw(44), raw(43)], choose) == (44,)
assert seen == [(50, 49, 48), (47,), (46, 45), (44,)]
pages = ayu.AlbumPages()
assert pages.consume([raw(-5, 2), raw(-4, 2)], choose) is None
assert pages.consume([], lambda album: [x.id for x in album], end=True) == [-5, -4]

video = load("video_seekbar_gesture_insets")
assert video.needed_lift(36, 0, 0, 8, 24) == 44
assert video.needed_lift(36, 0, 24, 8, 24) == 20
assert video.needed_lift(36, 0, 36, 8, 24) == 8
assert video.needed_lift(0, 0, 0, 8, 24) == 32
assert video.needed_lift(0, 0, 24, 8, 24) == 8
assert video.needed_lift(0, 48, 0, 8, 24) == 0
assert video.row_spacing(48, 16, 0) == (48, 0)
assert video.row_spacing(48, 32, 24) == (72, 24)
assert video.row_spacing(48, 70, 5) == (71, 14)
assert video.row_spacing(44, 16, 12, 4) == (64, 16)
assert video.VIDEO_CONTROLS_HEIGHT == 56 and video.VIDEO_ICON_SIZE == 24
for inset, scrubber_lift in ((0, 8), (14, 22), (32, 66)):
    lift, bottom = video.row_spacing(40, scrubber_lift, inset, video.PORTRAIT_TOOLS_GAP, 13)
    assert lift >= scrubber_lift and lift + 13 - (bottom + 40 - 8) == bottom + 8 - inset
    assert bottom + 8 - inset >= 16
assert video.symmetric_rail_bounds(720, 76, 628) == (92, 536)
assert video.symmetric_rail_bounds(381, 14, 360) == (21, 339)
assert video.popup_offsets(0, 0, 582, 249, 946, 84, 68, 318, 306, 12, 18) == (-117, -386, 306)
assert video.popup_offsets(0, 30, 360, 300, 250, 40, 44, 220, 400, 8, 12) == (-172, -252, 200)
assert video.side_popup_offsets(52, 0, 1100, 540, 910, 481, 44,
                                320, 520, 6, 8, 2, 12) == (-326, -519, 320, 520)
assert video.side_popup_offsets(52, 0, 1100, 540, 1020, 8, 44,
                                320, 520, 6, 8, 2, 12) == (-326, -50, 320, 520)
assert video.side_popup_offsets(28, 0, 210, 360, 180, 8, 44,
                                320, 90, 6, 8, 2, 12) == (-144, -50, 166, 90)

params = Obj(bottomMargin=10)
margin = video.ControlMargin(None, params.bottomMargin)
margin.update(params, 20)
assert params.bottomMargin == 30
margin.update(params, 20)
assert params.bottomMargin == 30
margin.update(params, 8)
assert params.bottomMargin == 18
margin.update(params, 0)
assert params.bottomMargin == 10
margin.update(params, 8)
params.bottomMargin = 15
margin.update(params, 8)
assert params.bottomMargin == 23
margin.update(params, 0)
assert params.bottomMargin == 15


class FooterView:
    def __init__(self, container, height, margin):
        self.container = container
        self.height = height
        self.visibility = 0
        self.params = Obj(bottomMargin=margin, height=height)

    def getParent(self):
        return self.container

    def getVisibility(self):
        return self.visibility

    def getLayoutParams(self):
        return self.params

    def getMeasuredHeight(self):
        return self.height

    def getMeasuredWidth(self):
        return 360

    def getPaddingLeft(self):
        return 0

    def getPaddingRight(self):
        return 0

    def setTranslationX(self, value):
        self.translation_x = value

    def measure(self, width, height):
        assert width == 360
        self.height = height


def value_field(value):
    return Obj(get=lambda _: value)


class MediaList(JavaList):
    add = list.append

    def indexOf(self, item):
        return self.index(item) if item in self else -1


media_fix = ayu.AyuFilterDisplayFix()
media_fix.java_list = MediaList
media_fix.java_boolean = bool
media_fix.integer = int
media_fix.weak = lambda target: Obj(get=lambda: target)
photo_grid, media_layout = object(), Obj(getParent=lambda: None)
photo_data = Obj(start=87, frozen=87, getMessages=lambda: MediaList([1, 2, 3]))
media_fix.shared_data = value_field([photo_data])
media_fix.photo_adapter = value_field(photo_grid)
media_fix.supporting_photo_adapter = value_field(None)
media_fix.photo_outer = value_field(media_layout)
media_fix.media_start = Obj(setInt=lambda target, value: setattr(target, "start", value))
media_fix.media_frozen_start = Obj(setInt=lambda target, value: setattr(target, "frozen", value))
media_fix.media_dialog = Obj(getLong=lambda _: 5)
media_fix.media_merge = Obj(getLong=lambda _: 0)
preferences = Obj(excluded=False)
media_fix.ayu = Obj(isDialogExcluded=lambda _: preferences.excluded, shouldHideFilteredMessages=lambda: True,
                    shouldHideIgnoredBlockedMessages=lambda: False, shouldMaskFilteredMessages=lambda: False)
media_fix.filtered_media_data = []
media_fix.media_layouts = []
media_fix.checked_media_data = []
counts = []
media_fix.after_photo_count(Obj(thisObject=photo_grid, setResult=counts.append))
assert counts == [3] and (photo_data.start, photo_data.frozen) == (0, 0)
preferences.excluded = True
media_fix.after_photo_count(Obj(thisObject=photo_grid, setResult=counts.append))
assert counts == [3]

media_fix.media_hidden = lambda msg, chat=None, group=None: msg.hidden and not preferences.excluded
preferences.excluded = False
hidden1 = Obj(hidden=True, getId=lambda: 89, getGroupId=lambda: 0)
hidden2 = Obj(hidden=True, getId=lambda: 88, getGroupId=lambda: 0)
available = Obj(hidden=False, getId=lambda: 87, getGroupId=lambda: 0)
media_fix.viewer_chat = value_field(None)
media_fix.viewer_media_type = Obj(getInt=lambda _: 0)
fake_viewer = Obj(getClassGuid=lambda: 77, isVisible=lambda: True)


def gallery_request(message, entries=None, index=0, chat=None):
    args = [None] * 16
    args[0], args[4], args[7], args[9], args[10] = message, entries, index, chat, 5
    return Obj(thisObject=fake_viewer, args=args, setResult=counts.append)


clicked = gallery_request(available, MediaList([hidden1, available]), 1)
media_fix.before_viewer_open(clicked)
assert clicked.args[4] == [available] and clicked.args[7] == 0
media_fix.before_viewer_open(gallery_request(hidden1, MediaList([hidden1, available])))
assert counts[-1] is False
media_fix.before_viewer_open(gallery_request(hidden1))
assert counts[-1] is False

media_fix.media_event = 10
media_fix.viewer_dialog = Obj(getLong=lambda _: 5)
media_fix.viewer_merge = Obj(getLong=lambda _: 0)
media_fix.viewer_topic = Obj(getLong=lambda _: 1)
media_fix.viewer_tag = value_field(None)
media_fix.object_array = list
media_fix.system = Obj(arraycopy=lambda source, start, target, index, length:
                       target.__setitem__(slice(index, index + length), source[start:start + length]))
media_fix.dialog_object = Obj(isEncryptedDialog=lambda _: False)
media_fix.viewer_cursors = {}
load_requests = []
media_fix.media_controller = Obj(getInstance=lambda _: Obj(loadMedia=lambda *args: load_requests.append(args)))


def viewer_page(items, end=False, from_start=False, guid=77, request=0):
    payload = [5, 130, MediaList(items), guid, 0, end, from_start, request]
    update = Obj(thisObject=fake_viewer, args=[10, 0, payload], setResult=counts.append)
    media_fix.before_viewer_page(update)
    assert payload[2] == items
    return update.args[2][2]


assert viewer_page([hidden1, available]) == [available]
assert not load_requests
assert viewer_page([hidden1, hidden2]) == []
assert load_requests[-1][2:4] == (88, 0) and counts[-1] is None
assert viewer_page([hidden1, hidden2]) == [] and len(load_requests) == 1
assert viewer_page([hidden1, hidden2], from_start=True) == []
assert load_requests[-1][2:4] == (0, 89)
assert viewer_page([hidden1, hidden2], end=True) == [] and len(load_requests) == 2
assert viewer_page([hidden1, available], guid=42) == [hidden1, available]
fast = ayu.FAST_VIEWER_PAGE_INDEX
assert viewer_page([hidden1, available], guid=fast, request=fast) == [available]
assert viewer_page([hidden1, hidden2], guid=fast, request=fast) == [] and len(load_requests) == 2

window = object()
container = Obj(getParent=lambda: window)
native = [(48, 0), (48, 0), (68, 48), (32, 58), (460, 116)]
controls, background, thumbnails, preview, caption = footer_views = [
    FooterView(container, height, margin) for height, margin in native
]
player = object()
viewer = Obj(getVideoPlayer=lambda: player, getCurrentMessageObject=lambda: None, isVisible=lambda: True)
plugin = video.VideoSeekbarGestureInsets()
plugin.active = True
plugin.outer = value_field(viewer)
plugin.window = value_field(window)
plugin.controls = value_field(controls)
plugin.web_player = value_field(None)
plugin.caption = value_field(caption)
plugin.background = value_field(background)
plugin.footer_fields = tuple((value_field(view), index in (2, 4))
                             for index, view in enumerate(footer_views) if index != 1)
plugin.edit_mode = Obj(getInt=lambda _: 0)
plugin.footer_lift = lambda *args: (16, 0)
plugin.measure_spec = Obj(EXACTLY=1, makeMeasureSpec=lambda size, _: size)
plugin.weak_reference = lambda view: Obj(get=lambda: view)
plugin.dp = int
plugin.margins = []
plugin.rows = []
plugin.compact_controls = []
plugin.footer_shades = []
plugin.top_captions = []
plugin.photo_headers = []
plugin.album_strip = value_field(None)
plugin.video_time = value_field(None)
plugin.refresh_zoom = lambda _: None


def footer_layout():
    # Nagram recalculates these two margins and the viewport on each measure.
    thumbnails.params.bottomMargin = native[2][1]
    caption.params.bottomMargin = native[4][1]
    background.height = native[1][0]
    caption.height = native[4][0]
    plugin.after_container_measure(Obj(thisObject=container))


for _ in range(2):
    footer_layout()
    assert [view.params.bottomMargin for view in footer_views] == [16, 0, 64, 74, 132]
    assert background.height == 64
    assert background.height + background.params.bottomMargin == controls.height + controls.params.bottomMargin
    assert caption.height == 444
    assert caption.height + caption.params.bottomMargin == sum(native[4])
    assert thumbnails.params.bottomMargin - controls.params.bottomMargin == 48
native[2] = (68, 64)
footer_layout()
assert thumbnails.params.bottomMargin == 80
native[2] = (68, 48)
player = None
footer_layout()
assert [view.params.bottomMargin for view in footer_views] == [0, 0, 48, 58, 116]
assert background.height == 48
assert caption.height == 460
player = object()
row = FooterView(background, 48, 0)
row.setVisibility = lambda visibility: setattr(row, "visibility", visibility)
row.measure = lambda width, height: setattr(row, "actual_size", (width, height))
plugin.rows = [(plugin.weak_reference(background), plugin.weak_reference(row))]
plugin.refresh_row = lambda _: None
plugin.hide_header = lambda _: None
plugin.hide_center_accessibility = lambda _: None
plugin.hide_floating_fullscreen = lambda _: None
plugin.video_menu = value_field(None)
plugin.overflow = value_field(None)
plugin.row_height = 48
plugin.bottom_gap = 0
plugin.footer_lift = lambda *args: (16, 18)
footer_layout()
assert row.params.bottomMargin == 18 and row.visibility == 0
assert row.actual_size == (156, 48)
assert controls.params.bottomMargin == 66 and controls.height == 48
assert background.height == 114 and background.params.bottomMargin == 0
assert thumbnails.params.bottomMargin - controls.params.bottomMargin == 48

container.getMeasuredHeight = lambda: 800
container.getPaddingBottom = lambda: 0
footer_rail = plugin.thumbnail_rail = video.ThumbnailRail(viewer, None, container, (64, 64))
footer_rail.ready = footer_rail.bottom_docked = True
footer_rail.safe_bottom = 20
plugin.footer_lift = lambda *args: (55, 20)
positions = []
for slide, drag_height in ((0.0, None), (0.5, None), (1.0, None), (0.0, 24), (0.0, None)):
    footer_rail.slide, footer_rail.drag_height = slide, drag_height
    footer_layout()
    lift, icon_offset = plugin.thumbnail_bottom_handle_offsets(footer_rail)
    arrow_y = plugin.thumbnail_bottom_top(footer_rail) - video.THUMBNAIL_BOTTOM_HANDLE_HEIGHT - lift + icon_offset
    positions.append((800 - controls.params.bottomMargin, 800 - row.params.bottomMargin, arrow_y))
start = positions[0]
for position in positions[1:]:
    deltas = tuple(end - initial for end, initial in zip(position, start))
    assert deltas[0] == deltas[1] == deltas[2]
assert positions[2][0] - start[0] == 84 and positions[-1] == start
plugin.thumbnail_rail = None
plugin.footer_lift = lambda *args: (16, 18)

compact_row = Obj(getVisibility=lambda: 0)
plugin.compact_controls = [(plugin.weak_reference(viewer), plugin.weak_reference(compact_row))]
compact_height = (video.SCRUBBER_HEIGHT + video.COMPACT_TOOLS_ROW_HEIGHT + 2 * video.COMPACT_VISIBLE_GAP
                  - video.SCRUBBER_TRANSPARENT_TAIL)
assert compact_height == 76
assert (compact_height - video.COMPACT_VISIBLE_GAP - video.COMPACT_TOOLS_ROW_HEIGHT
        - (video.SCRUBBER_HEIGHT - video.SCRUBBER_TRANSPARENT_TAIL)) == video.COMPACT_VISIBLE_GAP
controls.params.height = controls.height = compact_height
footer_layout()
assert row.visibility == 8 and plugin.footer_active(viewer)
assert controls.params.bottomMargin == 0 and background.height == compact_height
assert thumbnails.params.bottomMargin - controls.params.bottomMargin == compact_height
plugin.compact_controls = []
controls.params.height = controls.height = 48
player = None
footer_layout()
assert controls.params.bottomMargin == 0 and background.height == 48 and row.visibility == 8
assert video.double_tap_action(20, 360) == "back"
assert video.double_tap_action(180, 360) == "play"
assert video.double_tap_action(340, 360) == "forward"
assert video.selected_hold_speed(video.DEFAULT_HOLD_SPEED_INDEX, "") == 2.5
assert video.selected_hold_speed(len(video.HOLD_SPEED_PRESETS), "1.75") == 1.75
assert video.selected_hold_speed(len(video.HOLD_SPEED_PRESETS), "nan") == 2.5
assert video.fullscreen_swipe(12, 78, False, 60)
assert video.fullscreen_swipe(-12, -78, True, 60)
assert not video.fullscreen_swipe(12, -78, False, 60)
assert not video.fullscreen_swipe(12, 78, True, 60)
assert not video.fullscreen_swipe(95, -78, True, 60)
assert video.swipe_level(0.5, 300, 400, 0.02) == 0.02
assert video.swipe_level(0.5, 300, 400, 0.0) == 0
assert video.swipe_level(0.5, -300, 400, 0.0) == 1
assert 0.5 < video.swipe_level(0.5, -30, 400, 0.0) < 0.7
assert video.auto_video_orientation(1081, 1080) == 6
assert video.auto_video_orientation(1080, 1081) == 7
assert video.auto_video_orientation(1080, 1080) is None
assert video.auto_video_orientation(0, 1080) is None
orientation_test = video.VideoSeekbarGestureInsets()
orientation_test.pending_chat_jump = None
orientation_test.active = True
orientation_test.sdk = 35
orientation_test.edit_mode = Obj(getInt=lambda _: 0)
orientation_test.video_attribute = Obj(isInstance=lambda _: True)
orientation_test.weak_reference = plugin.weak_reference
orientation_test.auto_hide_controls = value_field(None)
orientation_test.boolean = bool
orientation_test.android = Obj(cancelRunOnUIThread=lambda _: None)
orientation_test.call = lambda *args: None
orientation_test.axis_lock = orientation_test.axis_target = orientation_test.axis_suspended = None
orientation_test.media_sensor = None
orientation_test.auto_processed = orientation_test.fullscreen_session = None
orientation_test.native_fullscreen_mode = Obj(getInt=lambda _: 0)
orientation_test.orientation_listener = value_field(object())
orientation_test.auto_entry = orientation_test.opening_auto_rotation = None
orientation_test.opening_landscape_controls = None
orientation_test.automatic_fullscreen = False
orientation_test.flags = {"auto_fullscreen_on_switch": True}
display = Obj(orientation=-1, w=1001, h=1000, video_id=1, is_video=True, is_photo=False)
display.animation = 0
orientation_test.viewer_animation = Obj(getInt=lambda _: display.animation)
display_activity = Obj(getRequestedOrientation=lambda: display.orientation, isInPictureInPictureMode=lambda: False,
                       isFinishing=lambda: False, getSystemService=lambda _: None,
                       setRequestedOrientation=lambda orientation: setattr(display, "orientation", orientation))
landscape_requests = (video.LANDSCAPE, video.SENSOR_LANDSCAPE, video.REVERSE_LANDSCAPE)
display_mode = Obj(getPhysicalWidth=lambda: 1080, getPhysicalHeight=lambda: 2400)
display_activity.getWindowManager = lambda: Obj(getDefaultDisplay=lambda: Obj(getMode=lambda: display_mode))
display_activity.getResources = lambda: Obj(getIdentifier=lambda *_: 0)
display_window = Obj(getWidth=lambda: 640 if display.orientation in landscape_requests else 360,
                     getHeight=lambda: 360 if display.orientation in landscape_requests else 640, requestLayout=lambda: None)
orientation_test.window = value_field(display_window)
orientation_test.viewer_video_dimensions = lambda _: (display.w, display.h)
display_message = Obj(isVideo=lambda: display.is_video, isSponsored=lambda: False, getId=lambda: display.video_id,
                      isPhoto=lambda: display.is_photo, getPhoto=lambda: Obj(sizes=[Obj(w=display.w, h=display.h)]),
                      getDialogId=lambda: 20,
                      getDocument=lambda: Obj(attributes=native_list([Obj(w=display.w, h=display.h)])))
display_viewer = Obj(isVisible=lambda: True, getCurrentMessageObject=lambda: display_message,
                     getParentActivity=lambda: display_activity, isOpenedFullScreenVideo=lambda: False)
opening_frames, opening_controls = [], []
rotation_namespace = orientation_test.defer_opening_rotation.__globals__
rotation_runner = rotation_namespace["run_on_ui_thread"]
try:
    rotation_namespace["run_on_ui_thread"] = lambda callback, _: opening_frames.append(callback)
    orientation_test.call = lambda *args: opening_controls.append(args[1:])
    display.animation = 1
    orientation_test.check_auto_fullscreen(display_viewer)
    assert display.orientation == -1 and not opening_controls and len(opening_frames) == 1
    opening_frames.pop(0)()
    assert display.orientation == -1 and len(opening_frames) == 1
    display.animation = 0
    orientation_test.check_auto_fullscreen(display_viewer, Obj(width=1920, height=1080,
                                                unappliedRotationDegrees=0, pixelWidthHeightRatio=1))
    assert display.orientation == -1 and len(opening_frames) == 1
    opening_frames.pop(0)()
    assert display.orientation == 6 and not opening_controls
    opening_control_layouts = []
    drawer_shape = Obj(width=360, height=640)
    opening_drawer = Obj(getWidth=lambda: drawer_shape.width, getHeight=lambda: drawer_shape.height,
                         requestLayout=lambda: opening_control_layouts.append("layout"))
    row_state = Obj(visibility=8, alpha=0.0)
    orientation_test.controls = value_field(Obj(getParent=lambda: opening_drawer,
        setVisibility=lambda value: setattr(row_state, "visibility", value),
        setAlpha=lambda value: setattr(row_state, "alpha", value)))
    orientation_test.video_controls_animator = value_field(Obj(cancel=lambda: opening_control_layouts.append("cancel")))
    drawer_shape.player_ready = False
    orientation_test.has_player = lambda _: drawer_shape.player_ready
    orientation_test.finish_opening_landscape_controls(display_viewer, opening_drawer)
    assert not opening_controls and orientation_test.opening_landscape_controls is not None
    drawer_shape.width, drawer_shape.height = 640, 360
    orientation_test.finish_opening_landscape_controls(display_viewer, opening_drawer)
    assert not opening_controls and orientation_test.opening_landscape_controls is not None
    drawer_shape.player_ready = True
    for _ in range(2):
        orientation_test.finish_opening_landscape_controls(display_viewer, opening_drawer)
    assert opening_controls == [("setVideoPlayerControlVisible", True, False), ("toggleActionBar", True, False)]
    assert (row_state.visibility, row_state.alpha) == (0, 1.0) and opening_control_layouts == ["cancel", "layout"]
    orientation_test.release_video_orientation(display_viewer)
    display.animation = 4
    orientation_test.check_auto_fullscreen(display_viewer)
    assert len(opening_frames) == 1
    orientation_test.release_video_orientation(display_viewer)
    opening_frames.pop(0)()
    assert display.orientation == -1
finally:
    display.animation = 0
    orientation_test.call = lambda *args: None
    rotation_namespace["run_on_ui_thread"] = rotation_runner
orientation_test.check_auto_fullscreen(display_viewer)
assert display.orientation == 6 and orientation_test.automatic_fullscreen
display.w, display.h, display.video_id = 1000, 1000, 2
orientation_test.check_auto_fullscreen(display_viewer)
assert display.orientation == 6  # A square video keeps the current orientation.
display.h, display.video_id = 1001, 3
orientation_test.check_auto_fullscreen(display_viewer)
assert display.orientation == 7 and orientation_test.fullscreen_session is None
orientation_test.release_video_orientation(display_viewer)
assert display.orientation == -1
display.w, display.h, display.video_id = 1001, 1000, 4
orientation_test.check_auto_fullscreen(display_viewer)
chat_clicked = []
orientation_test.can_show_in_chat = lambda _: True
orientation_test.header_menu = value_field(Obj(onItemClick=chat_clicked.append))
orientation_test.toggle_fullscreen(display_viewer)
assert chat_clicked == [5] and display.orientation == 6
display.w, display.h = 1000, 1001
assert orientation_test.fullscreen_target(display_viewer) == video.SENSOR_PORTRAIT
orientation_test.toggle_fullscreen(display_viewer)
assert chat_clicked == [5] and display.orientation == 7
orientation_test.check_auto_fullscreen(display_viewer, Obj(width=1020, height=1000,
                                      unappliedRotationDegrees=0, pixelWidthHeightRatio=1))
assert display.orientation == 7 and orientation_test.fullscreen_session is None
orientation_test.release_video_orientation(display_viewer)
assert display.orientation == -1
assert orientation_test.fullscreen_target(display_viewer) is None
display.w, display.h = 1001, 1000
assert orientation_test.fullscreen_target(display_viewer) == video.SENSOR_LANDSCAPE
display.video_id = 5
display_viewer.isOpenedFullScreenVideo = lambda: True
orientation_test.check_auto_fullscreen(display_viewer)
assert display.orientation == 6
orientation_test.release_video_orientation(display_viewer)
orientation_test.flags.clear()  # Default applies automation only on entry.
assert not orientation_test.option("auto_fullscreen_on_switch")
display.video_id, display.w, display.h = 10, 1000, 1001
orientation_test.check_auto_fullscreen(display_viewer)
assert display.orientation == 7
display.video_id, display.w, display.h = 11, 1001, 1000
orientation_test.check_auto_fullscreen(display_viewer)
orientation_test.check_auto_fullscreen(display_viewer, Obj(width=1920, height=1080,
                                      unappliedRotationDegrees=0, pixelWidthHeightRatio=1))
assert display.orientation == 7
orientation_test.release_video_orientation(display_viewer)
orientation_test.check_auto_fullscreen(display_viewer)
assert display.orientation == 6
display.video_id, display.w, display.h = 12, 1000, 1001
orientation_test.check_auto_fullscreen(display_viewer)
assert display.orientation == 6
orientation_events = []
listener = orientation_test.orientation_listener.get(display_viewer)


def rotate_phone(degrees):
    orientation_test.follow_device_orientation(Obj(thisObject=listener, args=[degrees],
                                                   setResult=orientation_events.append))


rotate_phone(90)
assert display.orientation == video.SENSOR_LANDSCAPE
rotate_phone(45)
assert display.orientation == video.SENSOR_LANDSCAPE
rotate_phone(2)
assert display.orientation == 7 and orientation_test.axis_lock[2] == -1
rotate_phone(270)
assert display.orientation == 7
display.is_video, display.video_id = False, 13
orientation_test.check_auto_fullscreen(display_viewer)
assert display.orientation == 7
display.is_video, display.video_id, display.w, display.h = True, 11, 1440, 1080
orientation_test.check_auto_fullscreen(display_viewer)
assert display.orientation == video.LANDSCAPE and orientation_events
rotate_phone(90)
assert display.orientation == video.REVERSE_LANDSCAPE and orientation_test.axis_lock[2] == -1
rotate_phone(180)
assert display.orientation == video.REVERSE_LANDSCAPE
rotate_phone(270)
assert display.orientation == video.LANDSCAPE and orientation_test.axis_lock[2] == -1
orientation_test.release_video_orientation(display_viewer)
assert display.orientation == -1
display.is_video, display.video_id = False, 14
orientation_test.check_auto_fullscreen(display_viewer)
display.is_video, display.video_id, display.w, display.h = True, 15, 1001, 1000
orientation_test.check_auto_fullscreen(display_viewer)
assert display.orientation == -1  # Opening a photo and then swiping to a video keeps the orientation.
orientation_test.release_video_orientation(display_viewer)
native_orientation = Obj(previous=-10, actions=[])
orientation_test.previous_native_orientation = Obj(setInt=lambda _, value: setattr(native_orientation, "previous", value))


def press_fullscreen(name, orientation):
    native_orientation.actions.append(name)
    display_activity.setRequestedOrientation(orientation)
    return True


orientation_test.fullscreen = value_field([Obj(performClick=lambda: press_fullscreen("enter", 0))])
orientation_test.exit_fullscreen = value_field(Obj(performClick=lambda: press_fullscreen("exit", 1)))
orientation_test.check_auto_fullscreen(display_viewer)
assert display.orientation == 6
orientation_test.swipe_fullscreen(display_viewer, True)
assert display.orientation == 1 and native_orientation.previous == -1 and native_orientation.actions == ["exit"]
assert orientation_test.fullscreen_session is None
orientation_test.swipe_fullscreen(display_viewer, False)
assert display.orientation == 6 and native_orientation.actions == ["exit", "enter"]

# CameraX maps a physical 90-degree turn to Surface.ROTATION_270 and vice versa.
for angle, up_vector, expected in (
        (0, (0, 9.8), 0), (90, (-9.8, 0), 3), (180, (0, -9.8), 2), (270, (9.8, 0), 1)):
    assert video.surface_rotation_from_angle(angle) == expected
    assert video.surface_rotation_from_gravity(*up_vector, 0) == expected
assert video.surface_rotation_from_angle(-1) is None
assert video.surface_rotation_from_angle(45) is None
assert video.surface_rotation_from_gravity(0.4, 0.2, 9.8) is None
assert video.surface_rotation_from_gravity(7, 7, 0) is None
assert video.device_orientation_request(1, False, True) == video.REVERSE_LANDSCAPE
assert video.device_orientation_request(3, False, True) == video.LANDSCAPE
assert video.device_orientation_request(0, True, False) == video.LANDSCAPE
assert video.device_orientation_request(2, True, False) == video.REVERSE_LANDSCAPE
assert video.device_orientation_request(1, True, False) == video.SENSOR_PORTRAIT
orientation_test.release_video_orientation(display_viewer)
display.orientation = -1
orientation_test.file_loader = Obj(getClosestPhotoSizeWithSize=lambda sizes, size: sizes[0])
orientation_test.android.getPhotoSize = lambda: 1280
orientation_test.sensor_manager = Obj(SENSOR_DELAY_NORMAL=3)
orientation_test.sensor_listener, orientation_test.accelerometer = object(), 1
orientation_test.gravity_sensor = 9
sensor_callbacks = []
sensor_manager = Obj(getDefaultSensor=lambda kind: object(),
                     registerListener=lambda callback, sensor, delay: not sensor_callbacks.append(callback),
                     unregisterListener=sensor_callbacks.remove)
display_activity.getSystemService = lambda name: sensor_manager if name == "sensor" else None
video_namespace = video.surface_rotation_from_gravity.__globals__
original_proxy = video_namespace["dynamic_proxy"]
video_namespace["dynamic_proxy"] = lambda kind: object
try:
    display.video_id, display.w, display.h = 16, 1920, 1080
    orientation_test.check_auto_fullscreen(display_viewer)
    assert display.orientation == 6
    display.is_video, display.is_photo = False, True
    display.video_id, display.w, display.h = 17, 1080, 1920
    orientation_test.check_auto_fullscreen(display_viewer)
    assert display.orientation == 6 and len(sensor_callbacks) == 1
    sensor_callbacks[0].onSensorChanged(Obj(values=[9.8, 0, 0]))
    sensor_callbacks[0].onSensorChanged(Obj(values=[0, 9.8, 0]))
    assert display.orientation == 7
    assert not orientation_test.video_surface(display_viewer)
    sensor_callbacks[0].onSensorChanged(Obj(values=[-9.8, 0, 0]))
    assert display.orientation == 7
    display.is_video, display.is_photo = True, False
    display.video_id, display.w, display.h = 18, 1920, 1080
    orientation_test.check_auto_fullscreen(display_viewer)
    assert len(sensor_callbacks) == 1 and display.orientation == video.REVERSE_LANDSCAPE
    sensor_callbacks[0].onSensorChanged(Obj(values=[9.8, 0, 0]))
    assert display.orientation == video.LANDSCAPE
    sensor_callbacks[0].onSensorChanged(Obj(values=[0.1, 0.1, 9.8]))
    assert display.orientation == video.LANDSCAPE
    orientation_test.release_video_orientation(display_viewer)
    assert display.orientation == -1
    display.is_video, display.is_photo = False, True
    display.video_id, display.w, display.h = 19, 1920, 1080
    orientation_test.check_auto_fullscreen(display_viewer)
    assert display.orientation == -1 and sensor_callbacks
    sensor_callbacks[0].onSensorChanged(Obj(values=[0, 9.8, 0]))
    assert display.orientation == -1
    sensor_callbacks[0].onSensorChanged(Obj(values=[-9.8, 0, 0]))
    assert display.orientation == video.REVERSE_LANDSCAPE
    orientation_test.release_video_orientation(display_viewer)
    assert display.orientation == -1 and not sensor_callbacks
finally:
    video_namespace["dynamic_proxy"] = original_proxy
time_params = Obj(gravity=53, leftMargin=0, topMargin=15, rightMargin=12, bottomMargin=0, width=-2)
time_alignment = []
time_size = []
time_view = Obj(getLayoutParams=lambda: time_params, setGravity=time_alignment.append,
                setTextSize=time_size.append, requestLayout=lambda: None,
                getPaddingTop=lambda: 0, getPaddingBottom=lambda: 0,
                getText=lambda: "00:28 / 15:00", getPaint=lambda: Obj(measureText=lambda _: 76.2,
                    getFontMetrics=lambda: Obj(ascent=-13, descent=3)))
plugin.video_time = value_field(time_view)
plugin.time_layouts = []
plugin.dp = int
plugin.move_time_under_scrubber(viewer, 68, 220)
assert (time_params.gravity, time_params.leftMargin, time_params.bottomMargin) == (83, 68, 10)
assert time_alignment == [51]
plugin.restore_time(time_view)
assert time_alignment == [51, 53] and time_params.rightMargin == 12
compact_params = [Obj(leftMargin=0, rightMargin=0) for _ in range(3)]
compact = Obj(getChildAt=lambda index: Obj(getLayoutParams=lambda: compact_params[index]),
              getChildCount=lambda: len(compact_params))
size, left, right = plugin.layout_compact_controls(viewer, compact, 640, 24, 28)
assert time_size[-1] == 12 and (time_params.leftMargin, time_params.width) == (62, 80)
assert time_params.bottomMargin == 20
assert size == 44
assert [item.rightMargin for item in compact_params] == [right + 3 * size, right + 2 * size, right + size]
small_size, small_left, small_right = plugin.layout_compact_controls(viewer, compact, 240, 24, 28)
assert small_size < size and time_params.width == 60
for button_size, play_left, fullscreen_right in ((size, left, right), (small_size, small_left, small_right)):
    assert (play_left + button_size // 2, fullscreen_right + button_size // 2) == (38, 42)
assert time_params.leftMargin + time_params.width < 240 - compact_params[0].rightMargin - small_size
plugin.restore_time(time_view)
assert time_size[-1] == 14 and time_params.width == -2

portrait = video.VideoSeekbarGestureInsets()
portrait.dp = int
portrait.weak_reference = plugin.weak_reference
portrait.measure_spec = Obj(getSize=int)
portrait.control_outer = value_field(viewer)
portrait.option = portrait.video_surface = lambda _: True
portrait.control_width = Obj(getInt=lambda _: 100, setInt=lambda *_: None)
portrait.control_height = Obj(getInt=lambda _: 72)
portrait.video_time, portrait.time_layouts = value_field(time_view), []
play_slot = Obj(width=44, height=44)
fullscreen_slot = Obj(width=44, height=44)
seek_slot = Obj()
play_view = Obj(getLayoutParams=lambda: play_slot, setVisibility=lambda _: None)
fullscreen_view = Obj(getLayoutParams=lambda: fullscreen_slot, setVisibility=lambda _: None)
for icon_view in (play_view, fullscreen_view):
    icon_view.getPaddingTop = icon_view.getPaddingLeft = icon_view.getPaddingRight = lambda: 0
    icon_view.setPadding = lambda *_: None
portrait.playback_control = lambda _: play_view
portrait.fullscreen_control = lambda _: fullscreen_view
portrait.compact_control = lambda _: None
portrait.video_seek_view = value_field(Obj(getLayoutParams=lambda: seek_slot))
portrait.scrubber_margins = lambda *_: (24, 32)
for width in (220, 360, 800):
    portrait.reserve_fullscreen_slot(Obj(thisObject=object(), args=[width]))
    assert (seek_slot.leftMargin, seek_slot.rightMargin, seek_slot.height) == (24, 32, 28)
    assert (play_slot.leftMargin, fullscreen_slot.rightMargin) == (20, 28)
    assert play_slot.height == fullscreen_slot.height == 36
    assert time_params.leftMargin == play_slot.leftMargin + play_slot.width + 4
    assert time_params.leftMargin + time_params.width == width - fullscreen_slot.rightMargin - fullscreen_slot.width - 8
portrait.restore_time(time_view)

# The track remains visible when the outer controls enter their thin-bar transition.
first_seek = Obj(alpha=0.0)
first_seek.getAlpha = lambda: first_seek.alpha
first_seek.setAlpha = lambda alpha: setattr(first_seek, "alpha", alpha)
portrait.video_seek_view = value_field(first_seek)
portrait.exit_fullscreen = value_field(None)
portrait.refresh_fullscreen_button = lambda *_: None
fullscreen_view.getVisibility = lambda: 0
landscape_control = Obj(isSeekBarTransitionEnabled=lambda: True, getProgress=lambda: 1.0)
portrait.finish_fullscreen_slot(Obj(thisObject=landscape_control))
assert first_seek.alpha == 1.0

draw_geometry = Obj(width=392, height=76, transition=1.0, dragging=False)
draw_playhead = []
draw_control = Obj(progress=1.0, isSeekBarTransitionEnabled=lambda: True)
draw_control.getProgress = lambda: draw_control.progress
laid_out_seek = Obj(width=704, height=28, getParent=lambda: draw_control)
laid_out_seek.getWidth, laid_out_seek.getHeight = lambda: laid_out_seek.width, lambda: laid_out_seek.height
draw_seekbar = Obj(getProgress=lambda: 0.25, isDragging=lambda: draw_geometry.dragging,
                   setProgress=lambda *args: draw_playhead.append(args),
                   getTransitionProgress=lambda: draw_geometry.transition,
                   setTransitionProgress=lambda value: setattr(draw_geometry, "transition", value))
portrait.video_control_type = Obj(isInstance=lambda control: control is draw_control)
portrait.active_seek_view = lambda seekbar: laid_out_seek if seekbar is draw_seekbar else None
portrait.scrubber_width = Obj(getInt=lambda _: draw_geometry.width,
                              setInt=lambda _, value: setattr(draw_geometry, "width", value))
portrait.scrubber_height = Obj(getInt=lambda _: draw_geometry.height,
                               setInt=lambda _, value: setattr(draw_geometry, "height", value))
draw_request = Obj(thisObject=draw_seekbar, args=[None, laid_out_seek])
portrait.sync_scrubber_draw(draw_request)
assert (draw_geometry.width, draw_geometry.height, draw_geometry.transition) == (700, 28, 0.0)
assert draw_playhead == [(0.25, False)]
laid_out_seek.width = 396
draw_control.progress, draw_geometry.dragging = 0.25, True
portrait.sync_scrubber_draw(draw_request)
assert (draw_geometry.width, draw_geometry.height, draw_geometry.transition) == (392, 28, 0.75)
assert draw_playhead == [(0.25, False)]

assert video.landscape_toolbar_gutters(int, 360, 44, 12, 40, 0) == (18, 18)
assert video.landscape_toolbar_gutters(int, 640, 44, 12, 0, 112) == (50, 28)
assert video.landscape_toolbar_gutters(int, 640, 12, 44, 0, 112) == (28, 28)
assert [video.landscape_gutter(int, width) for width in (220, 360, 640, 1280)] == [12, 18, 28, 28]
assert [video.portrait_toolbar_width(int, width) for width in (180, 240, 360, 800)] == [150, 156, 156, 156]


gesture = video.VideoSeekbarGestureInsets()
gesture.dp = int
gesture.boolean = bool
gesture.video_surface = lambda _: True
gesture.flags = {"hold_speed": False}
gesture.speed_hold = gesture.speed_press = None
gesture.hits_caption = lambda _, window, x, y: 68 <= y < 200
gesture.top_captions = []
gesture.status_slide = None
gesture.positions = list
gesture.action_bar_visible = Obj(getBoolean=lambda _: True)
gesture.action_bar = value_field(Obj(getHeight=lambda: 44, getParent=lambda: object(),
    getLocationInWindow=lambda origin: origin.__setitem__(1, 24)))
gesture.controls = value_field(Obj(getHeight=lambda: 56, getParent=lambda: object(), getVisibility=lambda: 0,
    getLocationInWindow=lambda origin: origin.__setitem__(1, 680)))
gesture.level_hud = None
gesture.hud_generation = 0
gesture.weak_reference = plugin.weak_reference
gesture.wide_video = lambda _: wide
gesture.swipe_fullscreen = lambda _, exiting: events.append(("fullscreen", exiting))
gesture.cancel_child_touch = lambda *_: events.append("cancel")
gesture.show_level_hud = lambda _, zone, level: events.append((zone, level))
gesture.sdk, gesture.music_stream, gesture.audio_manager_type = 35, 3, Obj()
volume_calls = []
swipe_haptics = []
gesture.haptic = Obj(SEGMENT_FREQUENT_TICK=27)
gesture.soft_adjustment_tick = None
gesture.swipe_tick_pending = gesture.last_swipe_haptic_ms = None
gesture_event_time = 1000
gesture.active = True
gesture.adjustment_clock = Obj(uptimeMillis=lambda: gesture_event_time)
gesture.configure_adjustment_ticks("12", "1")
device_audio = Obj(index=9, getStreamMinVolume=lambda stream: 0, getStreamMaxVolume=lambda stream: 15,
                   getStreamVolume=lambda stream: device_audio.index, isVolumeFixed=lambda: False)


def set_device_volume(stream, index, flags):
    assert (stream, flags) == (3, 0)
    device_audio.index = index
    volume_calls.append(index)


device_audio.setStreamVolume = set_device_volume
attributes = Obj(screenBrightness=-1.0)
gesture.window_params = value_field(attributes)
gesture.setting_system = Obj(SCREEN_BRIGHTNESS="brightness", getInt=lambda *_: 128)
gesture.volume_session = gesture.brightness_session = None
activity = Obj(getWindowManager=lambda: Obj(updateViewLayout=lambda *_: None))
media_viewer = Obj(getCurrentIndex=lambda: 0, getParentActivity=lambda: activity,
                   getCurrentMessageObject=lambda: None)
media_window = Obj(getWidth=lambda: 820 if fullscreen else 640, getHeight=lambda: 800, getParent=lambda: object(),
                   getLocationInWindow=lambda _: None,
                   performHapticFeedback=swipe_haptics.append,
                   getContext=lambda: Obj(getContentResolver=lambda: object(),
                                          getSystemService=lambda name: device_audio if name == "audio" else None))
gesture.window_outer = value_field(media_viewer)
events = []
fullscreen = False
wide = True


def deliver(x, y, action, fingers=1):
    event = Obj(getX=lambda: x, getY=lambda: y, getPointerCount=lambda: fingers,
                getActionMasked=lambda: action, getEventTime=lambda: gesture_event_time)
    results = []
    param = Obj(thisObject=media_window, args=[event], setResult=results.append)
    gesture.route_video_touch(param)
    return results == [True]


assert not deliver(320, 320, 0) and deliver(320, 336, 2) and deliver(320, 356, 1)
assert ("fullscreen", False) in events
events.clear()
fullscreen = True
assert not deliver(320, 320, 0) and deliver(320, 240, 2) and deliver(320, 234, 1)
assert ("fullscreen", True) in events
events.clear()
wide, fullscreen = False, False
assert not deliver(320, 320, 0) and deliver(320, 370, 2) and deliver(320, 384, 1)
assert events == ["cancel"]  # Portrait video neither rotates nor falls back to native dismiss.
events.clear()
assert not deliver(320, 146, 0) and not deliver(320, 210, 2) and not deliver(320, 220, 1)
assert gesture.video_swipe_bounds(media_viewer, media_window) == (68, 680)
assert not deliver(50, 44, 0) and not deliver(50, 90, 2)
assert not deliver(560, 730, 0) and not deliver(560, 770, 2)
assert not deliver(50, 320, 0) and not deliver(140, 321, 2) and not deliver(180, 379, 2)
assert not events and attributes.screenBrightness == -1.0
assert not deliver(50, 160, 0) and deliver(50, 148, 2) and deliver(50, 113, 1)
assert attributes.screenBrightness > 128 / 255
assert ("brightness", attributes.screenBrightness) in events
assert not deliver(50, 160, 0) and deliver(50, 470, 2) and deliver(50, 480, 1)
assert attributes.screenBrightness == 0 and ("brightness", 0) in events
assert not deliver(560, 156, 0) and not deliver(560, 156, 1)
assert not volume_calls and device_audio.index == 9
assert not deliver(560, 156, 0) and deliver(560, 500, 2)
assert deliver(560, 500, 1) and not volume_calls and device_audio.index == 9
assert not deliver(560, 156, 0) and deliver(560, 168, 2)
assert device_audio.index == 9 and not volume_calls
assert deliver(560, 200, 2) and deliver(560, 239, 1)
assert device_audio.index == 4 and ("volume", 4 / 15) in events and volume_calls == [7, 4]
assert swipe_haptics == [27]
gesture_event_time += gesture.adjustment_tick_interval_ms
assert not deliver(50, 230, 0) and deliver(50, 180, 2) and deliver(50, 177, 1)
assert swipe_haptics == [27, 27]
kept = attributes.screenBrightness
gesture.before_player_release(Obj(thisObject=media_viewer))
gesture.before_image_index(Obj(thisObject=media_viewer, args=[1]))
assert device_audio.index == 4 and attributes.screenBrightness == kept
gesture.leave_adjustments(media_viewer)
assert device_audio.index == 9 and attributes.screenBrightness == -1.0 and gesture.volume_session is None

stored_ticks, pending_ticks = [], []
tick_namespace = video.VideoSeekbarGestureInsets.emit_adjustment_tick.__globals__
tick_runner = tick_namespace["run_on_ui_thread"]
tick_clock = Obj(now=1000)
rate_test = video.VideoSeekbarGestureInsets()
rate_test.active, rate_test.swipe = True, object()
rate_test.swipe_tick_pending = rate_test.last_swipe_haptic_ms = None
rate_test.adjustment_clock = Obj(uptimeMillis=lambda: tick_clock.now)
rate_test.play_adjustment_tick = lambda _: stored_ticks.append(tick_clock.now)
rate_test.configure_adjustment_ticks("12", "1")
assert rate_test.adjustment_step(0.09) == 9 and rate_test.adjustment_step(0.10) == 10
tick_namespace["run_on_ui_thread"] = lambda callback, delay=0: pending_ticks.append((tick_clock.now + delay, callback))
try:
    rate_test.request_adjustment_tick(None)
    for tick_clock.now in (1035, 1040, 1083):
        rate_test.request_adjustment_tick(None)
    assert stored_ticks == [1000] and [due for due, _ in pending_ticks] == [1084]
    tick_clock.now, callback = pending_ticks.pop()
    callback()
    tick_clock.now = 1090
    rate_test.request_adjustment_tick(None)
    assert [due for due, _ in pending_ticks] == [1168]
    rate_test.swipe = None
    tick_clock.now, callback = pending_ticks.pop()
    callback()
    assert stored_ticks == [1000, 1084] and rate_test.swipe_tick_pending is None
    rate_test.configure_adjustment_ticks("0", "5")
    rate_test.swipe = object()
    rate_test.request_adjustment_tick(None)
    assert not pending_ticks and rate_test.adjustment_step(0.10) == 2

    def replay_ticks(input_times):
        rate_test.configure_adjustment_ticks("12", "1")
        rate_test.last_swipe_haptic_ms = None
        stored_ticks.clear()
        pending_ticks.clear()
        for sample_time in input_times:
            while pending_ticks and pending_ticks[0][0] <= sample_time:
                tick_clock.now, pending = pending_ticks.pop(0)
                pending()
            tick_clock.now = sample_time
            rate_test.request_adjustment_tick(None)
        return stored_ticks.copy()

    assert replay_ticks(range(0, 990, 90)) == list(range(0, 990, 90))
    assert replay_ticks(range(0, 1000, 47)) == list(range(0, 988, 84))
    rate_test.soft_adjustment_tick = 42
    rate_test.create_soft_adjustment_tick = lambda: rate_test.adjustment_tick_strength
    rate_test.configure_adjustment_ticks("12", "1", "65")
    assert rate_test.soft_adjustment_tick == 65
    rate_test.configure_adjustment_ticks("12", "1", "0")
    pending_ticks.clear()
    rate_test.request_adjustment_tick(None)
    assert not pending_ticks and rate_test.swipe_tick_pending is None
finally:
    tick_namespace["run_on_ui_thread"] = tick_runner

adjustment_vibrator = Obj(areAllPrimitivesSupported=lambda ids: ids == [8], hasAmplitudeControl=lambda: True)
adjustment_context = Obj(checkSelfPermission=lambda _: 0, getSystemService=lambda _: adjustment_vibrator)
native_haptics = {
    "org.telegram.messenger.ApplicationLoader": Obj(applicationContext=adjustment_context),
    "android.os.Vibrator": object(),
    "android.os.VibrationEffect$Composition": Obj(PRIMITIVE_LOW_TICK=8),
    "android.os.VibrationEffect": Obj(
        createOneShot=lambda duration, amplitude: ("pulse", duration, amplitude),
        startComposition=lambda: Obj(
            addPrimitive=lambda primitive, strength: Obj(compose=lambda: ("primitive", primitive, strength)))),
    "android.os.VibrationAttributes": Obj(USAGE_TOUCH=18, createForUsage=lambda usage: ("touch", usage)),
    "android.media.AudioAttributes": Obj(USAGE_ASSISTANCE_SONIFICATION=13),
    "android.media.AudioAttributes$Builder": lambda: Obj(
        setUsage=lambda usage: Obj(build=lambda: ("sonification", usage))),
}
tick_class = tick_namespace["jclass"]
tick_namespace["jclass"] = native_haptics.__getitem__
try:
    adjustable_tick = video.VideoSeekbarGestureInsets()
    adjustable_tick.adjustment_tick_strength, adjustable_tick.positions = 60, list
    for sdk, expected in (
            (25, None),
            (28, (adjustment_vibrator, ("pulse", 12, 92), ("sonification", 13))),
            (32, (adjustment_vibrator, ("primitive", 8, 0.6), ("sonification", 13))),
            (33, (adjustment_vibrator, ("primitive", 8, 0.6), ("touch", 18)))):
        adjustable_tick.sdk = sdk
        assert adjustable_tick.create_soft_adjustment_tick() == expected
    adjustable_tick.adjustment_tick_strength = 0
    assert adjustable_tick.create_soft_adjustment_tick() is None
finally:
    tick_namespace["jclass"] = tick_class

attrs = Obj(w=720, h=1440)
doc = Obj(getDocument=lambda: Obj(attributes=native_list([attrs])))
gesture.video_attribute = Obj(isInstance=lambda attribute: attribute == attrs)
assert gesture.video_dimensions(doc, None) == (720, 1440, False)
size = Obj(width=720, height=720, pixelWidthHeightRatio=2, unappliedRotationDegrees=90)
assert gesture.video_dimensions(doc, size) == (720, 1440, True)
gesture.video_size_set = Obj(getBoolean=lambda _: True)
gesture.video_width, gesture.video_height = Obj(getInt=lambda _: 1024), Obj(getInt=lambda _: 768)
assert gesture.viewer_video_dimensions(media_viewer) == (1024, 768)
gesture.video_size_set = Obj(getBoolean=lambda _: False)
assert not video.VideoSeekbarGestureInsets.wide_video(gesture, Obj(getCurrentMessageObject=lambda: doc))

hud_nodes, overlay_children = [], []


def hud_view(_):
    node = Obj()
    node.animate = lambda: Obj(cancel=lambda: None)
    node.layout = lambda *args: setattr(node, "bounds", args)
    node.measure = lambda *args: None
    node.addView = lambda *args: None
    for property_name in ("ImportantForAccessibility", "Background", "Gravity", "TextColor", "TextSize",
                          "Text", "PivotX", "Alpha", "Visibility", "ScaleX", "ImageResource", "ColorFilter", "ScaleType"):
        setattr(node, "set" + property_name, lambda value, name=property_name: setattr(node, name, value))
    hud_nodes.append(node)
    return node


hud = video.VideoSeekbarGestureInsets()
hud.level_hud, hud.hud_generation = None, 0
hud.dp, hud.positions, hud.weak_reference = int, list, plugin.weak_reference
hud.frame_layout = hud.text_view = hud.view_type = hud.image_view = hud_view
hud.drawable = Obj(msg_brightness_high=11, baseline_volume_up_24=12, msg_speed=13)
hud.fit_center = 0
hud.frame_params = lambda *_: Obj()
hud.round_background = lambda *args: args
hud.scrubber_margins = lambda *_: (0, 0)
hud.measure_spec = Obj(EXACTLY=1, makeMeasureSpec=lambda size, mode: size)
overlay = Obj(add=overlay_children.append, remove=overlay_children.remove)
hud_container = Obj(getHeight=lambda: 640, getWidth=lambda: 360, getContext=lambda: None,
                    getOverlay=lambda: overlay,
                    getRootWindowInsets=lambda: Obj(getStableInsetTop=lambda: 24))
hud.viewer_container = value_field(hud_container)
hud.show_level_hud(media_viewer, "brightness", 0.43)
card = overlay_children[0]
assert card.bounds == (93, 36, 267, 72) and hud_nodes[1].ImageResource == 11
assert hud_nodes[3].ScaleX == 0.43 and hud_nodes[4].Text == "43%"
hud.show_level_hud(media_viewer, "brightness", 0.24)
assert overlay_children == [card] and hud_nodes[4].Text == "24%" and card.bounds == (93, 36, 267, 72)
hud.show_level_hud(media_viewer, "volume", 0.67)
assert len(overlay_children) == 1 and overlay_children[0].bounds == card.bounds
assert hud_nodes[-4].ImageResource == 12 and hud_nodes[-2].ScaleX == 0.67 and hud_nodes[-1].Text == "67%"
hud.show_level_hud(media_viewer, "speed", 2.5)
assert overlay_children[0].bounds == (131, 36, 229, 72)
assert hud_nodes[-2].ImageResource == 13 and hud_nodes[-1].Text == "2.5×"
hud.remove_level_hud()
assert not overlay_children

video_layout = video.VideoSeekbarGestureInsets()
video_layout.option = video_layout.video_surface = lambda _: True
native_container = Obj(getMeasuredWidth=lambda: 840, getMeasuredHeight=lambda: 350)
aspect = Obj(getParent=lambda: native_container)
video_layout.drawer_type = Obj(isInstance=lambda value: value is native_container)
video_layout.outer, video_layout.aspect_frame = value_field(viewer), value_field(aspect)
video_layout.viewer_container = value_field(native_container)
video_layout.integer = int
video_layout.measure_spec = Obj(EXACTLY=1, makeMeasureSpec=lambda size, _: size)
aspect_measure = Obj(thisObject=aspect, args=[840, 390])
video_layout.measure_landscape_video(aspect_measure)
assert aspect_measure.args == [840, 350]
draw_heights = []
draw_measure = Obj(thisObject=viewer, args=[False, 0], setResult=draw_heights.append)
video_layout.landscape_media_height(draw_measure)
assert draw_heights == [350]
video_layout.video_surface = lambda _: False
video_layout.photo_surface = lambda _: True
video_layout.landscape_media_height(draw_measure)
assert draw_heights == [350, 350]
draw_measure.args[1] = 1
video_layout.landscape_media_height(draw_measure)
assert draw_heights == [350, 350]
video_layout.video_surface = lambda _: True
native_container.getMeasuredHeight = lambda: 980
aspect_measure.args[1] = 990
video_layout.measure_landscape_video(aspect_measure)
assert aspect_measure.args == [840, 990]
draw_measure.args[1] = 0
video_layout.landscape_media_height(draw_measure)
assert draw_heights == [350, 350]

hold = video.VideoSeekbarGestureInsets()
hold.speed_hold = hold.speed_press = None
hold.level_hud = None
hold.top_captions = []
hold.dp, hold.boolean, hold.integer = int, bool, int
hold.weak_reference = plugin.weak_reference
hold.video_surface = lambda _: True
hold.hits_caption = lambda *_: False
hold.swipe_tick_pending = None
hold.video_swipe_bounds = lambda *_: (60, 620)
hold.view_origin = lambda *_: (0, 0)
hold.viewer_container = value_field(object())
hold.aspect_frame = value_field(Obj(getVisibility=lambda: 0, getMeasuredWidth=lambda: 640,
                                      getMeasuredHeight=lambda: 360))
hold.call = lambda _, name: 640 if name == "getContainerViewWidth" else 680
hold.rectf = lambda left, top, right, bottom: Obj(left=left, top=top, right=right, bottom=bottom)


def place_video_frame(bounds):
    for edge in ("left", "right", "top", "bottom"):
        setattr(bounds, edge, getattr(bounds, edge) + (320 if edge in ("left", "right") else 340))
    bounds.contains = lambda x, y: bounds.left <= x < bounds.right and bounds.top <= y < bounds.bottom


hold.image_transform = value_field(Obj(mapRect=place_video_frame))
hold.playback_parameters = lambda speed, pitch: Obj(speed=speed, pitch=pitch)
original_playback = hold.playback_parameters(1.25, 0.98)
engine = Obj(parameters=original_playback)
engine.getPlaybackParameters = lambda: engine.parameters
engine.setPlaybackParameters = lambda parameters: setattr(engine, "parameters", parameters)
hold_viewer = Obj(getVideoPlayer=lambda: Obj(player=engine))
hold_events = []
hold.show_level_hud = lambda _, zone, rate: hold_events.append((zone, rate))
hold.cancel_child_touch = lambda *args: hold_events.append("cancel")
gesture_haptics = []
hold.haptic = Obj(LONG_PRESS=0, CLOCK_TICK=4)
hold.viewer_container = value_field(Obj(performHapticFeedback=gesture_haptics.append))
long_press = Obj(thisObject=hold_viewer, setResult=hold_events.append)


def hold_event(x, y, action):
    event = Obj(getX=lambda: x, getY=lambda: y, getPointerCount=lambda: 1)
    return hold.route_speed_touch(Obj(setResult=hold_events.append), Obj(getWidth=lambda: 640), hold_viewer, event,
                                  action)


assert not hold_event(3, 100, 0)
hold.start_held_speed(long_press)
assert engine.parameters.speed == 2.5  # Letterboxed area at the edge.
assert hold_event(3, 100, 1) and engine.parameters is original_playback
assert not hold_event(320, 42, 0)
hold.start_held_speed(long_press)
assert engine.parameters is original_playback and hold_events[-1] is None  # Header cannot start the native rewinder.
for x in (110, 320, 540):
    assert not hold_event(x, 340, 0)
    hold.start_held_speed(long_press)
    assert (engine.parameters.speed, engine.parameters.pitch) == (2.5, 0.98)
    assert hold_events[-1] == ("speed", 2.5)
    assert hold_event(x, 340, 1) and engine.parameters is original_playback
hold.hold_speed = 1.75
assert not hold_event(320, 340, 0)
hold.start_held_speed(long_press)
assert engine.parameters.speed == 1.75
assert hold_event(320, 340, 3) and engine.parameters is original_playback
assert gesture_haptics == [0, 0, 0, 0, 0]

hold.on_button = lambda ref, action: hold_events.append(action)
hold.has_player = lambda _: True
hold.native_tap_stack = []
seek_events = []
tap_x = 320
tap_param = Obj(thisObject=hold_viewer, args=[Obj(getX=lambda: tap_x)], setResult=hold_events.append)
native_drawable = Obj()
hold.seek_animation = value_field(native_drawable)
hold.viewer_container = value_field(Obj(invalidate=lambda: None, performHapticFeedback=gesture_haptics.append))
native_controls = Obj(visible=False, can_seek=True)
hold.seek_controls_visible = Obj(getBoolean=lambda _: native_controls.visible,
                                 setBoolean=lambda _, visible: setattr(native_controls, "visible", visible))


def seek_call(_, method, *args):
    seek_events.append(method)
    return {"getContainerViewWidth": 640, "canDoubleTapSeekVideo": native_controls.can_seek,
            "getCurrentVideoPosition": getattr(native_controls, "position", -1),
            "getVideoDuration": 10000, "seekVideoOrWebTo": None}[method]


hold.call = seek_call
hold_events.clear()
hold.defer_video_single_tap(tap_param)
assert hold_events == [False] and not seek_events
hold.before_native_double_tap(tap_param)
hold.after_native_double_tap(tap_param)
assert hold_events == [False, "play", True]
tap_x = 530
hold.before_native_double_tap(tap_param)
assert native_controls.visible and hold_events == [False, "play", True]
hold.after_native_seek_time(Obj(thisObject=native_drawable, args=[22000]))
assert hold.seek_visual[0].get() == native_drawable
hold.after_native_double_tap(tap_param)
assert not native_controls.visible
native_controls.can_seek = False
tap_x = 110
hold.before_native_double_tap(tap_param)
hold.after_native_double_tap(tap_param)
assert hold_events[-1] is True and not native_controls.visible
assert "seekVideoOrWebTo" not in seek_events and gesture_haptics == [0, 0, 0, 0, 0, 4, 4]
native_seek_progress, native_seek_feedback = [], []
tap_param.getResult = lambda: False
hold.long = int
hold.video_seek = value_field(Obj(setProgress=lambda progress, _: native_seek_progress.append(progress)))
hold.video_seek_view = value_field(Obj(invalidate=lambda: None))
native_drawable.setOneShootAnimation = lambda _: None
native_drawable.setLeftSide = native_seek_feedback.append
native_drawable.addTime = native_seek_feedback.append
for position, x, edge, remaining in ((2400, 40, 0.0, 2400), (8700, 615, 1.0, 1300)):
    tap_x = x
    native_controls.position = position
    hold.allow_boundary_double_tap(tap_param)
    assert hold_events[-1] is True
    hold.before_native_double_tap(tap_param)
    hold.after_native_double_tap(tap_param)
    assert native_seek_progress[-1] == edge
    assert native_seek_feedback[-2:] == [edge == 0, remaining]
    assert seek_events[-1] == "seekVideoOrWebTo" and not native_controls.visible
native_controls.position = 10000
hold.before_native_double_tap(tap_param)
hold.after_native_double_tap(tap_param)
assert native_seek_progress == [0.0, 1.0]

assert video.seek_edge_geometry(640, 300, int, True) == ((-288, -45, 96, 345), 48, 150, 96)
assert video.seek_edge_geometry(640, 300, int, False) == ((544, -45, 928, 345), 592, 150, 96)
for width, height in ((320, 720), (430, 920), (640, 300), (1080, 500)):
    (left, top, right, bottom), label_x, center_y, depth = video.seek_edge_geometry(width, height, int, True)
    radius_x, radius_y = (right - left) / 2, (bottom - top) / 2
    corner_width = (left + right) / 2 + radius_x * (1 - (center_y / radius_y) ** 2) ** 0.5
    assert top < 0 and bottom > height and corner_width > 0
    assert 0 < label_x < depth <= width * 0.20

seek_draw_ops = []
visual = video.VideoSeekbarGestureInsets()
visual.dp = int
visual.seek_visual_stack = []
seek_drawable = Obj()
seek_viewport = Obj(getWidth=lambda: 640, getHeight=lambda: 300)
visual.seek_visual = (Obj(get=lambda: seek_drawable), Obj(get=lambda: seek_viewport))
visual.seek_visual_left = Obj(getBoolean=lambda _: True)
visual.seek_visual_one_shot = Obj(getBoolean=lambda _: True)
visual.seek_visual_time = Obj(getLong=lambda _: 15000)
visual.seek_visual_progress = Obj(getFloat=lambda _: 0.4)
visual.seek_visual_rect = Obj(set=lambda *args: seek_draw_ops.append(("rect", args)))
visual.seek_visual_bg = Obj(setAlpha=lambda alpha: seek_draw_ops.append(("alpha", alpha)))
visual.seek_visual_text = Obj(setTextSize=lambda _: None, measureText=lambda _: 20,
                             setAlpha=lambda _: None, ascent=lambda: -10, descent=lambda: 4)
seek_canvas = Obj(drawOval=lambda *_: seek_draw_ops.append("oval"),
                  drawText=lambda text, x, y, _: seek_draw_ops.append((text, x, y)), save=lambda: 3,
                  clipRect=lambda *args: seek_draw_ops.append(("clip", args)),
                  restoreToCount=lambda depth: seek_draw_ops.append(("restore", depth)))
seek_draw = Obj(thisObject=seek_drawable, args=[seek_canvas])
visual.before_seek_visual_draw(seek_draw)
visual.after_seek_visual_draw(seek_draw)
assert seek_draw_ops == [("clip", (0, 0, 640, 300)), ("rect", (-288, -45, 96, 345)),
                         ("alpha", 60), "oval", ("15S", 48, 153),
                         ("clip", (0, 0, 0, 0)), ("restore", 3)]

zoom = video.VideoSeekbarGestureInsets()
zoom.dp = int
zoom_container = Obj(getHeight=lambda: 720, getWidth=lambda: 800)
zoom_controls = Obj(getY=lambda: 580)
zoom.controls = value_field(zoom_controls)
zoom.video_seek_view = value_field(Obj(getParent=lambda: zoom_controls, getHeight=lambda: 28, getY=lambda: 0))
zoom_button = Obj(left=365, offset_x=0, getWidth=lambda: 70,
                  getParent=lambda: zoom_container, getTranslationY=lambda: 0)
zoom_button.getLeft = lambda: zoom_button.left
zoom_button.getTranslationX = lambda: zoom_button.offset_x
zoom_button.setTranslationX = lambda value: setattr(zoom_button, "offset_x", value)
zoom_button.setTranslationY = lambda value: setattr(zoom_button, "top", value)
zoom.position_zoom_reset(viewer, zoom_button)
assert zoom_button.offset_x == 0
for left_inset, right_inset in ((54, 0), (0, 54), (64, 16), (28, 28)):
    zoom_button.left = left_inset + (800 - left_inset - right_inset - zoom_button.getWidth()) // 2
    zoom.position_zoom_reset(viewer, zoom_button)
    assert zoom_button.left + zoom_button.offset_x + zoom_button.getWidth() / 2 == 400
zoom_visibility = []
zoom_button.setVisibility = zoom_visibility.append
zoom.zoom_buttons = [(Obj(get=lambda: viewer), Obj(get=lambda: zoom_button))]
zoom.background = value_field(Obj(getParent=lambda: zoom_container))
zoom.option = zoom.video_surface = lambda _: True
zoom_scale = Obj(value=2, target=1, started=0)
zoom.scale = Obj(getFloat=lambda _: zoom_scale.value)
zoom.scale_animation_time = Obj(getLong=lambda _: zoom_scale.started)
zoom.scale_animation_target = Obj(getFloat=lambda _: zoom_scale.target)
zoom.refresh_zoom(viewer)
zoom_scale.started = 1
zoom.refresh_zoom(viewer)
zoom_scale.value, zoom_scale.started = 1, 0
zoom.refresh_zoom(viewer)
zoom_scale.value = 1.5
zoom.refresh_zoom(viewer)
assert zoom_visibility == [0, 8, 8, 0]
assert zoom_button.top + 38 < 580 and 500 < zoom_button.top < 555

class PopupChild:
    def __init__(self, _context=None):
        self.parent, self.params, self.visibility = None, Obj(height=8), 0

    def getParent(self):
        return self.parent

    def getLayoutParams(self):
        return self.params

    def getVisibility(self):
        return self.visibility

    def setVisibility(self, visibility):
        self.visibility = visibility

    def setBackgroundColor(self, color):
        self.color = color

    def setImportantForAccessibility(self, _):
        pass


class PopupRows:
    def __init__(self, *rows):
        self.rows = []
        for row in rows:
            self.addView(row, len(self.rows), row.params)

    def addView(self, row, index, params):
        self.rows.insert(index, row)
        row.parent, row.params = self, params

    def removeView(self, row):
        self.rows.remove(row)
        row.parent = None

    def getContext(self):
        return None

    def getChildCount(self):
        return len(self.rows)

    def getChildAt(self, index):
        return self.rows[index]

    def indexOfChild(self, row):
        return self.rows.index(row)


popup = video.VideoSeekbarGestureInsets()
popup.weak_reference, popup.dp = plugin.weak_reference, int
popup.view_type = PopupChild
popup.linear_params = lambda width, height: Obj(width=width, height=height)
popup.popup_rows = []
slider, speed_gap, presets, quality = [PopupChild() for _ in range(4)]
save, gallery_gap, share = [PopupChild() for _ in range(3)]
gear_popup = PopupRows(slider, speed_gap, presets, quality)
more_popup = PopupRows(save, gallery_gap, share)
popup.gallery_gap, popup.speed_gap, popup.speed_presets = map(value_field, (gallery_gap, speed_gap, presets))
popup.video_quality = value_field(quality)
popup.speed_slider = value_field(slider)
popup.style_popup_rows(viewer, True, False)
assert gear_popup.rows[0] is slider and gear_popup.rows[2] is quality and presets.parent is None
assert gear_popup.rows[1] is speed_gap and more_popup.rows[1].params.height == 8
assert more_popup.rows[1].color == video.MENU_DIVIDER_COLOR
assert more_popup.rows[0] is save and more_popup.rows[2] is share
gallery_gap.setVisibility(8)
quality.setVisibility(8)
popup.style_popup_rows(viewer, True, False)
assert gear_popup.rows[1] is speed_gap and more_popup.rows[1].visibility == 8
popup.style_popup_rows(viewer, False, True)
assert gear_popup.rows == [slider, speed_gap, presets, quality]
popup.style_popup_rows(viewer, False, False)
assert more_popup.rows == [save, gallery_gap, share] and not popup.popup_rows

quality_choices = (Obj(original=True, p=lambda: 1080), Obj(original=False, p=lambda: 720),
                   Obj(original=False, p=lambda: 480))
quality_player = Obj(getQualitiesCount=lambda: 3, getQuality=quality_choices.__getitem__,
                     getSelectedQuality=lambda: 1)
gear_viewer = Obj(getVideoPlayer=lambda: quality_player)
gear_rails, gear_commits = [], []
popup.integer = int
slider.getContext = quality.getContext = lambda: None
popup.viewer_video_dimensions = lambda _: (1920, 1080)


def gear_slider(_, *args):
    gear_rails.append(args)
    rail = PopupChild()
    rail.setTag = lambda tag: setattr(rail, "tag", tag)
    rail.getTag = lambda: rail.tag
    return rail


popup.make_gear_quality_slider = gear_slider
capsule = PopupChild()
popup.make_gear_speed_slider = lambda native: capsule if native is slider else None
popup.call = lambda _, *args: gear_commits.append(args)
popup.prepare_gear_sliders(gear_viewer)
assert gear_rails[0][:2] == (["自动", "480p", "720p", "原画 1080p"], 2)
assert not popup.prepare_gear_quality(gear_viewer) and len(gear_rails) == 1
assert gear_popup.rows[0] is capsule and slider.parent is None and speed_gap.parent is None
gear_rails[0][2](3)
assert gear_commits == [("chooseQuality", 0)]
quality_player.getQualitiesCount = lambda: 0
assert popup.prepare_gear_quality(gear_viewer)
assert gear_rails[-1] == (["原画 1080p"], 0, None)
assert gear_popup.rows[-1] is not quality and gear_popup.rows[-1].visibility == 0
gear_refresh = []
gear_menu = Obj(forceUpdatePopupPosition=lambda: gear_refresh.append(True))
popup.active = True
popup.video_surface = lambda _: True
popup.video_menu = value_field(gear_menu)
popup.gear_state = [(popup.weak_reference(gear_menu),)]
popup.popup_window = value_field(Obj(isShowing=lambda: True))
quality_player.getQualitiesCount = lambda: 3
popup.after_gear_quality_update(Obj(thisObject=gear_viewer))
popup.after_gear_quality_update(Obj(thisObject=gear_viewer))
assert gear_refresh == [True] and len(gear_rails) == 3
assert popup.gear_label_width([0.5], [60], 20) == 240
assert popup.gear_label_width([0.0, 0.1, 1.0], [28, 28, 28], 20) > 300
assert video.gear_snap_point([0.0, 0.5, 1.0], 0.58, None, None, 9, 15) == 1
assert video.gear_snap_point([0.0, 0.5, 1.0], 0.545, 240, 1, 9, 15) == 1
assert video.gear_snap_point([0.0, 0.5, 1.0], 0.58, 240, 1, 9, 15) is None

speed_calls = []
class SliderWidget:
    SLIDER_STYLE_MD3 = 2

    def __init__(self, *_):
        self.children, self.haptics = [], []

    def addView(self, child, *args):
        child.params = args[-1]
        if len(args) == 2:
            self.children.insert(args[0], child)
        else:
            self.children.append(child)

    def addOnLayoutChangeListener(self, callback):
        self.layout_callback = callback

    def getPaint(self):
        return Obj(measureText=lambda value: len(value) * 5)

    def getWidth(self):
        return 320

    def getLayoutParams(self):
        return self.params

    def performHapticFeedback(self, value):
        self.haptics.append(value)

    def __getattr__(self, method):
        if method.startswith("set"):
            return lambda *args: setattr(self, method[3:], args[0] if len(args) == 1 else args)
        raise AttributeError(method)


popup.linear_layout = popup.text_view = popup.frame_layout = popup.view_type = SliderWidget
popup.pill_background = popup.gear_seek = SliderWidget
popup.linear_params = lambda width, height, *args: Obj(width=width, height=height)
popup.frame_params = lambda *args: Obj()
popup.rect = lambda *args: args
popup.gear_seek_listener = lambda callback: Obj(apply=callback)
popup.gear_layout_listener = lambda callback: callback
popup.gear_touch_listener = object
popup.sdk, popup.haptic = 35, Obj(SEGMENT_TICK=26, SEGMENT_FREQUENT_TICK=27)
popup.float_value, popup.boolean, popup.arguments = float, bool, list
popup.native_speed_update = Obj(invoke=lambda native, args: speed_calls.append(tuple(args)))
speed_positions = [(value - 0.2) / 2.8 for value in (0.5, 1, 1.5, 2, 2.5)]
popup.native_speed_stops = value_field(speed_positions)
native_speed = Obj(getContext=lambda: None, getValue=lambda: speed_positions[1], getSpeed=lambda value: 0.2 + 2.8 * value)
speed_row = video.VideoSeekbarGestureInsets.make_gear_speed_slider(popup, native_speed)
body, speed_divider = speed_row.children[1:]
assert speed_divider.BackgroundColor == video.MENU_DIVIDER_COLOR and speed_divider.params.height == 8
capsule_bar = body.children[-1]
labels = [view for view in body.children if "Text" in vars(view)]
assert len(body.children[2:-2]) == len(labels) * 2 - 2  # Interior ticks only.
assert capsule_bar.Progress == round(speed_positions[1] * 2800)
assert [label.Text for label in labels] == ["0.2×", "0.5×", "1×", "1.5×", "2×", "2.5×", "3×"]
body.layout_callback(320)
assert labels[0].TranslationX < labels[-1].TranslationX
assert body.children[1].Right == 110 and body.children[1].params.width == 97
body.layout_callback(240)
assert labels[-1].TranslationX < 240 and body.children[1].Right == 87
capsule_bar.OnSeekBarChangeListener.apply(False, 0.367)
assert abs(speed_calls[-1][0] - 1 / 2.8) < 0.0001 and speed_calls[-1][1] is False
assert speed_row.children[0].children[1].Text == "1.2×"
assert capsule_bar.haptics == [27]
capsule_bar.OnSeekBarChangeListener.apply(False, speed_positions[2] + 0.02)
capsule_bar.OnSeekBarChangeListener.apply(True, speed_positions[2] + 0.025)
assert speed_calls[-2:] == [(speed_positions[2], False), (speed_positions[2], True)]
assert capsule_bar.haptics == [27, 26]
labels[1].OnClickListener(labels[1])
assert speed_calls[-1] == (speed_positions[0], True) and capsule_bar.haptics[-1] == 26

quality_picks = []
quality_row = video.VideoSeekbarGestureInsets.make_gear_quality_slider(popup, None, ["自动", "480p", "原画 1080p"], 0, quality_picks.append)
quality_body, quality_divider = quality_row.children[1:]
assert quality_divider.BackgroundColor == video.MENU_DIVIDER_COLOR
assert len(quality_body.children[2:-2]) == 4  # Three labels and one tick.
quality_bar = quality_body.children[-1]
quality_body.layout_callback(240)
quality_bar.OnSeekBarChangeListener.apply(False, 0.4)
assert not quality_picks and quality_bar.Progress == 1400
quality_bar.OnSeekBarChangeListener.apply(True, 0.4)
assert quality_body.children[1].Right == 129 and quality_picks == [1] and quality_bar.haptics == [26]
duplicate_quality = video.VideoSeekbarGestureInsets.make_gear_quality_slider(
    popup, None, ["自动", "1080p", "原画 1080p"], 2, quality_picks.append)
assert duplicate_quality.children[0].children[1].Text == "原画 1080p"
assert [view.Text for view in duplicate_quality.children[1].children if "Text" in vars(view)] == ["自动", "1080p", "原画"]
assert [view.Text for view in quality_body.children if "Text" in vars(view)][-1] == "原画 1080p"
fixed_quality = video.VideoSeekbarGestureInsets.make_gear_quality_slider(popup, None, ["原画 1080p"], 0, None)
assert len(fixed_quality.children) == 2 and fixed_quality.children[-1].BackgroundColor == video.MENU_DIVIDER_COLOR
assert [label.Text for label in fixed_quality.children[0].children] == ["画质", "1080p"]
mode_picks = []
mode_row = popup.make_gear_capsule(None, "Playback mode", (0.0, 0.5, 1.0),
    ("Continuous play", "Loop", "Stop after this"), 0.5, None,
    lambda final, _, point: mode_picks.append(point) if final else None, discrete=True)
mode_body, = mode_row.children
mode_labels = [view for view in mode_body.children if "Text" in vars(view)]
mode_body.layout_callback(220)
assert len(mode_body.children) == 10
mode_track = mode_body.children[0]
assert mode_track.Background.Color == video.jint(0x42FFFFFF)
assert mode_track.Background.CornerRadius == 9
assert mode_track.params.topMargin == (32 - 18) // 2
assert mode_body.children[1].Background.Color == video.SLIDER_ACTIVE
assert mode_body.children[1].params.width == 106
for first, second in zip(mode_labels, mode_labels[1:]):
    first_right = first.TranslationX + first.PivotX * (1.0 + first.ScaleX)
    second_left = second.TranslationX + second.PivotX * (1.0 - second.ScaleX)
    assert first_right <= second_left
mode_body.children[-1].OnSeekBarChangeListener.apply(False, 0.93)
assert not mode_picks
mode_body.children[-1].OnSeekBarChangeListener.apply(True, 0.93)
assert mode_picks == [2]
mode_labels[0].OnClickListener(mode_labels[0])
assert mode_picks == [2, 0] and sum(label.Selected for label in mode_labels) == 1
assert mode_body.children[-1].ContentDescription == "Playback mode Continuous play"


def thumbnail_message(dialog, *, account=0, msg_id=1, group=0, photo=True, video=False):
    return Obj(currentAccount=account, getDialogId=lambda: dialog, getId=lambda: msg_id, getGroupId=lambda: group,
               isPhoto=lambda: photo, isVideo=lambda: video)


first_pic = thumbnail_message(-100)
another_message = thumbnail_message(-100, msg_id=2, group=99, photo=False, video=True)
same_album = thumbnail_message(-100, msg_id=3, group=99)
other_chat = thumbnail_message(-101)
other_account = thumbnail_message(-101, account=1)
irrelevant_file = thumbnail_message(-44, photo=False)
items, extent = video.thumbnail_entries(
    [first_pic, irrelevant_file, another_message, same_album, other_chat, other_account], 74, 12, 24, 6)
assert items == [(6, first_pic), (80, video.THUMBNAIL_MESSAGE_DIVIDER), (92, another_message),
                 (166, same_album), (240, video.THUMBNAIL_CHAT_DIVIDER), (264, other_chat),
                 (338, video.THUMBNAIL_CHAT_DIVIDER), (362, other_account)] and extent == 442
assert video.thumbnail_entries([first_pic], 62, 12, 24, 6) == ([(6, first_pic)], 74)
another_message.caption, same_album.caption = object(), None
foreign_caption = thumbnail_message(-101, msg_id=1, group=99)
foreign_caption.caption = object()
other_account_caption = thumbnail_message(-100, account=1, msg_id=1, group=99)
other_account_caption.caption = object()
assert video.album_caption_source(same_album, native_list(
                                  [same_album, other_account_caption, foreign_caption, another_message]),
                                  lambda content: content is None) is another_message
assert video.album_caption_source(same_album, native_list([foreign_caption, other_account_caption]),
                                  lambda _: False) is None
assert video.album_caption_source(first_pic, native_list([another_message]), lambda _: False) is None
photo_controls = video.VideoSeekbarGestureInsets()
photo_control_events = []
photo_controls.boolean = bool
photo_controls.controls = value_field(Obj(getVisibility=lambda: 0,
    setAlpha=lambda alpha: photo_control_events.append(("alpha", alpha)),
    setVisibility=lambda visibility: photo_control_events.append(("visibility", visibility))))
photo_controls.video_controls_animator = value_field(Obj(cancel=lambda: photo_control_events.append("cancel")))
photo_controls.call = lambda _, name, *args: photo_control_events.append((name, *args))
photo_controls.clear_video_controls_on_photo(viewer)
assert photo_control_events == ["cancel", ("setVideoPlayerControlVisible", False, False),
                                ("alpha", 0.0), ("visibility", 8)]
assert video.selected_thumbnail_size("4") == 4
assert video.selected_thumbnail_size(-1) == video.DEFAULT_THUMBNAIL_SIZE
assert video.thumbnail_dimensions(int, 88, False, 360) == (88, 106)
assert video.thumbnail_dimensions(int, 88, True, 640) == (88, 66)
assert video.thumbnail_dimensions(int, 184, True, 440) == (128, 96)
assert video.thumbnail_dimensions(int, 184, False, 360) == (146, 175)
bookmarks = video.VideoSeekbarGestureInsets()
for original, expected in (("今天 15:20, DC4", "今天 15:20"), ("15:20, DC12", "15:20"),
                           ("15:20 UTC", "15:20 UTC"), (None, None)):
    label = Obj(args=[original, False])
    bookmarks.hide_media_dc(label)
    assert label.args[0] == expected

bookmarks.positions = list
choices = {}
bookmark_calls = []
bookmark_entries = set()
bookmark_screen = Obj(getCurrentMessageObject=lambda: first_pic, getParentActivity=lambda: object())
first_pic.isSponsored = lambda: False
first_pic.isSent = lambda: True
same_album.isSent = lambda: True
bookmarks.parent_chat = value_field(None)
bookmarks.album_messages = value_field(native_list([same_album, other_chat, first_pic, another_message]))
bookmarks.viewer_resources_provider = value_field(None)
bookmarks.bookmark_choice = lambda callback: callback
bookmarks.bookmark_dialog = lambda *_: Obj(
    setTitle=lambda _: None, setMessage=lambda _: None,
    setNegativeButton=lambda _, callback: choices.__setitem__("one", callback),
    setPositiveButton=lambda _, callback: choices.__setitem__("all", callback),
    setNeutralButton=lambda *_: None, create=lambda: Obj(show=lambda: bookmark_calls.append("shown")))
bookmarks.bookmark_result = Obj(ADDED="added")
bookmarks.bookmark_indices, bookmarks.bookmark_history = {0: {}}, {}
bookmarks.bookmark_pending, bookmarks.bookmark_waiting = {}, set()
bookmarks.bookmark_removed = {}
bookmarks.bookmark_users = Obj(getInstance=lambda _: Obj(getClientUserId=lambda: 777))
bookmarks.weak_reference = plugin.weak_reference
bookmarks.bookmark_source_keys = lambda message: [("message", message.getDialogId(), message.getId())]
star = Obj(selected=False, getVisibility=lambda: 0)
star.isSelected = lambda: star.selected
star.setSelected = lambda selected: setattr(star, "selected", selected)
star.setIcon = lambda icon, _: setattr(star, "icon", icon)
star.setIconColor = lambda color: setattr(star, "color", color)
star.getContentDescription = lambda: getattr(star, "description", None)
star.setContentDescription = lambda description: setattr(star, "description", description)
star.getIconView = lambda: None
bookmarks.drawable = Obj(msg_saved_solar=2, msg_saved_filled_solar=3)
bookmarks.header_menu = value_field(Obj(getItem=lambda _: star))


def add_media_bookmarks(account, dialog, ids):
    assert (account, dialog) == (0, -100)
    assert not bookmark_entries.intersection(ids)
    bookmark_entries.update(ids)
    bookmark_calls.append(tuple(ids))
    return "added"


def remove_media_bookmarks(account, dialog, ids):
    assert (account, dialog) == (0, -100) and bookmark_entries.issuperset(ids)
    bookmark_entries.difference_update(ids)
    return True


bookmarks.bookmarks = Obj(getBookmarkedMessageIds=lambda *_: list(bookmark_entries),
                          toggleBookmarks=add_media_bookmarks, removeBookmarks=remove_media_bookmarks)
try:
    first_pic.getGroupId = lambda: 55
    same_album.getGroupId = lambda: 55
    bookmarks.bookmark_current_media(bookmark_screen)
    assert bookmark_calls == ["shown"] and not bookmark_entries
    choices["one"]()
    assert bookmark_entries == {first_pic.getId()} and star.selected and star.icon == 3
    assert star.color == video.BOOKMARK_YELLOW
    bookmarks.bookmark_current_media(bookmark_screen)
    assert not bookmark_entries and not star.selected and star.icon == 2
    choices["all"]()
    assert bookmark_entries == {first_pic.getId(), same_album.getId()}
    calls_before = bookmark_calls[:]
    choices["all"]()
    bookmarks.bookmark_current_media(bookmark_screen)
    assert not bookmark_entries and not star.selected and bookmark_calls == calls_before
finally:
    first_pic.getGroupId = lambda: 0
    same_album.getGroupId = lambda: 99

saved_target = (777, 81)
media_key = ("photo", 101)
bookmarks.bookmark_source_keys = lambda message: [("message", message.getDialogId(), message.getId()), media_key]
bookmarks.bookmark_indices[0][media_key] = saved_target
duplicates = []
bookmarks.show_duplicate_bookmark = lambda activity, target, **source: duplicates.append((target, source))
bookmarks.update_media_bookmark_icon(star, first_pic)
assert star.selected and star.icon == 3 and star.color == video.BOOKMARK_YELLOW
assert star.description == "取消收藏"
removed_targets = []
remove_saved_target = bookmarks.remove_saved_bookmark
bookmarks.remove_saved_bookmark = lambda account, target: removed_targets.append((account, target))
bookmarks.bookmark_current_media(bookmark_screen)
assert removed_targets == [(0, saved_target)] and not bookmark_entries
bookmarks.remove_saved_bookmark = remove_saved_target
bookmarks.bookmark_indices[0].clear()
bookmarks.bookmark_history[0] = {"entries": {media_key: saved_target}}
assert bookmarks.existing_bookmark(first_pic) == saved_target
bookmarks.active = True
bookmarks.bookmark_selection = value_field(first_pic), value_field(None)
chat = Obj(getParentActivity=lambda: object())
prevented = []
bookmarks.before_bookmark_chat_action(Obj(args=[video.CHAT_SAVE_MESSAGE_ID], thisObject=chat, setResult=prevented.append))
assert prevented == [None] and duplicates[-1] == (saved_target, {"chat": chat})
drawn_stars = []
listing = object()
bookmarks.bookmark_active_chat = plugin.weak_reference(listing), 0, True
bookmarks.bookmark_draw_cache = {}
bookmarks.bookmark_share_hits = {}
bookmarks.bookmark_blur = Obj(drawingBlur=False)
bookmarks.bookmark_side_kind = Obj(getInt=lambda _: 1)
bookmarks.bookmark_side_visible = Obj(getBoolean=lambda _: True)
bookmarks.bookmark_quick_share = Obj(getBoolean=lambda _: False)
bookmarks.bookmark_clip_edge = object()
bookmarks.bookmark_theme = Obj(key_paint_chatActionBackground="chat", chat_actionBackgroundGradientDarkenPaint="darken")
bookmarks.bookmark_filled = Obj(setBounds=lambda *bounds: drawn_stars.append(bounds), draw=drawn_stars.append)
bookmarks.bookmark_outline = Obj(setBounds=lambda *bounds: drawn_stars.append(bounds), draw=lambda _: drawn_stars.append("outline"))
bookmarks.dp = int
first_pic.isOutOwner = lambda: False
bubble = Obj(getParent=lambda: listing, getMessageObject=lambda: first_pic, hashCode=lambda: 1,
             getSideButtonStartX=lambda: 160.0, getSideButtonStartY=lambda: 64.0,
             getCurrentMessagesGroup=lambda: None,
             applyServiceShaderMatrix=lambda: None, getThemedPaint=lambda value: value,
             hasGradientService=lambda: True)
chat_canvas = Obj(drawRoundRect=lambda *points: drawn_stars.append(points), quickReject=lambda *_: False)


def native_share_draw(*, quick=False, failed=False):
    param = Obj(thisObject=bubble, args=[chat_canvas, quick], hasThrowable=lambda: failed)
    bookmarks.draw_share_bookmark(param)


bookmarks.bookmark_side_kind.getInt = lambda _: 0
native_share_draw()
assert not drawn_stars
bookmarks.bookmark_side_kind.getInt = lambda _: 1
native_share_draw()
assert drawn_stars == [(160, 28, 192, 60, 16.0, 16.0, "chat"),
                       (160, 28, 192, 60, 16.0, 16.0, "darken"), (165, 33, 187, 55), chat_canvas]
bookmarks.bookmark_history[0]["entries"].clear()
bookmarks.bookmark_draw_cache.clear()
native_share_draw()
assert drawn_stars[-2:] == [(166, 34, 186, 54), "outline"]
group = Obj(messages=native_list([first_pic, same_album]), hashCode=lambda: 321, isDocuments=False)
bubble.getCurrentMessagesGroup = lambda: group
assert bookmarks.chat_bookmark_members(bubble, first_pic) == [first_pic, same_album]
first_pic_group = first_pic.getGroupId
first_pic.getGroupId = lambda: 40
read_members = bookmarks.chat_bookmark_members
album_checks = []
bookmarks.chat_bookmark_members = lambda *args: (album_checks.append(True), read_members(*args))[1]
native_share_draw()
native_share_draw()
assert len(album_checks) == 1
bookmarks.bookmark_draw_cache.clear()
native_share_draw()
assert len(album_checks) == 2
bookmarks.chat_bookmark_members, first_pic.getGroupId = read_members, first_pic_group
del drawn_stars[8:]
assert bookmarks.chat_bookmark_bounds(bubble) == (160, 28, 32)
group.isDocuments = True
bubble.getCurrentPosition = lambda: Obj(last=False)
native_share_draw()
assert bookmarks.chat_bookmark_bounds(bubble) is None
group.isDocuments = False
bookmarks.bookmark_side_visible.getBoolean = lambda _: False
native_share_draw()
bookmarks.bookmark_side_visible.getBoolean = lambda _: True
native_share_draw(quick=True)
native_share_draw(failed=True)
chat_canvas.quickReject = lambda left, top, *_: top == 64
native_share_draw()
assert bookmarks.chat_bookmark_bounds(bubble) is None
chat_canvas.quickReject = lambda *_: False
bubble.getCurrentMessagesGroup = lambda: None
bookmarks.bookmark_active_chat = plugin.weak_reference(listing), 0, False
native_share_draw()
assert len(drawn_stars) == 8

bookmarks.bookmark_active_chat = plugin.weak_reference(listing), 0, True
native_share_draw()
bubble.getMessageObject = lambda: same_album
assert bookmarks.chat_bookmark_bounds(bubble) is None
bubble.getMessageObject = lambda: first_pic
bubble.getDelegate = lambda: None
bubble.getEventX, bubble.getEventY = lambda event: event.x, lambda event: event.y
bubble.performHapticFeedback = lambda _: None
bookmarks.bookmark_press, bookmarks.caption_tap_timeout = None, 500
bookmarks.haptic, bookmarks.boolean = Obj(LONG_PRESS=0), bool
clicks, callbacks = [], []
activate_bookmark = bookmarks.activate_chat_bookmark
bookmarks.activate_chat_bookmark = lambda cell, message, hold: clicks.append(hold) or True
touch_namespace = bookmarks.touch_chat_bookmark.__globals__
old_touch_scheduler = touch_namespace["run_on_ui_thread"]
touch_namespace["run_on_ui_thread"] = lambda cb, delay: callbacks.append(cb)


def touch_bookmark(action, x=176, y=42):
    arguments = [Obj(getActionMasked=lambda: action, x=x, y=y)]
    bookmarks.touch_chat_bookmark(Obj(thisObject=bubble, args=arguments, setResult=lambda _: None))


try:
    touch_bookmark(0)
    touch_bookmark(1)
    callbacks.pop()()
    assert clicks == [False]
    touch_bookmark(0)
    callbacks.pop()()
    touch_bookmark(1)
    assert clicks == [False, True]
    touch_bookmark(0)
    touch_bookmark(2, y=16)
    callbacks.pop()()
    touch_bookmark(1)
    assert clicks == [False, True]
    bookmarks.bookmark_side_visible.getBoolean = lambda _: False
    native_share_draw()
    touch_bookmark(0)
    touch_bookmark(1)
    assert clicks == [False, True] and not callbacks
finally:
    touch_namespace["run_on_ui_thread"] = old_touch_scheduler
    bookmarks.activate_chat_bookmark = activate_bookmark
saved_index = {}
bookmarks.dialog_object = Obj(getPeerDialogId=lambda peer: peer)
bookmarks.bookmark_media_id = lambda raw: raw.media_key
bookmarks.index_saved_message(saved_index, 777, 81, Obj(media_key=media_key,
    fwd_from=Obj(saved_from_peer=-102, saved_from_msg_id=12, from_id=-105, channel_post=18)))
assert saved_index == {("message", -102, 12): saved_target, ("message", -105, 18): saved_target,
                       media_key: saved_target}
jump_fragments = []
bookmark_activity = Obj(isFinishing=lambda: False, presentFragment=jump_fragments.append)
saved_chat = Obj(getCurrentAccount=lambda: 0)
bookmarks.bookmark_collection = lambda dialog: ("bookmarks", dialog)


def saved_bundle():
    values = {}
    return Obj(values=values, putLong=values.__setitem__, putInt=values.__setitem__)


bookmarks.bookmark_bundle = saved_bundle
bookmarks.bookmark_chat = lambda arguments: ("saved messages", arguments.values)
for target in (saved_target, (-106, 81)):
    video.VideoSeekbarGestureInsets.show_duplicate_bookmark(bookmarks, bookmark_activity, target, chat=saved_chat)
    choices["all"]()
assert jump_fragments == [("saved messages", {"user_id": 777, "message_id": 81}), ("bookmarks", -106)]
bookmark_navigation = []
bookmark_origin = object()
bookmark_activity.getActionBarLayout = lambda: Obj(getLastFragment=lambda: bookmark_origin)
bookmark_activity.presentFragment = lambda collection, *flags: bookmark_navigation.append((collection, flags)) or True
bookmark_screen.closePhoto = lambda *args: bookmark_navigation.append(("close viewer", args))
bookmarks.launch_activity_type = Obj(isInstance=lambda _: True)
bookmarks.chat_activity = Obj(isInstance=lambda _: False)
bookmarks.library_return = None
bookmark_route = Obj(focus=None)


def capture_bookmark_return(viewer, activity, collection, origin, chat, message):
    assert viewer is bookmark_screen and activity is bookmark_activity and origin is bookmark_origin
    assert chat is None and message is first_pic
    bookmark_route.fragment = collection
    return bookmark_route


bookmarks.capture_library_return = capture_bookmark_return
bookmarks.open_bookmark_collection(bookmark_activity, 0, saved_target, viewer=bookmark_screen)
assert bookmarks.library_return is bookmark_route
assert bookmark_navigation == [(("saved messages", {"user_id": 777, "message_id": 81}), (False, True)),
                               ("close viewer", (False, False))]
bookmark_namespace = bookmarks.after_bookmark_collection_destroy.__globals__
bookmark_runner = bookmark_namespace["run_on_ui_thread"]
bookmarks.return_from_media_library = lambda route, remaining: bookmark_navigation.append((route, remaining))
try:
    bookmark_namespace["run_on_ui_thread"] = lambda callback, delay=0: callback()
    bookmarks.after_bookmark_collection_destroy(Obj(thisObject=object()))
    bookmarks.after_bookmark_collection_destroy(Obj(thisObject=bookmark_route.fragment))
    assert bookmark_navigation[-1] == (bookmark_route, 40)
finally:
    bookmark_namespace["run_on_ui_thread"] = bookmark_runner

native_deletions = []
bookmarks.bookmark_ids, bookmarks.integer = PinnedList, int
bookmarks.header_messages = Obj(getInstance=lambda account: Obj(
    deleteMessages=lambda ids, randoms, secret, dialog, topic, everyone, mode:
        native_deletions.append((account, list(ids), dialog, topic, everyone, mode))))
refresh_bookmarks = bookmarks.refresh_bookmark_views
bookmarks.refresh_bookmark_views = lambda _: None
bookmarks.remove_saved_bookmark(0, saved_target)
assert native_deletions == [(0, [81], 777, 0, False, 0)]
assert saved_target in bookmarks.bookmark_removed.pop(0)
bookmarks.refresh_bookmark_views = refresh_bookmarks

pending = video.VideoSeekbarGestureInsets()
pending.active = True
pending.bookmark_pending, pending.bookmark_waiting = {}, set()
pending.bookmark_indices, pending.bookmark_history, pending.bookmark_removed = {0: {}}, {}, {}
pending.bookmark_users, pending.bookmarks = bookmarks.bookmark_users, bookmarks.bookmarks
pending.bookmark_source_keys, pending.bookmark_media_id = bookmarks.bookmark_source_keys, bookmarks.bookmark_media_id
pending.bookmark_ids = PinnedList
pending.bookmark_draw_cache = {}
pending.bookmark_selection = bookmarks.bookmark_selection
pending.bookmark_new, pending.bookmark_ack, pending.bookmark_deleted, pending.bookmark_send_error = 1, 2, 3, 4
pending.bookmark_notification_account = Obj(getInt=lambda _: 0)
pending.request_bookmark_index = lambda *_, **__: None
queued_source = {"fwd_id": str(first_pic.getId()), "fwd_peer": str(first_pic.getDialogId())}
queued_params = Obj(containsKey=queued_source.__contains__, get=queued_source.get)
pending_removals = []
pending.remove_saved_bookmark = lambda account, target: pending_removals.append((account, target))
pending.drawable = bookmarks.drawable


def refresh_pending(_):
    pending.bookmark_draw_cache.clear()
    pending.update_media_bookmark_icon(star, first_pic)


def queue_saved(mid, dialog=777):
    outgoing = Obj(currentAccount=0, isSending=lambda: True, getId=lambda: mid,
                   messageOwner=Obj(params=queued_params, media_key=media_key))
    pending.after_bookmark_queued(Obj(args=[dialog, native_list([outgoing]), 0]))


def post_saved(event, *args):
    pending.after_bookmark_notification(Obj(args=[event, args], thisObject=object()))


pending.refresh_bookmark_views = refresh_pending
refresh_pending(0)
assert not star.selected
queue_saved(-31, 778)
assert not star.selected
queue_saved(-31)
assert star.selected and pending.is_chat_bookmarked(first_pic) and star.color == video.BOOKMARK_YELLOW
prevented.clear()
pending.before_bookmark_chat_action(Obj(args=[video.CHAT_SAVE_MESSAGE_ID], thisObject=chat, setResult=prevented.append))
assert prevented == [None]
for expected in (False, True, False):
    assert pending.toggle_pending_bookmark(first_pic)
    assert star.selected is expected and pending.is_chat_bookmarked(first_pic) is expected
queue_saved(-31)
assert not star.selected
post_saved(pending.bookmark_ack, -31, 91, None, 777)
assert not star.selected and pending_removals == [(0, (777, 91))]
queue_saved(-32)
assert star.selected
post_saved(pending.bookmark_send_error, -32)
assert not star.selected and pending.pending_bookmark(first_pic) is None
queue_saved(-33)
assert star.selected
post_saved(pending.bookmark_ack, -33, 92, None, 777)
assert star.selected and pending.bookmark_target(first_pic) == (777, 92) and not pending.bookmark_pending
pending.bookmark_source_keys = lambda item: [("message", item.getDialogId(), item.getId())]
group_additions = []
pending.save_bookmark_messages = lambda account, dialog, additions, chat: group_additions.append(additions) and False
pending.toggle_chat_bookmarks(chat, first_pic, [first_pic, same_album])
assert group_additions == [[same_album]] and pending_removals == [(0, (777, 91))]
pending.bookmark_pending[0, -34] = dict(keys=pending.bookmark_source_keys(same_album), cancelled=False)
pending.toggle_chat_bookmarks(chat, first_pic, [first_pic, same_album])
assert pending_removals[-1] == (0, (777, 92)) and pending.bookmark_pending[0, -34]["cancelled"]

saved_requests, saved_tasks, saved_refreshes = [], [], []
bookmarks.bookmark_history.clear()
bookmarks.bookmark_app = Obj(mainInterfacePaused=False)
bookmarks.bookmark_history_request = Obj
bookmarks.bookmark_peer_self = object
bookmarks.refresh_bookmark_views = saved_refreshes.append


def send_saved_page(request, callback):
    saved_requests.append((request, callback))
    return len(saved_requests)


bookmarks.bookmark_connections = Obj(getInstance=lambda _: Obj(sendRequest=send_saved_page))
bookmark_namespace = bookmarks.request_saved_bookmark_page.__globals__
old_callback = bookmark_namespace["RequestCallback"]
old_scheduler = bookmark_namespace["run_on_ui_thread"]
bookmark_namespace["RequestCallback"] = lambda callback, _: callback
bookmark_namespace["run_on_ui_thread"] = lambda callback, delay=0: saved_tasks.append(callback) if delay else callback()
try:
    bookmarks.request_saved_bookmark_page(0, 777)
    first_page, reply = saved_requests[0]
    assert first_page.offset_id == 0 and first_page.limit == video.SAVED_BOOKMARK_PAGE_SIZE
    raw = Obj(id=81, media_key=media_key, fwd_from=None)
    # Java ArrayList on NagramXF exposes size/get, without Python iteration.
    reply(Obj(messages=Obj(size=lambda: 1, get=lambda _: raw)), None)
    assert bookmarks.existing_bookmark(first_pic) == saved_target and saved_refreshes == [0]
    saved_tasks.pop()()
    next_page, reply = saved_requests[1]
    assert next_page.offset_id == 81
    reply(Obj(messages=Obj(size=lambda: 0)), None)
    assert bookmarks.bookmark_history[0]["offset"] is None and not saved_tasks
finally:
    bookmark_namespace["RequestCallback"] = old_callback
    bookmark_namespace["run_on_ui_thread"] = old_scheduler

class JavaThumbnailMessage(Obj):
    def __eq__(self, other):
        if not isinstance(other, JavaThumbnailMessage):
            raise TypeError("MessageObject.equals requires a Java-compatible argument")
        return (self.getDialogId(), self.getId()) == (other.getDialogId(), other.getId())


strict_current = JavaThumbnailMessage(**vars(first_pic))
strict_neighbor = JavaThumbnailMessage(**vars(another_message))
assert not video.same_thumbnail_item(video.THUMBNAIL_MESSAGE_DIVIDER, strict_current)
assert not video.same_thumbnail_item(strict_current, video.THUMBNAIL_CHAT_DIVIDER)
assert video.same_thumbnail_item(strict_current, JavaThumbnailMessage(**vars(first_pic)))
caption_source = JavaThumbnailMessage(**vars(another_message), isRestrictedMessage=False, isHiddenSensitive=lambda: False)
caption_member = JavaThumbnailMessage(**vars(same_album))
group_caption = video.VideoSeekbarGestureInsets()
group_caption.caption_exit = None
group_caption.caption_in_picker = Obj(getBoolean=lambda _: False)
group_caption.text_utils = Obj(isEmpty=lambda text: text is None, equals=lambda left, right: left is right)
group_caption.spanned_class = Obj(isInstance=lambda _: False)
group_caption.option = lambda _: True
group_caption.boolean = bool
group_caption.top_captions = []
native_group = Obj(messages=native_list([caption_member, caption_source]))
native_chat = Obj(getDialogId=caption_member.getDialogId, getGroup=lambda _: native_group)
group_caption.parent_chat = value_field(native_chat)
group_caption.album_messages = value_field(native_list([caption_member]))
caption_viewer = Obj(isVisible=lambda: True, getCurrentMessageObject=lambda: caption_member)
caption_args = Obj(thisObject=caption_viewer, args=[caption_member, None, False, True])
group_caption.before_caption_change(caption_args)
assert caption_args.args == [caption_source, caption_source.caption, False, False]
assert group_caption.caption_state_key(caption_viewer, caption_member) == (-100, 2)
own_caption = object()
caption_args.args = [caption_member, own_caption, False, True]
group_caption.before_caption_change(caption_args)
assert caption_args.args[0] is caption_member and caption_args.args[1] is own_caption
group_caption.caption_source_hidden = lambda item, chat, group: item is caption_source
caption_args.args = [caption_member, None, False, True]
group_caption.before_caption_change(caption_args)
assert caption_args.args[1] is None
group_caption.caption_source_hidden = lambda *args: False
caption_refreshes = []
group_caption.call = lambda *args: caption_refreshes.append(args)
group_caption.media_loaded_event = 22
group_caption.refresh_inherited_caption(Obj(thisObject=caption_viewer, args=[22]))
assert caption_refreshes == [(caption_viewer, "setCurrentCaption", caption_member, None, False, False)]

quote = Obj(styleSpan=object(), collapsedSpan=None, isCollapsing=True)
quote_removed, quote_added = [], []
rich_caption = Obj(length=lambda: 32, getSpans=lambda *_: [quote],
                   getSpanStart=lambda _: 2, getSpanEnd=lambda _: 28)
group_caption.quote_span_type = object()
group_caption.spanned = object()
group_caption.spanned_class = Obj(isInstance=lambda content: content is rich_caption)
group_caption.spannable_string = lambda caption: Obj(original=caption, removeSpan=quote_removed.append)
group_caption.quote_span = Obj(putQuote=lambda _, start, end, collapse: quote_added.append((start, end, collapse)))
previous_source_caption, caption_source.caption = caption_source.caption, rich_caption
for item, text in ((caption_source, rich_caption), (caption_member, None)):
    caption_args.args = [item, text, False, False]
    group_caption.before_caption_change(caption_args)
    assert caption_args.args[0] is caption_source and caption_args.args[1].original is rich_caption
assert quote_removed == [quote, quote.styleSpan] * 2 and quote_added == [(2, 28, True)] * 2
assert caption_source.caption is rich_caption
caption_source.caption = previous_source_caption

search_window = Obj(messages=JavaList([Obj(id=1011), Obj(id=1010), Obj(id=1008)]),
                    flags=4, offset_id_offset=100, count=250)
search_window.messages.isEmpty = lambda: False
assert video.media_grid_anchor(search_window, 1010) == (1012, 100, 250)
assert video.media_grid_anchor(search_window, 999) is None
assert video.media_grid_index(JavaList([other_chat, first_pic]), -100, 1) == 1
assert video.media_grid_scroll_target(101, 250, 3, 362, 100) == (101, 131)
assert video.media_grid_scroll_target(101, 250, 3, 362, 100, 24, 12) == (101, 137)
assert video.media_grid_scroll_target(1, 250, 3, 362, 100) == (0, 0)
assert video.media_grid_scroll_target(248, 250, 3, 362, 100) == (249, 262)
assert video.media_grid_scroll_target(7, 8, 3, 362, 100) == (0, 0)
assert video.media_grid_scroll_target(8, 8, 3, 362, 100) is None

library_plugin = video.VideoSeekbarGestureInsets()
library_plugin.active, library_plugin.integer, library_plugin.library_list_type = True, int, object()
library_plugin.library_visible_rect = Obj(top=0, bottom=0)
library_plugin.library_cell_type = Obj(getClass=lambda: Obj(isInstance=lambda cell: hasattr(cell, "getY")))
library_plugin.library_return = None
library_focus = library_plugin.pending_media_library = (object(), -100, 1, None)
library_scroll = []
library_manager = Obj(scrollToPositionWithOffset=lambda position, offset: library_scroll.append((position, offset)))
library_adapter = Obj(getPositionForIndex=lambda index: 100 + index, getItemCount=lambda: 250)
library_grid = Obj(getLayoutManager=lambda: library_manager, getAdapter=lambda: library_adapter,
                   getScrollState=lambda: 0, isComputingLayout=lambda: False, hasPendingAdapterUpdates=lambda: False,
                   isLayoutRequested=lambda: False,
                   getLocalVisibleRect=lambda _: False,
                   getHeight=lambda: 400, getWidth=lambda: 300,
                   getPaddingTop=lambda: 26, getPaddingBottom=lambda: 12, getPaddingLeft=lambda: 0,
                   getPaddingRight=lambda: 0, getColumnsCount=lambda: 3,
                   findViewHolderForAdapterPosition=lambda _: None, invalidate=lambda: None)
library_plugin.library_layout = value_field(Obj(isAttachedToWindow=lambda: True, getClosestTab=lambda: 0))
library_page = object()
library_plugin.library_page = Obj(invoke=lambda *_: library_page)
library_plugin.library_list = value_field(library_grid)
library_plugin.library_tabs = value_field(None)
library_plugin.library_adapter = value_field(library_adapter)
library_plugin.library_data = value_field([Obj(getMessages=lambda: JavaList([other_chat, first_pic]))])
library_plugin.focus_media_library(library_focus, 0)
assert library_scroll == [(101, 131)] and library_plugin.pending_media_library is None

library_focus = library_plugin.pending_media_library = (object(), -100, 1, None)
library_grid.getScrollState = lambda: 1
library_plugin.focus_media_library(library_focus, 1)
assert library_scroll == [(101, 131)] and library_plugin.pending_media_library is None
library_grid.getScrollState = lambda: 0
library_plugin.center_media_library_row(library_grid, 1, None)
assert library_scroll[-1] == (0, 0)
library_manager.getDecoratedMeasuredHeight = lambda _: 100
library_manager.getDecoratedTop = lambda _: 126
library_manager.getDecoratedBottom = lambda _: 226
library_grid.findViewHolderForAdapterPosition = lambda _: Obj(itemView=object())
library_grid.canScrollVertically = lambda _: False
library_plugin.center_media_library_row(library_grid, 1, None)
assert library_scroll == [(101, 131), (0, 0)]
library_grid.canScrollVertically = lambda direction: direction == -1
library_grid.scrollBy = lambda x, y: library_scroll.append(("scroll", x, y))
library_plugin.center_media_library_row(library_grid, 101, None)
assert library_scroll[-1] == ("scroll", 0, -31)
library_plugin.library_tabs = value_field(Obj(isShown=lambda: True, getHeight=lambda: 30))
library_plugin.view_origin = lambda *_: (0, 36)
library_plugin.center_media_library_row(library_grid, 101, object())
assert library_scroll[-1] == ("scroll", 0, -51)

preview_item = Obj(messageOwner=Obj(ttl=0), isVideo=lambda: True, hasMediaSpoilers=lambda: False,
                   isRestrictedMessage=False, isHiddenSensitive=lambda: False)
preview_player = Obj(isPlaying=lambda: True, getCurrentUri=lambda: "file:video", getCurrentPosition=lambda: 24000,
                     getPlaybackSpeed=lambda: 1.5)
preview_viewer = Obj(getVideoPlayer=lambda: preview_player)
assert library_plugin.capture_library_video(preview_viewer, preview_item) == ("file:video", 0, 24000, 1.5)
preview_item.hasMediaSpoilers = lambda: True
assert library_plugin.capture_library_video(preview_viewer, preview_item) is None

preview_start = []
preview_output = Obj(setOpaque=lambda value: preview_start.append(("opaque", value)))
preview_box_factory = lambda _: Obj(addView=lambda *_: None, setResizeMode=lambda _: None)
library_plugin.frame_layout = library_plugin.library_aspect = preview_box_factory
library_plugin.frame_params = lambda *args: args
library_plugin.library_texture = lambda _: preview_output
library_plugin.library_delegate = lambda _: "delegate"
library_plugin.position_library_preview = lambda *_: True
native_preview_player = Obj(setDelegate=lambda value: preview_start.append(("delegate", value)),
                            setTextureView=lambda value: preview_start.append(("texture", value)),
                            preparePlayer=lambda *args: preview_start.append(("prepare", *args)),
                            seekTo=lambda value: preview_start.append(("seek", value)),
                            setPlaybackSpeed=lambda value: preview_start.append(("speed", value)),
                            setPlayWhenReady=lambda value: preview_start.append(("playing", value)))
def make_preview_player(pause_other, audio_disabled):
    preview_start.append(("create", pause_other, audio_disabled))
    return native_preview_player

library_plugin.library_player_type = make_preview_player
preview_host = Obj(addView=lambda *_: None)
start_preview = video.LibraryVideoPreview(Obj(getFragmentView=lambda: preview_host), preview_host, -100, 1, 101,
                                         ("file:video", 32, 24000, 1.5))
library_plugin.start_library_preview(start_preview, Obj(getContext=lambda: None))
assert preview_start == [("opaque", False), ("create", False, True), ("delegate", "delegate"), ("texture", preview_output),
                         ("prepare", "file:video", "other", 0, 32), ("seek", 24000), ("speed", 1.5), ("playing", True)]

preview_events = []
preview_fragment = Obj()
preview_fragment.getParentLayout = lambda: Obj(getLastFragment=lambda: preview_fragment)
preview_list = Obj(isShown=lambda: True, getScrollState=lambda: 0)
playing_preview = library_plugin.library_preview = video.LibraryVideoPreview(
    preview_fragment, preview_list, -100, 1, 101, ("file:video", 0, 24000, 1.5))
playing_preview.player = Obj(releasePlayer=lambda _: preview_events.append("released"))
playing_preview.frame = Obj(getParent=lambda: Obj(removeView=preview_events.append))
playing_preview.cell = Obj(getMessageObject=lambda: other_chat, getParent=lambda: preview_list)
library_plugin.library_return = None
library_plugin.update_library_preview(playing_preview)
assert library_plugin.library_preview is None and preview_events == ["released", playing_preview.frame]

scroll_events = []
scroll_state = Obj(value=1)
scrolling_preview = library_plugin.library_preview = video.LibraryVideoPreview(
    preview_fragment, preview_list, -100, 1, 101, ("file:video", 0, 24000, 1.5))
preview_list.getScrollState = lambda: scroll_state.value
scrolling_preview.cell = Obj(getMessageObject=lambda: first_pic, getParent=lambda: preview_list)
scrolling_preview.player = Obj(setPlayWhenReady=lambda value: scroll_events.append(("playing", value)))
scrolling_preview.frame = Obj(setVisibility=lambda value: scroll_events.append(("visibility", value)))
library_plugin.update_library_preview(scrolling_preview)
library_plugin.update_library_preview(scrolling_preview)
assert scroll_events == [("visibility", 4), ("playing", False)]
scroll_state.value = 0
library_plugin.update_library_preview(scrolling_preview)
assert scroll_events[-2:] == [("visibility", 0), ("playing", True)]
library_plugin.library_preview = None

preview_rects = []
library_plugin.dp = int
library_plugin.sdk = 32
library_plugin.view_origin = lambda *_: (5, 6)
library_plugin.rect = lambda *args: args
library_plugin.measure_spec = Obj(EXACTLY=1, makeMeasureSpec=lambda size, _: size)
library_plugin.library_cell_image = value_field(Obj(getImageX=lambda: 2, getImageY=lambda: 3,
                                                   getImageWidth=lambda: 98, getImageHeight=lambda: 96,
                                                   getRoundRadius=lambda _: [18, 1, 4, 1]))
preview_bounds = Obj()
bounded_preview = video.LibraryVideoPreview(preview_fragment, Obj(getPaddingTop=lambda: 20,
    getHeight=lambda: 400, getPaddingBottom=lambda: 0), -100, 1, 101, None)
bounded_preview.frame = Obj(getLayoutParams=lambda: preview_bounds, measure=lambda *_: None,
    layout=lambda *args: preview_rects.append(("layout", args)),
    setTranslationX=lambda value: preview_rects.append(("x", value)),
    setTranslationY=lambda value: preview_rects.append(("y", value)),
    setClipBounds=lambda value: preview_rects.append(("clip", value)))
bounded_cell = Obj(getX=lambda: 10, getY=lambda: 10, getWidth=lambda: 102, getHeight=lambda: 104)
assert video.VideoSeekbarGestureInsets.position_library_preview(library_plugin, bounded_preview, bounded_cell)
assert preview_rects == [("layout", (0, 0, 98, 96)), ("x", 17), ("y", 19), ("clip", (0, 7, 98, 96))]

bounded_cell.getParent, bounded_cell.getMessageObject = lambda: library_grid, lambda: first_pic
bounded_cell.getY = lambda: 126
library_grid.findViewHolderForAdapterPosition = lambda _: Obj(itemView=bounded_cell)
def visible_grid_bounds(rect):
    rect.top, rect.bottom = 62, 350
    return True
library_grid.getLocalVisibleRect = visible_grid_bounds
library_plugin.library_tabs = value_field(None)
library_plugin.center_media_library_row(library_grid, 101, object())
assert library_scroll[-1] == ("scroll", 0, -29)

marker_events, root_children, overlay_children = [], [], []
library_grid.isChangeColumnsAnimation = lambda: False
marker = Obj(visibility=4, setImageResource=lambda resource: marker_events.append(("icon", resource)),
             setScaleType=lambda _: None, setColorFilter=lambda _: None, setBackground=lambda _: None,
             setImportantForAccessibility=lambda _: None, setPadding=lambda *_: None, measure=lambda *_: None,
             getVisibility=lambda: marker.visibility, setVisibility=lambda value: setattr(marker, "visibility", value),
             layout=lambda *args: marker_events.append(("position", args)))
marker_overlay = Obj(add=overlay_children.append, remove=overlay_children.remove)
marker_host = Obj(getContext=lambda: None, getOverlay=lambda: marker_overlay, addView=root_children.append)
marker_fragment = Obj(getFragmentView=lambda: marker_host)
marker_route = library_plugin.library_return = Obj(fragment=marker_fragment, selection=None, selection_cell=None,
    focus_geometry=(library_grid, None, 300, (62, 350), 101), key=(-100, first_pic.getId()))
library_plugin.image_view = lambda _: marker
library_plugin.drawable = Obj(msg_views=12)
library_plugin.fit_center = object()
library_plugin.round_background = lambda *_: None
library_plugin.weak_reference = lambda value: Obj(get=lambda: value)
library_plugin.install_library_selection(marker_route)
assert overlay_children == [marker] and not root_children and marker.visibility == 4
marker_update = Obj(thisObject=library_grid)
library_plugin.update_library_selection(marker_update)
assert marker_events == [("icon", 12), ("position", (87, 139, 111, 163))] and marker.visibility == 0
marker_host.addView(object())  # The video preview is added after the indicator.
library_plugin.update_library_selection(marker_update)
assert len(marker_events) == 2 and overlay_children == [marker] and marker.visibility == 0

background_cell = Obj(getY=lambda: 150, getX=lambda: 12, getWidth=lambda: 102, getHeight=lambda: 104,
                      getParent=lambda: library_grid, getMessageObject=lambda: other_chat)
bounded_cell.getMessageObject = lambda: other_chat
library_grid.findViewHolderForAdapterPosition = lambda _: Obj(itemView=background_cell)
library_plugin.update_library_selection(marker_update)
assert marker.visibility == 4
rebound = Obj(getY=lambda: 150, getX=lambda: 12, getWidth=lambda: 102, getHeight=lambda: 104,
              getParent=lambda: library_grid, getMessageObject=lambda: first_pic)
library_plugin.track_library_selection_cell(Obj(thisObject=library_adapter, args=[Obj(itemView=rebound), 118]))
library_plugin.update_library_selection(marker_update)
assert marker_events[-1] == ("position", (89, 163, 113, 187)) and marker.visibility == 0
library_plugin.remove_library_selection(marker_route)
assert not overlay_children and marker_route.selection is None

returned = []
saved_chat_position = object()
portrait_chat_position = object()
return_manager = Obj(onRestoreInstanceState=lambda state: returned.append(("restore chat", state)))
return_chat = return_origin = Obj(getChatListView=lambda: Obj(getLayoutManager=lambda: return_manager,
                                                             getAdapter=lambda: None),
                                 getParentLayout=lambda: Obj(getLastFragment=lambda: return_chat))
return_activity = Obj(isFinishing=lambda: False,
                      getActionBarLayout=lambda: Obj(getLastFragment=lambda: return_origin),
                      getResources=lambda: Obj(getConfiguration=lambda: Obj(orientation=1)))
return_player = Obj(isPlayerPrepared=lambda: True, seekTo=lambda value: returned.append(("seek", value)),
                    setPlaybackSpeed=lambda value: returned.append(("speed", value)),
                    setPlayWhenReady=lambda value: returned.append(("playing", value)))
return_viewer = Obj(visible=False, getCurrentMessageObject=lambda: first_pic, getVideoPlayer=lambda: return_player,
                    setParentActivity=lambda *args: returned.append(("origin", args)),
                    getParentActivity=lambda: return_activity)
return_viewer.isVisible = lambda: return_viewer.visible
def reopen_test_video(*args):
    returned.append(("open", args))
    return_viewer.visible = True
    return True

return_viewer.openPhoto = reopen_test_video
library_plugin.weak_reference = lambda value: Obj(get=lambda: value)
library_plugin.lock_playback_axis = lambda _, direction: returned.append(("axis", direction))
library_plugin.viewer_pending_seek = Obj(setFloat=lambda _, value: returned.append(("pending", value)))
return_provider, return_theme = object(), object()
direct_provider = object()
return_queue = Obj(indexOf=lambda item: 4 if item is first_pic else -1)
library_plugin.album_provider = lambda: direct_provider
library_plugin.seek_preview = value_field(None)
library_plugin.manual_pause = Obj(setBoolean=lambda *_: None)
library_plugin.viewer_container = value_field(Obj(isShown=lambda: True, getAlpha=lambda: 1.0,
                                                  getWidth=lambda: 820, getHeight=lambda: 440))
library_plugin.viewer_provider = Obj(set=lambda _, provider: returned.append(("provider", provider)))
return_route = library_plugin.library_return = video.LibraryReturn(
    return_viewer, return_activity, object(), return_origin, return_chat, return_provider, (return_origin, return_theme),
    first_pic, return_queue, (-100, 0, 7), video.SENSOR_LANDSCAPE, (24000, 1.5, True),
    (saved_chat_position, 10, None, False))
portrait_state = (portrait_chat_position, 12, None, False)
return_route.opening_chat_viewport = (library_plugin.weak_reference(return_viewer),
    library_plugin.weak_reference(return_chat), return_route.key, portrait_state)
library_plugin.return_from_media_library(return_route, 2)
assert library_plugin.opening_chat_viewport is return_route.opening_chat_viewport
assert returned[0] == ("origin", (return_activity, return_origin, return_theme))
assert returned[1][1][0] is None and returned[1][1][4] is return_queue and returned[1][1][7] == 4
assert returned[1][1][8:13] == (direct_provider, return_chat, -100, 0, 7)
assert returned[2] == ("provider", return_provider)
assert returned[-6:] == [("restore chat", saved_chat_position), ("axis", video.SENSOR_LANDSCAPE),
                         ("pending", 0), ("seek", 24000),
                         ("speed", 1.5), ("playing", True)]
assert return_route.chat_layout_state is None
assert library_plugin.library_return is None and library_plugin.library_resume is None

return_viewer.visible = False
return_fragment = Obj()
return_fragment.getParentLayout = lambda: Obj(getLastFragment=lambda: return_fragment)
return_fragment.onBackPressed = lambda invoked: bool(invoked)
return_route.fragment = return_fragment
return_route.chat_layout_state = (saved_chat_position, 10, None, False)
library_plugin.library_return = return_route
library_plugin.boolean = bool
library_plugin.leave_media_library = lambda _: returned.append("stop preview")
library_callbacks = []
library_namespace = video.VideoSeekbarGestureInsets.before_media_library_finish.__globals__
library_runner = library_namespace["run_on_ui_thread"]
library_namespace["run_on_ui_thread"] = lambda callback, delay=0: library_callbacks.append((callback, delay))

def test_finish_library(animated):
    request = Obj(thisObject=return_fragment, args=[animated], setResult=lambda result: returned.append(("handled", result)))
    if library_plugin.library_return is None:
        returned.append(("pop library", animated))
    else:
        library_plugin.before_media_library_finish(request)

return_fragment.finishFragment = test_finish_library
try:
    back_results = []
    back_request = Obj(thisObject=return_activity, args=[False], getResult=lambda: True, setResult=back_results.append)
    library_plugin.back_from_media_library(back_request)
    assert back_results == [False] and not return_viewer.visible and not library_callbacks
    back_request.args[0] = True
    library_plugin.back_from_media_library(back_request)
    assert back_results == [False, False] and return_viewer.visible
    assert returned[-1] == ("handled", True) and library_plugin.library_return is None
    callback, delay = library_callbacks.pop()
    assert delay == 240
    callback()
    assert returned[-7:-4] == [("pop library", False), ("restore chat", saved_chat_position),
                               ("axis", video.SENSOR_LANDSCAPE)]
    assert return_route.chat_layout_state is None
finally:
    library_namespace["run_on_ui_thread"] = library_runner
resume_jump = Obj(pending=True, unread=False)
library_plugin.chat_resume_scroll = Obj(getBoolean=lambda _: resume_jump.pending,
                                        setBoolean=lambda _, value: setattr(resume_jump, "pending", value))
library_plugin.chat_resume_unread = Obj(getBoolean=lambda _: resume_jump.unread)
library_plugin.paused_chat_viewports = {}
library_plugin.library_resume = return_route
return_route.chat_layout_state = (saved_chat_position, 10, None, False)
library_plugin.before_library_chat_resume(Obj(thisObject=object()))
assert resume_jump.pending
library_plugin.before_library_chat_resume(Obj(thisObject=return_chat))
assert not resume_jump.pending and return_route.chat_layout_state is not None
resume_jump.pending = resume_jump.unread = True
library_plugin.before_library_chat_resume(Obj(thisObject=return_chat))
assert resume_jump.pending and return_route.chat_layout_state is None
assert return_route.opening_chat_viewport[2:] == ((first_pic.getDialogId(), first_pic.getId()), None)
library_plugin.library_resume = None

native_chat_events = []
chat_layout = Obj(width=360, height=720, attached=True, requested=False, computing=False, updates=False)
return_chat.scrollToMessageId = lambda *args: native_chat_events.append(args)
return_chat.getDialogId = lambda: -100
library_plugin.chat_merged_dialog = Obj(getLong=lambda _: 0)

reflow_cell = Obj(relayout=lambda: native_chat_events.append("row layout"),
                  invalidate=lambda: native_chat_events.append("row redraw"))
reflow_animator = Obj(isRunning=lambda: True, endAnimations=lambda: native_chat_events.append("end animation"))
return_listing = Obj(isAttachedToWindow=lambda: chat_layout.attached, getChildCount=lambda: 1,
    getLayoutManager=lambda: return_manager, getAdapter=lambda: None,
    getWidth=lambda: chat_layout.width, getHeight=lambda: chat_layout.height,
    isLayoutRequested=lambda: chat_layout.requested, isComputingLayout=lambda: chat_layout.computing,
    hasPendingAdapterUpdates=lambda: chat_layout.updates,
    getChildAt=lambda _: reflow_cell, getItemAnimator=lambda: reflow_animator,
    requestLayout=lambda: native_chat_events.append("chat layout"),
    invalidate=lambda: native_chat_events.append("chat redraw"))
return_chat.getChatListView = lambda: return_listing
library_plugin.chat_cell = Obj(getClass=lambda: Obj(isInstance=lambda cell: cell is reflow_cell))
library_plugin.chat_cell_height_cache = Obj(setInt=lambda _, value: native_chat_events.append(("reset height", value)))
library_plugin.parent_chat = value_field(return_chat)
return_window = Obj(width=720, height=360)
library_plugin.window = value_field(Obj(getWidth=lambda: return_window.width, getHeight=lambda: return_window.height))
library_plugin.release_video_orientation = lambda _: native_chat_events.append("release orientation")
library_plugin.capture_chat_layout_state = lambda _: portrait_state
first_video = Obj(isVideo=lambda: True, getId=first_pic.getId, getDialogId=first_pic.getDialogId)
library_plugin.remember_opening_chat_viewport(return_viewer, first_video)
assert library_plugin.opening_chat_viewport[-1] is portrait_state
library_plugin.before_viewer_close(Obj(thisObject=return_viewer, args=[True, False]))
assert native_chat_events[-1] == "release orientation"
library_plugin.after_chat_rotation(Obj(thisObject=return_chat, args=[Obj(orientation=2)]))
assert len(native_chat_events) == 1
library_plugin.after_chat_rotation(Obj(thisObject=return_chat, args=[Obj(orientation=1)]))
assert native_chat_events[-4:] == ["end animation", ("reset height", -1), "row layout", "chat layout"]
library_plugin.after_viewer_closed(Obj(thisObject=return_viewer))
assert native_chat_events[-2:] == ["row redraw", "chat redraw"] and library_plugin.pending_chat_reflow is None

return_window.width, return_window.height = 360, 720
return_viewer.getCurrentMessageObject = lambda: first_pic
library_plugin.remember_opening_chat_viewport(return_viewer, first_pic)
return_viewer.getCurrentMessageObject = lambda: another_message
library_plugin.before_viewer_close(Obj(thisObject=return_viewer, args=[True, False]))
library_plugin.after_viewer_closed(Obj(thisObject=return_viewer))
assert (another_message.getId(), 0, False, 0, True, 0) in native_chat_events
return_viewer.getCurrentMessageObject = lambda: first_pic
assert returned[-1] == ("restore chat", portrait_chat_position)
return_window.width, return_window.height = 720, 360
library_plugin.before_viewer_close(Obj(thisObject=return_viewer, args=[True, False]))
library_plugin.after_viewer_closed(Obj(thisObject=return_viewer))
assert native_chat_events[-1] == "release orientation"
library_plugin.after_chat_rotation(Obj(thisObject=return_chat, args=[Obj(orientation=1)]))
assert native_chat_events[-2:] == ["row redraw", "chat redraw"] and library_plugin.pending_chat_reflow is None

# The viewer can rotate back to portrait before the chat receives its final layout.
# Keep its original chat reference even if the current native viewer parent has been cleared.
return_viewer.getCurrentMessageObject = lambda: first_video
library_plugin.remember_opening_chat_viewport(return_viewer, first_video)
library_plugin.parent_chat = value_field(None)
return_window.width, return_window.height = 360, 720
return_viewer.getCurrentMessageObject = lambda: another_message
native_chat_events.clear()
library_plugin.before_viewer_close(Obj(thisObject=return_viewer, args=[True, False]))
library_plugin.after_viewer_closed(Obj(thisObject=return_viewer))
assert native_chat_events[1] == (another_message.getId(), 0, False, 0, True, 0)
assert library_plugin.pending_chat_reflow is None and library_plugin.opening_chat_viewport is None
library_plugin.parent_chat = value_field(return_chat)

return_viewer.getCurrentMessageObject = lambda: first_video
return_window.width, return_window.height = 360, 720
library_plugin.remember_opening_chat_viewport(return_viewer, first_video)
return_viewer.getCurrentMessageObject = lambda: another_message
return_window.width, return_window.height = 720, 360
chat_layout.width, chat_layout.height = 720, 360
native_chat_events.clear()
scheduled_return = []
return_scope = library_plugin.after_viewer_closed.__globals__
old_return_scheduler = return_scope["run_on_ui_thread"]
return_scope["run_on_ui_thread"] = lambda callback, _: scheduled_return.append(callback)
try:
    library_plugin.before_viewer_close(Obj(thisObject=return_viewer, args=[True, False]))
    library_plugin.after_viewer_closed(Obj(thisObject=return_viewer))
    assert native_chat_events == ["release orientation"] and len(scheduled_return) == 1
    chat_layout.requested = True
    scheduled_return.pop(0)()
    chat_layout.width, chat_layout.height = 360, 720
    library_plugin.after_chat_rotation(Obj(thisObject=return_chat, args=[Obj(orientation=1)]))
    assert not any(isinstance(event, tuple) and len(event) == 6 for event in native_chat_events)
    chat_layout.requested = False
    scheduled_return.pop(0)()
    assert library_plugin.pending_chat_reflow is not None
    scheduled_return.pop(0)()
    assert native_chat_events[-3:] == [(another_message.getId(), 0, False, 0, True, 0),
                                       "row redraw", "chat redraw"]
finally:
    return_scope["run_on_ui_thread"] = old_return_scheduler

# The original message keeps its viewport. A changed item uses the current message and
# its native load index, including when the phone stays landscape after Back.
return_window.width, return_window.height = 360, 720
return_viewer.getCurrentMessageObject = lambda: first_video
library_plugin.remember_opening_chat_viewport(return_viewer, first_video)
native_chat_events.clear()
library_plugin.before_viewer_close(Obj(thisObject=return_viewer, args=[True, False]))
library_plugin.after_viewer_closed(Obj(thisObject=return_viewer))
assert native_chat_events == ["release orientation"]

merged_photo = Obj(getDialogId=lambda: -200, getId=lambda: 23, isPhoto=lambda: True)
library_plugin.chat_merged_dialog = Obj(getLong=lambda _: -200)
library_plugin.remember_opening_chat_viewport(return_viewer, first_video)
return_viewer.getCurrentMessageObject = lambda: merged_photo
return_window.width, return_window.height = 720, 360
chat_layout.width, chat_layout.height = 720, 360
native_chat_events.clear()
return_scope["run_on_ui_thread"] = lambda callback, _: scheduled_return.append(callback)
try:
    library_plugin.before_viewer_close(Obj(thisObject=return_viewer, args=[True, True]))
    library_plugin.leave_viewer = lambda _: None
    library_plugin.before_viewer_closed(Obj(thisObject=return_viewer))
    library_plugin.after_viewer_closed(Obj(thisObject=return_viewer))
    for _ in range(45):
        if not scheduled_return:
            break
        scheduled_return.pop(0)()
    assert not scheduled_return and native_chat_events.count((23, 0, False, 1, True, 0)) == 1

    return_viewer.getCurrentMessageObject = lambda: first_video
    library_plugin.remember_opening_chat_viewport(return_viewer, first_video)
    return_viewer.getCurrentMessageObject = lambda: merged_photo
    library_plugin.before_viewer_close(Obj(thisObject=return_viewer, args=[True, False]))
    library_plugin.after_viewer_closed(Obj(thisObject=return_viewer))
    return_viewer.getCurrentMessageObject = lambda: first_video
    library_plugin.remember_opening_chat_viewport(return_viewer, first_video)
    scheduled_return.pop(0)()
    assert native_chat_events.count((23, 0, False, 1, True, 0)) == 1
finally:
    return_scope["run_on_ui_thread"] = old_return_scheduler
# The previous chat is paused and removed from the hierarchy before the destination opens a video.
# Check that only the old viewport is restored, even if onResume beats the portrait resize.
outer_geometry = Obj(orientation=1, scroll=0)
outer_resume = Obj(pending=False, unread=False)
outer_manager = Obj(onRestoreInstanceState=lambda state: outer_restore.append(state))
outer_listing = Obj(getLayoutManager=lambda: outer_manager, getAdapter=lambda: None,
                    isAttachedToWindow=lambda: True, getScrollState=lambda: outer_geometry.scroll,
                    getResources=lambda: Obj(getConfiguration=lambda: outer_geometry),
                    requestLayout=lambda: outer_restore.append("layout"))
outer_chat = Obj(getClassGuid=lambda: 78, getChatListView=lambda: outer_listing,
                 getParentLayout=lambda: Obj(getLastFragment=lambda: return_chat))
outer_param = Obj(thisObject=outer_chat)
outer_restore, resumed_chats = [], []
library_plugin.track_bookmark_chat = resumed_chats.append
library_plugin.viewer_instances = (value_field(None), value_field(return_viewer))
return_viewer.isVisible = lambda: True
library_plugin.chat_resume_scroll = Obj(getBoolean=lambda _: outer_resume.pending,
                                        setBoolean=lambda _, value: setattr(outer_resume, "pending", value))
library_plugin.chat_resume_unread = Obj(getBoolean=lambda _: outer_resume.unread)
library_plugin.remember_paused_chat_viewport(outer_param)
library_plugin.before_chat_rotation(Obj(thisObject=outer_chat, args=[Obj(orientation=2)]))
assert library_plugin.paused_chat_viewports[78].rotated
outer_geometry.orientation, outer_resume.pending = 2, True
library_plugin.before_chat_resume(outer_param)
library_plugin.after_chat_resume(outer_param)
assert resumed_chats == [outer_chat] and not outer_restore and not outer_resume.pending
outer_geometry.orientation = 1
library_plugin.after_chat_rotation(Obj(thisObject=outer_chat, args=[outer_geometry]))
assert outer_restore == [portrait_state[0], "layout"] and not library_plugin.paused_chat_viewports
library_plugin.remember_paused_chat_viewport(outer_param)
library_plugin.before_chat_resume(outer_param)
assert not library_plugin.paused_chat_viewports   # No landscape playback.
library_plugin.remember_paused_chat_viewport(outer_param)
library_plugin.before_chat_rotation(Obj(thisObject=outer_chat, args=[Obj(orientation=2)]))
outer_resume.pending = outer_resume.unread = True
library_plugin.before_chat_resume(outer_param)
assert outer_resume.pending and not library_plugin.paused_chat_viewports   # Native unread navigation wins.

print("Passed cross-chat landscape return and native unread navigation")
print("Passed original, rotated, merged-chat, native-close and superseded media return paths")

many_offsets = list(range(6, 62000, 62))
first_window = video.thumbnail_range(many_offsets, 0, 200, 124)
next_window = video.thumbnail_range(many_offsets, 1200, 200, 124)
assert first_window.start == 0 and len(first_window) < 12 and len(next_window) < 12
assert not set(first_window).intersection(next_window)
queue_rail = video.ThumbnailRail(viewer, None, None, (18, 20))
queue_rail.entries = [(index * 20, thumbnail_message(-100, msg_id=index + 1)) for index in range(9)]
queue_rail.offsets = [offset for offset, _ in queue_rail.entries]
queue_rail.position, queue_rail.height, queue_rail.center, queue_rail.dirty = 60, 60, 30, False
queue_plugin = video.VideoSeekbarGestureInsets()
thumb_requests = []
queue_plugin.create_thumbnail_cell = lambda rail, item: thumb_requests.append(item.getId())
assert queue_plugin.thumbnail_visible_range(queue_rail) == range(3, 6)
assert queue_plugin.thumbnail_prefetch_range(queue_rail, range(3, 6)) == range(0, 9)
assert queue_plugin.render_thumbnail_window(queue_rail) == 16
assert thumb_requests == [5, 4, 6]
assert queue_plugin.render_thumbnail_window(queue_rail) == 16
assert thumb_requests == [5, 4, 6, 3, 7, 2]
assert queue_plugin.render_thumbnail_window(queue_rail) is None
assert thumb_requests == [5, 4, 6, 3, 7, 2, 8, 1, 9]
queue_rail.position = 80
assert queue_plugin.render_thumbnail_window(queue_rail) is None and len(thumb_requests) == 9

opening_plugin = video.VideoSeekbarGestureInsets()
opening_plugin.file_loader = Obj(PRIORITY_NORMAL=3)
opening_plugin.viewer_container = value_field(None)
opening_requests, opening_callbacks, opening_events = [], [], []
opening_messages = []
for mid in range(1, 8):
    item = thumbnail_message(-100, msg_id=mid)
    item.isRestrictedMessage = False
    item.isHiddenSensitive = lambda: False
    opening_messages.append(item)
opening_messages[2].isHiddenSensitive = lambda: True


def opening_receiver(container, strip, item, *, warm=False):
    mid = item.getId()
    opening_requests.append((mid, warm))
    return Obj(setParentView=lambda _: opening_events.append(("parent", mid)),
               setFileLoadingPriority=lambda _: opening_events.append(("priority", mid)),
               hasBitmapImage=lambda: False, moveImageToFront=lambda: opening_events.append(("promote", mid)),
               onDetachedFromWindow=lambda: opening_events.append(("detach", mid)))


opening_plugin.create_thumbnail_receiver = opening_receiver
opening_namespace = opening_plugin.prefetch_opening_thumbnails.__globals__
opening_runner = opening_namespace["run_on_ui_thread"]
try:
    opening_namespace["run_on_ui_thread"] = lambda callback, delay: opening_callbacks.append((callback, delay))
    opening_plugin.prefetch_opening_thumbnails(viewer, None, opening_messages[3], native_list(opening_messages), 3)
    assert opening_requests == [(2, True), (1, True), (5, True), (6, True)]
    assert opening_plugin.create_thumbnail_cell(queue_rail, opening_messages[4]) is not None
    assert opening_events == [("parent", 5), ("priority", 5), ("promote", 5)]
    assert len(opening_requests) == 4
    expire, delay = opening_callbacks.pop()
    assert delay == 3500
    expire()
    assert not opening_plugin.thumbnail_seed.receivers
    assert opening_events[3:] == [("detach", 2), ("detach", 1), ("detach", 6)]
    opening_plugin.clear_thumbnail_seed(viewer)
    assert opening_plugin.thumbnail_seed is None
finally:
    opening_namespace["run_on_ui_thread"] = opening_runner
queue_rail.entries = [(index * 20, thumbnail_message(-100, msg_id=index + 1)) for index in range(30)]
queue_rail.offsets = [offset for offset, _ in queue_rail.entries]
promoted = []
existing = Obj(hasBitmapImage=lambda: False, moveImageToFront=lambda: promoted.append(15),
               onDetachedFromWindow=lambda: None)
queue_rail.position, queue_rail.scroll_direction, queue_rail.cells = 280, -1, {14: existing}
thumb_requests.clear()
queue_plugin.render_thumbnail_window(queue_rail)
assert promoted == [15] and thumb_requests == [16, 17, 14]
queue_plugin.render_thumbnail_window(queue_rail)
assert thumb_requests[-3:] == [13, 12, 11]
queue_rail.position, queue_rail.scroll_direction = 340, 1
queue_plugin.render_thumbnail_window(queue_rail)
assert thumb_requests[-3:] == [20, 19, 18]
queue_plugin.render_thumbnail_window(queue_rail)
assert thumb_requests[-3:] == [21, 22, 23]
warm_rail = video.ThumbnailRail(viewer, None, object(), (18, 20))
warm_rail.entries, warm_rail.offsets = queue_rail.entries, queue_rail.offsets
warm_rail.collapsed, warm_rail.dirty = True, False
warm_rail.position, warm_rail.height, warm_rail.center = 60, 210, 105
queue_plugin.active, queue_plugin.thumbnail_rail = True, warm_rail
warm_jobs, warm_calls, parents = [], [], []
warm_namespace = queue_plugin.schedule_thumbnail_warmup.__globals__
old_scheduler = warm_namespace["run_on_ui_thread"]
warm_namespace["run_on_ui_thread"] = lambda callback, delay: warm_jobs.append((callback, delay))


def warm_receiver(parent, strip, item, *, warm):
    assert parent is None and warm
    warm_calls.append(item.getId() - 1)
    return Obj(setParentView=parents.append, setFileLoadingPriority=lambda _: None, hasBitmapImage=lambda: True)


queue_plugin.create_thumbnail_receiver = warm_receiver
queue_plugin.file_loader = Obj(PRIORITY_NORMAL=1)
try:
    queue_plugin.schedule_thumbnail_warmup(warm_rail)
    queue_plugin.schedule_thumbnail_warmup(warm_rail)
    assert len(warm_jobs) == 1 and warm_jobs[0][1] == video.THUMBNAIL_WARM_DELAY and not warm_calls
    warm_rail.position = 180
    warm_jobs.pop(0)[0]()
    assert len(warm_jobs) == 1 and not warm_calls
    while warm_jobs:
        previous_count = len(warm_calls)
        warm_jobs.pop(0)[0]()
        assert 0 < len(warm_calls) - previous_count <= 2
    assert tuple(warm_calls) == queue_plugin.thumbnail_warm_indices(warm_rail)
    assert len(warm_calls) == video.THUMBNAIL_WARM_LIMIT
    queue_plugin.schedule_thumbnail_warmup(warm_rail)
    assert not warm_jobs and not parents
    warm_rail.collapsed = False
    queue_plugin.render_thumbnail_window(warm_rail)
    assert parents == [warm_rail.container] * len(warm_calls) and not warm_rail.parked_cells
finally:
    warm_namespace["run_on_ui_thread"] = old_scheduler
unloaded = []
rail = Obj(cells={0: Obj(onDetachedFromWindow=lambda: unloaded.append("detached")), 1: None})
popup.drop_thumbnail_cells(rail, range(1, 2))
assert unloaded == ["detached"] and list(rail.cells) == [1]
edges = []
popup.on_thumbnail_edge = lambda viewer, index, direction: edges.append((viewer, index, direction))
rail.viewer, rail.source, rail.dirty = viewer, (None, 50), False
rail.provisional = False
rail.position, rail.height, rail.viewport, rail.extent = 180, 220, 220, 1000
popup.prefetch_thumbnail_edge(rail, -1)
popup.prefetch_thumbnail_edge(rail, 1)
rail.position = 570
popup.prefetch_thumbnail_edge(rail, 1)
assert edges == [(viewer, 0, "older"), (viewer, 49, "newer")]

first_layout = []
native_strip = Obj(visibility=0)
native_strip.getVisibility = lambda: native_strip.visibility
native_strip.setVisibility = lambda value: (first_layout.append(("native", value)), setattr(native_strip, "visibility", value))
gallery_container = Obj(getHeight=lambda: 440, getPaddingLeft=lambda: 0, getPaddingRight=lambda: 0, getContext=lambda: None,
                        getPaddingBottom=lambda: 0, getRootWindowInsets=lambda: None, requestLayout=lambda: None,
                        invalidate=lambda: None)
gallery_viewer = Obj(current=strict_current, index=0, primary=-100, merged=0, isVisible=lambda: True,
                     getCurrentMessageObject=lambda: gallery_viewer.current, getCurrentIndex=lambda: gallery_viewer.index)
first_images = native_list([strict_current])
rail_plugin = video.VideoSeekbarGestureInsets()
rail_plugin.active, rail_plugin.dp = True, int
rail_storage = {"thumbnail_rail_collapsed_0_-100": False, "thumbnail_rail_collapsed_0_-101": False}
rail_plugin.get_setting = rail_storage.get
rail_plugin.set_setting = rail_storage.__setitem__
rail_plugin.load_thumbnail_width()
rail_plugin.show_thumbnail_drag_hint = lambda _: None
rail_plugin.configure_thumbnail_state()
rail_plugin.viewer_dialogs = (Obj(getLong=lambda v: v.primary), Obj(getLong=lambda v: v.merged))
rail_plugin.searching_album = Obj(getBoolean=lambda _: False)
first_paint_rail = video.ThumbnailRail(gallery_viewer, None, gallery_container, (84, 102))
first_paint_rail.source = None, 1
rail_plugin.searching_album.getBoolean = lambda _: True
assert not rail_plugin.reveal_thumbnail_window(first_paint_rail)
first_paint_rail.opened_at = -1e10
assert rail_plugin.reveal_thumbnail_window(first_paint_rail)
first_paint_rail.source = None, 3
first_paint_rail.opened_at = rail_plugin.reveal_thumbnail_window.__globals__["monotonic"]()
assert rail_plugin.reveal_thumbnail_window(first_paint_rail)
rail_plugin.searching_album.getBoolean = lambda _: False
rail_plugin.album_strip, rail_plugin.album_messages = value_field(native_strip), value_field(first_images)
rail_plugin.thumbnail_scroller = lambda _: Obj(computeScrollOffset=lambda: False)
rail_plugin.window = rail_plugin.controls = rail_plugin.action_bar = value_field(None)
rail_plugin.action_bar_visible = Obj(getBoolean=lambda _: True)
rail_plugin.action_bar_animator = value_field(None)
rail_plugin.thumbnail_paint = Obj(setColor=lambda _: None)
rail_plugin.thumbnail_outline = Obj(setStrokeWidth=lambda _: None)
rail_plugin.thumbnail_fade = None
rail_plugin.positions = rail_plugin.thumbnail_fade_positions = list
rail_plugin.thumbnail_clamp = object()
rail_plugin.thumbnail_gradient = lambda *args: args
rail_plugin.thumbnail_mask = Obj(setShader=lambda _: None)
receiver_draws = []
detached_thumbnails = []
thumb_receiver = Obj(setImageCoords=lambda *coords: receiver_draws.append(coords), draw=lambda _: True,
                     hasBitmapImage=lambda: True,
                     onDetachedFromWindow=lambda: detached_thumbnails.append("detached"))
rail_plugin.create_thumbnail_cell = lambda _, item: (None if item is video.THUMBNAIL_MESSAGE_DIVIDER else thumb_receiver)
rail_plugin.install_thumbnail_handle = lambda _: None
mask_operations = []
canvas = Obj(save=lambda: 7, clipRect=lambda *args: mask_operations.append(("clip", *args)),
             saveLayerAlpha=lambda *args: mask_operations.append(("layer", *args)),
             translate=lambda *args: mask_operations.append(("translation", *args)),
             drawRoundRect=lambda *args: None,
             drawRect=lambda *args: mask_operations.append(("paint", *args[:-1])),
             restoreToCount=lambda depth: mask_operations.append(("restore", depth)))
mount_queue = []
mount_namespace = video.VideoSeekbarGestureInsets.prepare_thumbnail_rail.__globals__
mount_runner = mount_namespace["run_on_ui_thread"]
mount_namespace["run_on_ui_thread"] = lambda callback, delay=0: mount_queue.append(callback)
try:
    rail_plugin.prepare_thumbnail_rail(gallery_viewer, gallery_container, 360, 800, True)
    first_rail = rail_plugin.thumbnail_rail
    assert first_rail.entries[0][1] is strict_current and first_rail.center_pending
    assert first_rail.ready and native_strip.getVisibility() == 8
    first_rail.top, first_rail.height = 20, 400
    rail_plugin.layout_thumbnail_rail(gallery_viewer, gallery_container)
    mount_queue.pop()()
    rail_plugin.draw_thumbnail_rail(Obj(thisObject=gallery_container, args=[canvas]))
    assert first_rail.center == 200 and first_rail.position == -141
    assert receiver_draws[0] == (266, 167, 88, 106) and first_rail.ready
    rail_plugin.thumbnail_seed = video.ThumbnailSeed(gallery_viewer, strict_current, (strict_neighbor, strict_current), {})
    rail_plugin.searching_album.getBoolean = lambda _: True
    rail_plugin.prepare_thumbnail_rail(gallery_viewer, gallery_container, 360, 800, True)
    assert first_rail.provisional and first_rail.entries[0][1] is strict_neighbor
    assert rail_plugin.reveal_thumbnail_window(first_rail)
    assert first_rail.cells == {2: thumb_receiver}
    rail_plugin.thumbnail_seed = None
    rail_plugin.searching_album.getBoolean = lambda _: False
    # The native index can still refer to the previous ordering after a prepend.
    gallery_viewer.index = 0
    rail_plugin.album_messages = value_field(native_list([strict_neighbor, strict_current]))
    rail_plugin.prepare_thumbnail_rail(gallery_viewer, gallery_container, 360, 800, True)
    assert rail_plugin.thumbnail_rail is first_rail
    assert first_rail.entries[1][1] is video.THUMBNAIL_MESSAGE_DIVIDER
    assert first_rail.entries[2][1] is strict_current and first_rail.pending_offset is not None
    assert first_rail.cells == {2: thumb_receiver} and not detached_thumbnails
    rail_plugin.layout_thumbnail_rail(gallery_viewer, gallery_container)
    assert first_rail.top + first_rail.offsets[2] - first_rail.position + first_rail.tile_height // 2 == 220

    new_chat_item = JavaThumbnailMessage(**vars(other_chat))
    gallery_viewer.current, gallery_viewer.index, gallery_viewer.primary = new_chat_item, 0, -101
    rail_plugin.prepare_thumbnail_rail(gallery_viewer, gallery_container, 360, 800, True)
    assert first_rail.source[1] == 0 and first_rail.entries == [(6, new_chat_item)]
    assert not first_rail.cells and detached_thumbnails == ["detached"]
    rail_plugin.album_messages = value_field(native_list([new_chat_item, strict_current]))
    rail_plugin.prepare_thumbnail_rail(gallery_viewer, gallery_container, 360, 800, True)
    assert first_rail.entries == [(6, new_chat_item)]
    gallery_viewer.merged = -100
    rail_plugin.prepare_thumbnail_rail(gallery_viewer, gallery_container, 360, 800, True)
    assert first_rail.entries[1][1] is video.THUMBNAIL_CHAT_DIVIDER and first_rail.entries[2][1] is strict_current
finally:
    mount_namespace["run_on_ui_thread"] = mount_runner

state_descriptions = []
gallery_container.postOnAnimation = lambda _: None
state_rail = video.ThumbnailRail(gallery_viewer, None, gallery_container, (84, 102))
state_rail.handle = Obj(setContentDescription=state_descriptions.append)
rail_plugin.restore_thumbnail_collapse(state_rail, strict_current)
assert not state_rail.collapsed
rail_plugin.set_thumbnail_collapsed(state_rail, True)
assert rail_storage[state_rail.collapse_key] is True
rail_plugin.restore_thumbnail_collapse(state_rail, new_chat_item)
assert not state_rail.collapsed
rail_plugin.restore_thumbnail_collapse(state_rail, strict_current)
assert state_rail.collapsed and state_rail.slide == 1 and state_rail.slide_motion is None
assert state_descriptions[-1] == "展开缩略图，左右拖动可调宽度"
other_account_item = JavaThumbnailMessage(**vars(strict_current))
other_account_item.currentAccount += 1
rail_plugin.restore_thumbnail_collapse(state_rail, other_account_item)
assert state_rail.collapsed
closed_mounts = []
mount_namespace["run_on_ui_thread"] = lambda callback, delay=0: callback()
try:
    state_rail.handle = None
    rail_plugin.thumbnail_rail = state_rail
    rail_plugin.install_thumbnail_handle = lambda rail: (
        closed_mounts.append("handle"), setattr(rail, "handle", Obj(setContentDescription=state_descriptions.append)))
    rail_plugin.render_thumbnail_window = lambda _: closed_mounts.append("tiles")
    rail_plugin.schedule_thumbnail_window(state_rail)
    rail_plugin.schedule_thumbnail_window(state_rail)
    assert closed_mounts == ["handle"]
    rail_plugin.set_thumbnail_collapsed(state_rail, False)
    assert closed_mounts == ["handle", "tiles"] and rail_storage[state_rail.collapse_key] is False
finally:
    rail_plugin.thumbnail_rail = first_rail
    rail_plugin.install_thumbnail_handle = lambda _: None
    del rail_plugin.render_thumbnail_window
    mount_namespace["run_on_ui_thread"] = mount_runner
rail_storage["thumbnail_state_scope"] = video.THUMBNAIL_STATE_GLOBAL
rail_plugin.configure_thumbnail_state()
rail_plugin.restore_thumbnail_collapse(state_rail, strict_current)
assert state_rail.collapsed
rail_plugin.set_thumbnail_collapsed(state_rail, False)
rail_plugin.restore_thumbnail_collapse(state_rail, new_chat_item)
assert not state_rail.collapsed and rail_storage["thumbnail_rail_collapsed"] is False
rail_storage["thumbnail_state_scope"] = video.THUMBNAIL_STATE_CHAT
rail_plugin.configure_thumbnail_state()
rail_plugin.restore_thumbnail_collapse(state_rail, new_chat_item)
assert not state_rail.collapsed
gallery_viewer.current = JavaThumbnailMessage(**vars(thumbnail_message(-102)))
rail_plugin.restore_thumbnail_collapse(first_rail, gallery_viewer.current)
assert first_rail.collapsed
rail_storage["thumbnail_default_state"] = video.THUMBNAIL_START_EXPANDED
rail_plugin.configure_thumbnail_state()
assert not first_rail.collapsed and first_rail.slide == 0
rail_plugin.restore_thumbnail_collapse(first_rail, strict_current)
assert first_rail.collapsed
gallery_viewer.current = new_chat_item
rail_plugin.restore_thumbnail_collapse(first_rail, new_chat_item)

drawer = Obj(getPaddingLeft=lambda: 0, getPaddingRight=lambda: 16, getPaddingBottom=lambda: 0, getMeasuredHeight=lambda: 800,
             postOnAnimation=lambda _: None,
             getRootWindowInsets=lambda: Obj(getStableInsetRight=lambda: 22,
                                             getStableInsetTop=lambda: 16, getStableInsetBottom=lambda: 8,
                                             getInsetsIgnoringVisibility=lambda _: Obj(top=36)))
rail_plugin.sdk, rail_plugin.status_type = 30, 1
control_frame, bar_frame = Obj(rightMargin=0), Obj(rightMargin=4)
rail_plugin.controls = value_field(Obj(getParent=lambda: drawer, getLayoutParams=lambda: control_frame))
rail_plugin.action_bar = value_field(Obj(getParent=lambda: drawer, getLayoutParams=lambda: bar_frame))
rail_plugin.window = value_field(None)
rail_plugin.compact_control = lambda _: Obj(getVisibility=lambda: 0)
vertical_rail = video.ThumbnailRail(gallery_viewer, None, drawer, (88, 66))
vertical_rail.landscape = True
rail_plugin.measure_thumbnail_side_insets(gallery_viewer, drawer, vertical_rail, 650, 400)
assert (vertical_rail.top, vertical_rail.height, vertical_rail.left) == (0, 400, 534)
assert vertical_rail.status_height == 36
assert vertical_rail.right_reservation == 116
assert (bar_frame.rightMargin, control_frame.rightMargin) == (120, 116)
rail_plugin.measure_thumbnail_side_insets(gallery_viewer, drawer, vertical_rail, 650, 400)
assert (bar_frame.rightMargin, control_frame.rightMargin) == (120, 116)
for width, reservation in ((100, 128), (61, 89)):
    vertical_rail.drag_width = width
    rail_plugin.measure_thumbnail_side_insets(gallery_viewer, drawer, vertical_rail, 650, 400)
    assert vertical_rail.right_reservation == reservation
    assert (bar_frame.rightMargin, control_frame.rightMargin) == (4 + reservation, reservation)
vertical_rail.drag_width = None
vertical_rail.collapsed, vertical_rail.slide, vertical_rail.slide_motion = False, 1.0, (1.0, 0.0, 1.0)
rail_plugin.schedule_thumbnail_window = lambda _: None
rail_namespace = rail_plugin.measure_thumbnail_side_insets.__globals__
rail_clock = rail_namespace["monotonic"]
slide_frames = []
drawer.postOnAnimation = slide_frames.append
drawer.requestLayout = lambda: None
rail_plugin.thumbnail_rail = vertical_rail
rail_plugin.animate_thumbnail_slide(vertical_rail, vertical_rail.slide_motion)
try:
    for now, reservation in ((1.0, 30), (1.13, 72), (1.27, 116)):
        rail_namespace["monotonic"] = lambda: now
        slide_frames.pop(0)()
        rail_plugin.measure_thumbnail_side_insets(gallery_viewer, drawer, vertical_rail, 650, 400)
        assert (bar_frame.rightMargin, control_frame.rightMargin) == (4 + reservation, reservation)
        assert rail_plugin.caption_thumbnail_width(vertical_rail) == 88
finally:
    rail_namespace["monotonic"] = rail_clock
    drawer.postOnAnimation = lambda _: None
vertical_rail.landscape = False
vertical_rail.drag_width = 100
rail_plugin.measure_thumbnail_side_insets(gallery_viewer, drawer, vertical_rail, 360, 720)
assert (bar_frame.rightMargin, control_frame.rightMargin) == (4, 0)
vertical_rail.drag_width = 61
rail_plugin.measure_thumbnail_side_insets(gallery_viewer, drawer, vertical_rail, 360, 720)
assert (bar_frame.rightMargin, control_frame.rightMargin) == (4, 0)
vertical_rail.set_right_reservation((), 0)

portrait_rail = rail_plugin.thumbnail_rail = video.ThumbnailRail(gallery_viewer, None, drawer, (88, 106))
portrait_rail.safe_top, portrait_rail.safe_bottom = 24, 20
rail_plugin.action_bar.get(gallery_viewer).getMeasuredHeight = lambda: 64
control = rail_plugin.controls.get(gallery_viewer)
control.getVisibility, control.getMeasuredHeight = lambda: 0, lambda: 72
control_frame.bottomMargin = 110
rail_plugin.background = value_field(None)
rail_plugin.photo_surface = lambda _: False
rail_plugin.measure_thumbnail_rail_height(gallery_viewer, drawer)
assert (portrait_rail.top, portrait_rail.height) == (190, 420)
control_frame.bottomMargin = 122
rail_plugin.measure_thumbnail_rail_height(gallery_viewer, drawer)
assert (portrait_rail.top, portrait_rail.height) == (202, 396)
rail_plugin.photo_surface = lambda _: True
rail_plugin.measure_thumbnail_rail_height(gallery_viewer, drawer)
assert (portrait_rail.top, portrait_rail.height) == (68, 712)
assert portrait_rail.top + portrait_rail.height == 800 - portrait_rail.safe_bottom
rail_plugin.photo_surface = lambda _: False
rail_plugin.measure_thumbnail_rail_height(gallery_viewer, drawer)

mask_operations.clear()
portrait_rail.left, portrait_rail.alpha = 260, 1.0
portrait_rail.scroller = rail_plugin.thumbnail_scroller(None)
portrait_rail.entries, portrait_rail.offsets, portrait_rail.cells = [(130, first_pic)], [130], {0: thumb_receiver}
rail_plugin.thumbnail_fade = None
rail_plugin.positions = rail_plugin.thumbnail_fade_positions = list
rail_plugin.thumbnail_clamp = object()
rail_plugin.thumbnail_gradient = lambda *args: (args[3], args[4])
rail_plugin.thumbnail_mask = Obj(setShader=lambda span: mask_operations.append(("gradient", span)))
rail_plugin.draw_thumbnail_rail(Obj(thisObject=drawer, args=[canvas]))
assert mask_operations[0:2] == [("clip", 260, 202, 348, 598), ("layer", 260, 202, 348, 598, 255)]
assert mask_operations[-3:] == [("translation", 0, 202), ("paint", 260, 0, 348, 396), ("restore", 7)]
portrait_rail.extent, portrait_rail.position = 900, 10
mask_operations.clear()
rail_plugin.draw_thumbnail_rail(Obj(thisObject=drawer, args=[canvas]))
assert rail_plugin.thumbnail_fade == (False, 396, 32)
portrait_rail.landscape, portrait_rail.status_height = True, 36
rail_plugin.measure_thumbnail_rail_height(gallery_viewer, drawer)
assert (portrait_rail.top, portrait_rail.height) == (0, 800)
rail_plugin.draw_thumbnail_rail(Obj(thisObject=drawer, args=[canvas]))
assert rail_plugin.thumbnail_fade == (False, 800, 36)
portrait_rail.landscape = False
portrait_rail.bottom_docked = True
portrait_rail.span, portrait_rail.left, portrait_rail.position = 360, 0, 0
portrait_rail.tile_width = portrait_rail.tile_height = 64
rail_plugin.measure_thumbnail_rail_height(gallery_viewer, drawer)
assert (portrait_rail.top, portrait_rail.height) == (710, 70)
assert (portrait_rail.tile_length, portrait_rail.viewport) == (64, 360)
assert rail_plugin.caption_thumbnail_width(portrait_rail) == 0
mask_operations.clear()
rail_plugin.draw_thumbnail_rail(Obj(thisObject=drawer, args=[canvas]))
assert mask_operations[:2] == [("clip", 0, 710, 360, 780), ("layer", 0, 710, 360, 780, 255)]
assert mask_operations[-3:] == [("translation", 0, 0), ("paint", 0, 710, 360, 780), ("restore", 7)]
assert rail_plugin.thumbnail_fade == (True, 360, 32)
portrait_rail.collapsed = True
portrait_rail.slide = 1
mask_operations.clear()
rail_plugin.draw_thumbnail_rail(Obj(thisObject=drawer, args=[canvas]))
assert not mask_operations
portrait_rail.bottom_docked, portrait_rail.collapsed, portrait_rail.slide = False, False, 0
portrait_rail.left, portrait_rail.tile_width, portrait_rail.tile_height = 260, 88, 106
rail_plugin.measure_thumbnail_rail_height(gallery_viewer, drawer)

samples = video.PLAYER_SHADOW_BAND_SAMPLES
pixels = video.player_shadow_texture(samples)
combined_alpha = [(color >> 24) & 255 for color in pixels]
strength = video.PLAYER_SHADOW_ALPHA
assert strength == 224
assert len(combined_alpha) == 3 * samples
top, bottom = combined_alpha[:samples], combined_alpha[2 * samples:][::-1]
assert top[0] == bottom[0] == strength and top[-1] == bottom[-1] == 0
assert top == bottom == sorted(top, reverse=True)
assert bottom[3 * samples // 4] == round(
    strength * video.player_shadow_edge_alpha(((3 * samples // 4 + 0.5) / samples) ** 2.4)
)
assert combined_alpha[samples:2 * samples] == [0] * samples
for width, height in ((360, 780), (680, 330), (900, 480)):
    geometry = video.player_shadow_mesh(width, height, 96, 72)
    assert geometry[::2] == (0, width) * 4
    assert geometry[1::2] == (0, 0, 96, 96, height - 72, height - 72, height, height)
assert video.player_shadow_mesh(360, 150, 120, 80)[1::2] == (0, 0, 90, 90, 90, 90, 150, 150)
assert video.player_shadow_edge_alpha(0.99) < 0.001 and video.player_shadow_edge_alpha(1) == 0

shadow_plugin = video.VideoSeekbarGestureInsets()
backdrop = []
header_view = Obj(getAlpha=lambda: 0.8, getHeight=lambda: 156, getY=lambda: 0,
                  getScaleY=lambda: 1.0, getPivotY=lambda: 0, getVisibility=lambda: 0)
footer_view = Obj(getAlpha=lambda: 0.8, getHeight=lambda: 140, getY=lambda: 660,
                  getScaleY=lambda: 1.1, getPivotY=lambda: 140, getVisibility=lambda: 0)
shadow_drawer = Obj(getWidth=lambda: 360, getHeight=lambda: 800)
shadow_bar = Obj(alpha=0.8)
shadow_bar.getAlpha = lambda: shadow_bar.alpha
shadow_plugin.action_bar, shadow_plugin.background = value_field(shadow_bar), value_field(None)
shadow_plugin.photo_surface = lambda _: False
shadow_plugin.footer_shade = lambda _: footer_view
shadow_plugin.caption_exit, shadow_plugin.shadows = None, []
shadow_plugin.dp, shadow_plugin.positions = int, list
shadow_plugin.bitmap_config = object()
shadow_plugin.bitmap = Obj(createBitmap=lambda pixels, width, height, _: backdrop.append(
    ("build", len(pixels), width, height)) or object())
shadow_plugin.player_shadow_bitmap, shadow_plugin.player_shadow_geometry = None, None
shadow_plugin.thumbnail_fade_positions = tuple
shadow_plugin.player_shadow_paint = Obj(setAlpha=lambda a: backdrop.append(("alpha", a)))
shadow_canvas = Obj(drawBitmapMesh=lambda bitmap, x, y, vertices, *args: backdrop.append((x, y, vertices)))
shadow_rail = video.ThumbnailRail(viewer, None, shadow_drawer, (88, 100))
shadow_rail.left, shadow_rail.top, shadow_rail.height, shadow_rail.ready = 266, 42, 718, True
shadow_plugin.draw_player_shadows(shadow_canvas, viewer, shadow_drawer, header_view, shadow_rail)
geometry = video.player_shadow_mesh(360, 800, 156, 154)
assert backdrop == [("build", 3 * samples, 1, 3 * samples), ("alpha", 204), (1, 3, geometry)]
texture = shadow_plugin.player_shadow_bitmap
backdrop.clear()
shadow_bar.alpha = 0.4
shadow_rail.slide = 0.5
shadow_plugin.draw_player_shadows(shadow_canvas, viewer, shadow_drawer, header_view, shadow_rail)
assert backdrop == [("alpha", 102), (1, 3, geometry)]
backdrop.clear()
shadow_rail.drag_width = 122
shadow_plugin.draw_player_shadows(shadow_canvas, viewer, shadow_drawer, header_view, shadow_rail)
assert backdrop == [("alpha", 102), (1, 3, geometry)]
shadow_rail.slide = 1.0
shadow_rail.drag_width = None
shadow_plugin.draw_player_shadows(shadow_canvas, viewer, shadow_drawer, header_view, shadow_rail)
assert shadow_plugin.player_shadow_bitmap is texture and shadow_plugin.player_shadow_geometry == (360, 800, 156, 154)
shadow_plugin.photo_surface = lambda _: True
shadow_rail.slide = 0.0
shadow_plugin.draw_player_shadows(shadow_canvas, viewer, shadow_drawer, header_view, shadow_rail)
assert shadow_plugin.player_shadow_geometry == (360, 800, 156, 0)
backdrop.clear()
shadow_plugin.draw_player_shadows(shadow_canvas, viewer, shadow_drawer, None, shadow_rail)
assert not backdrop  # A visible thumbnail rail is not a source of shade.

divider_draws = []
receiver_draws.clear()
canvas.drawRoundRect = lambda left, top, right, bottom, *_: divider_draws.append((left, top, right, bottom))
spacing, message_gap, _ = video.thumbnail_gaps(portrait_rail.tile_width)
divider_offset = 6 + portrait_rail.tile_height + spacing
portrait_rail.entries = [(6, first_pic), (divider_offset, video.THUMBNAIL_MESSAGE_DIVIDER),
                         (divider_offset + message_gap, another_message)]
portrait_rail.offsets = [offset for offset, _ in portrait_rail.entries]
portrait_rail.cells = {0: thumb_receiver, 1: None, 2: thumb_receiver}
portrait_rail.position = 0
rail_plugin.draw_thumbnail_rail(Obj(thisObject=drawer, args=[canvas]))
first, second = receiver_draws
divider, = divider_draws
assert (divider[0] + divider[2]) / 2 == first[0] + first[2] / 2
assert (divider[1] + divider[3]) / 2 == (first[1] + first[3] + second[1]) / 2
portrait_rail.selected = first_pic
divider_draws.clear()
receiver_draws.clear()
rail_plugin.thumbnail_outline = Obj(setStrokeWidth=lambda _: None)
rail_plugin.draw_thumbnail_rail(Obj(thisObject=drawer, args=[canvas]))
assert tuple(receiver_draws) == (first, second)
outline = next(box for box in divider_draws if box[1] < divider[1])
assert outline == (first[0] + 1, first[1] + 1, first[0] + first[2] - 1, first[1] + first[3] - 1)
portrait_rail.selected = None
assert video.thumbnail_gaps(176) == tuple(2 * gap for gap in video.thumbnail_gaps(88))

auto_hide = []
native_runnable = object()
rail_plugin.android = Obj(cancelRunOnUIThread=lambda runnable: auto_hide.append(("cancel", runnable)))
rail_plugin.auto_hide_controls = value_field(native_runnable)
rail_plugin.call = lambda _, name: auto_hide.append(name)
rail_plugin.view_origin = lambda *_: (0, 0)
drawer.invalidate = drawer.postInvalidateOnAnimation = lambda: None
portrait_rail.scroller = Obj(forceFinished=lambda _: None, fling=lambda *args: auto_hide.append("fling"),
                            computeScrollOffset=lambda: False, isFinished=lambda: True)
event = Obj(event_time=100, y=450, getX=lambda: 300, getPointerCount=lambda: 1)
event.getEventTime, event.getY = lambda: event.event_time, lambda: event.y
hold = Obj(thisObject=gallery_viewer, setResult=lambda _: auto_hide.append("held"))
assert rail_plugin.route_thumbnail_touch(gallery_viewer, drawer, event, 0)
rail_plugin.hold_thumbnail_controls(hold)
event.event_time, event.y = 4400, 390
assert rail_plugin.route_thumbnail_touch(gallery_viewer, drawer, event, 2)
event.event_time, event.y = 4450, 355
assert rail_plugin.route_thumbnail_touch(gallery_viewer, drawer, event, 2)
assert rail_plugin.route_thumbnail_touch(gallery_viewer, drawer, event, 1)
rail_plugin.hold_thumbnail_controls(hold)
assert auto_hide == [("cancel", native_runnable), "held", "fling", "held"]
rail_plugin.draw_thumbnail_rail(Obj(thisObject=drawer, args=[canvas]))
rail_plugin.hold_thumbnail_controls(hold)
assert auto_hide[-1] == "scheduleActionBarHide" and not portrait_rail.flinging

saved_sizes = []
rail_plugin.set_setting = lambda key, value: (rail_storage.__setitem__(key, value), saved_sizes.append((key, value)))
rail_plugin.maximum_thumbnail_width = lambda _: 146
rail_plugin.schedule_thumbnail_window = lambda _: None
drawer.requestLayout = lambda: None
handle = portrait_rail.handle = Obj(getVisibility=lambda: 0, getX=lambda: 215, getWidth=lambda: 44,
                                    getY=lambda: 290, getHeight=lambda: 44, setPressed=lambda _: None,
                                    setContentDescription=lambda _: None)
handle.performClick = lambda: rail_plugin.set_thumbnail_collapsed(portrait_rail, not portrait_rail.collapsed)
assert rail_plugin.route_thumbnail_handle(portrait_rail, 0, 240, 310)
assert rail_plugin.route_thumbnail_handle(portrait_rail, 2, 220, 310)
assert rail_plugin.visible_thumbnail_width(portrait_rail) == 108
assert rail_plugin.route_thumbnail_handle(portrait_rail, 1, 220, 310)
assert saved_sizes == [("thumbnail_width_portrait_dp", 108)] and not portrait_rail.collapsed
assert rail_plugin.thumbnail_widths_dp == (108, 88)
assert rail_plugin.route_thumbnail_handle(portrait_rail, 0, 240, 310)
assert rail_plugin.route_thumbnail_handle(portrait_rail, 1, 240, 310)
assert portrait_rail.collapsed

# The portrait bottom mode routes taps and swipes along X while leaving the player layout intact.
bottom_rail = rail_plugin.thumbnail_rail = video.ThumbnailRail(gallery_viewer, None, drawer, (64, 64))
bottom_rail.bottom_docked, bottom_rail.alpha = True, 1.0
bottom_rail.span, bottom_rail.top, bottom_rail.height, bottom_rail.center = 360, 710, 70, 180
bottom_rail.offsets = [6, 75, 144, 213, 282, 351, 420]
bottom_rail.entries = [(offset, first_pic if index == 0 else same_album)
                       for index, offset in enumerate(bottom_rail.offsets)]
bottom_rail.cells, bottom_rail.extent = {0: thumb_receiver}, 490
bottom_rail.scroller = portrait_rail.scroller
chosen = []
rail_plugin.open_thumbnail = lambda rail, item: chosen.append((rail, item))
event.x, event.y = 16, 734
event.getX = lambda: event.x
assert rail_plugin.route_thumbnail_touch(gallery_viewer, drawer, event, 0)
assert rail_plugin.route_thumbnail_touch(gallery_viewer, drawer, event, 1)
assert chosen == [(bottom_rail, first_pic)]
event.x = 185
assert rail_plugin.route_thumbnail_touch(gallery_viewer, drawer, event, 0)
event.event_time, event.x = 4500, 110
assert rail_plugin.route_thumbnail_touch(gallery_viewer, drawer, event, 2)
assert bottom_rail.position == 75 and bottom_rail.scroll_direction == 1
assert rail_plugin.route_thumbnail_touch(gallery_viewer, drawer, event, 3)
event.y = 700
assert not rail_plugin.route_thumbnail_touch(gallery_viewer, drawer, event, 0)

bottom_rail.ready, bottom_rail.safe_bottom = True, 20
drawer.getHeight = lambda: 800
handle_position = Obj(x=0, y=0)
bottom_rail.handle = Obj(getVisibility=lambda: 0,
    getX=lambda: handle_position.x, getY=lambda: handle_position.y,
    getWidth=lambda: 44, getHeight=lambda: 24, getMeasuredWidth=lambda: 44, getMeasuredHeight=lambda: 24,
    setX=lambda x: setattr(handle_position, "x", x), setY=lambda y: setattr(handle_position, "y", y),
    setAlpha=lambda _: None, setPressed=lambda _: None)
bottom_rail.handle_icon = Obj(setRotation=lambda _: None,
    setTranslationX=lambda x: setattr(handle_position, "icon_x", x),
    setTranslationY=lambda y: setattr(handle_position, "icon_y", y))
rail_plugin.sync_thumbnail_handle(bottom_rail)
assert (handle_position.x, handle_position.y, handle_position.icon_x, handle_position.icon_y) == (158, 679, 0, 0)
bottom_rail.collapsed, bottom_rail.slide = True, 1.0
rail_plugin.sync_thumbnail_handle(bottom_rail)
assert (handle_position.x, handle_position.y, handle_position.icon_x, handle_position.icon_y) == (158, 756, 0, 7)
bottom_rail.collapsed, bottom_rail.slide = False, 0.0
rail_plugin.sync_thumbnail_handle(bottom_rail)

side_rail = video.ThumbnailRail(gallery_viewer, None, drawer, (88, 88))
side_rail.left, side_rail.height, side_rail.center = 266, 600, 300
side_rail.ready, side_rail.alpha = True, 1.0
side_rail.handle, side_rail.handle_icon = bottom_rail.handle, bottom_rail.handle_icon
side_rail.collapsed, side_rail.slide = True, 1.0
rail_plugin.sync_thumbnail_handle(side_rail)
assert (handle_position.x, handle_position.icon_x, handle_position.icon_y) == (314, 7, 0)
side_rail.collapsed, side_rail.slide = False, 0.0
rail_plugin.sync_thumbnail_handle(side_rail)
assert (handle_position.x, handle_position.icon_x, handle_position.icon_y) == (220, 0, 0)
rail_plugin.sync_thumbnail_handle(bottom_rail)
assert rail_plugin.maximum_thumbnail_bottom_height(320, 640) == 106
assert rail_plugin.maximum_thumbnail_bottom_height(420, 920) == 128
rail_plugin.video_surface = lambda _: True
assert rail_plugin.dock_album_strip(gallery_viewer, None, drawer, None) == 114
assert rail_plugin.route_thumbnail_handle(bottom_rail, 0, 180, 690)
assert rail_plugin.route_thumbnail_handle(bottom_rail, 2, 180, 660)
assert bottom_rail.drag_height == 94 and rail_plugin.thumbnail_bottom_top(bottom_rail) == 680
assert rail_plugin.thumbnail_draw_scale(bottom_rail) == 94 / 64
assert rail_plugin.dock_album_strip(gallery_viewer, None, drawer, None) == 144
assert rail_plugin.route_thumbnail_handle(bottom_rail, 1, 180, 660)
assert bottom_rail.drag_height is None and not bottom_rail.collapsed
assert saved_sizes[-1] == ("thumbnail_height_portrait_dp", 94)
rail_plugin.configure_thumbnail_state()
assert rail_plugin.thumbnail_bottom_height_dp == 94

# The native formula keeps scaling around the fingers while their midpoint moves.
pinch_plugin = video.VideoSeekbarGestureInsets()
pinch_plugin.option = lambda key: key == "pinch"
pinch_plugin.video_surface = lambda _: True
pinch_plugin.touch_stack = []
can_zoom = Obj(value=False)
pinch_plugin.can_zoom = Obj(getBoolean=lambda _: can_zoom.value,
                            setBoolean=lambda _, value: setattr(can_zoom, "value", value))
pinch_plugin.zooming = Obj(getBoolean=lambda _: True)
pinch_plugin.pinch_blockers = ()
pinch_plugin.viewer_animation = Obj(getInt=lambda _: 0)
pinch_plugin.scale_animation_time = Obj(getLong=lambda _: 0)
pinch_plugin.refresh_zoom = lambda _: None
anchors = {"center_x": 100.0, "center_y": 180.0, "start_x": 10.0, "start_y": 20.0}


def pinch_field(name):
    return Obj(getFloat=lambda _: anchors[name], setFloat=lambda _, value: anchors.__setitem__(name, value))


pinch_plugin.pinch_anchors = tuple((pinch_field("center_" + axis), pinch_field("start_" + axis)) for axis in ("x", "y"))
pinch_event = Obj(getPointerCount=lambda: 2, getActionMasked=lambda: 2,
                  getX=lambda index: (80.0, 160.0)[index], getY=lambda index: (130.0, 190.0)[index])
pinch_param = Obj(thisObject=gallery_viewer, args=[pinch_event])
pinch_plugin.before_touch(pinch_param)
assert can_zoom.value
assert anchors == {"center_x": 120.0, "center_y": 160.0, "start_x": 30.0, "start_y": 0.0}
pinch_plugin.after_touch(pinch_param)
assert not can_zoom.value
pinch_event.getX = lambda index: (100.0, 180.0)[index]
pinch_plugin.before_touch(pinch_param)
pinch_plugin.after_touch(pinch_param)
assert (anchors["center_x"], anchors["start_x"]) == (140.0, 50.0)

retry_queue = []
retry_plugin = video.VideoSeekbarGestureInsets()
retry_plugin.active = True
retry_plugin.thumbnail_log = Obj(w=lambda *_: None)
retry_plugin.remove_thumbnail_rail = lambda _: None
retry_container = Obj(isAttachedToWindow=lambda: True, requestLayout=lambda: retry_queue.append("layout"))
retry_namespace = video.VideoSeekbarGestureInsets.fail_thumbnail_rail.__globals__
retry_runner = retry_namespace["run_on_ui_thread"]
retry_namespace["run_on_ui_thread"] = lambda callback, delay=0: retry_queue.append((callback, delay))
try:
    retry_plugin.fail_thumbnail_rail(gallery_viewer, retry_container, RuntimeError("temporary"))
    retry, delay = retry_queue.pop()
    assert delay == 96
    retry()
    assert retry_queue == ["layout"]
    retry_plugin.fail_thumbnail_rail(gallery_viewer, retry_container, RuntimeError("again"))
    retry, delay = retry_queue.pop()
    assert delay == 266
    retry_plugin.thumbnail_failure = None
    retry()
    assert retry_queue == ["layout"]
finally:
    retry_namespace["run_on_ui_thread"] = retry_runner

landscape = video.VideoSeekbarGestureInsets()
landscape.landscape_header = None
landscape.header_buttons = None
landscape.status_slide = None
landscape.sdk, landscape.status_type, landscape.dp = 34, 1, int
status_layouts = []
status_events = []
landscape_viewer = Obj(getParentActivity=lambda: None)
landscape_bar = Obj()
landscape_drawer = Obj(flags=0x704, clip=True, getSystemUiVisibility=lambda: landscape_drawer.flags,
                       getRootWindowInsets=lambda: None,
                       setSystemUiVisibility=lambda value: setattr(landscape_drawer, "flags", value),
                       getClipToPadding=lambda: landscape_drawer.clip,
                       setClipToPadding=lambda value: setattr(landscape_drawer, "clip", value),
                       requestLayout=lambda: status_layouts.append("layout"), invalidate=lambda: None,
                       isAttachedToWindow=lambda: True, getPaddingLeft=lambda: 65, getPaddingRight=lambda: 0,
                       getWindowInsetsController=lambda: Obj(show=lambda mask: status_events.append(("show", mask)),
                                                             hide=lambda mask: status_events.append(("hide", mask))))
landscape.action_bar = value_field(landscape_bar)
landscape.option = landscape.video_surface = lambda _: True
landscape.viewer_container = value_field(landscape_drawer)
landscape.call = lambda *_: True
shown = Obj(value=True)
landscape.action_bar_visible = Obj(getBoolean=lambda _: shown.value)
edge_paint = Obj(filter="native", getColorFilter=lambda: edge_paint.filter,
                 setColorFilter=lambda value: setattr(edge_paint, "filter", value))
landscape.drawer_edge_paint = value_field(edge_paint)
landscape.clear_edge_paint = "clear"
landscape.set_landscape_header(landscape_viewer, landscape_drawer, True)
assert landscape_drawer.flags == 0x704 and edge_paint.filter == "clear" and status_events == [("show", 1)]
assert not landscape_drawer.clip
shown.value = False
landscape_drawer.flags = 0x701
landscape.sync_media_status_bar(landscape_viewer)
assert landscape_drawer.flags == 0x701 and status_events[-1] == ("hide", 1)
landscape_drawer.getWidth = lambda: 1280
landscape_bar.left = 65
landscape_bar.getLeft = lambda: landscape_bar.left
landscape_bar.getRight = lambda: landscape_bar.left + 1115
landscape_bar.getWidth = lambda: 1115


def header_control(left, width):
    item = Obj(left=left, translation=0.0, getVisibility=lambda: 0, getWidth=lambda: width)
    item.getLeft = lambda: item.left
    item.getX = lambda: item.left + item.translation
    item.getTranslationX = lambda: item.translation
    item.setTranslationX = lambda x: setattr(item, "translation", x)
    return item


back, header_menu = header_control(0, 54), header_control(1119, 96)
share, overflow = header_control(0, 48), header_control(48, 48)
share.getIconView = overflow.getIconView = lambda: header_control(12, 24)
header_menu.getChildCount = lambda: 2
header_menu.getChildAt = (share, overflow).__getitem__
landscape.header_menu, landscape.header_back = value_field(header_menu), value_field(back)
landscape.menu_item_type = Obj(isInstance=lambda _: True)
header_controls = Obj(getLeft=lambda: 65, getVisibility=lambda: 0)
header_seek = Obj(getParent=lambda: header_controls, getWidth=lambda: 1016,
                  getLeft=lambda: 67, getRight=lambda: 1083)
landscape.controls, landscape.video_seek_view = value_field(header_controls), value_field(header_seek)
header_play = header_control(65, 44)
header_fullscreen = header_control(1040, 44)
landscape.compact_control = lambda _: Obj(getVisibility=lambda: 0)
landscape.playback_control = lambda _: header_play
landscape.fullscreen_control = lambda _: header_fullscreen
for _ in range(2):
    landscape.align_header_buttons(landscape_viewer)
    assert (back.translation, header_menu.translation) == (60.0, -129.0)
landscape_bar.left, header_menu.left = 0, 1119
landscape_drawer.getPaddingLeft, landscape_drawer.getPaddingRight = lambda: 0, lambda: 65
landscape.controls = value_field(None)
landscape.align_header_buttons(landscape_viewer)
assert (back.translation, header_menu.translation) == (19.0, -122.0)
landscape.set_landscape_header(landscape_viewer, landscape_drawer, False)
assert edge_paint.filter == "native" and landscape_drawer.clip and status_layouts[-1] == "layout"
landscape_bar.getWidth = landscape_bar.getRight = lambda: 360
header_menu.left = 264
landscape.align_header_buttons(landscape_viewer)
assert (back.getX() + back.getWidth() / 2, header_menu.getX() + 72) == (22.0, 338.0)
landscape.restore_header_buttons(landscape_viewer)
assert (back.translation, header_menu.translation) == (0.0, 0.0)
shown.value = True
landscape.sync_media_status_bar(landscape_viewer)  # Portrait uses the same immediate control path.
assert landscape_drawer.flags == 0x701 and status_events[-1] == ("show", 1)
shown.value = False
landscape.sync_media_status_bar(landscape_viewer)
assert landscape_drawer.flags == 0x701 and status_events[-1] == ("hide", 1)

status_namespace = video.VideoSeekbarGestureInsets.before_status_toggle.__globals__
status_originals = {name: status_namespace[name] for name in ("jclass", "dynamic_proxy", "run_on_ui_thread")}
pending_status, requests, frames, completions, held_flags = [], [], [], [], []
status_namespace.update(jclass=lambda _: object, dynamic_proxy=lambda _: object,
                        run_on_ui_thread=lambda fn, delay=0: pending_status.append((fn, delay)))
try:
    landscape.status_animation_listener = landscape.make_status_animation_listener()
    landscape.status_end_listener = landscape.make_status_end_listener()
    landscape.status_cancel_signal = lambda: Obj(cancel=lambda: completions.append("cancel"))
    landscape.status_insets = Obj(of=lambda *edges: edges)
    native = Obj(animator=None)
    landscape.action_bar_animator = Obj(get=lambda _: native.animator)
    landscape.call = lambda _, name, *args: True if name == "isStatusBarVisible" else completions.append(args[0])
    landscape.boolean = bool
    landscape_bar.alpha = 1.0
    landscape_bar.getAlpha = lambda: landscape_bar.alpha
    landscape_drawer.getWindowInsetsController = lambda: Obj(
        controlWindowInsetsAnimation=lambda *args: requests.append(args),
        hide=lambda _: completions.append(False), show=lambda _: completions.append(True))
    landscape_drawer.getRootWindowInsets = lambda: Obj(isVisible=lambda _: True)

    def bar_animator():
        animator = Obj(paused=False, isStarted=lambda: True, getTotalDuration=lambda: 200)
        animator.isPaused = lambda: animator.paused
        animator.pause = lambda: setattr(animator, "paused", True)
        animator.resume = lambda: setattr(animator, "paused", False)
        animator.addListener = lambda listener: setattr(animator, "listener", listener)
        animator.removeListener = lambda _: setattr(animator, "listener", None)
        return animator

    native.animator = bar_animator()
    hide = Obj(thisObject=landscape_viewer, args=[False, True])
    landscape.before_status_toggle(hide)
    landscape.hold_status_flags(Obj(thisObject=landscape_viewer, args=[False], setResult=held_flags.append))
    landscape.after_status_toggle(hide)
    assert native.animator.paused and requests[0][:2] == (1, 200) and held_flags == [None]
    status_control = Obj(isReady=lambda: True, getHiddenStateInsets=lambda: Obj(left=0, top=0, right=0, bottom=0),
                         getShownStateInsets=lambda: Obj(left=0, top=24, right=0, bottom=0),
                         setInsetsAndAlpha=lambda *args: frames.append(args), finish=lambda visible: completions.append(visible))
    requests[0][-1].onReady(status_control, 1)
    assert not native.animator.paused and frames == [((0, 24, 0, 0), 1.0, 1.0)]
    landscape_bar.alpha = 0.5
    landscape.step_status_slide(landscape_drawer)
    assert frames[-1] == ((0, 12, 0, 0), 0.5, 0.5)

    previous = native.animator
    show = Obj(thisObject=landscape_viewer, args=[True, True])
    landscape.before_status_toggle(show)
    previous.listener.onAnimationEnd(previous)
    native.animator = bar_animator()
    shown.value = True
    landscape.after_status_toggle(show)
    assert len(requests) == 1 and not native.animator.paused and not completions
    landscape_bar.alpha = 0.75
    landscape.step_status_slide(landscape_drawer)
    assert frames[-1] == ((0, 18, 0, 0), 0.75, 0.75)
    native.animator.listener.onAnimationEnd(native.animator)
    assert completions == [True] and landscape.status_slide is None
    pending_status.pop()[0]()  # A stale timeout cannot change the committed state.
    assert completions == [True]

    shown.value, native.animator = False, bar_animator()
    landscape.before_status_toggle(hide)
    landscape.after_status_toggle(hide)
    assert native.animator.paused
    timeout, delay = pending_status.pop()
    assert delay == 120
    timeout()
    assert not native.animator.paused and completions[-2:] == ["cancel", False]
    assert landscape.status_slide is None

    landscape_bar.alpha, native.animator = 1.0, bar_animator()
    landscape.before_status_toggle(hide)
    landscape.after_status_toggle(hide)
    requests[-1][-1].onReady(status_control, 1)
    landscape_bar.alpha = 0.0
    landscape.step_status_slide(landscape_drawer)
    assert frames[-1] == ((0, 0, 0, 0), 0.0, 0.0)
    native.animator.listener.onAnimationEnd(native.animator)
    assert completions == [True, "cancel", False, False] and landscape.status_slide is None
finally:
    status_namespace.update(status_originals)

menu_geometry = video.VideoSeekbarGestureInsets()
menu_geometry.active, menu_geometry.dp, menu_geometry.positions = True, int, list
menu_geometry.native_popup_menu = None
menu_geometry.style_popup_color = lambda _: None
menu_geometry.rect = lambda: Obj(left=0, top=0, right=1280, bottom=582)
menu_geometry.measure_spec = Obj(EXACTLY=1, AT_MOST=2, UNSPECIFIED=0, makeMeasureSpec=lambda size, mode: size)
menu_geometry.action_bar_visible = Obj(getBoolean=lambda _: True)
popup_drawer = Obj(getWidth=lambda: 1280, getHeight=lambda: 582,
                   getPaddingLeft=lambda: 65, getPaddingRight=lambda: 0,
                   getPaddingTop=lambda: 0, getPaddingBottom=lambda: 0,
                   getLocationOnScreen=lambda _: None,
                   getRootWindowInsets=lambda: Obj(getStableInsetTop=lambda: 24))
menu_geometry.landscape_header = (landscape_viewer, popup_drawer)
popup_calls = []


def popup_anchor(x, y):
    return Obj(isAttachedToWindow=lambda: True, getWidth=lambda: 44, getHeight=lambda: 44,
               getLocationOnScreen=lambda location: location.__setitem__(slice(None), [x, y]),
               getWindowVisibleDisplayFrame=lambda _: None)


def text_menu_rows(label_width):
    text = Obj(getText=lambda: "一项", getPaint=lambda: None, getCompoundPaddingLeft=lambda: 30,
               getCompoundPaddingRight=lambda: 0, getLayoutParams=lambda: Obj(leftMargin=0, rightMargin=20))
    row = Obj(getTextView=lambda: text, getVisibility=lambda: 0, getPaddingLeft=lambda: 10, getPaddingRight=lambda: 10)
    text.width = label_width
    return Obj(scrollToTop=lambda: None, getItemsCount=lambda: 1, getItemAt=lambda _: row,
               getPaddingLeft=lambda: 8, getPaddingRight=lambda: 8)


gear_button, overflow_button = popup_anchor(930, 500), popup_anchor(1125, 24)
menu_parent = Obj(getParent=lambda: Obj(getParent=lambda: popup_drawer))
gear_rows, overflow_rows = text_menu_rows(120), text_menu_rows(84)
gear_menu = Obj(getAnchor=lambda: gear_button, getPopupLayout=lambda: gear_rows, getParent=lambda: menu_parent)
overflow_button.getParent = lambda: menu_parent
overflow_button.getPopupLayout = lambda: overflow_rows
menu_geometry.drawer_type, menu_geometry.outer = Obj(isInstance=lambda v: v is popup_drawer), value_field(landscape_viewer)
menu_geometry.option = menu_geometry.video_surface = lambda _: True
menu_geometry.popup_item_type = Obj(isInstance=lambda _: True)
menu_geometry.text_layout = Obj(getDesiredWidth=lambda text, paint: menu_width.value)
menu_width = Obj(value=120)
menu_geometry.video_menu, menu_geometry.gallery_menu = value_field(gear_menu), value_field(overflow_button)
menu_geometry.gear_state = [(plugin.weak_reference(gear_menu),)]
popup_layout = Obj(getMeasuredWidth=lambda: 1200, getMeasuredHeight=lambda: 550,
                   measure=lambda *args: popup_calls.append(("measure", *args)))
window_popup = Obj(isShowing=lambda: False, getContentView=lambda: popup_layout,
                   setWidth=lambda width: popup_calls.append(("width", width)),
                   setHeight=lambda height: popup_calls.append(("height", height)),
                   showAsDropDown=lambda anchor, *args: popup_calls.append(("show", anchor, *args)))
menu_geometry.popup_window = value_field(window_popup)
for menu, anchor, label_width, expected_width, expected_x, expected_y, expected_height in (
        (gear_menu, gear_button, 120, 206, -212, -518, 550),
        (overflow_button, overflow_button, 84, 170, -176, -42, 550)):
    menu_width.value = label_width
    popup_calls.clear()
    menu_geometry.place_popup(Obj(thisObject=menu, args=[True, False], setResult=popup_calls.append))
    expected_calls = [("measure", expected_width, 554), ("width", expected_width), ("height", expected_height),
                      ("show", anchor, expected_x, expected_y, 3), None]
    assert popup_calls == expected_calls, (popup_calls, expected_calls)

gear_steps, gear_errors = [], []
gear_open = video.VideoSeekbarGestureInsets()
gear_open.active, gear_open.dp, gear_open.native_popup_menu = True, int, None
open_popup = Obj(showing=False, isShowing=lambda: open_popup.showing)
gear_open.popup_window = value_field(open_popup)
gear_open.hide_header = lambda _: None
gear_open.log = gear_errors.append
gear_open.restore_gear_sliders = lambda _: gear_steps.append("restore")


def setup_gear(_):
    raise RuntimeError("slider construction rejected")


def toggle_gear():
    gear_steps.append(("open", gear_open.native_popup_menu is fallback_gear))
    open_popup.showing = True


fallback_gear = Obj(setAnchor=lambda _: None, setShowOnTop=lambda _: None,
                    setSubMenuOpenSide=lambda _: None, setAdditionalYOffset=lambda _: None,
                    toggleSubMenu=toggle_gear)
gear_open.prepare_gear_sliders = setup_gear
gear_open.open_menu(landscape_viewer, fallback_gear, gear_button)
assert gear_steps == ["restore", ("open", False)] and open_popup.showing
assert "slider construction rejected" in gear_errors[-1]
gear_steps.clear()
open_popup.showing = False
gear_open.prepare_gear_sliders = lambda _: gear_steps.append("sliders")


def toggle_gear_on_fallback():
    gear_steps.append(("open", gear_open.native_popup_menu is fallback_gear))
    open_popup.showing = gear_open.native_popup_menu is fallback_gear


fallback_gear.toggleSubMenu = toggle_gear_on_fallback
gear_open.open_menu(landscape_viewer, fallback_gear, gear_button)
assert gear_steps == ["sliders", ("open", False), "restore", ("open", True)]
assert open_popup.showing and gear_open.native_popup_menu is None

photo_caption = video.VideoSeekbarGestureInsets()
photo_caption.top_captions = []
photo_caption.weak_reference, photo_caption.dp, photo_caption.sdk = plugin.weak_reference, int, 35
photo_caption.frame_params = lambda *args: Obj()


def fixture_label(text="", visibility=0):
    label = Obj(text=text, visibility=visibility)
    label.getText = lambda: label.text
    label.setText = lambda value: setattr(label, "text", value)
    label.getVisibility = lambda: label.visibility
    label.setVisibility = lambda value: setattr(label, "visibility", value)
    return label


photo_caption.make_caption_arrow = lambda *_: None
photo_caption.header_messages = Obj(getInstance=lambda _: Obj(getUserOrChat=lambda _: object()))
photo_caption.dialog_object = Obj(getDialogTitle=lambda _: "示例聊天")
caption_children = []
photo_bar = Obj()
photo_container = Obj(getContext=lambda: None, addView=lambda child, _: caption_children.append(child),
                      removeView=caption_children.remove)
photo_shade = Obj(getParent=lambda: Obj(removeView=lambda _: None), getHeight=lambda: 228)
photo_caption.make_header_shade = lambda *_: photo_shade
photo_caption.action_bar = value_field(photo_bar)
photo_title, photo_date = fixture_label("默认标题"), fixture_label()
photo_title.size, photo_date.size = 20, 14
photo_title.getPaint = lambda: Obj(getTextSize=lambda: photo_title.size)
photo_title.setTextSize = photo_title.setTextSizePx = lambda size: setattr(photo_title, "size", size)
photo_date.getDrawable = lambda: Obj(getTextSize=lambda: photo_date.size)
photo_date.setTextSize = lambda size: setattr(photo_date, "size", size)
photo_date.getParent = lambda: Obj(getPaddingLeft=lambda: 56, getPaddingTop=lambda: 0,
    getPaddingRight=lambda: 0, getPaddingBottom=lambda: 0, setPadding=lambda *_: None)
photo_caption.header_title = value_field(Obj(getTitle=photo_title.getText, setTitle=photo_title.setText,
                                            setSubtitle=lambda text, _: photo_date.setText(text)))
photo_caption.header_texts, photo_caption.header_date = value_field([photo_title]), value_field(photo_date)
photo_caption.header_locale = Obj(formatDateAudio=lambda *_: "昨天 12:32")
photo_body = Obj()
photo_scroll = Obj(getParent=lambda: photo_container, getLayoutParams=lambda: Obj(
    gravity=80, leftMargin=0, topMargin=0, rightMargin=0), fading=True,
    getVisibility=lambda: 0, getAlpha=lambda: 1.0,
    stopScrolling=lambda: None, scrollTo=lambda *_: None,
    requestLayout=lambda: None)
photo_scroll.isVerticalFadingEdgeEnabled = lambda: photo_scroll.fading
photo_scroll.setVerticalFadingEdgeEnabled = lambda value: setattr(photo_scroll, "fading", value)
photo_text = Obj(tag="caption", getTag=lambda: photo_text.tag, getParent=lambda: photo_body,
                 getVisibility=lambda: 0, setVisibility=lambda _: None,
                 getCurrentView=lambda: None, getNextView=lambda: None)
photo_caption.caption, photo_caption.caption_text, photo_caption.caption_content = map(
    value_field, (photo_scroll, photo_text, photo_body))
photo_caption.caption_previous_height = Obj(setInt=lambda *_: None)
photo_caption.action_bar_visible = Obj(getBoolean=lambda _: True)
photo_msg = Obj(currentAccount=0, messageOwner=Obj(date=123), getDialogId=lambda: 7, getId=lambda: 55, getGroupId=lambda: 0, isPhoto=lambda: True,
                isVideo=lambda: False, isSponsored=lambda: False)
photo_viewer = Obj(getCurrentMessageObject=lambda: photo_msg)
photo_caption.prepare_top_caption(photo_viewer, photo_container, True)
assert photo_caption.top_caption(photo_viewer).scroll is photo_scroll and photo_title.visibility == 0
assert not photo_scroll.fading
assert (photo_title.text, photo_date.text, photo_title.size, photo_date.size) == ("示例聊天", "昨天 12:32", 16, 12)
assert photo_caption.visible_photo_caption_top(photo_viewer) is None
photo_caption.caption_exit, photo_caption.boolean = None, bool
photo_caption.caption_in_picker = Obj(getBoolean=lambda _: False)
photo_caption.text_utils = Obj(isEmpty=lambda text: not text)
photo_caption.option = lambda _: False
photo_caption.transition_manager = Obj(endTransitions=lambda _: None)
photo_caption.bitmap = Obj(createBitmap=lambda *_: object())
photo_caption.bitmap_config = photo_caption.fit_center = object()
snapshots, animations, pending_ui = [], [], []
photo_caption.canvas = lambda _: Obj(translate=lambda *args: snapshots.append(args))
photo_scroll.getWidth, photo_scroll.getHeight = lambda: 540, lambda: 90
photo_scroll.getLeft, photo_scroll.getTop = lambda: 14, lambda: 68
photo_scroll.getScrollY, photo_scroll.getTranslationX, photo_scroll.getTranslationY = lambda: 20, lambda: 0.0, lambda: 0.0
photo_scroll.draw = lambda _: snapshots.append("draw")
photo_container.getPaddingLeft = lambda: 14
photo_container.requestLayout = lambda: None
motion = Obj(start=lambda: animations.append("start"), cancel=lambda: animations.append("cancel"))
motion.alpha = motion.translationY = motion.setDuration = lambda value: (animations.append(value), motion)[1]
overlay = Obj(getParent=lambda: photo_container, animate=lambda: motion, setImportantForAccessibility=lambda _: None,
              setImageBitmap=lambda _: None, setScaleType=lambda _: None, setAlpha=lambda _: None,
              getAlpha=lambda: overlay.alpha,
              setTranslationX=lambda value: animations.append(value), setTranslationY=lambda value: animations.append(value))
photo_caption.image_view = lambda _: overlay
video_namespace = video.VideoSeekbarGestureInsets.before_caption_change.__globals__
original_ui = video_namespace["run_on_ui_thread"]
video_namespace["run_on_ui_thread"] = lambda callback, delay=0: pending_ui.append(callback)
try:
    exit_param = Obj(thisObject=photo_viewer, args=[photo_msg, None, False, True])
    photo_caption.before_caption_change(exit_param)
    assert exit_param.args[3] is False and snapshots == [(0.0, -20.0), "draw"]
    assert overlay in caption_children and animations[-4:] == [0.0, -8.0, 150, "start"]
    assert photo_caption.caption_exit[1] is overlay
    overlay.alpha = 1.0
    assert photo_caption.caption_exit_shadow_height(photo_viewer, 68) == 228
    overlay.alpha = 0.5
    assert photo_caption.caption_exit_shadow_height(photo_viewer, 68) == 163
    overlay.alpha = 0.0
    assert photo_caption.caption_exit_shadow_height(photo_viewer, 68) == 98
    next_caption = Obj(thisObject=photo_viewer, args=[photo_msg, "新说明", False, True])
    photo_caption.before_caption_change(next_caption)
    assert next_caption.args[3] is False
    assert photo_caption.caption_exit is None and overlay not in caption_children
    pending_ui.pop()()
finally:
    video_namespace["run_on_ui_thread"] = original_ui
photo_text.tag = None
photo_caption.prepare_top_caption(photo_viewer, photo_container, True)
assert photo_caption.top_caption(photo_viewer).scroll is None and photo_title.visibility == 0
assert photo_scroll.fading
assert not caption_children
photo_caption.prepare_top_caption(photo_viewer, photo_container, False)
assert photo_caption.top_caption(photo_viewer) is None and photo_title.visibility == photo_date.visibility == 0
assert (photo_title.size, photo_date.size) == (20, 14)
assert not caption_children

jump = video.VideoSeekbarGestureInsets()
jump.active = True
jump.pending_chat_jump = None
jump.opening_chat_viewport = None
jump.weak_reference = plugin.weak_reference
opened_chat = []
activity = Obj(isFinishing=lambda: False, setRequestedOrientation=lambda _: None)
jump_viewer = Obj(isVisible=lambda: True, getParentActivity=lambda: activity,
                  getCurrentMessageObject=lambda: photo_msg)
chat_drawer = Obj(width=700, getWidth=lambda: chat_drawer.width, getHeight=lambda: 450)
bar = Obj(getParent=lambda: chat_drawer, getActionBarMenuOnItemClick=lambda: Obj(onItemClick=opened_chat.append))
action_menu = Obj(getParent=lambda: bar)
jump.outer = value_field(jump_viewer)
jump.drawer_type = Obj(isInstance=lambda view: view is chat_drawer)
jump.header_menu = value_field(action_menu)
jump.gallery_menu = value_field(Obj(isSubItemVisible=lambda item: item == video.SHOW_IN_CHAT_MENU_ID))
jump.fullscreen_session, jump.axis_lock = (jump.weak_reference(jump_viewer),), None
jump.native_fullscreen_mode = Obj(getInt=lambda _: 0)
jump.release_video_orientation = lambda _: setattr(jump, "fullscreen_session", None)
handled = []
video_namespace["run_on_ui_thread"] = lambda callback, delay=0: pending_ui.append(callback)
try:
    jump.before_gallery_menu_click(Obj(thisObject=action_menu, args=[video.SHOW_IN_CHAT_MENU_ID], setResult=handled.append))
    assert handled == [None] and not opened_chat
    pending_ui.pop()()
    assert not opened_chat
    chat_drawer.width = 360
    pending_ui.pop()()
    assert opened_chat == [video.SHOW_IN_CHAT_MENU_ID] and jump.pending_chat_jump is None
    opened_library = []
    jump.option = jump.video_surface = lambda _: True
    jump.open_media_library = lambda viewer: opened_library.append(viewer) or True
    jump.before_gallery_menu_click(Obj(thisObject=action_menu, args=[video.SHOW_ALL_MEDIA_MENU_ID], setResult=handled.append))
    assert opened_library == [jump_viewer] and handled == [None, None]
finally:
    video_namespace["run_on_ui_thread"] = original_ui

caption_layout = Obj(getLineCount=lambda: 5, getLineStart=lambda i: i * 10,
                     getLineVisibleEnd=lambda i: i * 10 + (0 if i == 1 else 8),
                     getLineBottom=lambda i: 20 * (i + 1))
caption_text = Obj(getLayout=lambda: caption_layout, getCompoundPaddingTop=lambda: 2,
                   getCompoundPaddingBottom=lambda: 0)
caption_plugin = video.VideoSeekbarGestureInsets()
caption_plugin.top_captions = []
caption_plugin.landscape_header = None
caption_plugin.status_slide = None
caption_plugin.weak_reference = plugin.weak_reference
caption_plugin.integer = caption_plugin.dp = int
caption_plugin.drawer_type = Obj(isInstance=lambda _: True)
caption_plugin.outer = value_field(viewer)
caption_plugin.compact_control = lambda _: Obj(getVisibility=lambda: 0)
caption_plugin.caption_text = value_field(Obj(getCurrentView=lambda: caption_text, getPaddingBottom=lambda: 2))
adjusted = []
caption_plugin.expand_landscape_caption(Obj(thisObject=Obj(getParent=lambda: container), args=(640, 180),
                                           getResult=lambda: 140, setResult=adjusted.append))
assert adjusted == [90]
four_lines = Obj(getLineCount=lambda: 4, getLineBottom=lambda line: 20 * (line + 1),
                 getLineStart=lambda _: 0, getLineVisibleEnd=lambda _: 1, getText=lambda: "X")
long_lines = Obj(getLineCount=lambda: 8, getLineBottom=lambda line: 20 * (line + 1),
                 getLineStart=lambda _: 0, getLineVisibleEnd=lambda _: 1,
                 getText=lambda: Obj(subSequence=lambda start, end: "X"))
assert video.caption_viewport(four_lines, 96, 200, 8, 2, False) == (96, False)
assert video.caption_viewport(long_lines, 176, 200, 8, 2, False) == (88, True)
assert video.caption_viewport(long_lines, 176, 200, 14, 8, False) == (94, True)
long_lines.getLineForVertical = lambda y: min(long_lines.getLineCount() - 1, y // 20)
assert video.caption_complete_line_height(long_lines, 8, 101, 0) == 88
assert video.caption_complete_line_height(long_lines, 8, 108, 0) == 108
assert video.caption_complete_line_height(long_lines, 8, 101, 15) == 93
assert video.caption_viewport(long_lines, 176, 140, 8, 2, True) == (140, True)
assert video.caption_viewport(long_lines, 176, 8, 8, 2, False) == (0, True)
assert video.caption_viewport(long_lines, 176, 114, 8, 2, False, 28) == (68, True)
assert video.caption_viewport(four_lines, 96, 80, 8, 2, False, 28) == (48, True)
long_lines.getLineVisibleEnd = lambda line: 0 if line == 3 else 1
assert video.caption_viewport(long_lines, 176, 200, 8, 2, False) == (68, True)
long_lines.getLineCount = lambda: 4
assert video.caption_viewport(long_lines, 96, 200, 8, 2, False) == (70, False)
long_lines.getLineCount = lambda: 7
long_lines.getLineStart = lambda line: (0, 3, 5, 7, 10, 12, 15)[line]
long_lines.getLineVisibleEnd = lambda line: (2, 4, 6, 9, 11, 14, 16)[line]
long_lines.getText = lambda: "📷\na\nb\n  \nc\n\t \n "
assert video.caption_viewport(long_lines, 156, 200, 8, 2, False) == (68, True)
assert video.caption_viewport(long_lines, 156, 200, 8, 2, True) == (110, True)
long_lines.getText = lambda: "📷\na\nb\n  \n \n\t \n "
assert video.caption_viewport(long_lines, 156, 200, 8, 2, False) == (70, False)
caption_plugin.sdk = 34
caption_plugin.positions = tuple
header_location = [0, 40]
header_content = Obj(padding=(0, 0, 0, 0),
    getLocationInWindow=lambda position: position.__setitem__(slice(None), header_location))
header_content.getPaddingLeft = lambda: header_content.padding[0]
header_content.getPaddingTop = header_content.getPaddingRight = header_content.getPaddingBottom = lambda: 0
header_content.setPadding = lambda *padding: setattr(header_content, "padding", padding)
caption_plugin.top_captions = [Obj(viewer_ref=plugin.weak_reference(viewer), header_content=header_content)]
caption_plugin.positions = list
back_location = [0, 48]
caption_plugin.header_back = value_field(Obj(getLocationInWindow=lambda position: position.__setitem__(slice(None), back_location),
                                            getHeight=lambda: 44, getWidth=lambda: 54))
caption_plugin.align_caption_header(viewer)
assert header_content.padding[0] == 46
header_location[0], back_location[0] = 160, 145
caption_plugin.align_caption_header(viewer)
assert header_content.padding[0] == 31
caption_events = []
top_drawer = Obj()


def located(x, y, width, height):
    return Obj(getParent=lambda: top_drawer, getWidth=lambda: width, getHeight=lambda: height,
               getLocationInWindow=lambda origin: origin.__setitem__(slice(None), [x, y]),
               getVisibility=lambda: 0, getAlpha=lambda: 1.0)


top_scroll = located(56, 68, 300, 66)
top_scroll.stopScrolling = lambda: None
top_scroll.scrollTo = lambda *args: caption_events.append(args)
top_scroll.requestLayout = lambda: caption_events.append("layout")
top_scroll.getScrollY = lambda: 0
top_scroll.translation = 0.0
top_scroll.getTranslationY = lambda: top_scroll.translation
top_scroll.setTranslationY = lambda value: setattr(top_scroll, "translation", value)
top_scroll.canScrollVertically = lambda _: False
top_drawer.getLocationInWindow = lambda origin: None
top_entry = Obj(viewer_ref=plugin.weak_reference(viewer), scroll=top_scroll,
                shade=located(0, 0, 640, 158), caption_key=None)
caption_plugin.top_captions = [top_entry]
caption_plugin.cancel_child_touch = lambda *args: caption_events.append("cancel")
caption_plugin.boolean = bool
caption_plugin.positions = list
caption_plugin.android = Obj(cancelRunOnUIThread=lambda _: None)
caption_plugin.auto_hide_controls = value_field(None)
caption_plugin.action_bar_visible = Obj(getBoolean=lambda _: True)
caption_plugin.action_bar = value_field(located(0, 0, 640, 68))
caption_plugin.call = lambda _, *args: caption_events.append(args)
text_body = Obj(getLineCount=lambda: 12, getHeight=lambda: 300, getLineForVertical=lambda y: y // 20,
                getLineLeft=lambda line: 0, getLineRight=lambda line: 150,
                getLineTop=lambda line: line * 20, getLineBottom=lambda line: (line + 1) * 20,
                getLineStart=lambda line: line * 8, getLineVisibleEnd=lambda line: line * 8 + 7,
                getLineEnd=lambda line: (line + 1) * 8,
                getParagraphDirection=lambda _: 1)
text_view = Obj(getLayout=lambda: text_body, getLocationInWindow=lambda origin: origin.__setitem__(slice(None), [56, 68]),
                getScrollX=lambda: 0, getScrollY=lambda: 0, getTotalPaddingLeft=lambda: 16, getTotalPaddingTop=lambda: 8,
                getTextSize=lambda: 14,
                measure=lambda *args: None, getMeasuredHeight=lambda: 256,
                getCompoundPaddingBottom=lambda: 8, getCompoundPaddingTop=lambda: 8)
caption_plugin.style_caption_padding = lambda _: None
text_window = Obj(getLocationInWindow=lambda origin: None)
top_entry.switcher = Obj(getCurrentView=lambda: text_view, getPaddingBottom=lambda: 0)
caption_plugin.window = value_field(text_window)
caption_plugin.drawer_type = Obj(isInstance=lambda view: view is top_drawer)
caption_plugin.outer = value_field(viewer)
top_entry.switcher.getParent = lambda: Obj(getParent=lambda: top_scroll)
text_view.getParent = lambda: top_entry.switcher
caption_plugin.update_caption_state(top_entry, (7, 21))
assert not top_entry.expanded
top_entry.has_more = True
caption_plugin.caption_tap_timeout = 500
caption_plugin.spanned_class = Obj(isInstance=lambda _: False)
text_body.getText = lambda: "content\n" * 12
caption_plugin.toggle_caption(viewer)
assert top_entry.expanded
caption_plugin.update_caption_state(top_entry, (7, 21))
assert top_entry.expanded


def caption_touch(y, action, *, x=300, time=100):
    event = Obj(getX=lambda: x, getY=lambda: y, getPointerCount=lambda: 1, getEventTime=lambda: time)
    return caption_plugin.route_caption_touch(Obj(setResult=caption_events.append), text_window, viewer, event, action)


def caption_child_touch(child, x, y, action=0):
    results = []
    event = Obj(getActionMasked=lambda: action, getX=lambda: x, getY=lambda: y)
    caption_plugin.pass_caption_space(Obj(thisObject=child, args=[event], setResult=results.append),
                                      from_text=child is text_view)
    return results


assert not caption_touch(42, 0, x=590) and not caption_touch(42, 1, x=590)
assert not caption_touch(88, 0, x=150) and caption_touch(88, 1, x=150)
assert not top_entry.expanded
assert not caption_touch(88, 0, x=150) and not caption_touch(88, 1, x=150, time=701)
assert not top_entry.expanded
assert not caption_touch(88, 0, x=150) and caption_touch(88, 1, x=150)
assert top_entry.expanded
assert not caption_touch(88, 0) and not caption_touch(88, 1)  # Native gesture sequence.
assert not caption_touch(142, 0) and not caption_touch(142, 1)  # Gradient below the viewport.
for child in (text_view, top_scroll):
    assert caption_child_touch(child, 244, 20) == [False]  # Space to the right of a line.
    assert caption_child_touch(child, 72, 4) == [False]  # Padding above the first line.
    assert caption_child_touch(child, 72, 20) == []  # Text and links.
    assert caption_child_touch(child, 244, 20, action=2) == []  # A drag started on text can continue.
assert caption_child_touch(Obj(getParent=lambda: None), 244, 20) == []
assert top_entry.expanded
caption_plugin.toggle_caption(viewer)
assert not top_entry.expanded
assert not caption_touch(88, 0, x=150) and caption_touch(115, 2, x=150)
assert caption_touch(115, 1, x=150) and not top_entry.expanded
caption_plugin.toggle_caption(viewer)
caption_plugin.update_caption_state(top_entry, (7, 22))
assert not top_entry.expanded

viewports = []
caption_frame = Obj()
top_scroll.getLayoutParams = lambda: caption_frame
top_scroll.measure = lambda width, height: viewports.append(height)
caption_plugin.measure_spec = Obj(EXACTLY=1, UNSPECIFIED=0, makeMeasureSpec=lambda size, mode: size)
caption_plugin.header_back = value_field(None)
caption_plugin.caption_content = value_field(Obj(getLayoutParams=lambda: Obj(topMargin=50)))
caption_plugin.controls = value_field(Obj(getVisibility=lambda: 0, getMeasuredHeight=lambda: 80,
                                         getLayoutParams=lambda: Obj(bottomMargin=8)))
top_drawer.getMeasuredHeight = lambda: 360
top_drawer.getMeasuredWidth = lambda: 324
top_drawer.getPaddingBottom = lambda: 12
arrow_frame = Obj(width=40, height=28)
top_entry.arrow = fixture_label(visibility=8)
top_entry.arrow.getLayoutParams = lambda: arrow_frame
top_entry.arrow.getPaddingLeft = lambda: 7
top_entry.arrow.measure = lambda *args: args
top_entry.arrow.rotation, top_entry.arrow.description = 0, None
top_entry.arrow.getRotation = lambda: top_entry.arrow.rotation
top_entry.arrow.setRotation = lambda value: setattr(top_entry.arrow, "rotation", value)
top_entry.arrow.getContentDescription = lambda: top_entry.arrow.description
top_entry.arrow.setContentDescription = lambda value: setattr(top_entry.arrow, "description", value)
top_entry.arrow.setTooltipText = lambda value: None
top_entry.arrow.alpha, top_entry.arrow.translation_y, top_entry.arrow.clickable = 1.0, 0.0, True
top_entry.arrow.getAlpha = lambda: top_entry.arrow.alpha
top_entry.arrow.setAlpha = lambda value: setattr(top_entry.arrow, "alpha", value)
top_entry.arrow.getTranslationY = lambda: top_entry.arrow.translation_y
top_entry.arrow.setTranslationY = lambda value: setattr(top_entry.arrow, "translation_y", value)
top_entry.arrow.isClickable = lambda: top_entry.arrow.clickable
top_entry.arrow.setClickable = lambda value: setattr(top_entry.arrow, "clickable", value)

caption_ripple = video.VideoSeekbarGestureInsets()
caption_ripple.dp, caption_ripple.sdk, caption_ripple.ripple_radius = int, 35, 20
caption_ripple.center, caption_ripple.fit_center = "center", "fit_center"
caption_ripple.drawable = Obj(baseline_keyboard_arrow_down_24=101)
caption_ripple.frame_params = lambda *args: args
arrow_widget = Obj(**{name: lambda *args: None for name in (
    "setImageResource", "setColorFilter", "setScaleType", "setContentDescription", "setTooltipText",
    "setBackground", "setPadding", "setVisibility", "setOnClickListener")})
caption_ripple.image_view = lambda _: arrow_widget
ripple_calls = []
caption_ripple.theme = Obj(createSelectorDrawable=lambda *args: ripple_calls.append(args))
arrow_layouts = []
arrow_parent = Obj(getContext=lambda: None, addView=lambda _, params: arrow_layouts.append(params))
caption_ripple.make_caption_arrow(arrow_parent, plugin.weak_reference(viewer))
caption_ripple.make_button(None, "Regular tool", 101)
assert arrow_layouts == [(40, 28, 51)]
assert ripple_calls == [(0x24FFFFFF, 7, 14), (0x24FFFFFF, 1, 20)]

assert caption_plugin.measure_caption_viewport(viewer, top_drawer, top_entry, 68, 600) == 116
assert top_entry.arrow.visibility == 0 and arrow_frame.topMargin == 156 and arrow_frame.leftMargin == 9
assert (top_scroll.getLayoutParams().leftMargin, top_scroll.getLayoutParams().rightMargin) == (0, 0)
text_view.getTotalPaddingTop = lambda: 2  # The old laid-out view still has its previous vertical offset.
assert caption_plugin.measure_caption_viewport(viewer, top_drawer, top_entry, 68, 600) == 116
assert viewports.pop() == 88 and arrow_frame.topMargin == 156
top_entry.expanded = True
assert caption_plugin.measure_caption_viewport(viewer, top_drawer, top_entry, 68, 600) == 176
assert top_entry.arrow.visibility == 0 and arrow_frame.topMargin == 68 + 148
assert top_entry.arrow.rotation == 180 and top_entry.arrow.description == "收起说明"
top_entry.expanded = False
text_body.getLineCount = lambda: 4
text_view.getMeasuredHeight = lambda: 96
assert caption_plugin.measure_caption_viewport(viewer, top_drawer, top_entry, 68, 600) == 96
assert top_entry.arrow.visibility == 8
assert viewports == [88, 148, 96]
assert top_scroll.getLayoutParams().rightMargin == 0
top_drawer.getMeasuredWidth = lambda: 324
top_drawer.getMeasuredHeight = lambda: 600
top_drawer.getPaddingLeft = lambda: 0
caption_rail = caption_plugin.thumbnail_rail = video.ThumbnailRail(viewer, None, top_drawer, (100, 120))
caption_rail.left = 210
text_body.getLineCount = lambda: 12
for drag_width, collapsed, motion, expected_margin in (
        (None, False, None, 126), (125, False, None, 154),
        (None, True, (0, 1, 0), 0), (None, False, (1, 0, 0), 126), (None, True, None, 0)):
    caption_rail.drag_width, caption_rail.collapsed, caption_rail.slide_motion = drag_width, collapsed, motion
    caption_plugin.measure_caption_viewport(viewer, top_drawer, top_entry, 68, 324)
    assert caption_frame.rightMargin == expected_margin
caption_plugin.thumbnail_rail = None
text_body.getLineCount = lambda: 4
top_drawer.getMeasuredHeight = lambda: 360
top_drawer.getMeasuredWidth = lambda: 648
top_drawer.getPaddingLeft, top_drawer.getPaddingRight = lambda: 40, lambda: 8
caption_plugin.measure_caption_viewport(viewer, top_drawer, top_entry, 68, 600)
assert (caption_frame.leftMargin, caption_frame.rightMargin) == (26, 28)
caption_animation = Obj(caption_motion=(90, 1.0))
caption_frames = []
frame_container = Obj(postOnAnimation=caption_frames.append)
caption_namespace = caption_plugin.animate_caption_height.__globals__
previous_clock = caption_namespace["monotonic"]
try:
    caption_namespace["monotonic"] = lambda: 1.0
    assert caption_plugin.animate_caption_height(caption_animation, frame_container, 190) == 90
    caption_namespace["monotonic"] = lambda: 1.11
    assert caption_plugin.animate_caption_height(caption_animation, frame_container, 190) == 140
    assert len(caption_frames) == 1
    caption_namespace["monotonic"] = lambda: 1.3
    assert caption_plugin.animate_caption_height(caption_animation, frame_container, 190) == 190
    assert caption_animation.caption_motion is None
finally:
    caption_namespace["monotonic"] = previous_clock
text_body.getLineCount = lambda: 12
top_drawer.getMeasuredWidth = lambda: 948
caption_plugin.measure_caption_viewport(viewer, top_drawer, top_entry, 68, 900)
assert arrow_frame.leftMargin == caption_frame.leftMargin + 9
assert arrow_frame.topMargin == caption_frame.topMargin + viewports[-1]
caption_bar = caption_plugin.action_bar.get(viewer)
caption_bar.getMeasuredHeight = lambda: 68
caption_bar.getAlpha = lambda: 0.65
top_drawer.getMeasuredWidth = lambda: 600
top_drawer.getPaddingLeft = top_drawer.getPaddingRight = lambda: 0
shade = top_entry.shade
shade.getLayoutParams = lambda: Obj()
caption_sizes = []
shade.measure = lambda *args: caption_sizes.append(args)
shade.setAlpha = lambda alpha: setattr(shade, "alpha", alpha)
shade.getAlpha = lambda: shade.alpha
text_body.getLineCount = lambda: 12
text_view.getMeasuredHeight = lambda: 256
caption_plugin.sdk = 34
caption_plugin.measure_top_caption(viewer, top_drawer, top_entry)
assert caption_sizes[-1][-1] == 236
top_entry.expanded = True
caption_plugin.measure_top_caption(viewer, top_drawer, top_entry)
assert caption_sizes[-1][-1] > 236
caption_bar.getAlpha = lambda: 0.0
caption_bar.getBackground = lambda: None
caption_plugin.sync_footer_shadow = lambda *_: None
caption_plugin.draw_player_shadows = lambda *_: None
caption_plugin.video_surface = lambda _: False
caption_plugin.sync_caption_shadow(Obj(thisObject=top_drawer, args=[None]))
assert shade.getAlpha() == 0


def fake_panel(background):
    panel = Obj(background=background)
    panel.getBackground = lambda: panel.background
    panel.setBackground = lambda drawable: setattr(panel, "background", drawable)
    return panel


top_panel, bottom_panel, nav_panel = fake_panel("top-native"), fake_panel("bottom-native"), fake_panel("nav-native")
gradient_plugin = video.VideoSeekbarGestureInsets()
gradient_plugin.action_bar, gradient_plugin.background = value_field(top_panel), value_field(bottom_panel)
gradient_plugin.navigation_bar = value_field(nav_panel)
gradient_plugin.shadows = []
gradient_plugin.landscape_header = None
gradient_plugin.sdk = 34
gradient_plugin.top_captions = []
gradient_plugin.photo_headers = []
gradient_plugin.album_styles = []
gradient_plugin.shadow_orientation = "TOP_BOTTOM"
gradient_plugin.header_shadow_stops = video.shadow_ramp(1, 0, video.TOP_SHADOW_ALPHA)
gradient_plugin.footer_shadow_stops = video.shadow_ramp(0, 1, video.PLAYER_SHADOW_ALPHA)
gradient_plugin.thumbnail_widths_dp = (88, 88)
gradient_plugin.positions = tuple
gradient_plugin.weak_reference = lambda panel: Obj(get=lambda: panel)


def fake_gradient(direction, colors):
    drawable = Obj(direction=direction, colors=tuple(colors))
    drawable.getColors = lambda: drawable.colors
    drawable.setColors = lambda values: setattr(drawable, "colors", tuple(values))
    drawable.setAlpha = lambda alpha: setattr(drawable, "alpha", alpha)
    return drawable


gradient_plugin.pill_background = fake_gradient
shade = fake_panel(fake_gradient("TOP_BOTTOM", video.shadow_ramp(0, 1, video.PLAYER_SHADOW_ALPHA)))
shade.getParent = lambda: drawer
shade.scale, shade.pivot = 1.0, 0.0
shade.setVisibility = lambda value: setattr(shade, "visibility", value)
shade.setAlpha = lambda value: setattr(shade, "alpha", value)
shade.getVisibility = lambda: shade.visibility
shade.getAlpha = lambda: shade.alpha
shade.getScaleY = lambda: shade.scale
shade.setScaleY = lambda value: setattr(shade, "scale", value)
shade.getPivotY = lambda: shade.pivot
shade.setPivotY = lambda value: setattr(shade, "pivot", value)
shade_layout = Obj(height=0)
shade.getLayoutParams = lambda: shade_layout
shade.getHeight = lambda: shade_layout.height
shade.getBottom = lambda: 600
measurements = []
shade.measure = lambda *specs: measurements.append(specs)
gradient_plugin.footer_shades = [(gradient_plugin.weak_reference(bottom_panel), gradient_plugin.weak_reference(shade))]
gradient_plugin.dp = int
gradient_plugin.measure_spec = Obj(EXACTLY=1, makeMeasureSpec=lambda size, _: size)
bottom_panel.getAlpha = lambda: 0.8
bottom_panel.getMeasuredHeight = lambda: 70
bottom_panel.getMeasuredWidth = lambda: 360
bottom_panel.getVisibility = lambda: 0
top_panel.getAlpha = lambda: 0.8
nav_panel.getVisibility = lambda: 0
nav_panel.getLayoutParams = lambda: Obj(height=24)
caption_position = Obj(scroll=0)
subtitle = Obj(getTag=lambda: "caption", getMeasuredHeight=lambda: 36, getScrollY=lambda: caption_position.scroll)
gradient_plugin.caption_text = value_field(subtitle)
drawer = Obj(getMeasuredWidth=lambda: 360, getMeasuredHeight=lambda: 600,
             getPaddingLeft=lambda: 0, getPaddingRight=lambda: 0, getPaddingTop=lambda: 0)
gradient_plugin.style_video_shadows(viewer, True)
gradient_plugin.layout_footer_shade(viewer, drawer, bottom_panel, True)
gradient_plugin.landscape_header = (viewer, drawer)
drawer.getPaddingLeft, drawer.getPaddingRight = lambda: 26, lambda: 0
gradient_plugin.measure_panel_shadow(shade, drawer, 86)
assert measurements[-1] == (360, 86) and shade_layout.leftMargin == -26
drawer.getPaddingLeft, drawer.getPaddingRight = lambda: 0, lambda: 26
gradient_plugin.measure_panel_shadow(shade, drawer, 86)
assert measurements[-1] == (360, 86) and shade_layout.leftMargin == 0
gradient_plugin.landscape_header = None
gradient_plugin.measure_panel_shadow(shade, drawer, 86)
assert measurements[-1] == (334, 86) and shade_layout.leftMargin == 0
drawer.getPaddingRight = lambda: 0
gradient_plugin.layout_footer_shade(viewer, drawer, bottom_panel, True)
top_start, *_, top_end = top_panel.background.colors
assert top_panel.background.direction == "TOP_BOTTOM"
assert ((top_start & 0xFFFFFFFF) >> 24) > 0 and top_end >> 24 == 0
footer_colors = shade.background.colors
inner, outer = footer_colors[0], footer_colors[-1]
assert bottom_panel.background is None and nav_panel.background is None
assert inner >> 24 == 0 and ((outer & 0xFFFFFFFF) >> 24) > 200
alpha = [(color & 0xFFFFFFFF) >> 24 for color in video.shadow_ramp(0, 1, 208)]
assert alpha[0] == 0 and alpha[-1] == 208
assert alpha[4] - alpha[2] > alpha[8] - alpha[6]
assert shade_layout.height == 128 and measurements[-1] == (360, 128) and shade.alpha == 0.8
caption_position.scroll = 90
gradient_plugin.layout_footer_shade(viewer, drawer, bottom_panel, True)
assert shade.background.colors == footer_colors and measurements[-1] == (360, 128)
gradient_plugin.top_captions = [Obj(viewer_ref=gradient_plugin.weak_reference(viewer))]
gradient_plugin.layout_footer_shade(viewer, drawer, bottom_panel, True)
assert measurements[-1] == (360, 128)

film = Obj(width=42, height=56, pad=10, gap=1)
film_layout = Obj(height=68)
film.getLayoutParams = lambda: film_layout
film.visibility = 0
film.getVisibility = lambda: film.visibility
film.hasPhotos = lambda: True
film.getAlpha = lambda: 1.0
film.getY = lambda: 490
film.invalidate = lambda: None
film_paint = Obj(mode="original")
film_paint.getXfermode = lambda: film_paint.mode
film_paint.setXfermode = lambda value: setattr(film_paint, "mode", value)
gradient_plugin.album_strip = value_field(film)
gradient_plugin.album_paint = value_field(film_paint)
gradient_plugin.album_geometry = tuple(member(name) for name in ("width", "height", "pad", "gap"))
gradient_plugin.transparent_paint_mode = "preserve destination"
gradient_plugin.style_album_strip(viewer, True, True)
assert (film.width, film.height, film.pad, film.gap, film_layout.height) == (88, 106, 6, 3, 118)
assert film_paint.mode == "preserve destination"
gradient_plugin.margins = []
gradient_plugin.integer = int
gradient_plugin.photo_surface = lambda _: True
gradient_plugin.video_surface = lambda _: False
film.getParent = lambda: drawer
film.getMeasuredHeight = lambda: film_layout.height
for _ in range(2):
    film_layout.bottomMargin = 48  # Native layout reassigns this before every measure.
    assert gradient_plugin.dock_album_strip(viewer, None, drawer, 12) == 130
    assert film_layout.bottomMargin == 12
gradient_plugin.photo_surface = lambda _: False
gradient_plugin.sync_footer_shadow(viewer, drawer)
assert shade.scale * shade_layout.height == 130
assert shade.background.colors == footer_colors and nav_panel.background is None

gradient_plugin.top_captions = []
photo_header = fake_panel(fake_gradient("TOP_BOTTOM", (0, 0)))
photo_header.getMeasuredHeight = lambda: 0
photo_header.getLayoutParams = lambda: Obj()
photo_header.setAlpha = lambda value: None
photo_header.measure = lambda *specs: measurements.append(specs)
top_panel.getMeasuredHeight = lambda: 62
gradient_plugin.photo_headers = [(gradient_plugin.weak_reference(viewer), photo_header)]
gradient_plugin.photo_surface = lambda _: True
gradient_plugin.style_video_shadows(viewer, True)
gradient_plugin.measure_photo_header(viewer, drawer, photo_header)
gradient_plugin.caption = value_field(None)
gradient_plugin.layout_footer_shade(viewer, drawer, bottom_panel, False, photo=True)
gradient_plugin.sync_footer_shadow(viewer, drawer)
assert shade.alpha == 0.8 and bottom_panel.background is None
assert shade.scale * shade_layout.height == 130
assert shade.background.colors == footer_colors and nav_panel.background is None
film.visibility = 4  # Native phone landscape hides the album strip.
gradient_plugin.sync_footer_shadow(viewer, drawer)
assert shade.alpha == 0.0
assert nav_panel.background is None
subtitle.getVisibility = lambda: 0
subtitle.getTranslationY = lambda: 0.0
gradient_plugin.caption = value_field(Obj(getY=lambda: 100, getVisibility=lambda: 0,
    getAlpha=lambda: 1.0, getScrollY=lambda: 0, getHeight=lambda: 480))
gradient_plugin.caption_content = value_field(Obj(getTop=lambda: 415))
gradient_plugin.sync_footer_shadow(viewer, drawer)
assert shade.alpha == 0.8 and shade.scale * shade_layout.height == 111
assert shade.background.colors == footer_colors and nav_panel.background is None
gradient_plugin.caption = value_field(None)
gradient_plugin.sync_footer_shadow(viewer, drawer)
assert shade.alpha == 0.0
film.visibility = 0
gradient_plugin.sync_footer_shadow(viewer, drawer)
assert shade.alpha == 0.8 and shade.scale * shade_layout.height == 130
assert (film.width, film.height) == (88, 106) and film_paint.mode == "preserve destination"
assert top_panel.background is None
assert measurements[-2:] == [(360, 92), (360, 48)]
gradient_plugin.caption_shadow_stack = []
gradient_plugin.outer = value_field(viewer)
gradient_plugin.drawer_type = Obj(isInstance=lambda value: value is drawer)
gradient_plugin.caption_alpha = Obj(getFloat=lambda caption: caption.alpha,
                                    setFloat=lambda caption, alpha: setattr(caption, "alpha", alpha))
native_caption = Obj(getParent=lambda: drawer, alpha=1.0)
caption_draw = Obj(thisObject=native_caption)
gradient_plugin.hide_native_caption_shadow(caption_draw)
assert native_caption.alpha == 0.0
gradient_plugin.restore_native_caption_shadow(caption_draw)
assert native_caption.alpha == 1.0
gradient_plugin.photo_headers = []
gradient_plugin.photo_surface = lambda _: False
gradient_plugin.layout_footer_shade(viewer, drawer, bottom_panel, True)
gradient_plugin.sync_footer_shadow(viewer, drawer)
assert shade.visibility == 0 and nav_panel.background is None
assert (shade.background.colors[-1] & 0xFFFFFFFF) >> 24 == video.PLAYER_SHADOW_ALPHA
gradient_plugin.style_album_strip(viewer, False, False)
assert (film.width, film.height, film.pad, film.gap, film_layout.height) == (42, 56, 10, 1, 68)
assert film_paint.mode == "original" and not gradient_plugin.album_styles
gradient_plugin.style_video_shadows(viewer, False)
assert (top_panel.background, bottom_panel.background, nav_panel.background) == (
    "top-native", "bottom-native", "nav-native",
)
gradient_plugin.header_height_stack = [True]
gradient_plugin.looper, gradient_plugin.ui_looper, gradient_plugin.integer = Obj(myLooper=lambda: "ui"), "ui", int
heights = []
gradient_plugin.compact_header_height(Obj(getResult=lambda: 48, setResult=heights.append))
assert heights == [video.COMPACT_HEADER_HEIGHT]

plugin.sdk = 35
plugin.padding = 8
plugin.gesture_types = 1
plugin.float_value, plugin.integer = float, int
insets = Obj(getStableInsetLeft=lambda: 0, getStableInsetRight=lambda: 0,
             getInsets=lambda _: Obj(left=16, right=24))
assert plugin.scrubber_margins(viewer, Obj(getRootWindowInsets=lambda: insets)) == (24, 32)
seek_view = Obj(getMeasuredWidth=lambda: 304, getLayoutParams=lambda: Obj(leftMargin=24))
plugin.active_seek_view = lambda _: seek_view
size = Obj(thisObject=None, args=[0, 0])
plugin.size_scrubber(size)
assert size.args == [300, 28]
for outer_x, expected in ((12.0, -12.0), (24.0, 12.0), (174.0, 150.0), (325.0, 288.0)):
    touch = Obj(thisObject=None, args=[0, outer_x, 14.0])
    plugin.offset_scrubber_touch(touch)
    assert touch.args[1] == expected
preview = []
plugin.offset_preview_thumb(Obj(thisObject=None, getResult=lambda: 150, setResult=preview.append))
assert preview == [174]

scrubber_container = Obj(getHeight=lambda: 800, getPaddingBottom=lambda: 24)
scrubber_control = Obj(top=620, progress=1.0, offset=0.0, transition=True)
scrubber_control.getParent = lambda: scrubber_container
scrubber_control.getTop = lambda: scrubber_control.top
scrubber_control.getProgress = lambda: scrubber_control.progress
scrubber_control.isSeekBarTransitionEnabled = lambda: scrubber_control.transition
scrubber_control.getTranslationY = lambda: scrubber_control.offset
scrubber_control.setTranslationY = lambda offset: setattr(scrubber_control, "offset", offset)
collapsed_seek = Obj(getParent=lambda: scrubber_control, getHeight=lambda: 28, getBottom=lambda: 28)
plugin.video_seek_view = value_field(collapsed_seek)
plugin.fullscreen_control = lambda _: Obj(getVisibility=lambda: 0)
plugin.position_collapsed_scrubber(viewer, scrubber_control, 0.5)
assert scrubber_control.offset == 65.5
plugin.position_collapsed_scrubber(viewer, scrubber_control, 0.0)
assert scrubber_control.top + 28 - video.NATIVE_THIN_BAR_BOTTOM_GAP + scrubber_control.offset == 776
scrubber_control.top, scrubber_control.progress = 700, 0.0
plugin.position_collapsed_scrubber(viewer, scrubber_control)
assert scrubber_control.offset == 51
plugin.position_collapsed_scrubber(viewer, scrubber_control, 1.0)
assert scrubber_control.offset == 0
scrubber_control.transition, scrubber_control.offset = False, 24.0
plugin.position_collapsed_scrubber(viewer, scrubber_control)
assert scrubber_control.offset == 24.0

footer_sync = video.VideoSeekbarGestureInsets()
footer_sync.dp, footer_sync.option, footer_sync.video_surface = int, lambda _: True, lambda _: True
scrubber_control.getVisibility = lambda: 0
scrubber_control.offset, scrubber_control.progress = 72.0, 0.4
footer = Obj(offset=0, alpha=1.0)
footer.getTranslationY, footer.getAlpha = lambda: footer.offset, lambda: footer.alpha
footer.setTranslationY = lambda offset: setattr(footer, "offset", offset)
footer.setAlpha = lambda alpha: setattr(footer, "alpha", alpha)
footer_sync.controls, footer_sync.background = value_field(scrubber_control), value_field(footer)
footer_sync.action_bar, footer_sync.action_bar_visible = value_field(None), value_field(True)
footer_sync.action_bar_visible.getBoolean = lambda _: True
footer_rail = video.ThumbnailRail(viewer, None, None, (64, 64))
footer_sync.thumbnail_rail = footer_rail
footer_sync.sync_player_footer(viewer)
for bottom, expected_shift in ((True, 72), (False, 10)):
    footer_rail.bottom_docked = bottom
    footer_sync.sync_thumbnail_visibility(viewer)
    assert (footer.offset, footer.alpha, footer_rail.alpha, footer_rail.ui_shift) == (72.0, 0.4, 0.4, expected_shift)
thin_plugin = video.VideoSeekbarGestureInsets()
thin_plugin.control_outer = value_field(viewer)
thin_plugin.active, thin_plugin.boolean = True, bool
thin_plugin.video_surface = lambda _: True
thin_plugin.weak_reference = plugin.weak_reference
thin_plugin.native_seek_transition = None
transition_request = Obj(thisObject=scrubber_control, args=[False])
thin_plugin.keep_collapsed_scrubber(transition_request)
assert transition_request.args == [True] and thin_plugin.native_seek_transition[1] is False


class Engine:
    def getPlaybackState(self):
        return self.state

    def getPlayWhenReady(self):
        return True


class Player:
    def __init__(self, loop=False):
        self.loop = loop
        self.playing = True
        self.player = Engine()
        self.player.state = 3
        self.seeks = []

    def isPlaying(self):
        return self.playing

    def isLooping(self):
        return self.loop

    def setLooping(self, value):
        self.loop = value

    def pause(self):
        self.playing = False

    def seekTo(self, time):
        self.seeks.append(time)


class Handler:
    def __init__(self):
        self.callbacks = {}

    @property
    def delay(self):
        return self.callbacks.get(timer.tick_runnable)

    def postDelayed(self, fn, delay):
        self.callbacks[fn] = delay

    def post(self, fn):
        self.postDelayed(fn, 0)

    def removeCallbacks(self, fn):
        self.callbacks.pop(fn, None)


timer_module = load("media_sleep_timer")
guard = timer_module.MediaSleepTimer()
guard.active = True
guard.dialog = guard.editor_dialog = guard.dialog_viewer = None
guard.dialog_is_sheet = False
guard.dialog_generation = 0
guard.log = lambda _: None
anchor = Obj(isAttachedToWindow=lambda: True)
recoveries = []


def fail_panel(*_):
    raise RuntimeError("window attach failed")


guard.show_timer_panel = fail_panel
guard.show_timer_fallback = lambda *_: recoveries.append("fallback")
guard.show_timer(anchor, None)
assert recoveries == ["fallback"]
guard.show_timer_fallback = fail_panel
anchor.getContext = lambda: None
guard.toast = Obj(makeText=lambda *args: Obj(show=lambda: recoveries.append("toast")))
guard.show_timer(anchor, None)
assert recoveries == ["fallback", "toast"]


class TimerWidget:
    def __init__(self, *args):
        self.args = args
        self.children = []
        self.calls = {}

    def __getattr__(self, name):
        def record(*args):
            self.calls[name] = args
            return self
        return record

    def addView(self, view, params):
        self.children.append(view)

    def removeAllViews(self):
        self.children.clear()

    def isChecked(self):
        return self.calls.get("setChecked", (self.calls["setTextAndCheck"][1],))[0]

    def getText(self):
        return self.calls.get("setText", ("",))[0]

    def getVisibility(self):
        return self.calls.get("setVisibility", (0,))[0]

    def getChildCount(self):
        return len(self.children)

    def getChildAt(self, index):
        return self.children[index] if index < len(self.children) else None


class TimerDialog:
    def __init__(self):
        self.showing = False
        self.button = TimerWidget()

    def isShowing(self):
        return self.showing

    def show(self):
        self.showing = True

    def dismiss(self):
        self.showing = False

    def setCanDismissWithSwipe(self, value):
        self.dismiss_with_swipe = value

    def skipDismissAnimation(self):
        self.skip_animation = True

    def getButton(self, _):
        return self.button


class TimerBuilder(TimerWidget):
    instances = []

    def __init__(self, *args):
        super().__init__(*args)
        self.dialog = TimerDialog()
        self.instances.append(self)

    def create(self):
        return self.dialog


globals_timer = timer_module.MediaSleepTimer.show_timer_panel.__globals__
ui_root = "org.telegram.ui."
java_stubs = {
    ui_root + "ActionBar.BottomSheet$Builder": TimerBuilder,
    ui_root + "Cells.TextSettingsCell": TimerWidget,
    ui_root + "Cells.TextCheckCell": TimerWidget,
    ui_root + "Components.SlideChooseView": TimerWidget,
    ui_root + "Components.SlideChooseView$Callback": object,
    ui_root + "Components.EditTextBoldCursor": TimerWidget,
    ui_root + "Stories.recorder.ButtonWithCounterView": TimerWidget,
    "java.lang.String": str,
    "androidx.core.widget.NestedScrollView": TimerWidget,
    "android.view.View$OnLayoutChangeListener": object,
    "android.widget.FrameLayout$LayoutParams": lambda *args: args,
}
ui_queue = []
globals_timer.update(jclass=java_stubs.__getitem__, jarray=lambda _: list,
                     dynamic_proxy=lambda interface: interface,
                     run_on_ui_thread=lambda fn, delay=0: ui_queue.append(fn))
timer_ui = timer_module.MediaSleepTimer()
timer_ui.active = True
timer_ui.last_minutes = 60
timer_ui.last_finish = False
timer_ui.dialog = timer_ui.session = timer_ui.waiting = None
timer_ui.editor_dialog = timer_ui.dialog_viewer = None
timer_ui.dialog_is_sheet = False
timer_ui.dialog_generation = 0
timer_ui.weak = lambda target: Obj(get=lambda: target)
timer_ui.timer_labels = list
timer_ui.timer_layout = TimerWidget
timer_ui.text_view = TimerWidget
timer_ui.linear_params = lambda *args: Obj()
timer_ui.dp = int
timer_ui.frame_params = lambda *args: args
timer_ui.sdk = 34
timer_button, clock_icon = TimerWidget(), TimerWidget()
timer_button.addView(clock_icon, None)
timer_ui.render_timer_control(timer_button, -1, -2, "12:34")
assert clock_icon.calls["setTranslationY"] == (0.0,)
assert timer_button.getChildAt(1).calls["setText"] == ("12:34",)
timer_ui.render_timer_control(timer_button, -1, -2, "")
assert clock_icon.calls["setTranslationY"] == (0.0,) and timer_button.getChildAt(1).getVisibility() == 4
timer_ui.dialog_option_listener = object
timer_ui.layout_helper = Obj(createLinear=lambda *args: args)
timer_ui.theme = Obj(key_listSelector=0, key_dialogTextBlack=1, key_dialogTextGray2=2,
                     key_featuredStickers_addButton=3, getColor=lambda key, *_: -123456 if key == 3 else 0,
                     createSelectorDrawable=lambda *args: None)
timer_ui.native_alert = TimerBuilder
activity, provider = object(), object()
video_alerts = []


def show_viewer_alert(builder):
    video_alerts.append(builder)
    builder.create().show()


video_ui = Obj(getParentActivity=lambda: activity, isVisible=lambda: True, showAlertDialog=show_viewer_alert)
video_ref = timer_ui.weak(video_ui)
timer_ui.timer_provider = lambda viewer: provider if viewer else None
starts = []
timer_ui.start_timer = lambda *args: starts.append(args)
errors = []
timer_ui.log = errors.append

timer_ui.show_timer(anchor, video_ref)
native_panel = TimerBuilder.instances[-1]
assert native_panel.args == (activity, False, provider, timer_module.VIDEO_SHEET_COLOR)
assert native_panel.dialog.scrollNavBar and native_panel.dialog.isShowing()
panel_scroll = native_panel.calls["setCustomView"][0]
duration, presets, finish, status, actions = panel_scroll.children[0].children
panel_scroll.children[0].getMeasuredHeight = lambda: 250
panel_layout = panel_scroll.calls["addOnLayoutChangeListener"][0]
panel_layout.onLayoutChange(panel_scroll, 0, 0, 320, 180, 0, 0, 0, 0)
assert not native_panel.dialog.dismiss_with_swipe
panel_layout.onLayoutChange(panel_scroll, 0, 0, 420, 250, 0, 0, 0, 0)
assert native_panel.dialog.dismiss_with_swipe
cancel, start = actions.children
assert presets.calls["setOptions"] == (3, ["15", "30", "45", "60", "90", "120"])
presets.calls["setCallback"][0].onOptionSelected(5)
assert duration.calls["setTextAndValue"][1] == "120 分钟"
presets.calls["setCallback"][0].onOptionSelected(2)
assert duration.calls["setTextAndValue"][1] == "45 分钟"
duration.calls["setOnClickListener"][0](duration)
custom_dialog = video_alerts[-1]
editor = custom_dialog.calls["setView"][0].children[0]
editor.setText("1441")
custom_dialog.dialog.button.calls["setOnClickListener"][0](None)
assert editor.calls.get("setError") and custom_dialog.dialog.isShowing()
editor.setText("240")
custom_dialog.dialog.button.calls["setOnClickListener"][0](None)
assert not custom_dialog.dialog.isShowing()
assert presets.calls["setOptions"] == (6, ["15", "30", "45", "60", "90", "120", "自定义"])
assert duration.calls["setTextAndValue"][1] == "240 分钟"
finish.calls["setOnClickListener"][0](finish)
start.calls["setOnClickListener"][0](start)
assert starts == [(240, True, video_ref)] and not native_panel.dialog.isShowing()

normal_panel = timer_ui.show_timer_panel
timer_ui.show_timer_panel = fail_panel
timer_ui.show_timer(anchor, video_ref)
native_options = video_alerts[-1]
labels, listener = native_options.calls["setItems"]
assert labels[:6] == [f"{value} 分钟" for value in timer_module.PRESETS]
listener.onClick(native_options.dialog, len(timer_module.PRESETS) + 1)
ui_queue.pop()()
labels, listener = video_alerts[-1].calls["setItems"]
assert labels[-1].endswith("已开启")
listener.onClick(video_alerts[-1].dialog, 1)
assert starts[-1] == (30, True, video_ref)
assert len(errors) == 1 and "native timer sheet" in errors[0]
timer_ui.show_timer_fallback(anchor, None)
assert TimerBuilder.instances[-1].dialog.isShowing() and len(video_alerts) == 3
timer_ui.show_timer_panel = normal_panel
timer_ui.show_timer(anchor, video_ref)
parent_sheet = TimerBuilder.instances[-1].dialog
timer_ui.edit_timer_minutes(anchor, video_ref, 45, lambda _: None)
custom = TimerBuilder.instances[-1].dialog
timer_ui.session = ("countdown",)
timer_ui.before_launch_transition(Obj(thisObject=activity))
assert not parent_sheet.isShowing() and parent_sheet.skip_animation and not custom.isShowing()
assert timer_ui.session == ("countdown",)
timer_ui.session = None
timer_ui.open_video_timer(anchor, video_ref)
timer_ui.dismiss_timer_ui(video_ui)
ui_queue.pop()()
assert timer_ui.dialog is None and timer_ui.dialog_viewer is None

capsule_requests = []
timer_ui.last_minutes = 60
timer_ui.make_timer_capsule = lambda *args, **kwargs: (capsule_requests.append((args, kwargs)), TimerWidget())[1]
timer_ui.show_timer_panel(anchor, video_ref)
shared_panel = TimerBuilder.instances[-1]
shared_duration, shared_slider, _, _, shared_actions = shared_panel.calls["setCustomView"][0].children[0].children
assert len(shared_slider.children) == 1 and shared_duration.calls["setTextAndValue"][1] == ""
capsule_args, capsule_kwargs = capsule_requests[-1]
assert capsule_args[3] == ("15", "30", "45", "60", "90", "120")
assert capsule_kwargs["value_labels"][-1] == "120 分钟"
assert capsule_kwargs["palette"][2] == -123456
capsule_args[-1](True, 1.0, 5)
shared_actions.children[-1].calls["setOnClickListener"][0](None)
assert starts[-1] == (120, False, video_ref)
print("Passed compact timer panel, editor lifecycle, fallback options, and audio alert flows")

for screen_width in (320, 360, 480, 690):
    slots = timer_module.audio_slots(screen_width, 4, 9)
    assert slots[0][0] == 4 and slots[-1][1] == screen_width - 4
    assert all(left[1] == right[0] for left, right in zip(slots, slots[1:]))
    assert abs(sum(slots[4]) - screen_width) <= 1
    for left, right in ((3, 3), (2, 3), (4, 4), (0, 2)):
        centered = timer_module.centered_audio_slots(screen_width, 10, left, right)
        assert len(centered) == left + 1 + right
        assert abs(sum(centered[left]) - screen_width) <= 1
        assert all(sl[1] == sr[0] for sl, sr in zip(centered, centered[1:]))
centered = timer_module.centered_audio_slots(360, 10, 3, 3)
assert max(end - start for start, end in centered) - min(end - start for start, end in centered) <= 1

music_row = Obj(getWidth=lambda: 360, getHeight=lambda: 66, getLeft=lambda: 0, getTop=lambda: 111)


class MusicButton(TimerWidget):
    def __init__(self, parent, width=48, height=48):
        super().__init__()
        self.parent = parent
        self.params = Obj(width=width, height=height)
        self.width = width

    def getParent(self):
        return self.parent

    def getLayoutParams(self):
        return self.params

    def getMeasuredWidth(self):
        return self.width

    def measure(self, width, height):
        self.width = width

    def getPaddingLeft(self):
        return 8


native_music = [MusicButton(music_row) for _ in range(7)]
speed, clock_button = MusicButton(object(), 36, 36), MusicButton(music_row, 56, 56)
eye = MusicButton(music_row)
music_row.findViewWithTag = lambda tag: eye if tag == timer_module.AUDIO_SHOW_IN_CHAT_TAG else None
timer_ui.controller = Obj(getPlayingMessageObject=lambda: Obj(getId=lambda: 26))
timer_ui.audio_native_buttons = value_field(native_music)
timer_ui.audio_speed = value_field(speed)
timer_ui.dp = int
timer_ui.measure_spec = Obj(EXACTLY=1, AT_MOST=2, makeMeasureSpec=lambda size, _: size)
timer_ui.style_audio_track_icons = lambda *args, **kwargs: None
for with_tracks in (True, False):
    for i in (2, 4):
        native_music[i].parent = music_row if with_tracks else None
    speed.setVisibility(8)  # Native updateTitle hides it on short audio.
    timer_ui.layout_audio_buttons(object(), clock_button)
    assert speed.getVisibility() == 0
    for controls in (native_music[1:6], [native_music[0], speed, clock_button, eye, native_music[6]]):
        centers = [sum(button.calls["layout"][::2]) / 2 for button in controls if button.getParent() is not None]
        gaps = [right - left for left, right in zip(centers, centers[1:])]
        assert abs((centers[0] + centers[-1]) / 2 - 180) <= 0.5
        assert max(gaps) - min(gaps) <= 1
    assert native_music[3].calls["layout"][1] == 5
    assert clock_button.calls["layout"][1] == 49
    assert speed.calls["layout"][1] == 170
    assert eye.calls["layout"][1] == 53
    assert abs(sum(eye.calls["layout"][::2]) / 2 - 246) <= 1

native_audio_jumps, hidden_audio_items = [], []
timer_ui.audio_show_in_chat_args = [4]
timer_ui.audio_show_in_chat = Obj(invoke=lambda *args: native_audio_jumps.append(args))
audio_view = object()
timer_ui.open_audio_in_chat(Obj(get=lambda: audio_view))
assert native_audio_jumps == [(audio_view, [4])]
timer_ui.audio_options_stack, timer_ui.audio_menu_chat_icon = [True], 88
menu_options = object()
timer_ui.hide_audio_chat_menu_item(Obj(args=[True, 88], thisObject=menu_options, setResult=hidden_audio_items.append))
timer_ui.hide_audio_chat_menu_item(Obj(args=[True, 89], thisObject=menu_options, setResult=hidden_audio_items.append))
assert hidden_audio_items == [menu_options]

mini_audio = Obj(getCurrentStyle=lambda: 0)
mini_speed = TimerWidget()
mini_speed.getAlpha = lambda: mini_speed.calls.get("setAlpha", (0.0,))[0]
mini_speed.isEnabled = lambda: mini_speed.calls.get("setEnabled", (False,))[0]
mini_track = Obj(duration=180, getDuration=lambda: mini_track.duration, isMusic=lambda: True)
mini_title = Obj(getPaddingLeft=lambda: 2, getPaddingTop=lambda: 0, getPaddingBottom=lambda: 3,
                 setPadding=lambda *padding: setattr(mini_title, "padding", padding))
mini_updates = []
timer_ui.active, timer_ui.mini_audio_bars = True, []
timer_ui.object_args, timer_ui.boolean = list, bool
timer_ui.mini_audio_title, timer_ui.mini_audio_message = value_field(mini_title), value_field(mini_track)
timer_ui.mini_audio_speed, timer_ui.mini_audio_join_width = value_field(mini_speed), Obj(getInt=lambda _: 12)
timer_ui.mini_audio_update_speed = Obj(invoke=lambda *args: mini_updates.append(args))
mini_params = Obj(thisObject=mini_audio)
timer_ui.after_mini_audio_player(mini_params)
assert mini_speed.isEnabled() and mini_speed.getAlpha() == 1.0 and mini_title.padding == (2, 0, 56, 3)
assert mini_updates == [(mini_audio, [False])]
timer_ui.after_mini_audio_player(mini_params)
assert len(mini_updates) == len(timer_ui.mini_audio_bars) == 1
timer_ui.restore_mini_audio_speed()
assert not mini_speed.isEnabled() and mini_speed.getAlpha() == 0 and mini_title.padding == (2, 0, 12, 3)
mini_track.duration = 600
timer_ui.after_mini_audio_player(mini_params)
assert len(mini_updates) == 1 and not timer_ui.mini_audio_bars

assert [timer_module.duration_minutes(i, "") for i in range(6)] == [15, 30, 45, 60, 90, 120]
assert timer_module.duration_minutes(6, "1") == 1
assert timer_module.duration_minutes(6, "1440") == 1440
assert all(timer_module.duration_minutes(6, value) is None
           for value in ("0", "-1", "1441", "", "2.5"))
timer = timer_module.MediaSleepTimer()
saved_timer_options = {}
timer.set_setting = saved_timer_options.__setitem__
timer.active = True
timer.session = timer.waiting = None
timer.now = 0
timer.clock = Obj(elapsedRealtime=lambda: timer.now)
timer.handler = Handler()
timer.tick_runnable = timer.tick
timer.countdown_runnable = timer.run_countdown
timer.target = lambda: (player, message_obj, key)
timer.manually_paused = Obj(setBoolean=lambda *args: None)
video_owner = object()
viewer = Obj(get=lambda: video_owner)
timer.dp = int
timer.sdk = 30
timer.frame_params = lambda *args: Obj(args=args)
timer.text_view = TimerWidget
timer.log = lambda msg: (_ for _ in ()).throw(AssertionError(msg))
audio_clock, video_clock, video_menu = TimerWidget(), TimerWidget(), TimerWidget()
audio_icon, video_icon = TimerWidget(), TimerWidget()
audio_clock.addView(audio_icon, None)
audio_counter = timer.add_timer_countdown(audio_clock, height=16, min_sp=8)
assert audio_counter.getVisibility() == 4
video_clock.addView(video_icon, None)
video_menu.getTextView = lambda: video_menu
timer.viewer_window = value_field(Obj(findViewWithTag=lambda tag: video_clock))
timer.menus = [(None, timer_ui.weak(video_menu), viewer)]
timer.audio_rows = [(Obj(get=lambda: object()), timer_ui.weak(audio_clock), None)]
timer.audio_title_color = value_field(Obj(getCurrentTextColor=lambda: 33))
timer.theme = Obj(isCurrentThemeDark=lambda: False)

player, message_obj, key = Player(), None, 12
timer.start_timer(1, False, viewer)
assert timer.handler.delay == 60000 and player.playing
timer.countdown_runnable()
assert video_clock.getChildAt(1).getText() == "01:00"
assert video_icon.calls["setColorFilter"] == (timer_module.VIDEO_TIMER_BLUE,)
assert audio_counter.getVisibility() == 4 and audio_icon.calls["setColorFilter"] == (33,)
assert timer.handler.callbacks[timer.countdown_runnable] == 1000
timer.now += 59999
timer.countdown_runnable()
assert video_clock.getChildAt(1).getText() == "00:01"
timer.tick()
assert player.playing and timer.handler.delay == 1
timer.now += 1
timer.tick()
assert not player.playing and timer.session is None
timer.countdown_runnable()
assert video_clock.getChildAt(1).getVisibility() == 4
assert video_icon.calls["setColorFilter"] == (timer_module.WHITE,)

player = Player(loop=True)
timer.start_timer(1, True, viewer)
assert saved_timer_options == {"sleep_timer_minutes": 1, "sleep_timer_finish_current": True}
timer.now += 60000
timer.tick()
assert player.playing and not player.loop and timer.waiting[:2] == (player, 12)
player.player.state = 4
timer.after_player_state(Obj(thisObject=player))
assert not player.playing and player.loop and timer.session is None

player = Player(loop=True)
timer.start_timer(1, True, viewer)
timer.now += 60000
timer.tick()
key = 13
timer.tick()
assert player.playing and player.loop and timer.session is None

player, message_obj = Player(), Obj(audioProgress=0.2)
timer.controller = Obj(pauseMessage=lambda item, fade: player.pause())
timer.start_timer(1, True, None)
timer.countdown_runnable()
assert audio_counter.getText() == "01:00" and audio_counter.getVisibility() == 0
assert audio_icon.calls["setColorFilter"] == (timer_module.AUDIO_TIMER_BLUE,)
assert audio_icon.calls["setTranslationY"] == (0.0,)
assert timer_module.format_timer_time(7200) == "2:00:00"
timer.now += 1000
timer.countdown_runnable()
assert audio_clock.getChildAt(1) is audio_counter and audio_counter.getText() == "00:59"
timer.now += 59000
timer.tick()
assert player.playing and timer.waiting is not None
assert (timer.reached_deadline_for(Player()) is None)
player.player.state = 4
overrides = []
timer.before_player_state(Obj(thisObject=player, setResult=overrides.append))
assert overrides == [None] and not player.playing and timer.session is None
assert player.seeks == [0]
timer.countdown_runnable()
assert audio_counter.getVisibility() == 4

player, message_obj = Player(loop=True), None
timer.start_timer(1, True, viewer)
timer.now += 60000
timer.tick()
timer.clear()
assert player.playing and player.loop and timer.handler.delay is None

print("Passed photo and video captions, album shadows, swipe dispatch, and shared orientation rules")
print("Passed pinned-message visibility, date visibility, paged albums, inset offsets, and timer state transitions")


pip = load("system_video_pip")
assert pip.media_title("  \n片名  第 1 集\n介绍", "test.mp4") == "片名 第 1 集"
assert pip.media_title("", "test.mp4") == "test.mp4"
assert pip.media_title(None, None) == "视频播放"
assert len(pip.media_title("长" * 120, None)) == 96
assert pip.cover_size(1080, 1920) == (144, 256)
assert pip.cover_size(1920, 1080) == (256, 144)
assert pip.cover_size(60, 80) == (60, 80)
assert pip.skip_position(10000, 60000, pip.BACK) == 0
assert pip.skip_position(10000, 60000, pip.FORWARD) == 25000
assert ayu.media_cursor(50, 100, 20, False) == (50, 50)
assert ayu.media_cursor(-20, -40, -70, True) == (-20, -70)
media_fix = ayu.AyuFilterDisplayFix()
media_fix.ayu = Obj(isDialogExcluded=lambda dialog: dialog == 102,
                    shouldHideFilteredMessages=lambda: True,
                    shouldHideIgnoredBlockedMessages=lambda: False,
                    shouldMaskMessage=lambda message, group: message.masked,
                    shouldHideFilteredMessage=lambda message, group: True)


def media_message(dialog, *, sensitive=False, restricted=False, masked=False, raw_hide=False):
    return Obj(messageOwner=Obj(hide=raw_hide), getDialogId=lambda: dialog, isRestrictedMessage=restricted,
               isHiddenSensitive=lambda: sensitive, masked=masked, getGroupId=lambda: 0)


assert media_fix.media_hidden(media_message(101))
assert not media_fix.media_hidden(media_message(102, raw_hide=True, masked=True))
assert media_fix.media_hidden(media_message(102, sensitive=True))
assert media_fix.media_hidden(media_message(102, restricted=True))
media_fix.ayu.shouldHideFilteredMessages = lambda: False
assert media_fix.media_hidden(media_message(101, masked=True))
assert not media_fix.media_hidden(media_message(101))
chat_mode = Obj(hiding=True)
member = media_message(101)
member.getGroupId = lambda: 66
primary = media_message(101, masked=True)
album_object = Obj(findPrimaryMessageObject=lambda: primary)
chat_media = Obj(getGroup=lambda group_id: album_object if group_id == 66 else None)
media_fix.hide_mode = Obj(getBoolean=lambda _: chat_mode.hiding)
assert media_fix.media_hidden(member, chat_media)
chat_mode.hiding = False
assert not media_fix.media_hidden(member, chat_media)
assert pip.video_dimensions(Obj(width=1920, height=1080, unappliedRotationDegrees=90), 0, 0) == (1080, 1920)
assert pip.video_dimensions(Obj(width=1920, height=1080, unappliedRotationDegrees=0), 0, 0) == (1920, 1080)
assert pip.video_dimensions(Obj(width=0, height=0), 720, 1280) == (720, 1280)

events = []
state = Obj(in_pip=False, accepted=True, priority=True, internal=False, available=True)
engine = Obj(
    getPlayWhenReady=lambda: state.playing,
    getPlaybackState=lambda: state.playback_state,
    pause=lambda: events.append("pause"),
    play=lambda: events.append("play"),
    seekTo=lambda position: events.append(("seek", position)),
)
controller = Obj(getHandler=lambda: "handler")
source = Obj(
    controller=controller,
    invalidatePosition=lambda: events.append("position"),
    invalidateAvailability=lambda: events.append("availability"),
    isAvailable=lambda: state.available,
    buildPictureInPictureParams=lambda: "params",
    getPlayer=lambda: engine,
)


def enter(params):
    events.append(("platform", params))
    return state.accepted


activity = Obj(isInPictureInPictureMode=lambda: state.in_pip, enterPictureInPictureMode=enter)
viewer = Obj(getParentActivity=lambda: activity)
plugin = pip.SystemVideoPip()
plugin.ensure_source = lambda _: source
plugin.maximum = Obj(get=lambda _: source if state.priority else None)
plugin.handler_internal = Obj(getBoolean=lambda _: state.internal)
plugin.start_enter = Obj(invoke=lambda handler, args: events.append(("host", handler)))
plugin.no_args = []
assert plugin.enter(viewer)
assert events == ["position", "availability", ("platform", "params"), ("host", "handler")]
events.clear()
state.accepted = False
assert not plugin.enter(viewer)
assert events == ["position", "availability", ("platform", "params")]
events.clear()
state.priority = False
assert not plugin.enter(viewer)
assert events == ["position", "availability"]
events.clear()
state.priority = True
state.internal = True
assert plugin.enter(viewer)
assert events == ["position", "availability"]
events.clear()
state.in_pip = True
assert plugin.enter(viewer)
assert not events

source.delegate = viewer
plugin.active = True
plugin.stash_source = Obj(get=lambda handler: handler.source)
plugin.viewer_type = Obj(isInstance=lambda delegate: delegate is viewer)
plugin.source = Obj(get=lambda delegate: source)
docked = Obj(thisObject=Obj(source=source), setResult=lambda _: events.append("skip"))

# While docked the app must neither auto-pause nor auto-play a manually paused video.
for original in (engine.pause, engine.play):
    events.clear()
    plugin.before_stash_playback(docked)
    if not events:
        original()
    assert events == ["skip"]
events.clear()
plugin.before_stash_playback(Obj(thisObject=Obj(source=Obj(delegate=object())), setResult=docked.setResult))
plugin.before_stash_playback(Obj(thisObject=Obj(source=Obj(delegate=viewer)), setResult=docked.setResult))
plugin.flags = {"system_pip": False}
plugin.before_stash_playback(docked)
assert not events

card = pip.PlaybackCard.__new__(pip.PlaybackCard)
card.source = source
card.plugin = Obj(active=True, card=card)
state.playing = True
state.playback_state = 3
card.on_action(pip.PLAY_PAUSE)
assert events == ["pause"]
events.clear()
state.playback_state = pip.STATE_ENDED
card.on_action(pip.PLAY_PAUSE)
assert events == [("seek", 0), "play"]
events.clear()
card.plugin.card = None
card.on_action(pip.PLAY_PAUSE)
assert not events
print("Passed native PiP routing, edge docking, device refusal, duplicate-entry guards, and media actions")

available_thumbnail = object()
first_publication, frame_reads = [], []
art_viewer = Obj(getVideoSurfaceView=lambda: Obj(
    getWidth=lambda: 640, getHeight=lambda: 360,
    getHolder=lambda: Obj(getSurface=lambda: Obj(isValid=lambda: True)),
))
art_engine = Obj(getPlayWhenReady=lambda: True, getPlaybackState=lambda: 3, getDuration=lambda: 42)
art_card = pip.PlaybackCard.__new__(pip.PlaybackCard)
art_card.plugin = Obj(
    option=lambda _: True, update_visual_card=lambda item, _: first_publication.append(item.cover),
    viewer_texture_uploaded=Obj(getBoolean=lambda _: False), viewer_frame_rendered=Obj(getBoolean=lambda _: True),
)
art_card.source = Obj(delegate=art_viewer)
art_card.cover_key = art_card.cover = art_card.pending_cover = None
art_card.media_details = lambda _: ("cover-key", "视频", "聊天")
art_card.remote, art_card.remote_playing = object(), True
art_card.read_thumbnail = lambda _: available_thumbnail
art_card.publish(art_engine)
assert first_publication == [available_thumbnail] and art_card.cover_key == "cover-key"
art_card.read_thumbnail = lambda _: None
art_card.cover = None
art_card.still_current = lambda key: key == "cover-key"
art_card.copy_cover_from_surface = lambda key, surface: frame_reads.append((key, surface.getWidth()))
art_card.capture_cover("cover-key", 0)
assert frame_reads == [("cover-key", 640)]

background_plugin = pip.SystemVideoPip()
background_plugin.background = None
source_doc = Obj(id=12, access_hash=34, file_reference=b"ref", date=23, size=1000, dc_id=4,
                 file_name="test.mkv", file_name_fixed="test.mkv", mime_type="video/x-matroska", attributes=["video"])
source_item = Obj(currentAccount=1, eventId=0, getId=lambda: 56, getDialogId=lambda: -78,
                  getDuration=lambda: 127.5, getDocument=lambda: source_doc,
                  messageOwner=Obj(peer_id=object(), from_id=object(), date=90, out=False, attachPath=""))
background_plugin.audio_document = lambda: Obj(attributes=MediaList())
background_plugin.audio_attribute = background_plugin.audio_media = background_plugin.audio_message = Obj
background_plugin.message_object = lambda *args: Obj(account=args[0], raw=args[1])
audio_descriptor = background_plugin.make_background_message(source_item, "视频名称", "聊天名称")
assert (audio_descriptor.account, audio_descriptor.raw.id, audio_descriptor.raw.dialog_id) == (1, 56, -78)
audio_doc = audio_descriptor.raw.media.document
assert (audio_doc.id, audio_doc.mime_type, audio_doc.file_name) == (12, "audio/mp4", "test.mkv")
assert [(attr.title, attr.performer, attr.duration) for attr in audio_doc.attributes] == [("视频名称", "聊天名称", 127.5)]
assert source_doc.attributes == ["video"]


def album_video(id, group, text, dialog=-78, account=1):
    return Obj(currentAccount=account, getId=lambda: id, getGroupId=lambda: group,
               getDialogId=lambda: dialog, getDocumentName=lambda: "原始文件.mp4",
               messageOwner=Obj(message=text), caption=None)


album_first = album_video(71, 17, "群组相册的标题\n下一行")
album_second = album_video(72, 17, "")
album_third = album_video(73, 17, "独立说明")
background_plugin.viewer_media = value_field(native_list([
    album_video(1, 17, "其他聊天", -33), album_third, album_second, album_first,
]))
assert background_plugin.video_title(None, album_second) == "群组相册的标题"
assert background_plugin.video_title(None, album_third) == "独立说明"
assert background_plugin.video_title(None, album_video(1, 0, "")) == "原始文件.mp4"
background_plugin.dialog_object = Obj(isChatDialog=lambda dialog: dialog < 0, isUserDialog=lambda dialog: dialog > 0)
background_plugin.java_long = int
background_plugin.messages = Obj(getInstance=lambda account: Obj(getChat=lambda id: Obj(title="聊天名称")))
assert background_plugin.video_artist(album_second) == "聊天名称"
background_plugin.sdk = 35
background_plugin.active = True
target_api = Obj(targetSdkVersion=32)
background_plugin.application = Obj(getApplicationInfo=lambda: target_api)
background_plugin.music_channel = lambda: "native-music-channel"
background_plugin.seek_actions = ((pip.BACK, "后退 15 秒", 102), (pip.FORWARD, "前进 15 秒", 103))
background_plugin.play_icon, background_plugin.pause_icon = 104, 105
background_plugin.stop_icon, background_plugin.notification_icon = 106, 107
assert [row[2] for row in background_plugin.transport_buttons(False)] == [102, 104, 103]
assert [row[2] for row in background_plugin.transport_buttons(True)] == [102, 105, 103]
playback_state = Obj(paused=False, foreground=False)
focus_events, publications, seeks, background_metadata, active_states = [], [], [], [], []
session = Obj(
    setPlaybackState=lambda value: focus_events.append(value),
    setMetadata=background_metadata.append, setActive=active_states.append,
    getSessionToken=lambda: Obj(getToken=lambda: "token"),
)


class MediaNotification(TimerWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.actions = []

    def addAction(self, *args):
        self.actions.append(args)

    def build(self):
        return self


background_plugin.music_session = value_field(session)
session_activity = []
session.getController = lambda: Obj(getSessionActivity=lambda: "native-route")
session.setSessionActivity = session_activity.append
background_plugin.background_session_activity = None
background_plugin.music_foreground = Obj(
    getBoolean=lambda _: playback_state.foreground,
    setBoolean=lambda _, value: setattr(playback_state, "foreground", value),
)
background_plugin.music_playback_state = Obj(set=lambda *_: None)
background_plugin.state_builder = TimerWidget
background_plugin.action_builder = TimerWidget
background_plugin.metadata_builder = TimerWidget
background_plugin.media_style = TimerWidget
background_plugin.notification_builder = MediaNotification
background_plugin.media = Obj(
    isMessagePaused=lambda: playback_state.paused,
    pauseMessage=lambda *args: setattr(playback_state, "paused", True),
    playMessage=lambda *args: setattr(playback_state, "paused", False),
    seekToProgressMs=lambda _, position: seeks.append(position),
)
background_plugin.media_playing_message = Obj(get=lambda _: native_media.message)
background_plugin.manager = Obj(notify=lambda *args: publications.append(("updated", *args)))
background_plugin.stop_background = lambda: events.append("stopped")
service = Obj(startForeground=lambda *args: publications.append(("foreground", *args)))
background_audio = pip.BackgroundAudio.__new__(pip.BackgroundAudio)
background_audio.plugin = background_plugin
background_audio.title, background_audio.cover = "测试视频", None
background_audio.artist = "聊天来源名称"
background_audio.action_names = {code: str(code) for code in (pip.BACK, pip.PLAY_PAUSE, pip.FORWARD, pip.STOP_AUDIO)}
background_audio.pending = background_audio.action_names.copy()
background_audio.open_player = "open-background-video"
background_audio.playback_message = object()
background_audio.player = Obj(
    getCurrentPosition=lambda: 10000,
    getDuration=lambda: 20000,
    player=Obj(getPlaybackParameters=lambda: Obj(speed=1.0)),
)
background_audio.publish(service)
assert publications[0][:2] == ("foreground", pip.MUSIC_NOTIFICATION_ID)
assert focus_events[-1].calls["setState"] == (3, 10000, 1.0)
assert [row[0] for row in publications[-1][2].actions] == [102, 105, 103, 106]
assert background_audio.dispatch(str(pip.PLAY_PAUSE))
background_audio.publish(service)
assert publications[-1][:2] == ("updated", pip.MUSIC_NOTIFICATION_ID)
assert focus_events[-1].calls["setState"] == (2, 10000, 0.0)
assert publications[-1][2].calls["setOngoing"] == (True,)
assert [row[0] for row in publications[-1][2].actions] == [102, 104, 103, 106]
assert "setDeleteIntent" not in publications[-1][2].calls
assert publications[-1][2].calls["setContentText"] == ("聊天来源名称",) and active_states[-1] is True
target_api.targetSdkVersion = 35
background_audio.publish(service)
assert [row[0] for row in publications[-1][2].actions] == [102, 103, 106]
assert publications[-1][2].calls["setStyle"][0].calls["setShowActionsInCompactView"] == (0, 1)
assert focus_events[-1].calls["setActions"] == (4 | 256 | 512,)
assert publications[-1][2].calls["setContentIntent"] == ("open-background-video",)
assert session_activity == ["open-background-video"]
background_plugin.clear_background_session_activity()
assert session_activity[-1] == "native-route"
audio_event_results = []
current_background = background_plugin.current_background
background_plugin.current_background = lambda: background_audio
background_plugin.visual_owner = None
background_plugin.play_state_event = 77
background_plugin.before_music_stop(Obj(setResult=audio_event_results.append))
background_plugin.before_music_event(Obj(args=[77], thisObject=service, setResult=audio_event_results.append))
assert audio_event_results == [None, None] and playback_state.paused and not events
assert focus_events[-1].calls["setState"] == (2, 10000, 0.0)
background_plugin.current_background = current_background
assert background_audio.dispatch(str(pip.BACK)) and background_audio.dispatch(str(pip.FORWARD))
assert seeks == [0, 20000]
assert not background_audio.dispatch("previous-session")
assert background_audio.dispatch(str(pip.STOP_AUDIO)) and events == ["stopped"]
print("Passed foreground audio card, paused card retention, and shared transport icons")

visual = pip.PlaybackCard.__new__(pip.PlaybackCard)
visual_engine = Obj(
    getPlayWhenReady=lambda: not playback_state.paused, getPlaybackState=lambda: 3,
    getDuration=lambda: 20000, getCurrentPosition=lambda: 8000,
    getPlaybackParameters=lambda: Obj(speed=1.0),
    pause=lambda: setattr(playback_state, "paused", True),
)
visual.plugin, visual.source = background_plugin, Obj(getPlayer=lambda: visual_engine, controller=Obj(activity="video"))
visual.tag, visual.cover, visual.open_player = "video-session", None, None
visual.media_details = lambda _: ("video-key", "视频", "视频聊天")
visual.remote = JavaList([Obj(getActionIntent=lambda: None) for _ in range(3)])
visual.last_publication, visual.service_publication = ("video-key", True), None
visual.native_bindings = None
background_plugin.card = visual
background_plugin.visual_owner = None
background_plugin.active = True
background_plugin.music_service_instance = Obj(get=lambda: service)
playback_state.paused = False
background_plugin.update_visual_card(visual, True)
assert background_plugin.current_visual() is visual
assert publications[-1][:2] == ("updated", pip.MUSIC_NOTIFICATION_ID)
assert publications[-1][2].args == (service, "native-music-channel")
assert publications[-1][2].calls["setStyle"][0].calls["setMediaSession"] == ("token",)
assert focus_events[-1].calls["setState"] == (3, 8000, 1.0)
assert publications[-1][2].calls["setContentTitle"] == ("视频",)

pip_state = Obj(active=True)
pip_session = Obj(setActive=lambda value: setattr(pip_state, "active", value),
                  getSessionToken=lambda: Obj(getToken=lambda: "native-video-token"),
                  setMetadata=lambda _: None)
background_plugin.session = value_field(pip_session)
background_plugin.connector = value_field(None)
background_plugin.suppressed_pip = None
assert pip_state.active
background_plugin.manager.getActiveNotifications = lambda: []
background_plugin.confirm_shared_visual(visual, service, 0)
assert pip_state.active and visual.shared_verified is None
assert publications[-1][1] == pip.MUSIC_NOTIFICATION_ID
assert publications[-1][2].calls["setStyle"][0].calls["setMediaSession"] == ("native-video-token",)
background_plugin.update_visual_card(visual, True)
posted = Obj(getId=lambda: pip.MUSIC_NOTIFICATION_ID, getNotification=lambda: Obj(
    extras=Obj(getParcelable=lambda _: "token")))
background_plugin.manager.getActiveNotifications = lambda: [posted]
background_plugin.confirm_shared_visual(visual, service, 0)
assert visual.shared_verified is service
assert not pip_state.active
background_plugin.after_music_destroy(Obj(thisObject=service))
assert pip_state.active
assert publications[-1][2].calls["setStyle"][0].calls["setMediaSession"] == ("native-video-token",)
background_plugin.service_start_requested = False
background_plugin.application = Obj(startService=lambda _: None, getApplicationInfo=lambda: target_api)
background_plugin.music_service = object()
background_plugin.intent = lambda *args: Obj(setAction=lambda name: name)
background_plugin.visual_service_action = "video-card"
startup_errors = []
background_plugin.log = startup_errors.append
visual.native_publication = None
background_plugin.update_visual_card(visual, True)
assert len(startup_errors) == 1 and "MusicPlayerService did not start" in startup_errors[0]
assert not background_plugin.service_start_requested and pip_state.active
assert publications[-1][2].calls["setStyle"][0].calls["setMediaSession"] == ("native-video-token",)
background_plugin.music_service_instance = Obj(get=lambda: service)

audio_selection = Obj(isMusic=lambda: True)
background_plugin.media.getPlayingMessageObject = lambda: audio_selection
native_restore = []
background_plugin.music_create_notification = Obj(invoke=lambda *args: native_restore.append(args))
background_plugin.java_boolean, background_plugin.object_args = bool, list
background_plugin.after_native_music_play(Obj(args=[audio_selection, False], getResult=lambda: True))
assert playback_state.paused and background_plugin.current_visual() is None
assert native_restore == [(service, [audio_selection, False])]
assert all(row[1] == pip.MUSIC_NOTIFICATION_ID for row in publications)
print("Passed video and audio ownership changes on the same native service, token, and notification ID")

handoff_events = []
native_media = Obj(video=None, message=None)
background_plugin.active = True
background_plugin.background = None
background_plugin.background_choice = background_plugin.background_before_pause = None
background_plugin.detached_background_viewer = None
background_plugin.ordinary_video = lambda _, **kwargs: True
background_plugin.drop_card = lambda **_: handoff_events.append("remove-video-card")
window = Obj(clearFlags=lambda flags: handoff_events.append(("clear-screen-on", flags)))
parent = Obj(getWindow=lambda: window, isInPictureInPictureMode=lambda: False)
message = Obj(isVideo=lambda: True, getDocument=lambda: object(), currentAccount=0,
              getDialogId=lambda: 3, getId=lambda: 7)
pip_playback = Obj(playing=True, pip_closed=False)
engine = Obj(getPlaybackState=lambda: 3, getPlayWhenReady=lambda: pip_playback.playing)
player = Obj(
    player=engine, setTextureView=lambda value: handoff_events.append(("texture", value)),
    setSurfaceView=lambda value: handoff_events.append(("surface-view", value)),
    setSurface=lambda value: handoff_events.append(("surface", value)),
    getVolume=lambda: 0.7, setVolume=lambda value: handoff_events.append(("volume", value)),
    play=lambda: handoff_events.append("play"), pause=lambda: handoff_events.append("direct-pause"),
)
viewer = Obj(
    isVisible=lambda: True, getCurrentMessageObject=lambda: message,
    getParentActivity=lambda: parent, video=player,
    closePhoto=lambda *args: handoff_events.append(("close-viewer", *args)),
)
viewer.getVideoPlayer = lambda: viewer.video


def inject(player_to_move, item):
    native_media.video, native_media.message = player_to_move, item
    handoff_events.append("native-ownership")


background_plugin.media = Obj(
    getVideoPlayer=lambda: native_media.video, getPlayingMessageObject=lambda: native_media.message,
    injectVideoPlayer=inject, pauseMessage=lambda *_: handoff_events.append("pause"),
)
original_tracks = Obj(buildUpon=lambda: Obj(
    setTrackTypeDisabled=lambda kind, disabled: Obj(build=lambda: (kind, disabled))))
background_plugin.track_selector = value_field(Obj(
    getParameters=lambda: original_tracks,
    setParameters=lambda value: handoff_events.append(("tracks", value)),
))
background_plugin.viewer_player = Obj(set=lambda target, value: setattr(target, "video", value))
background_plugin.music_service = object()
background_plugin.intent = lambda *args: args
background_plugin.application = Obj(
    startForegroundService=lambda intent: handoff_events.append("foreground-service") or object(),
)
background_plugin.music_service_instance = None
background_plugin.weak = lambda current: Obj(get=lambda: current)
background_plugin.source = value_field(None)
background_plugin.update_background_item = lambda current: handoff_events.append(
    ("item", background_plugin.background_armed(current)))
background_plugin.on_background_handoff = lambda _: handoff_events.append("transfer-timer")
background_plugin.background_chats = {}
background_plugin.get_setting = lambda key, default: default
setting_updates = []
background_plugin.set_setting = lambda *args: setting_updates.append(args)
background_plugin.toggle_background(viewer)
assert viewer.video is player and handoff_events == [("item", True)]
background_plugin.toggle_background(viewer)
assert viewer.video is player and handoff_events[-1] == ("item", False)
background_plugin.toggle_background(viewer)
assert setting_updates == [("background_audio_chat_0_3", value) for value in (True, False, True)]
other_chats = (Obj(currentAccount=0, getDialogId=lambda: 4), Obj(currentAccount=1, getDialogId=lambda: 3))
assert not any(background_plugin.background_chat_enabled(item) for item in other_chats)
prior_background = background_plugin.current_background
prior_stop = background_plugin.stop_background
old_media = object()
stopped_old_media = []
background_plugin.current_background = lambda: old_media
background_plugin.stop_background = lambda: stopped_old_media.append(old_media)
second_video = Obj(isVideo=lambda: True, getDocument=lambda: object(), currentAccount=0,
                   getDialogId=lambda: 3, getId=lambda: 8)
second_viewer = Obj(isVisible=lambda: True, getCurrentMessageObject=lambda: second_video)
background_plugin.toggle_background(second_viewer)
assert stopped_old_media == [old_media] and not background_plugin.background_chat_enabled(second_video)
background_plugin.current_background = prior_background
background_plugin.stop_background = prior_stop
background_plugin.toggle_background(viewer)
loop_row, cast_row, listen_row, autoplay_row = (PopupChild() for _ in range(4))
background_menu = PopupRows(loop_row, cast_row, listen_row, autoplay_row)
background_plugin.loop_item = value_field(loop_row)
for _ in range(2):
    background_plugin.place_video_item_by_loop(viewer, listen_row, below=True)
    background_plugin.place_video_item_by_loop(viewer, autoplay_row, below=False)
    assert background_menu.rows == [autoplay_row, loop_row, listen_row, cast_row]
styles = []
background_plugin.style_background_item(Obj(setColors=lambda *args: styles.append(args),
                                            setSelected=styles.append), True)
assert styles == [(pip.BACKGROUND_AUDIO_BLUE, pip.BACKGROUND_AUDIO_BLUE), True]
handoff_events.clear()

params_state = Obj(result=None, auto=True)
builder = Obj()
builder.setActions = lambda actions: builder
builder.setAutoEnterEnabled = lambda enable: setattr(params_state, "auto", enable) or builder
builder.build = lambda: "manual-pip-params"
source = Obj(delegate=viewer, params=Obj(build=lambda: builder), getPlayer=lambda: engine)
background_plugin.sdk = 35
background_plugin.viewer_type = Obj(isInstance=lambda target: target is viewer)
background_plugin.remote_actions = value_field("actions")
background_plugin.pip_action_stack = [(False, None)]
background_plugin.after_pip_params(Obj(thisObject=source,
                                       setResult=lambda result: setattr(params_state, "result", result)))
assert not params_state.auto and params_state.result == "manual-pip-params"

background_plugin.handler_activity = value_field(parent)
background_plugin.handler_internal = Obj(getBoolean=lambda _: pip_playback.pip_closed)
background_plugin.launch = Obj(isInstance=lambda _: True)
parent.getPipController = lambda: object()
background_plugin.maximum = value_field(source)
handled = []
background_plugin.before_native_enter(Obj(thisObject=object(), setResult=handled.append))
assert handled == [None]

pip_globals = pip.SystemVideoPip.start_background.__globals__
real_background_type = pip_globals["BackgroundAudio"]
playback_message = Obj(isMusic=lambda: True, isVideo=lambda: False)
pip_globals["BackgroundAudio"] = lambda _, viewer, message, player, original: Obj(
    message=message, playback_message=playback_message, player=player, track_selection=original,
    title="当前视频", artist="聊天名字", open_action="test.open-background-video.active",
)
try:
    background_plugin.before_leave(Obj(thisObject=viewer, setResult=handled.append))
    assert handled == [None, None]
    assert viewer.video is None and background_plugin.current_background().player is player
    assert native_media.message is playback_message and native_media.message.isMusic() and not native_media.message.isVideo()
    assert message.isVideo()
    assert handoff_events == [
        "remove-video-card", "native-ownership", ("texture", None), ("surface-view", None), ("surface", None),
        ("tracks", (2, True)), ("volume", 0.7), "play", "foreground-service", "transfer-timer",
        ("close-viewer", False, False), ("clear-screen-on", 128),
    ]
    audio = background_plugin.current_background()
    audio.notification_requested = False
    service_start = background_plugin.application.startForegroundService
    background_plugin.application.startForegroundService = lambda _: None
    delivery_errors = []
    background_plugin.log = delivery_errors.append
    background_plugin.ensure_background_notification(audio)
    assert background_plugin.current_background() is audio and not audio.notification_requested
    assert delivery_errors and "MusicPlayerService did not start" in delivery_errors[-1]
    background_plugin.application.startForegroundService = service_start
    background_plugin.after_background_resume(Obj())
    assert background_plugin.current_background() is audio and audio.notification_requested
    guarded = []
    scrolled = Obj(args=[True, True, False, False], setResult=guarded.append)
    two_args = Obj(args=[True, True], setResult=guarded.append)
    frame = Obj(owner="org.telegram.ui.ChatActivity", name="updateMessagesVisiblePart")
    frame.getClassName = lambda: frame.owner
    frame.getMethodName = lambda: frame.name
    background_plugin.java_thread = Obj(currentThread=lambda: Obj(getStackTrace=lambda: [frame]))
    background_plugin.before_background_cleanup(two_args)
    background_plugin.before_background_cleanup(scrolled)
    background_plugin.before_background_video_attachment(scrolled)
    frame.name = "onRemoveFromParent"
    background_plugin.before_background_cleanup(two_args)
    frame.owner, frame.name = "org.telegram.messenger.MediaController$7", "lambda$onSurfaceDestroyed$0"
    background_plugin.before_background_cleanup(two_args)
    background_plugin.before_background_surface_destroyed(Obj(thisObject=object(), setResult=guarded.append))
    background_plugin.before_background_surface_destroyed(Obj(thisObject=player, setResult=guarded.append))
    assert guarded == [None, None, None, None, None, False]
    assert background_plugin.current_background().player is player
    frame.owner, frame.name = "org.telegram.ui.Components.FragmentContextView", "closePlayer"
    background_plugin.before_background_cleanup(two_args)  # The intentional close reaches native cleanup.
    assert len(guarded) == 6
    assert background_plugin.background_chat_enabled(message)
    background_plugin.before_background_cleanup(Obj(args=[True, True, False, True]))
    assert background_plugin.background is None and handoff_events[-1] == ("tracks", original_tracks)
    native_media.video = native_media.message = None
    viewer.video = player
    background_plugin.sync_background_choice(viewer)
    assert background_plugin.background_armed(viewer)
    background_plugin.before_viewer_pause(Obj(thisObject=viewer))
    pip_playback.playing = False
    pip_playback.pip_closed = True
    handoff_events.clear()
    background_plugin.before_activity_stop(Obj(thisObject=object()))
    assert "pause" in handoff_events and "play" not in handoff_events
    assert viewer.video is None and background_plugin.current_background().player is player
    assert background_plugin.detached_background_viewer.get() is viewer
    background_plugin.transfers = []
    background_plugin.viewer_window_hidden = Obj(setBoolean=lambda _, hidden: handoff_events.append(hidden))
    transfer = Obj(thisObject=viewer, args=[None], setResult=handled.append)
    background_plugin.before_transfer(transfer)
    background_plugin.after_transfer(transfer)
    assert handled[-1] is None and handoff_events[-1] is False
    assert background_plugin.current_background().player is player
    background_plugin.before_background_cleanup(Obj(args=[True, True, False, True]))
    native_media.video = native_media.message = None
    viewer.video = player
    pip_playback.playing = False
    background_plugin.sync_background_choice(viewer)
    background_plugin.remember_background_playback(Obj(thisObject=viewer))
    pip_playback.playing = True
    handoff_events.clear()
    background_plugin.before_viewer_closed(Obj(thisObject=viewer))
    assert handoff_events[0] == "direct-pause" and "pause" in handoff_events
    assert "play" not in handoff_events and background_plugin.current_background().notification_requested
    background_plugin.before_background_cleanup(Obj(args=[True, True, False, True]))
    native_media.video = native_media.message = None
    viewer.video = player
    pip_playback.playing = True
    handoff_events.clear()
    background_plugin.before_activity_stop(Obj(thisObject=object()))
    assert not handoff_events
    background_plugin.sync_background_choice(viewer)
    background_plugin.before_activity_stop(Obj(thisObject=object()))
    assert "play" in handoff_events and "pause" not in handoff_events
    assert background_plugin.current_background().player is player
    changes = []
    bar = Obj(style=0, message=message)
    bar.getCurrentStyle = lambda: bar.style
    label = Obj(text="未知艺术家 - 当前视频")
    label.getText = lambda: label.text
    label.setText = lambda text: (changes.append(text), setattr(label, "text", text))
    background_plugin.in_app_title_view = value_field(Obj(getTextView=lambda: label))
    background_plugin.in_app_message = Obj(get=lambda view: view.message)
    bar_update = Obj(thisObject=bar)
    background_plugin.after_in_app_player(bar_update)
    bar.message, bar.style = playback_message, 3
    background_plugin.after_in_app_player(bar_update)
    assert not changes
    bar.style = 0
    background_plugin.after_in_app_player(bar_update)
    background_plugin.after_in_app_player(bar_update)
    assert changes == ["聊天名字 - 当前视频"] and label.text == "聊天名字 - 当前视频"
    background_plugin.current_background().artist = None
    background_plugin.after_in_app_player(bar_update)
    assert label.text == "当前视频"
    refreshed = []
    background_plugin.dialogs_bar = value_field(bar)
    background_plugin.check_player = Obj(invoke=lambda *args: refreshed.append(args))
    background_plugin.after_dialogs_visible(Obj(thisObject=object()))
    assert refreshed == [(bar, [False])]
    background_plugin.android = Obj(findActivity=lambda _: parent, needShowPasscode=lambda _: False)
    bar.getContext = lambda: object()
    bar.getCurrentStyle = lambda: 3
    audio = background_plugin.current_background()
    return_events = []
    open_background_video = background_plugin.open_background_video
    background_plugin.open_background_video = lambda *args: return_events.append(args)
    bar_click = Obj(thisObject=bar, setResult=lambda _: return_events.append("consume"))
    background_plugin.before_in_app_bar_click(bar_click)
    assert not return_events
    bar.getCurrentStyle = lambda: 0
    background_plugin.before_in_app_bar_click(bar_click)
    assert return_events == ["consume", (audio, parent)]
    background_plugin.open_background_action = "test.open-background-video."
    background_plugin.shared_config = Obj(isWaitingForPasscodeEnter=True)
    pending_open = []
    previous_ui = pip_globals["run_on_ui_thread"]
    pip_globals["run_on_ui_thread"] = lambda callback, _: pending_open.append(callback)
    try:
        intent = Obj(getAction=lambda: audio.open_action)
        intent_results = []
        click = Obj(args=[intent], thisObject=parent, setResult=intent_results.append)
        background_plugin.before_background_intent(click)
        assert not pending_open and not intent_results
        background_plugin.shared_config.isWaitingForPasscodeEnter = False
        background_plugin.before_background_intent(click)
        assert intent_results == [True] and len(pending_open) == 1
        pending_open.pop()()
        assert return_events[-1] == (audio, parent)
        intent.getAction = lambda: "test.open-background-video.stale"
        background_plugin.before_background_intent(click)
        assert not pending_open and intent_results == [True, True]
    finally:
        pip_globals["run_on_ui_thread"] = previous_ui
    background_plugin.open_background_video = open_background_video
    background_plugin.before_background_cleanup(Obj(args=[True, True, False, True]))
    native_media.video = native_media.message = None
    viewer.video = player
    background_plugin.sync_background_choice(viewer)
    handoff_events.clear()
    background_plugin.before_viewer_release(Obj(thisObject=viewer, args=[False]))
    assert not handoff_events and viewer.video is player
    background_plugin.before_viewer_release(Obj(thisObject=viewer, args=[True]))
    background_plugin.before_viewer_closed(Obj(thisObject=viewer))
    assert handoff_events.count("native-ownership") == 1 and ("close-viewer", False, False) not in handoff_events
    assert background_plugin.current_background().player is player

    audio = background_plugin.current_background()
    audio.dialogs, audio.uri, audio.qualities = (3, 0, 0), "video-uri", None
    background_plugin.background_return = None
    background_plugin.launch = Obj(isInstance=lambda activity: activity is parent)
    parent.isFinishing = lambda: False
    background_plugin.user_config = Obj(selectedAccount=message.currentAccount)
    background_plugin.no_place_provider = lambda: "no-cell"
    background_plugin.media_video_player = Obj(
        get=lambda _: native_media.video, set=lambda _, value: setattr(native_media, "video", value))
    background_plugin.media.resetGoingToShowMessageObject = lambda: return_events.append("reset-target")
    background_plugin.media.isMessagePaused = lambda: True
    background_plugin.java_long = int
    reopened = Obj(isVisible=lambda: False, getCurrentMessageObject=lambda: message,
                   setParentActivity=lambda activity: return_events.append(activity))
    background_plugin.photo_viewer = Obj(getInstance=lambda: reopened)
    reopened.openPhoto = lambda *args: return_events.append(args) or False
    background_plugin.open_background_video(audio, parent)
    assert background_plugin.current_background() is audio and background_plugin.background_return is None

    def finish_transfer(*args):
        background_plugin.before_background_cleanup(Obj(args=args))
        assert args == (True, False, False, True)
        native_media.message = None
        return_events.append(native_media.video)

    background_plugin.media.cleanupPlayer = finish_transfer
    reopened.openPhoto = lambda *args: return_events.append(args) or True

    def prepare_reopened(target, args):
        assert args == [None, "video-uri", False, False, None, False, 0]
        background_plugin.before_background_return(Obj(thisObject=target))

    background_plugin.prepare_video = Obj(invoke=prepare_reopened)
    background_plugin.open_background_video(audio, parent)
    assert return_events[-4:] == [parent, (message, 3, 0, 0, "no-cell", True), player, "reset-target"]
    assert background_plugin.background_return is None and native_media.video is None
    assert background_plugin.current_background() is None and handoff_events[-1] == ("tracks", original_tracks)
finally:
    pip_globals["BackgroundAudio"] = real_background_type

viewer.video = player
background_plugin.card = Obj(source=Obj(delegate=viewer, getPlayer=lambda: engine))
background_plugin.eligible = lambda _: True
kept = []
background_plugin.retain_paused_card(Obj(thisObject=viewer, getResult=lambda: False, setResult=kept.append))
assert kept == [True]
print("Passed background audio, viewer and PiP handoffs, and native in-app playback bar scope")

autoplay = pip.SystemVideoPip()
autoplay.active, autoplay.autoplay_enabled, autoplay.autoplay_pending = True, True, None
autoplay.flags = {"video_autoplay": True}
autoplay_player = Obj(isLooping=lambda: False)
movie = Obj(currentAccount=0, getDialogId=lambda: -100, getId=lambda: 1,
            isVideo=lambda: True, getDocument=lambda: object())
next_movie = Obj(currentAccount=0, getDialogId=lambda: -100, getId=lambda: 3,
                 isVideo=lambda: True, getDocument=lambda: object())
foreign_movie = Obj(currentAccount=0, getDialogId=lambda: -200, getId=lambda: 2,
                    isVideo=lambda: True, getDocument=lambda: object())
autoplay_viewer = Obj(getCurrentMessageObject=lambda: movie)
autoplay.viewer_media = value_field(native_list([movie, first_pic, foreign_movie, next_movie]))
assert list(autoplay.next_viewer_video(autoplay_viewer, 0)) == [(3, next_movie)]
assert autoplay.allow_autoplay(autoplay_player)
autoplay.autoplay_timer_due = lambda _: True
assert not autoplay.allow_autoplay(autoplay_player)
autoplay.autoplay_timer_due = lambda _: False
tracks = Obj(player=autoplay_player, playback_message=object(), queue=(foreign_movie, next_movie))
autoplay.current_background = lambda: tracks
autoplay.media = Obj(isMessagePaused=lambda: False)
autoplay.background_video_uri = lambda message: "next" if message is next_movie else None
advance_calls, scheduled, blocked = [], [], []
autoplay.advance_background_video = lambda *args: advance_calls.append(args)
pipeline = autoplay.before_background_player_state.__globals__
old_scheduler = pipeline["run_on_ui_thread"]
pipeline["run_on_ui_thread"] = lambda callback, _: scheduled.append(callback)
try:
    ended = Obj(args=[tracks.playback_message, None, True, True, pip.STATE_ENDED], setResult=blocked.append)
    autoplay.before_background_player_state(ended)
    autoplay.before_background_player_state(ended)
    assert blocked == [None, None] and len(scheduled) == 1
    scheduled.pop()()
    assert advance_calls == [(tracks, next_movie, "next", ())] and autoplay.autoplay_pending is None
finally:
    pipeline["run_on_ui_thread"] = old_scheduler

modes = pip.SystemVideoPip()
modes.autoplay_enabled, modes.loop_override = False, None
modes.flags = {"video_autoplay": True}
modes.ordinary_video = lambda _: True
saved_modes, saved_looping = [], []
modes.set_setting = lambda _, value: saved_modes.append(value)
modes.video_type = Obj(saveLooping=lambda enabled, _: saved_looping.append(enabled))
playing = Obj(looping=True)
playing.setLooping = lambda enabled: setattr(playing, "looping", enabled)
mode_viewer = Obj(loop=True, getVideoPlayer=lambda: playing, getCurrentMessageObject=lambda: movie)
modes.viewer_looping = Obj(getBoolean=lambda target: target.loop,
                           setBoolean=lambda target, value: setattr(target, "loop", value))
modes.loop_item = value_field(None)
modes.weak = lambda item: Obj(get=lambda: item)
assert modes.video_playback_mode(mode_viewer) == pip.VIDEO_PLAY_LOOP
for selected, looping in ((pip.VIDEO_PLAY_CONTINUOUS, False), (pip.VIDEO_PLAY_STOP, False),
                          (pip.VIDEO_PLAY_LOOP, True)):
    modes.select_video_playback_mode(mode_viewer, selected)
    assert modes.video_playback_mode(mode_viewer) == selected and playing.looping is looping
assert saved_modes == [True, False] and saved_looping == [False, True]

suite_module = load("nagramxf_media_suite")
assert suite_module.__name__ == "NagramXF 增强 · Enhancer"
mode_suite = suite_module.NagramXFMediaSuite()
mode_suite.get_capsule_ui = lambda: popup
mode_order = (suite_module.VIDEO_PLAY_STOP, suite_module.VIDEO_PLAY_CONTINUOUS, suite_module.VIDEO_PLAY_LOOP)
for initial in mode_order:
    picks = []
    mode_menu = mode_suite.make_playback_mode_capsule(None, initial, picks.append)
    labels = [label for label in mode_menu.children[0].children if "Text" in vars(label)]
    assert [label.Text for label in labels] == ["播完停止", "连续播放", "循环播放"]
    assert labels[mode_order.index(initial)].Selected
    for label in labels:
        label.OnClickListener(label)
    assert tuple(picks) == mode_order
results = []
format_counts = object.__new__(suite_module.TenThousandCounts)
for original, native, label, rounded in ((48000, "48K", "4.8W", 48000),
                                         (48000, "48000", None, 48000),
                                         (9800, "9.8K", "9800", 9800),
                                         (190_000_000, "190M", "1.9亿", 190_000_000)):
    results.clear()
    out = [original]
    format_counts.after_format(Obj(args=[original, out], getResult=lambda: native, setResult=results.append))
    assert results == ([] if label is None else [label]) and out == [rounded]
suite = suite_module.NagramXFMediaSuite()
assert {feature: keys for feature, keys in suite_module.FEATURES}[suite_module.FastViewerPlugin] == ("fast_viewer",)
assert {feature: keys for feature, keys in suite_module.FEATURES}[suite_module.AyuFilterDisplayFix] == ("filter_display",)
suite.get_setting = lambda key, default: key == "double_tap"
suite.set_setting = lambda key, value: None
suite.log = lambda value: None
suite.hook_method = lambda *args, **kwargs: None
suite.hook_all_constructors = lambda *args, **kwargs: []
suite.unhook_method = lambda *args: None
suite.on_plugin_load()
assert sum(suite.flags.values()) == 1 and suite.flags["double_tap"]
suite.change_feature("pinch", True)
assert suite.flags["double_tap"] and suite.flags["pinch"] and not suite.flags["video_toolbar"]
assert set(suite.flags) == {key for key, _, _ in suite_module.SETTINGS}
suite.on_plugin_unload()
suite.get_setting = lambda key, default: default
suite.on_plugin_load()
assert suite.flags["auto_fullscreen"] and not suite.flags["auto_fullscreen_on_switch"]
sys.modules["ui.settings"] = ModuleType("ui.settings")
for control in ("Input", "Switch"):
    setattr(sys.modules["ui.settings"], control, Obj)
sys.modules["ui.settings"].Selector = lambda *, key, text, default, items, on_change: Obj(
    key=key, text=text, default=default, items=items, on_change=on_change)
sys.modules["ui.settings"].Header = lambda **kwargs: Obj(section=True, **kwargs)


class SettingsFactory:
    def __init__(self, create, bind):
        self.create_view, self.bind_view = create, bind

    def __call__(self):
        return Obj(factory=self)


sys.modules["ui.settings"].SimpleSettingFactory = SettingsFactory
rows = suite.create_settings()
video_settings = {row.key: row for row in rows if hasattr(row, "key")}
assert "double_tap_seconds" not in video_settings
assert video_settings["thumbnail_portrait_position"].default == suite_module.THUMBNAIL_POSITION_BOTTOM
assert suite_module.SUITE_DEFAULTS["adjustment_tick_strength"] == 60
assert suite_module.SUITE_DEFAULTS["adjustment_tick_rate"] == 30
assert video_settings["thumbnail_portrait_position"].items == ["右侧", "屏幕底部"]
assert video_settings["thumbnail_default_state"].default == suite_module.THUMBNAIL_START_COLLAPSED
assert video_settings["thumbnail_default_state"].items == ["收起", "展开"]
assert video_settings["thumbnail_state_scope"].default == suite_module.THUMBNAIL_STATE_CHAT
assert video_settings["thumbnail_state_scope"].items == ["全局记忆", "按聊天记忆"]
assert [row.text for row in rows if getattr(row, "section", False)] == [
    "媒体浏览", "播放器界面", "聊天界面", "播放手势", "手势振动", "全屏与旋转", "音频与播控"]

dynamic_rows = object.__new__(suite_module.PluginSettingRows)
dynamic_rows.dp = int
dynamic_rows.measure_spec = Obj(getSize=int, makeMeasureSpec=lambda size, mode: size, EXACTLY=1, UNSPECIFIED=0)
settings_list = object()
dynamic_rows.lists = [Obj(get=lambda: settings_list)]
title_layout = Obj(topMargin=10, leftMargin=20, rightMargin=70)
detail_layout = Obj(topMargin=35)
title_measure = Obj(height=20, width=0)
setting_title = Obj(getLayoutParams=lambda: title_layout, getMaxLines=lambda: 2147483647,
                    getEllipsize=lambda: None, getMeasuredHeight=lambda: title_measure.height,
                    measure=lambda width, _: setattr(title_measure, "width", width))
setting_detail = Obj(getLayoutParams=lambda: detail_layout, getMaxLines=lambda: 2147483647,
                     getEllipsize=lambda: None, getVisibility=lambda: 0)
dynamic_rows.row_title, dynamic_rows.row_detail = value_field(setting_title), value_field(setting_detail)
setting_cell = Obj(getParent=lambda: settings_list, getPaddingLeft=lambda: 0, getPaddingRight=lambda: 0)
for width, lines, detail_top in ((420, 1, 33), (260, 2, 53), (220, 3, 73)):
    title_measure.height = 20 * lines
    dynamic_rows.measure_text_rows(Obj(thisObject=setting_cell, args=[width, 0]))
    assert title_measure.width == width - 90 and detail_layout.topMargin == detail_top
setting_cell.getParent = lambda: object()
dynamic_rows.measure_text_rows(Obj(thisObject=setting_cell, args=[420, 0]))
assert detail_layout.topMargin == 73
setting_writes, intercepted = [], []
engine = Obj(setPluginSetting=lambda *args: setting_writes.append(args))
controller = Obj(getPluginEngine=lambda _: engine)
dynamic_rows.settings_engine_type = object()
dynamic_rows.settings_reset = None
for plugin_id, key in ((suite_module.__id__, "pinch"), ("other_plugin", "pinch"), (suite_module.__id__, "plugin_language")):
    dynamic_rows.save_switch_without_rebind(Obj(thisObject=controller, args=[plugin_id, key, False],
                                               setResult=intercepted.append))
assert setting_writes == [(suite_module.__id__, "pinch", False)] and intercepted == [None]
slider_factories = dict(suite.slider_factories)
assert set(slider_factories) == {"hold_speed_preset", "adjustment_tick_strength",
                                 "adjustment_tick_rate", "adjustment_tick_percent"}
suite.create_settings()
assert slider_factories == suite.slider_factories
preferences = Obj()
suite.get_setting = lambda key, default: getattr(preferences, key, default)
suite.set_setting = lambda key, value: setattr(preferences, key, value)
slider_events = []
capsule = Obj(frame_layout=object(), frame_params=lambda *args: args,
              make_gear_capsule=lambda *args, **kwargs: slider_events.append((args, kwargs)))
suite.get_capsule_ui = lambda: capsule
theme = Obj(getColor=lambda key: key, key_windowBackgroundWhiteBlackText=-16777216,
            key_dialogTextGray2=-6250336, key_windowBackgroundWhiteBlueText=-11183361,
            key_windowBackgroundWhite=-1)
slider_host = Obj(getContext=lambda: None, setBackgroundColor=lambda _: None,
                  removeAllViews=lambda: None, addView=lambda *_: None)
suite_namespace = suite_module.NagramXFMediaSuite.slider_setting.__globals__
original_jclass = suite_namespace["jclass"]
suite_namespace["jclass"] = lambda _: theme
try:
    slider_factories["adjustment_tick_strength"].bind_view(slider_host, None, False, None, None)
    args, kwargs = slider_events[-1]
    assert kwargs["steps"] == 100 and args[5](args[4]) == "60%"
    args[6](False, 0.6, None)
    assert not hasattr(preferences, "adjustment_tick_strength")
    args[6](True, 0.6, None)
finally:
    suite_namespace["jclass"] = original_jclass
video_settings["thumbnail_default_state"].on_change(suite_module.THUMBNAIL_START_EXPANDED)
video_settings["thumbnail_state_scope"].on_change(suite_module.THUMBNAIL_STATE_GLOBAL)
video_settings["thumbnail_portrait_position"].on_change(suite_module.THUMBNAIL_POSITION_BOTTOM)
suite.change_video_value("thumbnail_size", 4)
suite.change_video_value("adjustment_tick_rate", 9)
suite.change_video_value("adjustment_tick_percent", 2)
configured_video = suite_module.VideoSeekbarGestureInsets(suite, {})
suite.configure_video_values(configured_video)
assert configured_video.thumbnail_widths_dp == (120, 120)
assert configured_video.adjustment_tick_interval_ms == 112 and configured_video.adjustment_tick_percent == 2
assert configured_video.adjustment_tick_strength == 60
assert configured_video.thumbnail_state_config == (suite_module.THUMBNAIL_STATE_GLOBAL, False)
assert configured_video.thumbnail_portrait_position == suite_module.THUMBNAIL_POSITION_BOTTOM
suite.change_feature("auto_fullscreen_on_switch", True)
assert suite.flags["auto_fullscreen_on_switch"]
suite.on_plugin_unload()

fast_feature = suite_module.FastViewerPlugin
filter_feature = suite_module.AyuFilterDisplayFix
folder_feature = suite_module.ChatFolderReturn
folder_return = object.__new__(folder_feature)
active_folder_page = Obj(selected=1)
folder_ui = Obj(stable=42, account=0, order=[0, 42, 57], locked=set())
folder_return.origins = []
folder_return.weak = lambda item: Obj(get=lambda: item)
folder_return.selected = Obj(getInt=lambda page: page.selected, setInt=lambda page, value: setattr(page, "selected", value))
folder_return.pages = value_field([active_folder_page])
folder_events = []


def folder_selection(stable):
    folder_events.append(("selected", stable))
    folder_ui.stable = stable
    return True


folder_tabs = Obj(
    getVisibility=lambda: 0, getTabsCount=lambda: len(folder_ui.order), getCurrentTabStableId=lambda: folder_ui.stable,
    isFirstTabSelected=lambda: folder_ui.stable == folder_ui.order[0],
    getStableId=lambda position: folder_ui.order[position],
    getTab=lambda position: Obj(id=position, isLocked=folder_ui.order[position] in folder_ui.locked),
    selectTabWithStableId=folder_selection, finishAddingTabs=lambda animated: folder_events.append(("tabs", animated)),
    getTabsContainer=lambda: Obj(scrollToPosition=lambda position: folder_events.append(("scroll", position))),
)
folder_filters = Obj(getDialogFilters=lambda: JavaList(
    Obj(localId=stable, isDefault=lambda stable=stable: stable == 0) for stable in folder_ui.order))
folder_nav = Obj(stack=JavaList())
folder_nav.getLastFragment = lambda: folder_nav.stack[-1]
folder_nav.getFragmentStack = lambda: folder_nav.stack
folder_dialogs = Obj(
    getParentLayout=lambda: folder_nav, getCurrentAccount=lambda: folder_ui.account,
    getMessagesController=lambda: folder_filters,
    switchToCurrentSelectedMode=lambda animated: folder_events.append(("page", active_folder_page.selected, animated)),
)
folder_chat = Obj(getParentLayout=lambda: folder_nav, getCurrentAccount=lambda: 0, isInPreviewMode=lambda: False)
folder_return.tabs = value_field(folder_tabs)
folder_return.dialogs_type = Obj(isInstance=lambda item: item is folder_dialogs)
folder_home = Obj(getCurrentVisibleFragment=lambda: folder_dialogs)
folder_return.main_tabs_type = Obj(isInstance=lambda item: item is folder_home)
folder_nav.stack[:] = [folder_home, folder_chat]
folder_chat_event, folder_dialog_event = Obj(thisObject=folder_chat), Obj(thisObject=folder_dialogs)
folder_return.remember_folder(folder_chat_event)
assert len(folder_return.origins) == 1
folder_ui.order[:], folder_ui.stable, active_folder_page.selected = [0, 57, 42], 0, 0
folder_return.remember_folder(folder_chat_event)  # The chat may resume again after the list was rebuilt.
folder_return.restore_folder(folder_dialog_event)
assert folder_events == [("selected", 42), ("page", 2, False), ("tabs", False), ("scroll", 2)]
assert folder_return.origins  # A predictive-back preview can still be canceled.
folder_events.clear()
folder_return.restore_folder(folder_dialog_event, committed=True)
assert folder_return.origins and not folder_events  # Chat is still at the top of the stack.
folder_nav.stack.pop()
folder_return.restore_folder(folder_dialog_event, committed=True)
assert not folder_return.origins and not folder_events
folder_ui.stable = 57
folder_return.restore_folder(folder_dialog_event)
assert folder_ui.stable == 57 and not folder_events
for unavailable in ("deleted", "locked", "other account"):
    folder_ui.order[:], folder_ui.stable, folder_ui.account = [0, 57, 42], 42, 0
    folder_ui.locked.clear()
    folder_nav.stack[:] = [folder_dialogs, folder_chat]
    folder_return.remember_folder(folder_chat_event)
    folder_nav.stack.pop()
    folder_ui.stable, active_folder_page.selected = 0, 0
    if unavailable == "deleted":
        folder_ui.order.remove(42)
    elif unavailable == "locked":
        folder_ui.locked.add(42)
    else:
        folder_ui.account = 1
    folder_return.restore_folder(folder_dialog_event, committed=True)
    assert not folder_return.origins and not folder_events

for feature in (fast_feature, filter_feature, folder_feature):
    feature.on_plugin_load = lambda self: setattr(self, "loaded", True)
    feature.on_plugin_unload = lambda self: setattr(self, "loaded", False)
suite.get_setting = lambda key, default: key in ("fast_viewer", "filter_display")
suite.on_plugin_load()
suite.apply_settings()
assert set(suite.components) == {fast_feature, filter_feature, folder_feature}
fast_component = suite.components[fast_feature][1]
filter_component = suite.components[filter_feature][1]
assert fast_component.loaded and filter_component.loaded
suite.change_feature("fast_viewer", False)
suite.apply_settings()
assert not fast_component.loaded and fast_feature not in suite.components
assert suite.components[filter_feature][1] is filter_component and filter_component.loaded
suite.on_plugin_unload()
assert not filter_component.loaded

print("Passed independent suite settings and component unload")

language_suite = suite_module.NagramXFMediaSuite()
language_suite.components = {}
language_setting = {}
reload_events = []
language_suite.get_setting = language_setting.get


def save_language(key, value, reload_settings=False):
    language_setting[key] = value
    reload_events.append(reload_settings)


language_suite.set_setting = save_language
native_language = Obj(code="en")
android_version = Obj(SDK_INT=35)
system_locales = Obj(isEmpty=lambda: False, get=lambda _: Obj(getLanguage=lambda: native_language.code))
system_locale_manager = Obj(getSystemLocales=lambda: system_locales)
system_resources = Obj(getSystem=lambda: Obj(getConfiguration=lambda: Obj(getLocales=lambda: system_locales)))
suite_namespace["jclass"] = {
    "android.os.Build$VERSION": android_version,
    "org.telegram.messenger.ApplicationLoader": Obj(applicationContext=Obj(getSystemService=lambda _: system_locale_manager)),
    "android.app.LocaleManager": object(),
    "android.content.res.Resources": system_resources,
}.__getitem__
try:
    english = language_suite.create_settings()
    assert english[1].text == "Media browsing" and english[0].key == "plugin_language"
    assert english[0].default == suite_module.LANGUAGE_AUTO
    assert english[0].text == "Plugin language" and english[0].items == ["Follow system language", "Simplified Chinese", "English"]
    assert suite_module.media_title(None, None) == "Video playback"
    assert suite_module.thumbnail_state_scope_setting(None).items == ["Globally", "Per chat"]
    english[0].on_change(suite_module.LANGUAGE_CHINESE)
    assert reload_events == [True] and language_suite.create_settings()[1].text == "媒体浏览"
    assert suite_module.media_title(None, None) == "视频播放"
    native_language.code = "zh-CN"
    language_suite.change_language(suite_module.LANGUAGE_ENGLISH)
    assert language_suite.create_settings()[1].text == "Media browsing"
    language_suite.change_language(suite_module.LANGUAGE_AUTO)
    assert language_suite.create_settings()[1].text == "媒体浏览"
    android_version.SDK_INT = 32
    native_language.code = "ja"
    assert language_suite.create_settings()[1].text == "Media browsing"
finally:
    suite_namespace["jclass"] = original_jclass
print("Passed native locale detection and in-plugin English and Chinese switching")

glass = object.__new__(suite_module.MainTabsGlass)
glass.fragments, glass.margin, glass.dp, glass.tabs_type, glass.render_node = [], 16, round, object(), None
glass.weak = lambda fragment: Obj(get=lambda: fragment)
glass_events = []
glass.style_background = lambda drawable, height, enabled, provider: glass_events.append((drawable, height, enabled))
glass.dialogs_type = Obj(isInstance=lambda _: False)


def tabs_test_view(width, height, background=None):
    params = Obj(width=width, height=height)
    return Obj(params=params, getLayoutParams=lambda: params, setLayoutParams=lambda *_: None,
               getBackground=lambda: background)


glass_tabs, glass_bar = tabs_test_view(360, 88, "tabs"), tabs_test_view(360, 88)
glass_search = tabs_test_view(56, 56, "search")
search_padding = [14]
glass_search.getChildAt = lambda _: Obj(getPaddingTop=lambda: search_padding[-1],
                                        setPadding=lambda top, *_: search_padding.append(top))
glass.views = tuple(value_field(view) for view in (glass_tabs, glass_bar, glass_search))
glass_fragment = Obj(getCurrentVisibleFragment=lambda: None, getFragmentView=lambda: None)
glass.style_tabs(glass_fragment)
assert (glass_tabs.params.height, glass_bar.params.height, glass_search.params.height) == (80, 80, 48)
assert glass_search.params.width == 48 and search_padding[-1] == 12
assert glass_events == [("tabs", 48, True), ("search", 48, True)]
glass.style_tabs(glass_fragment, enabled=False)
assert (glass_tabs.params.height, glass_bar.params.height, glass_search.params.height) == (88, 88, 56)
assert glass_search.params.width == 56 and search_padding[-1] == 14
assert glass_events[-2:] == [("tabs", 56, False), ("search", 56, False)]
render_events = []
glass.enabled_effects = []
glass.style_background = suite_module.MainTabsGlass.style_background.__get__(glass)
glass.render_node = glass.blurred_drawable = Obj(getClass=lambda: Obj(isInstance=lambda _: True))
glass.effect = Obj(get=lambda node: node.effect, set=lambda node, effect: setattr(node, "effect", effect))
glass.fill = Obj(get=lambda _: Obj(setRenderEffect=lambda _: render_events.append("clear")))
glass.glass_tint = Obj(getInt=lambda node: node.color, setInt=lambda node, color: setattr(node, "color", color))
glass.glass_provider = Obj(get=lambda node: node.provider)
glass.chat_glass = Obj(bottomPanelChatActivity=lambda _: "input glass")


def glass_drawable(effect):
    node = Obj(effect=effect, color=0xD9ABACAD, provider="tabs glass")
    node.setLiquidGlassEffectAllowed = lambda: setattr(node, "effect", "created")
    node.updateColors = lambda: setattr(node, "color", 0xD9ABACAD)
    node.setColorProvider = lambda provider: (setattr(node, "provider", provider), node.updateColors())
    node.setRadius = lambda radius: render_events.append(("radius", radius))
    node.invalidateDisplayList = lambda: render_events.append("rerecord")
    node.invalidateSelf = lambda: render_events.append("redraw")
    return node


plain_node, native_node = glass_drawable(None), glass_drawable("native")
for node in (plain_node, native_node):
    glass.style_background(node, 48, True)
    assert node.provider == "input glass"
    assert node.color & 0xFFFFFFFF == 0x9EABACAD
    render_count = len(render_events)
    assert not glass.style_background(node, 48, True) and len(render_events) == render_count
    node.updateColors()
    glass.after_glass_colors(Obj(thisObject=node))
    assert node.color & 0xFFFFFFFF == 0x9EABACAD
assert plain_node.effect == "created" and native_node.effect == "native"
assert -2**31 <= plain_node.color < 0 and -2**31 <= native_node.color < 0
for node in (plain_node, native_node):
    glass.style_background(node, 56, False)
    assert node.provider == "tabs glass"
    assert node.color == 0xD9ABACAD
assert plain_node.effect is None and native_node.effect == "native"
assert render_events.count("clear") == 1 and render_events.count("rerecord") == 4
print("Passed native glass bar sizing, search sizing and restoration")

host_settings, app_settings = {}, {}


class SettingsFixture:
    def get_setting(self, key, default=None):
        return host_settings.get(key, default)

    def set_setting(self, key, value, reload_settings=False):
        host_settings[key] = value


class SettingsPreferences:
    def getString(self, key, default):
        return app_settings.get(key, default)

    def edit(self):
        return self

    def putString(self, key, value):
        app_settings[key] = value
        return self

    def apply(self):
        pass


base_module = sys.modules["base_plugin"]
original_base = base_module.BasePlugin
base_module.BasePlugin = SettingsFixture
try:
    reloadable_suite = load("nagramxf_media_suite").NagramXFMediaSuite
finally:
    base_module.BasePlugin = original_base
before_update = reloadable_suite()
before_update.settings_preferences = SettingsPreferences()
host_settings["auto_fullscreen_on_switch"] = False
assert before_update.get_setting("auto_fullscreen_on_switch", True) is False
before_update.set_setting("sleep_timer_minutes", 37)
before_update.set_setting("sleep_timer_finish_current", True)
before_update.set_setting("thumbnail_size", 4)
host_settings.clear()
after_update = reloadable_suite()
after_update.settings_preferences = SettingsPreferences()
assert after_update.get_setting("auto_fullscreen_on_switch", True) is False
assert after_update.get_setting("sleep_timer_minutes", 60) == 37
assert after_update.get_setting("sleep_timer_finish_current", False) is True
assert after_update.get_setting("thumbnail_size", 2) == 4
