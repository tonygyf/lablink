import argparse
import json
import socket
import subprocess
import sys
import webbrowser
from pathlib import Path
from . import __version__
from .config import DEFAULT, home, load, save
from .transport import connect, executable, ssh_args, tunnel, viewer


def setup():
    path = home() / "config.json"
    c = load() if path.exists() else DEFAULT.copy()
    print("配置仅保存在用户目录，不写入源码；留空保留当前值。")
    labels = {"host": "服务器 IP / 域名", "user": "SSH 用户", "ssh_port": "SSH 端口",
              "identity_file": "私钥文件路径（可空，不复制密钥）", "vnc_port": "服务器 VNC 端口",
              "vnc_viewer": "TigerVNC Viewer 程序路径（可空自动查找）",
              "panel_port": "1Panel 端口（0 禁用）", "panel_scheme": "面板 http / https",
              "panel_path": "面板安全入口，如 /login-path（没有则 /）"}
    for k, label in labels.items():
        value = input(f"{label} [{c[k]}]: ").strip()
        if value:
            c[k] = int(value) if type(DEFAULT[k]) is int else value
    save(c)
    print(f"配置已保存：{path}\n首次运行 lablink ssh，请核对服务器主机指纹。")


def doctor(c):
    print("SSH 程序：", executable("ssh"))
    with socket.create_connection((c["host"], c["ssh_port"]), timeout=8):
        print("SSH TCP 端口：可达（不代表认证成功）")
    result = subprocess.run(ssh_args(c) + ["-o", "BatchMode=yes", c["host"], "printf LABLINK_OK"],
                            capture_output=True, text=True, timeout=25)
    if result.returncode != 0:
        print("免交互认证未通过：请先 lablink ssh 确认指纹/密钥；密码登录也会在此失败。")
        print(result.stderr.strip())
        return 1
    print("SSH 命令执行：通过" if "LABLINK_OK" in result.stdout else "服务器响应异常")
    return 0 if "LABLINK_OK" in result.stdout else 1


def main(argv=None):
    p = argparse.ArgumentParser(description="LabLink · 中文实验室远程连接工具")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="action", required=True)
    for name in ("setup", "ssh", "gpu", "vnc", "panel", "gui", "doctor", "config-path"):
        sub.add_parser(name)
    imp = sub.add_parser("import-config")
    imp.add_argument("file", type=Path)
    ad = sub.add_parser("addon")
    ad.add_argument("name", choices=["tailscale", "vnc", "1panel"])
    ad.add_argument("--server", action="store_true")
    ad.add_argument("--apply", action="store_true")
    args = p.parse_args(argv)
    try:
        if args.action == "setup":
            setup()
        elif args.action == "config-path":
            print(home() / "config.json")
        elif args.action == "import-config":
            save(json.loads(args.file.read_text(encoding="utf-8-sig")))
            print("已导入到用户目录")
        elif args.action == "gui":
            from .gui import launch
            launch()
        elif args.action == "addon":
            from .addons import install
            return install(args.name, args.server, args.apply)
        else:
            c = load()
            if args.action == "ssh":
                return connect(c)
            if args.action == "gpu":
                return connect(c, "watch -n 2 nvidia-smi")
            if args.action == "doctor":
                return doctor(c)
            if args.action == "vnc":
                v = viewer(c)
                with tunnel(c, c["vnc_port"]) as port:
                    return subprocess.call([v, f"127.0.0.1::{port}"])
            if args.action == "panel":
                if not c["panel_port"]:
                    raise ValueError("尚未配置面板端口，请运行 setup")
                with tunnel(c, c["panel_port"]) as port:
                    url = f"{c['panel_scheme']}://127.0.0.1:{port}{c['panel_path']}"
                    print(url)
                    webbrowser.open(url)
                    input("隧道已开启。保持此窗口，使用结束后按 Enter 关闭。")
        return 0
    except (ValueError, OSError, ImportError, subprocess.SubprocessError) as e:
        print(f"错误：{e}", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\n已退出；本次隧道已清理。")
        return 130
