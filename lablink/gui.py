import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
from .config import home


def launch():
    root = tk.Tk()
    root.title("LabLink · 远程连接")
    root.geometry("620x440")
    root.configure(bg="#181D27")
    root.resizable(False, False)
    tk.Label(root, text="LabLink", font=("Microsoft YaHei UI", 24, "bold"),
             bg="#181D27", fg="#D1D3DB").pack(pady=(25, 8))
    tk.Label(root, text="连接你的服务器 · 配置仅保存在本机", bg="#181D27", fg="#D1D3DB").pack()

    def run(action):
        command = [sys.executable, "-m", "lablink", action]
        try:
            if os.name == "nt":
                subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                messagebox.showinfo("命令行操作", f"请在终端运行：lablink {action}\n此窗口的启动按钮目前针对 Windows。")
        except OSError as e:
            messagebox.showerror("启动失败", str(e))

    grid = tk.Frame(root, bg="#181D27")
    grid.pack(pady=20)
    items = [("填写 / 修改配置", "setup"), ("连接诊断", "doctor"),
             ("SSH 终端", "ssh"), ("GPU 监控", "gpu"),
             ("VNC 远程桌面", "vnc"), ("1Panel 管理", "panel")]
    for i, (label, action) in enumerate(items):
        tk.Button(grid, text=label, command=lambda a=action: run(a), width=23, height=2,
                  bg="#283348", fg="#D1D3DB", activebackground="#43506A",
                  activeforeground="white", relief="flat").grid(row=i // 2, column=i % 2, padx=8, pady=7)
    tk.Label(root, text=f"配置位置：{home()}", bg="#181D27", fg="#A1ACBF", wraplength=570).pack()
    root.mainloop()
