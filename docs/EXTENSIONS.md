# 扩展与排障

## x11vnc 示例（仅已有 X11 桌面）

先安装包，随后由服务器用户设置密码：

```bash
x11vnc -storepasswd
x11vnc -display :0 -auth guess -localhost -rfbauth ~/.vnc/passwd -rfbport 5900 -forever -shared
```

显示号、Xauthority 与权限必须根据实际桌面确认。上述命令以前台形式启动；不要照抄为 root 开机服务。无图形桌面或使用 Wayland 时，先选择合适的远程桌面方案。本项目不提供“任意 Linux 一键创建桌面”的承诺。

## Tailscale / 代理冲突

Tailscale 和 Clash TUN 等软件同时运行时，虚拟 DNS 地址或路由可能冲突。先用官方 `tailscale status`、`tailscale netcheck` 排查。不要直接照搬他人的代理端口或修改整机 DNS。LabLink 不自动给服务器服务注入代理，也不承诺所有校园网均可直连；必要时使用中继。

## 常见错误

- **尚未配置**：运行 setup，填写实际主机与用户。
- **SSH 指纹提示**：向服务器管理员核对指纹；已知主机密钥变化需要先核实，不能直接关闭校验。
- **doctor 失败但 ssh 能登录**：密码认证或密钥口令需要交互，doctor 使用 BatchMode，会拒绝交互。
- **VNC 拒绝连接**：检查服务是否在服务器 `127.0.0.1` 对应端口监听。只安装 Viewer 不会自动创建服务器桌面。
- **面板显示无入口**：填写真实安全入口，不要仅填写端口。
- **localhost 页面仍被代理**：浏览器若通过扩展或特殊参数代理本机地址，需要在该浏览器排除 localhost；工具不会接管系统代理。
- **学校之外不可达**：检查两端是否在线、是否在同一 tailnet、访问策略和中继可用性。

## 官方来源

- Tailscale：https://tailscale.com/docs/install/linux
- TigerVNC：https://tigervnc.org/
- 1Panel：https://1panel.cn/ （安装入口 https://resource.fit2cloud.com/1panel/package/v2/quick_start.sh）

第三方安装脚本是上游提供的当前版本，本项目未固定其内容哈希。`addon --server` 可先查看下载地址和执行命令，审阅后再用 `--apply`。安装过程可能要求输入 sudo 密码，密码仅交给 SSH 终端。
