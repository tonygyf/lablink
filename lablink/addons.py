"""Explicit optional installers. No installer runs during pip install or setup."""
import os
import shlex
import subprocess
import webbrowser
from .config import load
from .transport import executable, ssh_args

URLS = {
    "tailscale": "https://tailscale.com/install.sh",
    "1panel": "https://resource.fit2cloud.com/1panel/package/v2/quick_start.sh",
}


def server_script(name):
    if name == "vnc":
        return "set -eu; command -v apt-get >/dev/null; sudo apt-get update; sudo apt-get install -y x11vnc; echo 'Installed only. Configure a local desktop, VNC password and localhost binding before use.'"
    check = "tailscale" if name == "tailscale" else "1pctl"
    script = f"""set -eu
if command -v {check} >/dev/null; then echo 'Already installed; no changes made.'; exit 0; fi
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
curl -fL --proto '=https' --tlsv1.2 --connect-timeout 15 --max-time 180 {shlex.quote(URLS[name])} -o "$tmp"
sudo bash "$tmp"
"""
    if name == "tailscale":
        script += "echo 'Next: sudo tailscale up --accept-dns=false (sign in interactively)'\n"
    return script


def install(name, server=False, apply=False):
    if server:
        c = load()
        script = server_script(name)
        print("将在所配置服务器执行（需要 sudo；1Panel 可能安装 Docker 并修改系统服务）：\n" + script)
        if not apply:
            print("这是预览。确认后添加 --apply 执行。")
            return 0
        return subprocess.call(ssh_args(c) + ["-tt", c["host"], "bash -c " + shlex.quote(script)])
    if name == "1panel":
        raise ValueError("1Panel 安装在 Linux 服务器：addon 1panel --server")
    if name == "vnc":
        print("TigerVNC 官方下载：https://tigervnc.org/\n安装 Viewer 后运行 lablink setup 填写路径；服务器端另用 --server 安装 x11vnc。")
        if apply:
            webbrowser.open("https://tigervnc.org/")
        return 0
    if os.name != "nt":
        print("本机请按官方指南安装：https://tailscale.com/download\n也可在 Linux 服务器使用 addon tailscale --server")
        return 0
    cmd = [executable("winget"), "install", "--id", "Tailscale.Tailscale", "--exact", "--source", "winget"]
    print(subprocess.list2cmdline(cmd))
    return subprocess.call(cmd) if apply else 0
