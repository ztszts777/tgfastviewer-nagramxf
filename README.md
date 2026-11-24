# TG快点滑 · NagramXF

TG 快点滑的 NagramXF 内置插件版。从聊天或频道里打开单张图片或视频时，插件会优先加载当前媒体附近的记录，方便滑到相邻媒体。

## 实测

- **NagramXF 12.10.1.1251 ARM64 插件版，Android 16**
- 启用插件后，冷启动约 **1.1 秒**。
- 打开公开频道的一条旧视频时，从发出媒体查询到投递 **39 条媒体**约 **0.29 秒**，实测能滑到相邻视频。耗时为这次测试的记录。

## 安装

1. 从 [Release 的 Assets](../../releases/latest) 下载 `tgfastviewer_nagramxf.plugin`。
2. 打开 **NagramXF → N-设置 → 插件**，确认插件引擎已启用。
3. 点右上角 **＋**，选中下载的文件，勾选 **安装后启用**，再点 **安装插件**。

如果之前用过 **TG 快点滑 · NagramXF 的 LSPosed APK**，先在 **LSPosed 管理器 → 模块**里关闭该模块，再强制停止并重新打开 NagramXF。实测旧模块会让该版本的 NagramXF 卡在启动遮罩。

原作者为 **dunxuan**。插件文件内含完整 MIT 许可证与原作者版权声明。[原项目](https://github.com/dunxuan/tgfastviewer) · [实测客户端版本](https://github.com/Keeperorowner/NagramXF/releases/tag/1251)
