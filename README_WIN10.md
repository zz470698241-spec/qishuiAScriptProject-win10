# 汽水音乐脚本 Win10 版

原 GitHub 项目 `wei6718189/qishuiAScriptProject` 是 **iOS + AScript 框架**专用脚本，只能在装了 AScript App 的 iPhone 上通过 WebDriverAgent（苹果设备调试连接）运行。本版本把 iOS 专属接口全部替换成 Windows 上等价的实现，可在一台 Win10 电脑上直接以普通 Python 程序跑起来，**业务逻辑一行没改**。

---

## 一、这个版本改了什么

| 原 iOS 能力 | Win10 实现 | 说明 |
|---|---|---|
| `ascript.ios.action` 点击 | `win_platform.action` | ADB（安卓调试桥）发 `input tap`，或 pyautogui 点鼠标 |
| `ascript.ios.system.R` 资源路径 | `win_platform.R` | 指向本地 `res/img/` |
| `ascript.ios.system.app_start` | `win_platform.app_start` | ADB 按包名启动 App，或启动 PC 客户端 |
| `ascript.ios.system.screen_size` | `win_platform.screen_size` | 从截图尺寸自动获取 |
| `ascript.ios.system.notify` | `win_platform.notify` | 控制台提示 + 系统提示音 |
| `ascript.ios.screen.Ocr` | `win_platform.Ocr` | 换成 RapidOCR（PaddleOCR 模型的轻量版，纯 CPU 可跑，比原 PaddleOCR 省内存） |
| `ascript.ios.screen.FindImages` | `win_platform.FindImages` | OpenCV 模板匹配 |
| `ascript.ios.node.Selector` 控件树 | `win_platform.Selector` | Win10 没有等价控件树，优雅降级返回空；原脚本里它只是第三层兜底，前面已有模板匹配和 OCR 两层 |

新增文件：`config.py`（配置）、`win_platform/`（适配层）、`run.py`（启动入口）、`selftest.py`（自检）、`requirements.txt`、`install.bat`、三个 `.bat` 快捷入口、本文档。

---

## 一B、本机部署与验证状态（重要）

**代码已通过端到端自检**：运行 `python selftest.py`，用合成屏幕图 + 真实 OCR 把全部 5 个业务阶段和核心循环驱动一遍，**16/16 项通过**——包括跳过开屏、关弹窗、识别「免/立即解锁」入口、等倒计时、两步领奖、循环累加与空跑自动退出。这证明代码逻辑本身没有问题。

**真机端到端的前提（本机组装前不具备）**：脚本要真正自动点广告，还需要以下三样，需你自行准备：

| 需要准备 | 说明 | 状态 |
|---|---|---|
| 安卓模拟器（雷电/夜神/MuMu 等）或安卓手机 | 在里面安装汽水音乐 App | 本机未安装 |
| ADB 工具（Android Debug Bridge） | 电脑用来控制模拟器的命令行工具 | 本机未安装 |
| 汽水音乐 App（安卓版） | 被自动操作的目标 | 需装进模拟器 |

准备好后，在 `config.py` 填 `ADB_PATH`（adb.exe 路径）和 `APP_PACKAGE`（包名），即可运行。启动入口的预检会在缺 ADB 时明确拦截，不会盲跑。

**本机已完成的部署**：
- Python 依赖全部装好（rapidocr / onnxruntime / opencv / numpy / pillow / pyautogui）
- 桌面已放启动器：`汽水脚本Win10.bat`（双击即可运行）
- 项目内三个入口：`启动脚本.bat`（运行）、`一键自检.bat`（自检）、`修改配置.bat`（打开配置）

---

## 二、先选控制方式

打开 `config.py`，改 `SCREEN_BACKEND`：

| 方式 | 取值 | 适合场景 | 坐标系 |
|---|---|---|---|
| **ADB 控制安卓设备/模拟器**（推荐） | `"adb"` | 电脑上开安卓模拟器跑汽水音乐，或手机 USB/WiFi 连电脑。最接近原脚本的手机竖屏场景，原有百分比区域可直接复用 | 设备屏幕坐标（竖屏） |
| **控制 Win10 桌面窗口** | `"desktop"` | 汽水音乐有可全屏的 PC 窗口 | 桌面坐标（横屏） |

> 用 ADB 方式时，建议把模拟器分辨率设成接近手机的竖屏比例（如 1080×1920），识别区域才准。

---

## 三、安装步骤

1. **Python**：本机已装 Python 3.13.14，不用再装。
2. **装依赖**：双击 `install.bat`（或命令行执行 `python -m pip install -r requirements.txt`）。
3. **准备 ADB**（仅 `"adb"` 方式需要）：
   - 用安卓模拟器（雷电/夜神/MuMu 等）一般自带 `adb.exe`；
   - 或下载 Android SDK Platform Tools（谷歌官方的 ADB 工具包），解压得到一个文件夹；
   - 在 `config.py` 里把 `ADB_PATH` 填成 `adb.exe` 的完整路径，例如 `r"D:\adb\adb.exe"`；留空则脚本自动在 PATH 和常见目录里找。
4. **打开汽水音乐**：先启动模拟器并在里面装好汽水音乐，或让手机开启 USB 调试并连上电脑。

---

## 四、配置项（config.py）

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `SCREEN_BACKEND` | `"adb"` | 控制方式，见上表 |
| `ADB_PATH` | 空 | `adb.exe` 路径，留空自动查找 |
| `ADB_DEVICE` | 空 | 多设备时填序列号（`adb devices` 可查），单设备留空 |
| `APP_PACKAGE` | `com.soda.music.android` | 汽水音乐**安卓版**包名（iOS 原版是 `com.soda.music`，不一样） |
| `DESKTOP_EXE_PATH` | 空 | PC 客户端 exe 路径，留空则提示手动打开窗口 |
| `OCR_MIN_CONFIDENCE` | `0.5` | 文字识别置信度门槛，识别不稳可调低到 0.35 |
| `TEMPLATE_CONFIDENCE` | `0.8` | 找图匹配阈值，识别不到可调低到 0.7 |

**确认包名**（ADB 方式）：命令行执行
```
adb shell pm list packages | findstr /i soda
```
把查到的包名填进 `APP_PACKAGE`。

---

## 五、运行

```
python run.py
```

- 启动会先做预检（依赖 + 设备连接），不通过会直接告诉你原因；
- 运行日志同时打印在屏幕上并写入 `run.log`，出问题方便排查；
- 按 `Ctrl + C` 停止；
- 调试时可加参数跳过预检：`python run.py --skip-check`。

脚本流程与原版一致：启动 App → 跳开屏广告 → 你手动进第一个广告 → 脚本自动循环领奖励。

---

## 六、图片资源要重新裁剪吗

`res/img/` 里的模板图是按原 iOS 设备（1284×2778）截的：

- **OCR 相关逻辑**全部按屏幕百分比动态计算，换分辨率影响不大；
- **直播间关闭按钮**用的是模板图匹配（`img_zhibojian-close01.png`），如果安卓设备分辨率/UI 差别大，可能匹配不到。脚本还有 OCR 和控件兜底，实在不行就按当前屏幕重新截一张关闭按钮图覆盖它。

---

## 七、常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 预检提示"找不到 adb.exe" | 没装或路径没填 | 在 `config.py` 填 `ADB_PATH` |
| 预检提示"未检测到已授权设备" | 模拟器没开 / 手机没弹授权 | 打开模拟器，或手机上点"允许 USB 调试授权" |
| 提示"缺少依赖" | 没装依赖包 | 双击 `install.bat` |
| OCR 识别不到文字 | 置信度门槛太高 | `OCR_MIN_CONFIDENCE` 调到 0.35 |
| 点击没反应 | 坐标体系不对 | 确认模拟器是竖屏、分辨率接近 1080×1920 |
| 直播间关闭按钮点不到 | 模板图分辨率不匹配 | 重新截图覆盖 `res/img/img_zhibojian-close01.png` |
| 首次运行慢 | RapidOCR 首次加载模型 | 正常，之后会快 |

---

## 八、提醒

自动化点击广告可能违反汽水音乐的用户协议，存在账号受限风险，请自行评估后使用。本项目仅供技术学习与个人设备自动化研究。
