# 发布 GitHub

本源码包未自动创建远端仓库或发布 Release。仓库名建议 `lablink`。

1. 在 GitHub 创建空仓库（可先 Private）。
2. 解压源码包，在根目录执行以下命令，将占位项替换为你的 GitHub 信息：

```bash
git init -b main
git add .
git commit -m "Initial LabLink release"
git remote add origin https://github.com/YOUR_ACCOUNT/lablink.git
git push -u origin main
git tag v0.1.0
git push origin v0.1.0
```

3. 查看 Actions 测试结果。
4. `python scripts/release.py` 生成白名单源码 ZIP 及 SHA256 文件，在 GitHub 创建 `v0.1.0` Release 并上传这两个文件。

## 发布验收

- [ ] 测试：Python 3.10/3.12，Windows/Linux CI。
- [ ] 新 Windows 用户：安装、setup、首次 SSH 指纹、密码/密钥登录。
- [ ] 含空格路径下安装，删除解压目录后桌面快捷方式仍可启动。
- [ ] 原有 SSH config、系统代理和其他 LabServer 版本不受影响。
- [ ] VNC 前台启动、退出清理、连续打开两次不占用固定端口。
- [ ] 1Panel 页面资源加载、关闭隧道、HTTPS/域名限制说明。
- [ ] 手机热点校外验证；不能以同校园网的 ping 代替。
- [ ] 在可丢弃 Linux 虚拟机验证扩展安装；不在生产训练服务器验收安装器。
- [ ] 仓库无实际 IP、账号、密钥、日志、本机 config.json。

v0.1.0 的自动测试覆盖配置验证、命令参数隔离、隧道实际子进程生命周期。维护者必须自行完成平台和外部软件的真实验收，不能将本地自动测试结果写成跨网实测结果。
