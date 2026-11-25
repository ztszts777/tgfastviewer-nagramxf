# NagramXF 插件合集

一个 `.plugin` 包含 TG 快点滑、AyuGram 过滤显示修复以及视频和音乐播放工具。安装后可在插件设置中单独开关各项功能。

## 安装

1. 从 [GitHub Releases](https://github.com/ztszts777/tgfastviewer-nagramxf/releases) 下载 `nagramxf_media_suite.plugin`。
2. 在 NagramXF 打开「N-设置 → 插件」，点「＋」选择下载的文件。已有同名媒体工具插件时，选择更新。
3. 如果之前单独安装过 TG 快点滑、AyuGram 显示修复，或独立的进度条、定时、画中画插件，先禁用旧插件，再启用合集，避免同一功能执行两次。

本版已通过 Python 回归测试，并核对 NagramXF `12.10.1.1251`（构建 `30dcd6c`，插件版，arm64-v8a）的 APK 接口。新版的画中画贴边行为还需在手机上验证。

## 源码与许可

发布附件是可读的 Python 源码，也可以直接安装。维护用的各模块源码在 `plugins/`。在仓库根目录运行 `python tools/build_media_suite.py`，可以重新生成 `plugins/nagramxf_media_suite.plugin`。

合集以 [GPLv3](LICENSE) 发布。TGFastViewer 由 dunxuan 创建，原代码的 [MIT 声明](LICENSES/TGFastViewer-MIT.txt) 随插件附带。此前按 MIT 发布的 [v1.0.1](https://github.com/ztszts777/tgfastviewer-nagramxf/releases/tag/v1.0.1) 继续适用原许可。
