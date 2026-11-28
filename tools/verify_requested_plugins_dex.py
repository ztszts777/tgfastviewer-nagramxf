from pathlib import Path
import subprocess

base = Path("build/nagram-reference")
dump = Path("build/android-sdk/build-tools/36.0.0/dexdump.exe").resolve()
tl = "Lorg/telegram/tgnet/TLRPC$"
ui = "Lorg/telegram/ui/"
msg = "Lorg/telegram/messenger/"
msg_obj = msg + "MessageObject;"
player = ui + "Components/VideoPlayer;"
group = msg + "MessageObject$GroupedMessages;"
ayufilter = "Ltw/nekomimi/nekogram/filters/AyuFilter;"
chat = ui + "ChatActivity;"
adapter = ui + "ChatActivity$ChatActivityAdapter;"
viewer = ui + "PhotoViewer;"
window = ui + "PhotoViewer$PhotoViewerWindowView;"
drawer = ui + "PhotoViewer$FrameLayoutDrawer;"
menu = ui + "ActionBar/ActionBarMenuItem;"
subitem = ui + "ActionBar/ActionBarMenuSubItem;"
cell = ui + "Cells/DialogCell;"
alert = ui + "ActionBar/AlertDialog;"
builder = ui + "ActionBar/AlertDialog$Builder;"
sheet = ui + "ActionBar/BottomSheet;"
sheet_builder = ui + "ActionBar/BottomSheet$Builder;"
theme_provider = ui + "ActionBar/Theme$ResourcesProvider;"
slide_choose = ui + "Components/SlideChooseView;"
slide_callback = ui + "Components/SlideChooseView$Callback;"
timer_button = ui + "Stories/recorder/ButtonWithCounterView;"
events = msg + "NotificationCenter;"
obj_array = "[Ljava/lang/Object;"
array_list = "Ljava/util/ArrayList;"
view = "Landroid/view/View;"
pip = msg + "pip/"
pip_source = pip + "PipSource;"
pip_controller = pip + "PipActivityController;"
pip_builder = pip + "PipSource$Builder;"
pip_action_listener = pip + "activity/IPipActivityActionListener;"
pip_activity_handler = pip + "activity/IPipActivityHandler;"
media_session = "Landroid/support/v4/media/session/MediaSessionCompat;"
exo_player = "Lcom/google/android/exoplayer2/Player;"
connector = "Lcom/google/android/exoplayer2/ext/mediasession/MediaSessionConnector;"
provider = connector.removesuffix(";") + "$MediaMetadataProvider;"
custom_provider = connector.removesuffix(";") + "$CustomActionProvider;"
metadata = "Landroid/support/v4/media/MediaMetadataCompat;"
metadata_builder = "Landroid/support/v4/media/MediaMetadataCompat$Builder;"
receiver = msg + "ImageReceiver;"
image_holder = msg + "ImageReceiver$BitmapHolder;"
pic_params = "Landroid/app/PictureInPictureParams;"
expected = {
    chat: {("chatAdapter", adapter), ("replyMessageHeaderObject", msg_obj),
           ("hideFilteredMessages", "Z"), ("didReceivedNotification", f"(II{obj_array})V"),
           ("<init>", "(Landroid/os/Bundle;)V"), ("getChatMode", "()I"),
           ("pinnedMessageIds", array_list), ("pinnedMessageObjects", "Ljava/util/HashMap;"),
           ("messagesDict", "[Landroid/util/SparseArray;"), ("currentPinnedMessageId", "I"),
           ("currentPinnedMessageIndex", "[I"), ("loadedPinnedMessagesCount", "I"),
           ("totalPinnedMessagesCount", "I"), ("updatePinnedMessageView", "(Z)V"),
           ("updatePinnedMessageView", "(ZI)V"), ("updatePinnedListButton", "(Z)V"),
           ("openPinnedMessagesList", "(Z)V"), ("getPinnedMessagesCount", "()I"),
           ("hidePinnedMessageView", "(Z)Z"), ("checkListViewPaddings", "()V"),
           ("findClosest", f"({array_list}I[I)Ljava/lang/Integer;"),
           ("isThreadChat", "()Z"), ("isTopic", "Z"), ("getThreadMessage", f"(){msg_obj}"),
           ("getValidGroupedMessage", f"({msg_obj}){group}"),
           ("updateMessagesVisiblePart", "(Z)V"), ("isFeedSearch", "()Z"), ("isSecretChat", "()Z"),
           ("updateTextureViewPosition", "(ZZ)V"), ("onRemoveFromParent", "()V"),
           ("onPageDownClicked", "()V"), ("scrollToLastMessage", "(ZZLjava/lang/Runnable;)V"),
           ("getChatListView", f"(){ui}Components/RecyclerListView;"),
           ("onConfigurationChanged", "(Landroid/content/res/Configuration;)V"),
           ("forwardEndReached", "[Z"), ("paused", "Z"), ("firstLoading", "Z"),
           ("postponedScrollToLastMessageQueryIndex", "I"), ("postponedScrollIsCanceled", "Z"),
           ("postponedScrollMessageId", "I")},
    adapter: {("this$0", chat), ("messagesStartRow", "I"), ("messagesEndRow", "I"),
              ("getMessages", f"(){array_list}"), ("getItemViewType", "(I)I"),
              ("notifyItemChanged", "(I)V"), ("notifyDataSetChanged", "(Z)V"),
              ("isFiltered", "Z"), ("isFrozen", "Z")},
    cell: {("currentAccount", "I"), ("message", msg_obj), ("groupMessages", array_list),
           ("lastMessageDate", "I"), ("filteredDummyMessages", f"[{msg_obj}"),
           ("buildLayout", "()V"), ("onAttachedToWindow", "()V"), ("getDialogId", "()J"),
           ("update", "(IZ)Z"),
           ("isDialogFolder", "()Z"), ("isDialogCommunity", "()Z"),
           ("insideCommunityListNoDialog", "Z"), ("isDialogCell", "Z")},
    msg_obj: {("isDateObject", "Z"), ("isVideoConversionObject", "Z"), ("type", "I"),
              ("contentType", "I"), ("dateKeyInt", "I"), ("stableId", "I"),
              ("TYPE_DATE", "I"), ("currentAccount", "I"), ("audioProgress", "F"), ("skipAyuFiltering", "Z"),
              ("<init>", f"(I{tl}Message;ZZ)V"), ("messageOwner", tl + "Message;"),
              ("isHiddenSensitive", "()Z"), ("getId", "()I"), ("getDialogId", "()J"),
              ("isPhoto", "()Z"), ("getPhoto", f"(){tl}Photo;")},
    ayufilter: {("shouldHideFilteredMessages", "()Z"), ("shouldHideIgnoredBlockedMessages", "()Z"),
                ("shouldHideFilteredMessage", f"({msg_obj}{group})Z"),
                ("isIgnoredBlockedMessage", f"({msg_obj})Z"), ("rebuildCache", "()V"),
                ("invalidateFilteredCache", "()V"), ("onMessageEdited", "(IJ)V")},
    group: {("<init>", "()V"), ("groupId", "J"), ("messages", array_list),
            ("calculate", "()V"), ("findPrimaryMessageObject", f"(){msg_obj}")},
    events: {(name, "I") for name in ("messagesDidLoad", "didReceiveNewMessages", "messagesDeleted",
                                     "replaceMessagesObjects", "regexFiltersUpdated", "pinnedInfoDidLoad",
                                     "didLoadPinnedMessages")},
    viewer: {("videoPlayerControlFrameLayout", ui + "PhotoViewer$VideoPlayerControlFrameLayout;"),
             ("videoPreviewFrame", ui + "Components/VideoSeekPreviewImage;"), ("videoItem", menu),
             ("loopItem", subitem), ("getParentActivity", "()Landroid/app/Activity;"),
             ("bottomLayout", "Landroid/widget/FrameLayout;"),
             ("groupedPhotosListView", ui + "Components/GroupedPhotosListView;"),
             ("captionScrollView", ui + "PhotoViewer$CaptionScrollView;"),
             ("captionContainer", "Landroid/widget/FrameLayout;"),
             ("captionTextViewSwitcher", ui + "PhotoViewer$CaptionTextViewSwitcher;"),
             ("navigationBar", view), ("actionBarBackButton", "Landroid/widget/ImageView;"),
             ("photoViewerWebView", ui + "Components/PhotoViewerWebView;"),
             ("pipSource", pip_source), ("pipPlaceholderView", view), ("menuItem", menu),
             ("sendItem", menu),
             ("galleryGap", ui + "ActionBar/ActionBarPopupWindow$GapView;"),
             ("speedGap", ui + "ActionBar/ActionBarPopupWindow$GapView;"),
             ("chooseSpeedLayout", ui + "SpeedButtonsLayout;"),
             ("speedItem", ui + "ActionBar/ActionBarMenuSlider$SpeedSlider;"), ("currentVideoSpeed", "F"),
             ("videoQualityLayout", "Landroid/widget/LinearLayout;"),
             ("chooseSpeed", "(FZZ)V"), ("chooseQuality", "(I)V"),
             ("loopItem", subitem),
             ("windowLayoutParams", "Landroid/view/WindowManager$LayoutParams;"),
             ("isInline", "Z"), ("currentEditMode", "I"), ("isEmbedVideo", "Z"),
             ("containerView", drawer),
             ("videoWidth", "I"), ("videoHeight", "I"), ("videoSizeSet", "Z"),
             ("aspectRatioFrameLayout", "Lcom/google/android/exoplayer2/ui/AspectRatioFrameLayout;"),
             ("getCurrentMessageObject", f"(){msg_obj}"),
             ("preparePlayer", f"({array_list}Landroid/net/Uri;ZZ{msg}MediaController$SavedFilterState;ZJ)V"),
             ("updatePlayerState", "(ZI)V"), ("switchToPip", "(Z)V"),
             ("createVideoControlsInterface", "()V"), ("pipItem", subitem), ("playerLooping", "Z"),
             ("centerImage", receiver), ("getCurrentIndex", "()I"),
             ("getVideoTextureView", "()Landroid/view/TextureView;"),
             ("getVideoSurfaceView", "()Landroid/view/SurfaceView;"),
             ("checkFullscreenButton", "()V"),
             ("showAlertDialog", f"({builder})V"),
             ("updateActionBarTitlePadding", "()V"),
             ("actionBarContainer", ui + "PhotoViewer$PhotoViewerActionBarContainer;"),
             ("menu", ui + "ActionBar/ActionBarMenu;"),
             ("videoPlayerTime", ui + "ActionBar/SimpleTextView;"),
             ("videoPlayerSeekbar", ui + "Components/VideoPlayerSeekBar;"), ("videoPlayerSeekbarView", view),
             ("toggleVideoPlayer", "()V"), ("isVideoPlaying", "()Z"), ("onActionClick", "(Z)V"),
             ("getCurrentVideoPosition", "()J"), ("getVideoDuration", "()J"),
             ("seekVideoOrWebTo", "(J)V"), ("switchToNextIndex", "(IZ)V"),
             ("toggleActionBar", "(ZZ)V"), ("getContainerViewWidth", "()I"),
             ("getContainerViewHeight", "()I"), ("closePhoto", "(ZZ)V"),
             ("isStatusBarVisible", "()Z"), ("updateContainerFlags", "(Z)V"),
             ("actionBarAnimator", "Landroid/animation/AnimatorSet;"),
             ("toggleActionBar", f"(ZZ{ui}PhotoViewer$ActionBarToggleParams;)V"),
             ("onPhotoClosed", f"({ui}PhotoViewer$PlaceProviderObject;)V"), ("onHideView", "()V"),
             ("onTouchEvent", "(Landroid/view/MotionEvent;)Z"),
             ("onDoubleTap", "(Landroid/view/MotionEvent;)Z"),
             ("canDoubleTap", "(Landroid/view/MotionEvent;)Z"),
             ("onSingleTapUp", "(Landroid/view/MotionEvent;)Z"),
             ("canDoubleTapSeekVideo", "(Landroid/view/MotionEvent;)Z"),
             ("onLongPress", "()V"),
             ("onSingleTapConfirmed", "(Landroid/view/MotionEvent;)Z"),
             ("updateAccessibilityOverlayVisibility", "()V"),
             ("setImageIndex", "(IZZZ)V"),
             ("setCurrentCaption", f"({msg_obj}Ljava/lang/CharSequence;ZZ)V"), ("needCaptionLayout", "Z"),
             ("setIndexToImage", f"({receiver}I{ui}Components/Crop/CropTransform;)V"),
             ("prevOrientation", "I"), ("fullscreenedByButton", "I"),
             ("orientationEventListener", "Landroid/view/OrientationEventListener;"),
             ("videoForwardDrawable", ui + "Components/VideoForwardDrawable;"),
             ("leftImage", receiver), ("rightImage", receiver), ("canZoom", "Z"),
             ("doubleTap", "Z"), ("discardTap", "Z"), ("scale", "F"),
             ("zooming", "Z"), ("draggingDown", "Z"), ("changingPage", "Z"),
             ("pinchCenterX", "F"), ("pinchCenterY", "F"), ("pinchStartX", "F"), ("pinchStartY", "F"),
             ("animationStartTime", "J"), ("animateToScale", "F"),
             ("animationInProgress", "I"),
             ("menuItem", menu), ("fullscreenButton", "[Landroid/widget/ImageView;"),
             ("exitFullscreenButton", "Landroid/widget/ImageView;"), ("playButtonAccessibilityOverlay", view),
             ("isActionBarVisible", "Z"), ("actionBar", ui + "ActionBar/ActionBar;"),
             ("photoProgressViews", "[Lorg/telegram/ui/PhotoViewer$PhotoProgressView;"),
             ("onUserLeaveHint", "()V"), ("isVisible", "()Z"),
             ("pipHidePrimaryWindowView", "(Ljava/lang/Runnable;)V"),
             ("pipShowPrimaryWindowView", "(Ljava/lang/Runnable;)V"),
             ("windowView", "Landroid/widget/FrameLayout;"), ("currentIndex", "I"), ("manuallyPaused", "Z"),
             ("Instance", viewer), ("Instance2", viewer), ("PipInstance", viewer),
             ("setParentActivity", f"(Landroid/app/Activity;{ui}ActionBar/BaseFragment;{ui}ActionBar/Theme$ResourcesProvider;)V"),
             ("getVideoPlayer", f"(){player}"), ("pipIsAvailable", "()Z"), ("videoPlayer", player),
             ("firstFrameRendered", "Z"), ("textureUploaded", "Z"), ("windowViewSkipRender", "Z"),
             ("onPause", "()V"), ("onResume", "()V"), ("destroyPhotoViewer", "()V"),
             ("releasePlayer", "(Z)V")},
    window: {("onLayout", "(ZIIII)V"), ("this$0", viewer),
             ("drawChild", "(Landroid/graphics/Canvas;Landroid/view/View;J)Z"),
             ("dispatchTouchEvent", "(Landroid/view/MotionEvent;)Z")},
    ui + "PhotoViewer$PhotoProgressView;": {("onDraw", "(Landroid/graphics/Canvas;)V"),
                                              ("backgroundState", "I"), ("this$0", viewer)},
    ui + "PhotoViewer$VideoPlayerControlFrameLayout;": {
        ("this$0", viewer), ("parentWidth", "I"), ("parentHeight", "I"),
        ("onMeasure", "(II)V"), ("onProgressChanged", "(F)V"), ("getProgress", "()F"),
        ("isSeekBarTransitionEnabled", "()Z"),
        ("setSeekBarTransitionEnabled", "(Z)V"),
    },
    drawer: {("onMeasure", "(II)V"), ("onLayout", "(ZIIII)V"), ("this$0", viewer), ("paint", "Landroid/graphics/Paint;"),
             ("onDraw", "(Landroid/graphics/Canvas;)V"), ("dispatchDraw", "(Landroid/graphics/Canvas;)V")},
    ui + "PhotoViewer$CaptionScrollView;": {("draw", "(Landroid/graphics/Canvas;)V"), ("backgroundAlpha", "F"),
                                              ("onTouchEvent", "(Landroid/view/MotionEvent;)Z"),
                                              ("calculateNewContainerMarginTop", "(II)I"), ("prevHeight", "I"),
                                              ("stopScrolling", "()V")},
    ui + "PhotoViewer$CaptionTextView;": {("onTouchEvent", "(Landroid/view/MotionEvent;)Z")},
    ui + "Components/QuoteSpan;": {("putQuote", "(Landroid/text/Spannable;IIZ)I"), ("isCollapsing", "Z"),
        ("styleSpan", ui + "Components/QuoteSpan$QuoteStyleSpan;"),
        ("collapsedSpan", ui + "Components/QuoteSpan$QuoteCollapsedPart;")},
    ui + "ActionBar/ActionBar;": {("getCurrentActionBarHeight", "()I"),
                                  ("getActionBarMenuOnItemClick", f"(){ui}ActionBar/ActionBar$ActionBarMenuOnItemClick;"),
                                  ("getOccupyStatusBar", "()Z"), ("setOccupyStatusBar", "(Z)V")},
    ui + "ActionBar/ActionBarMenu;": {
        ("onItemClick", "(I)V"),
        ("addItemAt", f"(IIILjava/lang/CharSequence;ILandroid/graphics/drawable/Drawable;ILjava/lang/CharSequence;{theme_provider}){menu}"),
    },
    ui + "PhotoViewer$PhotoViewerActionBarContainer;": {("setSubtitle", "(Ljava/lang/CharSequence;Z)V")},
    "Lxyz/nextalone/nagram/helper/BookmarksHelper;": {
        ("getBookmarkedMessageIds", "(IJ)[I"),
        ("toggleBookmarks", "(IJ[I)Lxyz/nextalone/nagram/ToggleResult;"),
    },
    "Lxyz/nextalone/nagram/ToggleResult;": {("ADDED", "Lxyz/nextalone/nagram/ToggleResult;")},
    "Landroidx/recyclerview/widget/LinearLayoutManager;": {
        ("onSaveInstanceState", "()Landroid/os/Parcelable;"),
        ("onRestoreInstanceState", "(Landroid/os/Parcelable;)V"),
    },
    "Landroidx/recyclerview/widget/LinearLayoutManager$SavedState;": {("mAnchorPosition", "I")},
    ui + "PhotoViewer$PhotoViewerActionBarContainer;": {("updateRightPadding", "(FZ)V")},
    ui + "Components/VideoPlayerSeekBar;": {("setSize", "(II)V"), ("onTouch", "(IFF)Z"), ("getThumbX", "()I"),
        ("setProgress", "(FZ)V"), ("getProgress", "()F"), ("isDragging", "()Z"),
        ("draw", f"(Landroid/graphics/Canvas;{view})V"), ("width", "I"), ("height", "I"),
        ("getTransitionProgress", "()F"), ("setTransitionProgress", "(F)V")},
    ui + "Components/VideoForwardDrawable;": {("setOneShootAnimation", "(Z)V"), ("setLeftSide", "(Z)V"),
                                               ("addTime", "(J)V"), ("draw", "(Landroid/graphics/Canvas;)V"),
                                               ("leftSide", "Z"), ("isOneShootAnimation", "Z"),
                                               ("time", "J"), ("animationProgress", "F")},
    ui + "ActionBar/SimpleTextView;": {
        ("setGravity", "(I)V"), ("setTextSize", "(I)V"), ("getText", "()Ljava/lang/CharSequence;"),
    },
    ui + "Components/RLottieImageView;": {
        ("getAnimatedDrawable", f"(){ui}Components/RLottieDrawable;"),
    },
    ui + "Components/PhotoViewerWebView;": {("isControllable", "()Z")},
    player: {("isLooping", "()Z"), ("setLooping", "(Z)V"), ("isPlaying", "()Z"), ("pause", "()V"),
             ("getVolume", "()F"), ("setVolume", "(F)V"),
             ("onRenderedFirstFrame", "()V"),
             ("maybeReportPlayerState", "()V"), ("seekTo", "(J)V"),
             ("setTextureView", "(Landroid/view/TextureView;)V"),
             ("onSurfaceDestroyed", "(Landroid/graphics/SurfaceTexture;)Z"),
             ("setSurfaceView", "(Landroid/view/SurfaceView;)V"), ("setMute", "(Z)V"),
             ("setSurface", "(Landroid/view/Surface;)V"),
             ("trackSelector", "Lcom/google/android/exoplayer2/trackselection/MappingTrackSelector;"),
             ("player", "Lcom/google/android/exoplayer2/ExoPlayer;"),
             ("onPositionDiscontinuity", "(Lcom/google/android/exoplayer2/Player$PositionInfo;Lcom/google/android/exoplayer2/Player$PositionInfo;I)V")},
    ui + "Components/AudioPlayerAlert;": {
        ("<init>", f"(Landroid/content/Context;{ui}ActionBar/Theme$ResourcesProvider;)V"),
        ("buttons", f"[{view}"), ("updateColors", "()V"),
        ("playerLayout", "Landroid/widget/FrameLayout;"), ("listView", ui + "Components/RecyclerListView;"),
        ("playbackSpeedButton", menu), ("forwardButton", "Landroid/widget/TextView;"),
        ("saveToProfileButton", ui + "Stories/recorder/ButtonWithCounterView;"),
        ("unsaveFromProfileButton", ui + "Stories/recorder/ButtonWithCounterView;"),
        ("playerShadow", view), ("noforwards", "Z"), ("isMyList", "()Z"),
        ("updateTitle", "(Z)V"), ("setVisibleInProfile", "(Z)V"),
        ("showMenuOptions", f"({view})V"), ("onSubItemClick", "(I)V"),
    },
    ui + "Components/ItemOptions;": {("show", f"(){ui}Components/ItemOptions;"),
                                    ("addIf", f"(ZILjava/lang/CharSequence;Ljava/lang/Runnable;){ui}Components/ItemOptions;"),
                                    ("add", f"(ILjava/lang/CharSequence;Ljava/lang/Runnable;){ui}Components/ItemOptions;")},
    msg + "MediaController;": {("audioPlayer", player), ("getVideoPlayer", f"(){player}"),
                             ("getPlayingMessageObject", f"(){msg_obj}"),
                             ("pauseMessage", f"({msg_obj}Z)Z")},
    ui + "DialogsActivity;": {("didReceivedNotification", f"(II{obj_array})V")},
    msg + "MessagesStorage;": {("getMessageLegit", f"(JJ){tl}Message;"),
                              ("getStorageQueue", f"(){msg}DispatchQueue;"),
                              ("getDatabase", "()Lorg/telegram/SQLite/SQLiteDatabase;")},
    msg + "DispatchQueue;": {("postRunnable", "(Ljava/lang/Runnable;)Z")},
    msg + "MessagesController;": {("removeDeletedMessagesFromArray", f"(J{array_list})V"),
                                  ("getNotificationsSettings", "(I)Landroid/content/SharedPreferences;"),
                                  ("isPeerNoForwards", "(J)Z"), ("ignoreSetOnline", "Z"),
                                  ("dialogs_dict", "Landroidx/collection/LongSparseArray;"),
                                  ("markDialogAsRead", "(JIIIZJIZI)V")},
    tl + "Dialog;": {("top_message", "I"), ("unread_count", "I")},
    ui + "ActionBar/BaseFragment;": {("getCurrentAccount", "()I"), ("getClassGuid", "()I"),
                                    ("isInPreviewMode", "()Z")},
    ui + "Components/RecyclerListView;": {("isFastScrollAnimationRunning", "()Z")},
    menu: {("addSubItem", f"(IILjava/lang/CharSequence;){ui}ActionBar/ActionBarMenuSubItem;"),
           ("getIconView", f"(){ui}Components/RLottieImageView;"),
           ("toggleSubMenu", f"({view}{view}Z)V"), ("closeSubMenu", "()V"),
           ("isSubItemVisible", "(I)Z"), ("getAnchor", f"(){view}"), ("setAnchor", f"({view})V"),
           ("isShowOnTop", "()Z"), ("setShowOnTop", "(Z)V"), ("setSubMenuOpenSide", "(I)V"),
           ("setAdditionalYOffset", "(I)V"), ("subMenuOpenSide", "I"), ("additionalYOffset", "I"),
           ("updateOrShowPopup", "(ZZ)V"), ("popupWindow", ui + "ActionBar/ActionBarPopupWindow;")},
    subitem: {("setColors", f"(II){subitem}"), ("setSelectorColor", "(I)V"),
              ("setText", "(Ljava/lang/CharSequence;)V"),
              ("getTextView", f"(){ui}Components/AnimatedEmojiSpan$TextViewEmojis;")},
    msg + "R$drawable;": {(name, "I") for name in
                         ("msg_timer", "menu_video_loop", "menu_video_pip", "video_settings",
                          "msg_maxvideo", "msg_minvideo", "msg_media", "ic_ab_other", "msg_header_share", "arrow_more",
                          "msg_brightness_high", "baseline_volume_up_24", "msg_speed", "msg_views", "msg_fave",
                          "baseline_skip_previous_24_white", "baseline_skip_next_24_white",
                          "baseline_play_arrow_36_white", "baseline_pause_36_white", "msg_voice_headphones")},
    ui + "ActionBar/Theme;": {("createSelectorDrawable", "(III)Landroid/graphics/drawable/Drawable;"),
                             ("createSelectorDrawable", "(II)Landroid/graphics/drawable/Drawable;"),
                             ("getColor", "(I)I"), ("key_windowBackgroundWhite", "I"),
                             ("key_windowBackgroundWhiteBlackText", "I"), ("key_dialogTextGray2", "I"),
                             ("key_windowBackgroundWhiteBlueText", "I"), ("key_featuredStickers_addButton", "I"),
                             ("isCurrentThemeDark", "()Z")},
    sheet: {
        ("<init>", f"(Landroid/content/Context;Z{ui}ActionBar/Theme$ResourcesProvider;)V"),
        ("setCustomView", f"({view})V"), ("setApplyTopPadding", "(Z)V"),
        ("scrollNavBar", "Z"), ("show", "()V"), ("skipDismissAnimation", "()V"),
        ("setCanDismissWithSwipe", "(Z)V"),
    },
    sheet_builder: {
        ("<init>", "(Landroid/content/Context;)V"),
        ("<init>", f"(Landroid/content/Context;Z{theme_provider}I)V"),
        ("setTitle", f"(Ljava/lang/CharSequence;){sheet_builder}"),
        ("setCustomView", f"({view}){sheet_builder}"),
        ("create", f"(){sheet}"),
    },
    ui + "Components/LayoutHelper;": {
        ("createLinear", "(IIIIIII)Landroid/widget/LinearLayout$LayoutParams;"),
    },
    ui + "Cells/TextSettingsCell;": {
        ("<init>", f"(Landroid/content/Context;{theme_provider})V"),
        ("setTextAndValue", "(Ljava/lang/CharSequence;Ljava/lang/CharSequence;Z)V"),
    },
    ui + "Cells/TextCheckCell;": {
        ("<init>", f"(Landroid/content/Context;{theme_provider})V"),
        ("setTextAndCheck", "(Ljava/lang/CharSequence;ZZ)V"), ("isChecked", "()Z"),
        ("setChecked", "(Z)V"), ("setHeight", "(I)V"),
        ("onMeasure", "(II)V"), ("textView", "Landroid/widget/TextView;"),
        ("valueTextView", "Landroid/widget/TextView;"),
    },
    "Lcom/exteragram/messenger/plugins/ui/PluginSettingsActivity;": {
        ("createView", f"(Landroid/content/Context;){view}"),
        ("plugin", "Lcom/exteragram/messenger/plugins/Plugin;"),
        ("listView", ui + "Components/UniversalRecyclerView;"),
        ("resetItem", menu),
    },
    "Lcom/exteragram/messenger/plugins/PluginsController;": {
        ("setPluginSetting", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;)V"),
        ("getPluginEngine", "(Ljava/lang/String;)Lcom/exteragram/messenger/plugins/PluginsController$PluginsEngine;"),
    },
    "Lcom/exteragram/messenger/plugins/PluginsController$PluginsEngine;": {
        ("setPluginSetting", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;)V"),
    },
    slide_choose: {
        ("<init>", f"(Landroid/content/Context;{theme_provider})V"),
        ("setOptions", "(I[Ljava/lang/String;)V"), ("setCallback", f"({slide_callback})V"),
    },
    slide_callback: {("onOptionSelected", "(I)V"), ("onTouchEnd", "()V")},
    timer_button: {
        ("<init>", f"(Landroid/content/Context;{theme_provider})V"),
        ("setRound", f"(){timer_button}"), ("setNeutral", f"(){timer_button}"),
        ("setText", "(Ljava/lang/CharSequence;)V"),
    },
    ui + "Stories/DarkThemeResourceProvider;": {("<init>", "()V")},
    ui + "Components/EditTextBoldCursor;": {("<init>", "(Landroid/content/Context;)V")},
    alert: {("setDismissDialogByButtons", "(Z)V"), ("getButton", f"(I){view}")},
    builder: {("create", f"(){alert}"), ("<init>", "(Landroid/content/Context;)V"),
              ("<init>", f"(Landroid/content/Context;{theme_provider})V"),
              ("setTitle", f"(Ljava/lang/CharSequence;){builder}"),
              ("setMessage", f"(Ljava/lang/CharSequence;){builder}"),
              *((name, f"(Ljava/lang/CharSequence;{ui}ActionBar/AlertDialog$OnButtonClickListener;){builder}")
                for name in ("setNegativeButton", "setPositiveButton", "setNeutralButton")),
              ("setItems", f"([Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;){builder}"),
              ("setView", f"({view}){builder}")},
    "Lde/robv/android/xposed/XposedBridge;": {
        ("invokeOriginalMethod", f"(Ljava/lang/reflect/Member;Ljava/lang/Object;{obj_array})Ljava/lang/Object;"),
        ("deoptimizeMethod", "(Ljava/lang/reflect/Member;)Z"),
    },
    tl + "TL_messages_getHistory;": {("<init>", "()V"), ("offset_id", "I"), ("limit", "I"),
                                       ("peer", tl + "InputPeer;")},
    tl + "messages_Messages;": {("messages", array_list), ("users", array_list), ("chats", array_list)},
    tl + "TL_messageEmpty;": set(),
    tl + "Dialog;": {("top_message", "I"), ("last_message_date", "I")},
    tl + "Message;": {("id", "I"), ("date", "I"), ("dialog_id", "J"), ("grouped_id", "J"),
                      ("edit_date", "I"), ("hide", "Z")},
}
expected[ui + "LaunchActivity;"] = {("getPipController", f"(){pip_controller}"), ("onPause", "()V"), ("onResume", "()V"),
                                   ("switchToAccount", "(IZ)V"),
                                   ("handleIntentInternal", f"(Landroid/content/Intent;ZZZ{msg}browser/Browser$Progress;ZZ)Z"),
                                   ("onNewIntent", f"(Landroid/content/Intent;{msg}browser/Browser$Progress;)V")}
bar_title = ui + "Components/AudioPlayerAlert$ClippingTextViewSwitcher;"
expected[ui + "Components/FragmentContextView;"] = {
    ("checkPlayer", "(Z)V"), ("titleTextView", bar_title),
    ("lastMessageObject", msg_obj),
    ("getCurrentStyle", "()I"), ("lambda$checkCreateView$8", f"({view})V"),
    ("playbackSpeedButton", menu), ("joinButtonWidth", "I"), ("updatePlaybackButton", "(Z)V"),
}
expected[ui + "DialogsActivity;"] = {
    ("fragmentContextView", ui + "Components/FragmentContextView;"), ("onBecomeFullyVisible", "()V"),
    ("filterTabsView", ui + "Components/FilterTabsView;"),
    ("viewPages", "[" + ui + "DialogsActivity$ViewPage;"),
    ("switchToCurrentSelectedMode", "(Z)V"),
}
expected[ui + "DialogsActivity$ViewPage;"] = {("selectedType", "I")}
expected[ui + "Components/FilterTabsView;"] = {
    ("getTabsCount", "()I"), ("getCurrentTabStableId", "()I"), ("getStableId", "(I)I"),
    ("isFirstTabSelected", "()Z"), ("selectTabWithStableId", "(I)Z"), ("finishAddingTabs", "(Z)V"),
    ("getTab", f"(I){ui}Components/FilterTabsView$Tab;"), ("getTabsContainer", f"(){ui}Components/RecyclerListView;"),
}
expected[ui + "Components/FilterTabsView$Tab;"] = {("id", "I"), ("isLocked", "Z")}
expected[msg + "SharedConfig;"] = {("isWaitingForPasscodeEnter", "Z")}
expected[msg_obj].update({("<init>", f"(I{tl}Message;ZZ)V"), ("eventId", "J")})
expected[tl + "Document;"] = {
    ("id", "J"), ("access_hash", "J"), ("file_reference", "[B"), ("date", "I"), ("size", "J"),
    ("dc_id", "I"), ("file_name", "Ljava/lang/String;"), ("file_name_fixed", "Ljava/lang/String;"),
    ("mime_type", "Ljava/lang/String;"), ("attributes", array_list), ("thumbs", array_list),
}
expected[tl + "DocumentAttribute;"] = {
    ("title", "Ljava/lang/String;"), ("performer", "Ljava/lang/String;"), ("duration", "D"),
}
for name in ("TL_document", "TL_documentAttributeAudio", "TL_messageMediaDocument", "TL_message"):
    expected[tl + name + ";"] = {("<init>", "()V")}
expected[ui + "PhotoViewer$EmptyPhotoViewerProvider;"] = {("<init>", "()V")}
expected[viewer].update({
    ("getInstance", f"(){viewer}"), ("setParentActivity", "(Landroid/app/Activity;)V"),
    ("openPhoto", f"({msg_obj}JJJ{ui}PhotoViewer$PhotoViewerProvider;Z)Z"),
    ("currentPlayingVideoFile", "Landroid/net/Uri;"), ("currentPlayingVideoQualityFiles", array_list),
    ("currentDialogId", "J"), ("mergeDialogId", "J"), ("topicId", "J"), ("updateQualityItems", "()V"),
})
expected[menu].add(("forceUpdatePopupPosition", "()V"))
expected[viewer].update({("imagesArr", array_list), ("didReceivedNotification", f"(II{obj_array})V")})
expected[events].add(("mediaDidLoad", "I"))
expected[msg + "MessagesController;"].update({("getChat", f"(Ljava/lang/Long;){tl}Chat;"),
                                             ("getUser", f"(Ljava/lang/Long;){tl}User;")})
expected[msg + "DialogObject;"] = {("isChatDialog", "(J)Z"), ("isUserDialog", "(J)Z")}
expected[msg + "UserObject;"] = {("getUserName", f"({tl}User;)Ljava/lang/String;")}
expected[msg + "LocaleController;"] = {("getString", "(I)Ljava/lang/String;")}
expected[msg + "R$string;"] = {("SavedMessages", "I")}
expected[tl + "User;"] = {("self", "Z")}
expected[tl + "Chat;"] = {("title", "Ljava/lang/String;")}
speed_slider = ui + "ActionBar/ActionBarMenuSlider;"
expected[speed_slider] = {("updateValue", "(FZ)V"), ("getValue", "()F"), ("stops", "[F")}
expected[ui + "ActionBar/ActionBarMenuSlider$SpeedSlider;"] = {("getSpeed", "(F)F")}
expected[msg + "MediaController;"].update({("playingMessageObject", msg_obj),
                                            ("resetGoingToShowMessageObject", "()V")})
expected[bar_title] = {("getTextView", "()Landroid/widget/TextView;")}
expected[ui + "ActionBar/ActionBarPopupWindow$ActionBarPopupWindowLayout;"] = {
    ("getItemsCount", "()I"), ("getItemAt", f"(I){view}"),
    ("getBackgroundColor", "()I"), ("setBackgroundColor", "(I)V"),
}
quality = ui + "Components/VideoPlayer$Quality;"
expected[player].update({("getQualitiesCount", "()I"), ("getSelectedQuality", "()I"), ("getQuality", f"(I){quality}")})
expected[quality] = {("original", "Z"), ("p", "()I")}
expected[msg_obj].update((name, signature) for name, signature in (
    ("isVideo", "()Z"), ("getMusicTitle", "()Ljava/lang/String;"), ("getMusicAuthor", "()Ljava/lang/String;")))
expected[msg_obj].add(("hasRevealedExtendedMedia", "()Z"))
expected[msg_obj].update({("caption", "Ljava/lang/CharSequence;"),
                          ("getDocumentName", "()Ljava/lang/String;")})
expected[tl + "Message;"].update({("noforwards", "Z"), ("ttl", "I"), ("message", "Ljava/lang/String;")})
expected[receiver] = {("getParentObject", "()Ljava/lang/Object;"), ("getParentView", f"(){view}"),
                      ("hasBitmapImage", "()Z"), ("getBitmapWidth", "()I"), ("getBitmapHeight", "()I"),
                      ("setImageBitmapByKey", "(Landroid/graphics/drawable/Drawable;Ljava/lang/String;IZI)Z"),
                      ("getThumbBitmapSafe", f"(){image_holder}"), ("getBitmapSafe", f"(){image_holder}")}
expected[image_holder] = {("bitmap", "Landroid/graphics/Bitmap;"), ("release", "()V")}
expected[msg + "AndroidUtilities;"] = {("checkPipPermissions", "(Landroid/content/Context;)Z"),
                                      ("findActivity", "(Landroid/content/Context;)Landroid/app/Activity;"),
                                      ("needShowPasscode", "(Z)Z")}
expected[msg + "FileLoader;"] = {("getClosestPhotoSizeWithSize", f"({array_list}I){tl}PhotoSize;")}
expected[tl + "Photo;"] = {("sizes", array_list)}
expected[tl + "PhotoSize;"] = {("w", "I"), ("h", "I")}
expected[ui + "Components/GroupedPhotosListView;"] = {
    ("itemWidth", "I"), ("itemHeight", "I"), ("itemY", "I"), ("itemSpacing", "I"),
    ("backgroundPaint", "Landroid/graphics/Paint;"), ("hasPhotos", "()Z"),
    ("fillList", "()V"), ("currentObjects", array_list), ("currentPhotos", array_list),
    ("delegate", ui + "Components/GroupedPhotosListView$GroupedPhotosListViewDelegate;"),
}
expected[ui + "Components/GroupedPhotosListView$GroupedPhotosListViewDelegate;"] = {("setCurrentIndex", "(I)V")}
expected[ui + "Components/BackupImageView;"] = {
    ("<init>", "(Landroid/content/Context;)V"), ("getImageReceiver", f"(){receiver}"),
    ("setRoundRadius", "(I)V"),
}
expected[receiver].update({("setCurrentAccount", "(I)V"), ("setImage", f"({msg}ImageLocation;Ljava/lang/String;{msg}ImageLocation;Ljava/lang/String;JLjava/lang/String;Ljava/lang/Object;I)V")})
expected[receiver].add(("clearImage", "()V"))
expected[receiver].add(("setCrossfadeAlpha", "(B)V"))
expected[receiver].add(("moveImageToFront", "()V"))
expected[receiver].update({
    ("<init>", f"({view})V"), ("onAttachedToWindow", "()Z"), ("onDetachedFromWindow", "()V"),
    ("setRoundRadius", "(I)V"), ("setImageCoords", "(FFFF)V"), ("draw", "(Landroid/graphics/Canvas;)Z"),
    ("getImageX", "()F"), ("getImageY", "()F"), ("getImageWidth", "()F"), ("getImageHeight", "()F"),
    ("getRoundRadius", "(Z)[I"),
})
expected[msg + "ImageLocation;"] = {
    ("getForObject", f"({tl}PhotoSize;Lorg/telegram/tgnet/TLObject;){msg}ImageLocation;"),
}
expected[msg_obj].update({("photoThumbs", array_list), ("photoThumbsObject", "Lorg/telegram/tgnet/TLObject;"),
                          ("getPhoto", f"(){tl}Photo;")})
music_service = msg + "MusicPlayerService"
playback_builder = "Landroid/support/v4/media/session/PlaybackStateCompat$Builder;"
exo = "Lcom/google/android/exoplayer2/"
expected[exo + "PlaybackParameters;"] = {("<init>", "(FF)V"), ("pitch", "F")}
track_params = exo + "trackselection/TrackSelectionParameters;"
track_builder = exo + "trackselection/TrackSelectionParameters$Builder;"
expected[music_service + ";"] = {
    ("mediaSession", media_session), ("playbackState", playback_builder), ("foregroundServiceIsStarted", "Z"),
    ("createNotification", f"({msg_obj}Z)V"), ("updatePlaybackState", "(J)V"),
    ("onStartCommand", "(Landroid/content/Intent;II)I"), ("onCreate", "()V"), ("onDestroy", "()V"),
    ("didReceivedNotification", f"(II{obj_array})V"),
}
expected[music_service + "$2;"] = {
    ("onCustomAction", "(Ljava/lang/String;Landroid/os/Bundle;)V"), ("onStop", "()V"),
    ("onPlay", "()V"), ("onPause", "()V"), ("onSeekTo", "(J)V"),
}
expected[msg + "NotificationsController;"] = {
    ("checkOtherNotificationsChannel", "()V"), ("OTHER_NOTIFICATIONS_CHANNEL", "Ljava/lang/String;"),
}
expected[msg + "MediaController;"].update({
    ("injectVideoPlayer", f"({player}{msg_obj})V"), ("cleanupPlayer", "(ZZ)V"), ("cleanupPlayer", "(ZZZZ)V"),
    ("setCurrentVideoVisible", "(Z)V"),
    ("setTextureView", "(Landroid/view/TextureView;Lcom/google/android/exoplayer2/ui/AspectRatioFrameLayout;Landroid/widget/FrameLayout;ZLjava/lang/Runnable;)V"),
    ("updateVideoState", f"({msg_obj}[IZZI)V"), ("seekToProgressMs", f"({msg_obj}J)Z"),
    ("playMessage", f"({msg_obj}Z)Z"),
})
expected[exo + "trackselection/TrackSelector;"] = {
    ("getParameters", f"(){track_params}"), ("setParameters", f"({track_params})V"),
}
expected[track_params] = {("buildUpon", f"(){track_builder}")}
expected[track_builder] = {("setTrackTypeDisabled", f"(IZ){track_builder}"), ("build", f"(){track_params}")}
expected[pip + "utils/PipSourceParams;"] = {("build", "()Landroid/app/PictureInPictureParams$Builder;")}
expected[pip_source] = {
    ("controller", pip_controller),
    ("delegate", pip + "source/IPipSourceDelegate;"),
    ("state2", pip + "source/PipSourceHandlerState2;"),
    ("params", pip + "utils/PipSourceParams;"),
    ("getPlayer", f"(){exo_player}"), ("buildPictureInPictureParams", f"(){pic_params}"),
    ("isAvailable", "()Z"), ("invalidateAvailability", "()V"), ("invalidatePosition", "()V"),
    ("destroy", "()V"),
    ("remoteActions", array_list),
}
expected[pip_builder] = {
    ("<init>", f"(Landroid/app/Activity;{pip}source/IPipSourceDelegate;)V"),
    ("setTagPrefix", f"(Ljava/lang/String;){pip_builder}"), ("setContentView", f"({view}){pip_builder}"),
    ("setPlaceholderView", f"({view}){pip_builder}"), ("setContentRatio", f"(II){pip_builder}"),
    ("setPlayer", f"({exo_player}){pip_builder}"), ("setNeedMediaSession", f"(Z){pip_builder}"),
    ("build", f"(){pip_source}"),
}
expected[pip_controller] = {
    ("mediaSession", media_session), ("maxPrioritySource", pip_source),
    ("onMaxPrioritySourceChanged", f"({pip_source}{pip_source})V"),
    ("activity", "Landroid/app/Activity;"), ("getHandler", f"(){pip_activity_handler}"),
    ("addActionListener", f"(Ljava/lang/String;{pip_action_listener})V"),
    ("removeActionListener", f"(Ljava/lang/String;{pip_action_listener})V"),
    ("mediaSessionConnector", connector),
}
expected[pip + "PipActivityHandler;"] = {
    ("dispatchStartEnterPip", "()V"), ("isInPictureInPictureModeInternal", "Z"),
    ("activity", "Landroid/app/Activity;"),
    ("manualEnterPictureInPictureModeInternal", "()V"),
    ("onStop", "()V"),
}
expected[pip + "source/PipSourceHandlerState2;"] = {
    ("source", pip_source), ("onPipStashStart", "()V"), ("onPipStashEnd", "()V"),
}
expected[pip + "utils/PipActions;"] = {
    ("create", "(Landroid/content/Context;Ljava/lang/String;ILjava/lang/String;Ljava/lang/String;Landroid/graphics/drawable/Icon;)Landroid/app/RemoteAction;"),
}
expected[pip_action_listener] = {("onPipAction", "(I)V")}
expected[media_session] = {
    ("setMetadata", "(Landroid/support/v4/media/MediaMetadataCompat;)V"),
    ("setActive", "(Z)V"),
    ("getSessionToken", "()Landroid/support/v4/media/session/MediaSessionCompat$Token;"),
    ("setSessionActivity", "(Landroid/app/PendingIntent;)V"),
    ("getController", "()Landroid/support/v4/media/session/MediaControllerCompat;"),
}
expected["Landroid/support/v4/media/session/MediaControllerCompat;"] = {
    ("getSessionActivity", "()Landroid/app/PendingIntent;"),
}
expected[connector] = {
    ("mediaMetadataProvider", provider),
    ("setMediaMetadataProvider", f"({provider})V"),
    ("invalidateMediaSessionMetadata", "()V"),
    ("customActionProviders", f"[{custom_provider}"),
    ("setCustomActionProviders", f"([{custom_provider})V"),
}
expected[provider] = {("getMetadata", f"({exo_player}){metadata}")}
expected[metadata_builder] = {
    ("putBitmap", f"(Ljava/lang/String;Landroid/graphics/Bitmap;){metadata_builder}"),
}
expected[ayufilter].update({
    ("isDialogExcluded", "(J)Z"), ("setDialogExcluded", "(JZ)V"), ("shouldMaskFilteredMessages", "()Z"),
    ("shouldMaskMessage", f"({msg_obj}{group})Z"),
})
expected[msg_obj].add(("isRestrictedMessage", "Z"))
expected[viewer].update({
    ("currentDialogId", "J"), ("mergeDialogId", "J"), ("topicId", "J"), ("opennedFromMedia", "Z"),
    ("placeProvider", ui + "PhotoViewer$PhotoViewerProvider;"), ("seekToProgressPending", "F"),
    ("parentFragment", ui + "ActionBar/BaseFragment;"), ("resourcesProvider", theme_provider),
    ("getClassGuid", "()I"), ("didReceivedNotification", f"(II{obj_array})V"),
    ("currentFilterTag", ui + "Components/Reactions/ReactionsLayoutInBubble$VisibleReaction;"),
    ("parentChatActivity", chat), ("sharedMediaType", "I"),
    ("parentFragment", ui + "ActionBar/BaseFragment;"),
    ("addPhoto", f"({msg_obj}I)V"),
    ("openPhoto", f"({msg_obj}{tl}FileLocation;{msg}ImageLocation;{msg}ImageLocation;"
                  f"{array_list}{array_list}{array_list}I{ui}PhotoViewer$PhotoViewerProvider;"
                  f"{chat}JJJZ{ui}PhotoViewer$PageBlocksAdapter;Ljava/lang/Integer;)Z"),
    ("onPhotoShow", f"({msg_obj}{tl}FileLocation;{msg}ImageLocation;{msg}ImageLocation;"
                    f"{array_list}{array_list}Ljava/util/List;I{ui}PhotoViewer$PlaceProviderObject;)V"),
    ("drawFancyShadows", "(Landroid/graphics/Canvas;)V"),
    ("hideActionBarRunnable", "Ljava/lang/Runnable;"), ("scheduleActionBarHide", "()V"),
    ("scheduleActionBarHide", "(I)V"),
    ("videoPlayerControlAnimator", "Landroid/animation/Animator;"),
    ("setVideoPlayerControlVisible", "(ZZ)V"),
    ("needSearchImageInArr", "Z"), ("currentFileNames", "[Ljava/lang/String;"),
    ("getContainerViewHeight", "(ZI)I"),
    ("videoSurfaceView", "Landroid/view/SurfaceView;"), ("videoTextureView", "Landroid/view/TextureView;"),
})
expected[chat].update({("getFilteredMessages", f"(){array_list}"), ("getGroup", f"(J){group}")})
expected[chat].add(("onConfigurationChanged", "(Landroid/content/res/Configuration;)V"))
expected[chat].update({("onResume", "()V"), ("onPause", "()V"), ("onFragmentDestroy", "()V"),
                       ("scrollToTopOnResume", "Z"), ("scrollToTopUnReadOnResume", "Z"),
                       ("mergeDialogId", "J"), ("scrollToMessageId", "(IIZIZI)V")})
expected[msg_obj].add(("getGroupId", "()J"))
expected["Landroidx/core/widget/NestedScrollView;"] = {("<init>", "(Landroid/content/Context;)V")}
expected[ui + "Components/QuoteSpan$QuoteStyleSpan;"] = set()
expected[msg + "CodeHighlighting$Span;"] = set()
expected["Lcom/google/android/exoplayer2/ui/AspectRatioFrameLayout;"] = {("onMeasure", "(II)V")}
expected[receiver].add(("getBitmap", "()Landroid/graphics/Bitmap;"))
expected[player].add(("onVideoSizeChanged", "(Lcom/google/android/exoplayer2/video/VideoSize;)V"))
expected[tl + "TL_documentAttributeVideo;"] = set()
expected[ui + "PhotoViewer$PhotoViewerActionBarContainer;"].update({
    ("titleLayout", "Landroid/widget/FrameLayout;"), ("subtitleTextView", ui + "Components/AnimatedTextView;"),
    ("container", "Landroid/widget/FrameLayout;"), ("onMeasure", "(II)V"), ("onLayout", "(ZIIII)V"),
})
expected[msg + "MediaDataController;"] = {
    ("getInstance", f"(I){msg}MediaDataController;"),
    ("loadMedia", f"(JIIIIJIII{ui}Components/Reactions/ReactionsLayoutInBubble$VisibleReaction;Ljava/lang/String;)V"),
}
expected[ui + "Components/SharedMediaLayout$SharedMediaData;"] = {
    ("addMessage", f"({msg_obj}IZZ)Z"), ("max_id", "[I"), ("min_id", "I"),
    ("messages", array_list), ("getMessages", f"(){array_list}"), ("requestIndex", "I"),
    ("deleteMessage", f"(II){msg_obj}"), ("startOffset", "I"), ("frozenStartOffset", "I"), ("loading", "Z"),
    ("setTotalCount", "(I)V"),
}
expected[ui + "Components/SharedMediaLayout;"] = {
    ("didReceivedNotification", f"(II{obj_array})V"),
    ("mediaPages", f"[{ui}Components/SharedMediaLayout$MediaPage;"),
    ("profileActivity", ui + "ActionBar/BaseFragment;"),
    ("dialog_id", "J"), ("mergeDialogId", "J"),
    ("sharedMediaData", f"[{ui}Components/SharedMediaLayout$SharedMediaData;"),
    ("sharedMediaPreloader", ui + "Components/SharedMediaLayout$SharedMediaPreloader;"),
    ("photoVideoAdapter", ui + "Components/SharedMediaLayout$SharedPhotoVideoAdapter;"),
    ("animationSupportingPhotoVideoAdapter", ui + "Components/SharedMediaLayout$SharedPhotoVideoAdapter;"),
    *((name, ui + "Components/SharedMediaLayout$SharedDocumentsAdapter;")
      for name in ("documentsAdapter", "voiceAdapter", "audioAdapter")),
    ("fillMediaData", "(I)Z"), ("jumpToDate", "(IIIZ)V"),
    ("getMediaPage", f"(I){ui}Components/SharedMediaLayout$MediaPage;"),
    ("getClosestTab", "()I"), ("scrollToPage", "(I)V"),
    ("checkLoadMoreScroll", f"({ui}Components/SharedMediaLayout$MediaPage;{ui}Components/RecyclerListView;Landroidx/recyclerview/widget/LinearLayoutManager;)V"),
}
expected[ui + "Components/SharedMediaLayout$SharedMediaPreloader;"] = {
    ("getSharedMediaData", f"()[{ui}Components/SharedMediaLayout$SharedMediaData;"),
}
expected[ui + "Components/SharedMediaLayout$SharedPhotoVideoAdapter;"] = {
    ("this$0", ui + "Components/SharedMediaLayout;"), ("getItemCount", "()I"), ("getTotalItemsCount", "()I"),
    ("getPositionForIndex", "(I)I"),
    ("onBindViewHolder", "(Landroidx/recyclerview/widget/RecyclerView$ViewHolder;I)V"),
}
expected[ui + "Components/SharedMediaLayout$SharedMediaListView;"] = {
    ("getColumnsCount", "()I"), ("isChangeColumnsAnimation", "()Z"),
    ("dispatchDraw", "(Landroid/graphics/Canvas;)V"),
}
expected[ui + "Components/SharedMediaLayout;"].add(
    ("scrollSlidingTextTabStrip", ui + "Components/SharedMediaLayout$ScrollSlidingTextTabStripInner;"))
expected[ui + "Components/VideoPlayerSeekBar;"].add(("isDragging", "()Z"))
expected[ui + "ActionBar/ActionBarLayout;"] = {("closeLastFragment", "(ZZ)V")}
expected[ui + "DialogsActivity;"].add(("onResume", "()V"))
expected[msg + "AccountInstance;"] = {("getInstance", f"(I){msg}AccountInstance;")}
expected[msg + "MessagesController;"].update({("getAllDialogs", f"(){array_list}"),
                                               ("getDialogs", f"(I){array_list}"),
                                               ("getDialogFilters", f"(){array_list}")})
expected.setdefault(msg + "UserConfig;", set()).add(("selectedAccount", "I"))
expected.setdefault(tl + "TL_dialog;", set())
ayu_preview = "Lcom/radolyn/ayugram/messages/AyuMessagesController;"
expected[ayu_preview] = {("getInstance", f"(){ayu_preview}"), ("getLastMessageCached", f"(IJ){msg_obj}")}
expected[msg + "MessagesController$DialogFilter;"] = {
    ("includesDialog", f"({msg}AccountInstance;J{tl}Dialog;)Z"),
    ("localId", "I"), ("isDefault", "()Z"),
}
expected[ui + "Components/MediaActivity;"] = {
    ("<init>", f"(Landroid/os/Bundle;{ui}Components/SharedMediaLayout$SharedMediaPreloader;)V"),
    ("sharedMediaLayout", ui + "Components/SharedMediaLayout;"), ("setChatInfo", f"({tl}ChatFull;)V"),
    ("onFragmentDestroy", "()V"),
    ("onBackPressed", "(Z)Z"),
}
expected[ui + "LaunchActivity;"].add(("presentFragment", f"({ui}ActionBar/BaseFragment;ZZ)Z"))
expected[ui + "LaunchActivity;"].add(("getActionBarLayout", f"(){ui}ActionBar/INavigationLayout;"))
expected[ui + "LaunchActivity;"].add(("onBackPressed", "(Z)Z"))
expected[ui + "ActionBar/BaseFragment;"].update({
    ("onFragmentDestroy", "()V"),
    ("getMessagesController", f"(){msg}MessagesController;"), ("getConnectionsManager", "()Lorg/telegram/tgnet/ConnectionsManager;"),
    ("getParentLayout", f"(){ui}ActionBar/INavigationLayout;"),
    ("getFragmentView", f"(){view}"),
    ("finishFragment", "(Z)Z"),
})
expected[viewer].add(("classGuid", "I"))
expected[viewer].update({("needShowOnReady", "Z"), ("showVideoSeekPreviewPosition", "(Z)V")})
expected[ui + "ActionBar/INavigationLayout;"] = {("getLastFragment", f"(){ui}ActionBar/BaseFragment;")}
expected[ui + "Cells/SharedPhotoVideoCell2;"] = {
    ("getMessageObject", f"(){msg_obj}"), ("imageReceiver", receiver),
}
expected[ui + "Cells/ChatMessageCell;"] = {("lastHeight", "I"), ("relayout", "()V")}
expected[msg_obj].add(("hasMediaSpoilers", "()Z"))
expected[player].update({
    ("<init>", "(ZZ)V"), ("getCurrentUri", "()Landroid/net/Uri;"), ("getCurrentPosition", "()J"),
    ("getPlaybackSpeed", "()F"), ("setPlaybackSpeed", "(F)V"), ("setPlayWhenReady", "(Z)V"),
    ("isPlayerPrepared", "()Z"),
    ("preparePlayer", "(Landroid/net/Uri;Ljava/lang/String;IJ)V"), ("releasePlayer", "(Z)V"),
    ("setDelegate", f"({ui}Components/VideoPlayer$VideoPlayerDelegate;)V"),
    ("getQualityForThumb", f"({array_list}){ui}Components/VideoPlayer$VideoUri;"),
})
expected[ui + "Components/VideoPlayer$VideoUri;"] = {("uri", "Landroid/net/Uri;"), ("fileVideoOffset", "J")}
expected["Lcom/google/android/exoplayer2/ui/AspectRatioFrameLayout;"] = {
    ("<init>", "(Landroid/content/Context;)V"), ("setAspectRatio", "(FI)V"), ("setResizeMode", "(I)V"),
}
expected[msg + "DialogObject;"].add(("isEncryptedDialog", "(J)Z"))
expected[tl + "TL_messages_search;"] = {
    ("<init>", "()V"), ("offset_id", "I"), ("add_offset", "I"), ("limit", "I"), ("q", "Ljava/lang/String;"),
    ("peer", tl + "InputPeer;"), ("filter", tl + "MessagesFilter;"),
}
expected[tl + "TL_inputMessagesFilterPhotoVideo;"] = {("<init>", "()V")}
expected[tl + "messages_Messages;"].update({("flags", "I"), ("count", "I"), ("offset_id_offset", "I")})
expected[ui + "Components/SharedMediaLayout$SharedDocumentsAdapter;"] = {
    ("this$0", ui + "Components/SharedMediaLayout;"), ("currentType", "I"),
    ("getItemCount", "()I"), ("getTotalItemsCount", "()I"),
}
expected[ui + "Components/SharedMediaLayout$MediaPage;"] = {
    ("listView", ui + "Components/SharedMediaLayout$InternalListView;"), ("selectedType", "I"),
}
expected[ui + "Components/SharedMediaLayout$MediaSearchAdapter;"] = {
    ("getItemCount", "()I"), ("searchResult", array_list), ("globalSearch", array_list),
}

expected[chat].update({("headerItem", menu), ("bookmarksItem", ui + "ActionBar/ActionBarMenuItem$Item;"),
                       ("updateVisibleRows", "()V")})
expected[menu].add(("setSubItemShown", "(IZ)V"))
expected[menu].add(("setIcon", "(IZ)V"))
expected[ui + "ActionBar/ActionBarMenu;"] = {("getItem", f"(I){menu}")}
expected[ui + "PhotoViewer$PhotoViewerActionBarContainer;"].update({
    ("getTitle", "()Ljava/lang/CharSequence;"), ("setTitle", "(Ljava/lang/CharSequence;)V"),
    ("titleTextView", "[" + ui + "ActionBar/SimpleTextView;"),
})
expected[ui + "ActionBar/SimpleTextView;"].update({("setTextSizePx", "(I)V"),
                                                  ("getPaint", "()Lcom/exteragram/messenger/utils/ui/TextPaint;")})
expected[ui + "Components/AnimatedTextView;"] = {
    ("getDrawable", f"(){ui}Components/AnimatedTextView$AnimatedTextDrawable;"), ("setTextSize", "(F)V"),
}
expected[ui + "Components/AnimatedTextView$AnimatedTextDrawable;"] = {("getTextSize", "()F")}
expected[msg + "MessagesController;"].add(("getUserOrChat", "(J)Lorg/telegram/tgnet/TLObject;"))
expected[msg + "DialogObject;"].add(("getDialogTitle", "(Lorg/telegram/tgnet/TLObject;)Ljava/lang/String;"))
expected[msg + "LocaleController;"] = {("formatShortNumber", "(I[I)Ljava/lang/String;"),
                                     ("formatDateAudio", "(JZ)Ljava/lang/String;"),
                                     ("getCurrentLocale", "()Ljava/util/Locale;")}
expected[msg + "R$drawable;"].update({("photo_star", "I"), ("photo_star_fill", "I")})
expected["Lxyz/nextalone/nagram/helper/BookmarksHelper;"].add(("removeBookmarks", "(IJ[I)Z"))
expected[ui + "MainTabsActivity;"] = {
    ("tabsView", f"{ui}MainTabsLayout;"),
    ("tabsBarContainer", "Landroid/widget/LinearLayout;"),
    ("searchTabButton", "Landroid/widget/FrameLayout;"),
    ("onResume", "()V"), ("createView", "(Landroid/content/Context;)Landroid/view/View;"),
    ("blur3_invalidateBlur", "()V"),
}
expected[ui + "ViewPagerActivity;"] = {("getCurrentVisibleFragment", f"(){ui}ActionBar/BaseFragment;")}
expected[ui + "DialogsActivity;"].update({("refreshSearchSettingsUi", "()V"), ("blur3_InvalidateBlur", "()V")})
expected["Ltw/nekomimi/nekogram/helpers/MainTabsHelper;"] = {
    (name, "()I") for name in ("getMainTabsHeight", "getMainTabsHeightWithMargins", "getMainTabsMargin")
}
blur_drawable = ui + "Components/blur3/drawable/BlurredBackgroundDrawable"
expected[blur_drawable + "RenderNode;"] = {
    ("renderNodeFill", "Landroid/graphics/RenderNode;"),
    ("liquidGlassEffect", f"{ui}Components/blur3/LiquidGlassEffect;"),
    ("setLiquidGlassEffectAllowed", "()V"),
    ("invalidateDisplayList", "()V"), ("updateColors", "()V"),
}
expected[blur_drawable + ";"] = {("setRadius", f"(F){blur_drawable};"), ("backgroundColor", "I")}
expected[ui + "LaunchActivity;"].add(("instance", ui + "LaunchActivity;"))
expected[ui + "ActionBar/INavigationLayout;"].add(("getFragmentStack", "()Ljava/util/List;"))
expected[viewer].update({("playerLooping", "Z"), ("manuallyPaused", "Z"), ("onActionClick", "(Z)V"),
                         ("videoPlayerControlVisible", "Z")})
expected[player].add(("saveLooping", f"(Z{msg_obj})V"))
expected[ui + "Components/VideoPlayer$VideoUri;"].add(
    ("getUri", f"(I{tl}Document;I)Landroid/net/Uri;"))
expected[receiver].update({("setParentView", "(Landroid/view/View;)V"), ("setFileLoadingPriority", "(I)V")})
expected[msg + "FileLoader;"].update({("PRIORITY_LOW", "I"), ("PRIORITY_NORMAL", "I")})
expected[chat].update({
    ("selectedObject", msg_obj), ("selectedObjectGroup", group),
    ("nkbtn_onclick", "(I)V"),
})
expected[ui + "Cells/ChatMessageCell;"].update({
    ("onDraw", "(Landroid/graphics/Canvas;)V"), ("getMessageObject", f"(){msg_obj}"),
    ("getBackgroundDrawableLeft", "()I"), ("getBackgroundDrawableRight", "()I"),
    ("getBackgroundDrawableTop", "()I"),
    ("drawSideButton", "(Landroid/graphics/Canvas;Z)V"), ("drawSideButton", "I"),
    ("getCurrentMessagesGroup", f"(){group}"),
    ("getCurrentPosition", f"(){msg}MessageObject$GroupedMessagePosition;"),
    ("sideButtonVisible", "Z"), ("hideSideButtonByQuickShare", "Z"),
    ("getSideButtonStartX", "()F"), ("getSideButtonStartY", "()F"),
    ("applyServiceShaderMatrix", "()V"), ("getThemedPaint", "(Ljava/lang/String;)Landroid/graphics/Paint;"),
    ("hasGradientService", "()Z"),
    ("onTouchEvent", "(Landroid/view/MotionEvent;)Z"), ("getEventX", "(Landroid/view/MotionEvent;)F"),
    ("getEventY", "(Landroid/view/MotionEvent;)F"), ("getDelegate", f"(){ui}Cells/ChatMessageCell$ChatMessageCellDelegate;"),
})
expected[ui + "Cells/ChatMessageCell$ChatMessageCellDelegate;"] = {("canPerformActions", "()Z")}
expected[group].add(("isDocuments", "Z"))
expected.setdefault(msg + "MessageObject$GroupedMessagePosition;", set()).add(("last", "Z"))
expected[chat].update({("forwardMessagesExternally", f"({array_list}JZZZI)V"), ("isSecretChat", "()Z")})
expected[msg + "MessagesController;"].update({("isChatNoForwards", "(J)Z"),
    ("updateInterfaceWithMessages", f"(J{array_list}I)Z"),
    ("deleteMessages", f"({array_list}{array_list}{tl}EncryptedChat;JIZI)V")})
expected[msg_obj].update({("canForwardMessage", "()Z"), ("isSent", "()Z"), ("isSending", "()Z")})
expected[tl + "Message;"].add(("params", "Ljava/util/HashMap;"))
expected[events].update({("currentAccount", "I"), ("postNotificationName", f"(I{obj_array})V"),
                         ("messageReceivedByServer", "I"), ("messageSendError", "I")})
expected.setdefault(msg + "ApplicationLoader;", set()).add(("mainInterfacePaused", "Z"))
expected.setdefault(ui + "Components/SizeNotifierFrameLayout;", set()).add(("drawingBlur", "Z"))
expected[msg + "R$drawable;"].update({("msg_saved_solar", "I"), ("msg_saved_filled_solar", "I"),
                                      ("baseline_keyboard_arrow_down_24", "I")})
expected.setdefault(tl + "TL_inputPeerSelf;", set()).add(("<init>", "()V"))
expected[menu].add(("setIconColor", "(I)V"))
expected[msg_obj].update({("getDocument", f"({tl}Message;){tl}Document;"),
                          ("getPhoto", f"({tl}Message;){tl}Photo;"), ("isOutOwner", "()Z")})
expected[msg + "DialogObject;"].add(("getPeerDialogId", f"({tl}Peer;)J"))
expected["Lxyz/nextalone/nagram/helper/BookmarksHelper;"].add(("getBookmarkedDialogsCounts", "(I)Ljava/util/Map;"))
expected["Ltw/nekomimi/nekogram/ui/BookmarksActivity;"] = {("<init>", "(J)V"),
    ("updateVisibleMessageCells", "()V"), ("filteredMessages", array_list), ("listView", ui + "Components/RecyclerListView;")}
blur_color = ui + "Components/blur3/drawable/color/"
expected[blur_drawable + ";"].update({("colorProvider", blur_color + "BlurredBackgroundColorProvider;"),
    ("setColorProvider", f"({blur_color}BlurredBackgroundColorProvider;){blur_drawable};")})
expected[blur_color + "impl/BlurredBackgroundProviderImpl;"] = {
    ("bottomPanelChatActivity", f"({ui}ActionBar/Theme$ResourcesProvider;){blur_color}BlurredBackgroundProvider;")}
expected[msg + "R$drawable;"].add(("msg_message", "I"))

flavor = next(path for path in base.glob("NagramXF*plugin-arm64*") if path.is_dir())
found = {}
for dex in flavor.glob("classes*.dex"):
    with subprocess.Popen([str(dump), str(dex)], stdout=subprocess.PIPE) as process:
        current = None
        name = None
        for line in process.stdout:
            if line.startswith(b"  Class descriptor"):
                descriptor = line.split(b"'")[1].decode()
                current = found.setdefault(descriptor, set()) if descriptor in expected else None
                name = None
            elif current is not None:
                if line.startswith(b"      name "):
                    name = line.split(b"'")[1].decode()
                elif line.startswith(b"      type ") and name:
                    current.add((name, line.split(b"'")[1].decode()))
                    name = None
        assert process.wait() == 0, dex
missing = {key: members - found.get(key, set()) for key, members in expected.items()
           if key not in found or members - found[key]}
for key, members in missing.items():
    print(key, members)
    for name, _ in members:
        print("  ", sorted(item for item in found.get(key, []) if item[0] == name))
assert not missing, f"{len(missing)} classes with missing signatures"
print(f"{flavor.name}: verified {len(expected)} classes and {sum(map(len, expected.values()))} members")
