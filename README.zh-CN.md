# NagramXF 媒体增强

[English](README.md) · **简体中文**

在 NagramXF 中更快地浏览聊天媒体、补齐 AyuGram 过滤后的显示，并调整照片、视频和音乐播放器。安装一个 `.plugin` 即可使用，功能可以按需开关。

**[下载最新版插件](https://github.com/ztszts777/tgfastviewer-nagramxf/releases/latest/download/nagramxf_media_suite.plugin)** · [文档站](https://ztszts777.github.io/tgfastviewer-nagramxf/zh-cn/) · [发布说明](https://github.com/ztszts777/tgfastviewer-nagramxf/releases/latest) · [版本记录](CHANGELOG.md) · [反馈问题](https://github.com/ztszts777/tgfastviewer-nagramxf/issues)

## 安装与升级

1. 在 NagramXF 打开「N-设置 → 插件」，确认插件引擎已启用。
2. 下载 `nagramxf_media_suite.plugin`，点插件页右上角的「＋」导入，然后启用「NagramXF 媒体增强」。
3. 已安装「NagramXF 媒体工具」或「NagramXF 插件合集」时，直接导入新版并选择更新，原有设置可继续使用。如果还装有同功能的旧版独立插件，请先禁用对应的独立插件。

在「NagramXF 媒体增强」设置中，可按媒体浏览、播放器界面、播放手势、手势振动、全屏与旋转、音频与播控分别调整。

## 功能

| 功能 | 使用方式 |
| --- | --- |
| **TG 快点滑** | 从聊天或频道点开照片或视频时，优先加载当前位置附近的媒体。左右滑到已加载范围的边缘时继续补页，分页时保留完整相册。 |
| **AyuGram 过滤显示修复** | 沿用当前聊天的 AyuGram 规则和排除设置。过滤后没有可见消息的日期会隐藏，聊天列表预览会尝试回落到最近一条可见消息。规则也应用于置顶栏、共享媒体、文件及全屏媒体的左右切换。 |
| **过滤聊天的未读更新** | 在普通聊天点右下角箭头跳到最新位置，且已加载的最新消息被过滤时，使用客户端原生流程更新已读。跳到未读分隔线或取消跳转时沿用原有行为。 [v1.1.1 更新说明](https://github.com/ztszts777/tgfastviewer-nagramxf/releases/tag/v1.1.1) |
| **照片与视频界面** | 横竖屏使用统一的顶栏与可展开说明。视频齿轮提供倍速、可用画质、播放模式和后台听视频。 |
| **缩略图侧栏** | 横竖屏都可使用。点击小箭头展开或收起，拖动小箭头调整宽度或高度。默认收起，可改为默认展开，状态可按聊天或全局记忆。包含单媒体消息，按消息或聊天分隔，并沿滚动方向预载。 |
| **共享媒体库** | 从查看器进入媒体库时，尽量将当前媒体移到可见范围中部，并用角标提示当前位置。返回会先回查看器，再回聊天中的消息位置。 |
| **音乐工具栏** | 播放按键和功能按键分两行，倍速和睡眠定时可从工具栏直接打开。可独立隐藏「添加到个人资料页」按钮。 |
| **睡眠定时** | 在视频或音乐播放器点时钟。支持 15、30、45、60、90、120 分钟预设，自定义 1–1440 分钟，以及到点后播完当前媒体再停止。定时启动后，时钟点亮并显示剩余时间。 |
| **系统画中画与播控** | 从视频的「更多」进入 Android 系统小窗。小窗和系统播控提供播放、暂停、前进和后退 15 秒。贴边收起或拉出小窗时，保留原来的播放状态。系统播控支持视频标题与可用封面。 |
| **后台听视频** | 在视频的齿轮菜单点亮「后台听视频」，离开播放页后可通过应用顶部的播放条继续听。开关按聊天保存。 |

## 播放手势与默认值

| 操作 | 效果 |
| --- | --- |
| 双击中间 | 播放或暂停。 |
| 双击左右两侧 | 左侧后退，右侧前进。跳转时长沿用 NagramXF 自身的设置。 |
| 长按播放页的空白区域或画面 | 临时切换到 2.5 倍速，松手恢复。可选 1.5、2、2.5、3、4 倍或自定义。 |
| 双指缩放 | 缩放画面，缩放后可点还原按钮。 |
| 中央上下滑 | 横向视频下滑进入全屏，上滑退出全屏。 |
| 左右侧上下滑 | 左侧调亮度，右侧调媒体音量。同一播放页切换视频时保留调整，退出时恢复。可调整升降刻度的振动强度和频率上限。 |

「宽视频自动横屏」默认开启，以宽度大于高度为门槛。照片初始沿用手机当前方向，打开后可跟随设备旋转。需要在切换媒体时也自动旋转，可以开启「切换媒体时自动旋转」。

插件界面默认跟随 Android 系统语言，也可在插件设置里手动选择简体中文或 English。竖屏缩略图默认在底部、初始收起并按聊天记忆。手势振动每 1% 一刻，默认强度 60%，每秒最多 30 次。

## 兼容性与排查

| 项目 | 范围 |
| --- | --- |
| 插件声明的最低客户端版本 | NagramXF `12.10.1`，需带插件引擎。 |
| 已核对的 APK | NagramXF `12.10.1.1251`，构建 `30dcd6c`，`arm64-v8a` 插件版。 [客户端发布页](https://github.com/Keeperorowner/NagramXF/releases/tag/1251) |
| 合集验证范围 | `v1.7.0` 通过 Python 回归测试及上述 APK 的接口核验，设置页切换开关的滚动位置已通过真机确认。 |

- **找不到插件入口**时，确认安装的是 NagramXF 插件版并启用了插件引擎。
- **小窗无法打开**时，在 Android 系统设置中确认 NagramXF 获准使用画中画，并检查插件的「Android 系统小窗」开关。
- **控件重复或功能冲突**时，在插件列表禁用同功能的旧版独立插件，再复试。
- **提交问题**时，请附 NagramXF 的版本和构建号、Android 版本、插件版本、相关开关以及复现步骤。如果只在某类聊天或媒体中出现，也请一并注明。 [GitHub Issues](https://github.com/ztszts777/tgfastviewer-nagramxf/issues)

## 源码与构建

Release 里的 `.plugin` 是可直接安装和阅读的 Python 文件。维护用源码位于 `plugins/`，下载单个模块进行开发时，可在下表找到对应文件。

| 文件 | 内容 |
| --- | --- |
| [`nagramxf_media_suite.plugin`](plugins/nagramxf_media_suite.plugin) | 合集安装文件，由构建脚本生成。 |
| [`tgfastviewer_nagramxf.plugin`](plugins/tgfastviewer_nagramxf.plugin) | 媒体快速加载、补页与相册分组。 |
| [`ayufilter_display_fix.plugin`](plugins/ayufilter_display_fix.plugin) | AyuGram 过滤显示与未读更新。 |
| [`video_seekbar_gesture_insets.plugin`](plugins/video_seekbar_gesture_insets.plugin) | 照片与视频布局、手势和旋转。 |
| [`media_sleep_timer.plugin`](plugins/media_sleep_timer.plugin) | 睡眠定时、音乐工具栏和资料页按钮。 |
| [`system_video_pip.plugin`](plugins/system_video_pip.plugin) | Android 画中画、系统播控和后台听视频。 |

如需修改合集，从仓库根目录运行以下命令。生成的 `plugins/nagramxf_media_suite.plugin` 可在 NagramXF 中导入测试。

```sh
python tools/build_media_suite.py
```

## 许可证与署名

合集按 GNU GPLv3 发布，许可标识为 `GPL-3.0-only`。 [完整许可证](LICENSE)

TGFastViewer 原作者为 **dunxuan**。合集保留原作者的版权声明和完整 MIT 文本，已按 MIT 发布的独立适配版 `v1.0.1` 继续适用原许可。 [上游项目](https://github.com/dunxuan/tgfastviewer) · [MIT 声明](LICENSES/TGFastViewer-MIT.txt) · [v1.0.1 旧版](https://github.com/ztszts777/tgfastviewer-nagramxf/releases/tag/v1.0.1)
