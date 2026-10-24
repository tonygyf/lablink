import ipaddress
import json
import os
from pathlib import Path
import re

DEFAULT = {
    "host": "", "user": "", "ssh_port": 22, "identity_file": "",
    "vnc_port": 5900, "vnc_viewer": "",
    "panel_port": 0, "panel_scheme": "http", "panel_path": "/",
}


def home():
    if os.environ.get("LABLINK_HOME"):
        return Path(os.environ["LABLINK_HOME"]).expanduser().resolve()
    base = Path(os.environ.get("LOCALAPPDATA", Path.home())) if os.name == "nt" else Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "LabLink"


def validate(c):
    if not isinstance(c, dict) or set(c) != set(DEFAULT):
        raise ValueError("配置字段不匹配，请参考 config.example.json")
    h = c["host"]
    if not isinstance(h, str) or not h or len(h) > 253:
        raise ValueError("请填写服务器 IP 或域名")
    try:
        ipaddress.ip_address(h)
    except ValueError:
        if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?", h):
            raise ValueError("服务器地址只能是 IP 或域名，不含端口、空格或命令")
    if not isinstance(c["user"], str) or not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_.-]{0,63}", c["user"]):
        raise ValueError("请填写有效的 SSH 用户名")
    for k in ("ssh_port", "vnc_port", "panel_port"):
        low = 0 if k == "panel_port" else 1
        if type(c[k]) is not int or not low <= c[k] <= 65535:
            raise ValueError(f"{k} 端口无效")
    for k in ("identity_file", "vnc_viewer", "panel_path"):
        if not isinstance(c[k], str) or any(ord(ch) < 32 for ch in c[k]):
            raise ValueError(f"{k} 必须是无控制字符的文本")
    if c["panel_scheme"] not in ("http", "https"):
        raise ValueError("面板协议必须是 http 或 https")
    if not c["panel_path"].startswith("/") or c["panel_path"].startswith("//") or "\\" in c["panel_path"]:
        raise ValueError("面板入口必须是 / 开头的路径")
    return c


def save(c):
    validate(c)
    c = c.copy()
    for key in ("identity_file", "vnc_viewer"):
        if c[key]:
            c[key] = str(Path(c[key]).expanduser().resolve())
    root = home()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = root / "config.tmp"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=2)
        f.write("\n")
    if os.name != "nt":
        tmp.chmod(0o600)
    tmp.replace(root / "config.json")


def load():
    try:
        return validate(json.loads((home() / "config.json").read_text(encoding="utf-8")))
    except FileNotFoundError:
        raise ValueError("尚未配置，请先运行 lablink setup") from None
