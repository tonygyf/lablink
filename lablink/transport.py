from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time
from .config import home


def executable(name):
    # Resolve the executable, never a same-named .cmd in the working directory.
    if os.name == "nt" and name == "ssh":
        p = Path(os.environ.get("WINDIR", "C:/Windows")) / "System32/OpenSSH/ssh.exe"
        if p.is_file():
            return str(p)
    result = shutil.which(name + ".exe" if os.name == "nt" else name)
    if not result:
        raise ValueError(f"未找到 {name}，请安装并加入 PATH")
    return str(Path(result).resolve())


def ssh_args(c):
    home().mkdir(parents=True, exist_ok=True)
    args = [executable("ssh"), "-F", os.devnull,
            "-o", "StrictHostKeyChecking=ask",
            "-o", f"UserKnownHostsFile={home() / 'known_hosts'}",
            "-o", "ConnectTimeout=15", "-o", "ServerAliveInterval=30",
            "-o", "ServerAliveCountMax=3", "-p", str(c["ssh_port"]), "-l", c["user"]]
    if c["identity_file"]:
        key = Path(c["identity_file"]).expanduser().resolve()
        if not key.is_file():
            raise ValueError("SSH 密钥文件不存在")
        args += ["-i", str(key), "-o", "IdentitiesOnly=yes"]
    return args


def connect(c, command=None):
    return subprocess.call(ssh_args(c) + ["-t", c["host"]] + ([command] if command else []))


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def stop_process(p):
    if p.poll() is None:
        p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()


@contextmanager
def tunnel(c, remote_port, timeout=120):
    port = free_port()
    command = ssh_args(c) + ["-N", "-o", "ExitOnForwardFailure=yes", "-L",
                             f"127.0.0.1:{port}:127.0.0.1:{remote_port}", c["host"]]
    # stdin/stderr stay attached so first-use host fingerprint and passwords work.
    p = subprocess.Popen(command)
    try:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if p.poll() is not None:
                raise ValueError("SSH 隧道启动失败，请先运行 lablink ssh 检查登录")
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=.2):
                    break
            except OSError:
                time.sleep(.2)
        else:
            raise ValueError("隧道启动超时（请确认终端中的登录提示）")
        if p.poll() is not None:
            raise ValueError("隧道已退出")
        yield port
    finally:
        stop_process(p)


def viewer(c):
    if c["vnc_viewer"]:
        p = Path(c["vnc_viewer"]).expanduser().resolve()
        if p.is_file():
            return str(p)
        raise ValueError("VNC 客户端路径不存在")
    if os.name == "nt":
        p = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "TigerVNC/vncviewer.exe"
        if p.is_file():
            return str(p)
    return executable("vncviewer")
