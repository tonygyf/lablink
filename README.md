# LabLink

中文、深蓝主题的实验室服务器连接工具。填写自己的地址和 SSH 用户后，用一个窗口或一条命令打开终端、GPU 监控、VNC 和 1Panel。

**这是独立发行项目，不包含任何实际服务器地址、用户账号或私钥，也不会改动已有的 LabServer、SSH config、系统代理或防火墙。**

## 三步开始（Windows 10/11）

前提：安装 Python 3.10+（包含 tkinter）与 Windows OpenSSH 客户端。下载源码 ZIP 并解压，在项目根目录打开 PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
.\lablink.cmd setup
.\lablink.cmd gui
```

安装器把项目安装到 `%LOCALAPPDATA%\LabLink\venv`，并创建桌面 `LabLink` 快捷方式。安装完成后可以移动或删除解压目录，快捷方式和配置不依赖源码位置。重复安装会更新程序，保留用户配置。

`setup` 依次询问：服务器地址、SSH 用户、端口、密钥路径、可选 VNC 客户端路径、1Panel 端口与安全入口。默认模板的主机、用户、密钥路径都为空。**不会自动沿用你原来的 SSH 配置**。

首次运行终端登录，请核对服务器主机指纹，再输入 SSH 密码或密钥口令。程序不保存密码、VNC 密码、私钥内容或 Tailscale 授权密钥。

## 校外连接

LabLink 是连接工具，不是 VPN 服务。校外访问需要先让电脑和服务器加入同一 Tailscale 网络，或者自行提供可达的 SSH 地址。

```powershell
.\lablink.cmd addon tailscale --apply
```

在客户端登录 Tailscale 后，服务器端已有 Tailscale 的直接登录即可。尚未安装时，先在可访问服务器的网络里填写校园内网地址，再执行：

```powershell
.\lablink.cmd addon tailscale --server       # 展示安装步骤
.\lablink.cmd addon tailscale --server --apply
```

随后通过 SSH 在服务器运行 `sudo tailscale up --accept-dns=false`，按链接登录同一账号；再执行 `tailscale ip -4`，把结果填入 LabLink 的服务器地址。切换手机热点后重新运行 `doctor` 和 `ssh` 验证，不能仅凭校园网内成功就认定校外成功。

## 命令

| 命令 | 功能 |
|---|---|
| `setup` | 交互填写 / 修改配置 |
| `ssh` | SSH 终端 |
| `gpu` | `watch -n 2 nvidia-smi`（服务器需具备此命令） |
| `vnc` | 临时本机隧道 + TigerVNC Viewer |
| `panel` | 临时本机隧道 + 浏览器打开 1Panel |
| `gui` | 中文深蓝窗口（启动按钮支持 Windows） |
| `doctor` | TCP 可达性及免交互 SSH 验证 |
| `config-path` | 显示配置文件位置 |
| `import-config FILE` | 校验并导入 JSON 配置 |
| `addon NAME [--server] [--apply]` | 可选组件，默认预览 |

Windows 安装器装好后，也可以直接运行 `%LOCALAPPDATA%\LabLink\venv\Scripts\lablink.exe`。Python CLI 支持 Windows/Linux；GUI 主要面向 Windows。Linux 开发环境可运行 `python3 -m venv .venv`、`.venv/bin/pip install .`、`.venv/bin/lablink setup`。

## 可选扩展

### VNC（用户有时写成 NVC）

```powershell
.\lablink.cmd addon vnc --apply
```

此命令打开 **TigerVNC 官方下载页**，不下载第三方修改版。安装 Viewer 后在 setup 填写其完整路径，常见 Windows 安装路径也会自动检测。

```powershell
.\lablink.cmd addon vnc --server --apply
```

服务器端仅支持 Debian/Ubuntu 的 `apt-get`，此命令**只安装 x11vnc 软件包**。仍需按已有桌面环境配置显示器、认证文件、VNC 密码及仅本机监听；不会擅自修改桌面会话或创建开机服务。Wayland、无桌面服务器不保证适用。详见 [扩展指南](docs/EXTENSIONS.md)。

### 1Panel

```powershell
.\lablink.cmd addon 1panel --server
.\lablink.cmd addon 1panel --server --apply
```

调用 1Panel 官方 Linux 安装器，需要 sudo；安装器可能安装 Docker、创建服务和配置监听端口。建议先在新服务器测试。已有 `1pctl` 时跳过安装，不重置现有面板。

安装后把实际面板端口、HTTP/HTTPS 和安全入口填入 setup。`panel` 通过 `127.0.0.1` 隧道访问，无需修改系统代理或公开面板端口。使用结束后在对应终端按 Enter，隧道自动关闭；关闭浏览器标签不会自动结束隧道。HTTPS 的证书可能与 localhost 不匹配；本项目不关闭证书校验。绑定域名的面板需要自行配置与该域名相容的访问方式。

## 配置、隐私与卸载

- Windows：`%LOCALAPPDATA%\LabLink\config.json`；Linux：`~/.config/LabLink/config.json`。
- `LABLINK_HOME` 可覆盖配置目录，**不要将它指向公开仓库**。
- SSH 使用独立 `known_hosts`，首次核验指纹；不会禁用主机密钥校验。
- 不修改 `~/.ssh/config`、系统代理、现有 Tailscale 服务；不自动设置公网端口或子网路由。
- 隧道仅监听 `127.0.0.1`，每次自动选空闲端口；客户端退出时回收本次 SSH 进程。
- 用 SSH key/agent 可减少重复输入；密码登录可用，但 `doctor` 的免交互检查会失败。
- 卸载：关闭 LabLink 与它启动的终端，删除桌面快捷方式及 `%LOCALAPPDATA%\LabLink`。此操作会删除 LabLink 配置和主机指纹记录，**不会卸载**独立安装的 Tailscale/VNC/1Panel。

## 开发与发布

```bash
python -m pip install .
python -m unittest discover -s tests -v
python scripts/release.py
```

发布脚本按白名单打包源码，不携带本机配置、密钥、虚拟环境和 Git 历史。Windows/Linux CI 已配置。详见 [发布指南](docs/RELEASING.md)。

当前版本：`0.1.0`。真实 Windows UI、管理员安装、跨网连接请按发布检查表验收；自动测试不替代这些环境测试。

MIT License。第三方软件的许可、账号和服务政策由各自提供方负责。
