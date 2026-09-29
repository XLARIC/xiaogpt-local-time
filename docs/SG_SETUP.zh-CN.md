# SG 自动构建接入

开源仓库：`XLARIC/xiaogpt-local-time`。发布镜像：`alaricx/xiaogpt-local-time`。

## Runner

复用现有 SG 的独立仓库 Runner 安装方式，不能仅复制其他仓库的 `runs-on`，因为 Runner 是按仓库授权的。

SG root 终端使用已审核的安装脚本：

```sh
bash /root/add-github-runner.sh XLARIC/xiaogpt-local-time
```

使用当前最新修复版脚本，来源：[XLARIC/github-runner](https://github.com/XLARIC/github-runner)。在新项目的 Settings → Actions → Runners → New self-hosted runner 页面取得临时注册 Token，按脚本提示隐藏输入。不要将 Token 放到命令参数或聊天中。

脚本配置独立用户、rootless Docker 和 systemd。注册成功后确认 Runner 在线，标签包含 `aliyun-sg-t5`。

## GitHub 配置

仓库 Settings → Secrets and variables → Actions：

- Variable：`DOCKERHUB_USERNAME` = `alaricx`
- Secret：`DOCKERHUB_TOKEN` = Docker Hub 写入权限访问令牌
- Variable：`SG_PUBLISH_ENABLED` = `true`（在 Runner 和令牌准备好后启用）

Docker Hub 浏览器登录只授权本机 CLI，不能代替 GitHub 自动构建所需的访问令牌。令牌应在 GitHub 的 Secret 输入框中输入，不要发到聊天、写入源码或配置文件。

## 触发与验证

- 主分支提交：发布 `latest`、`sha-<commit>`。
- 推送 `v0.1.0` 等版本标签：另发布版本标签 `0.1.0`。
- Actions → Build and publish on SG → Run workflow：手动重试。
- Docker Hub 仓库页面和镜像 manifest 均应存在 `linux/amd64`。
- 发布前在 SG 运行本地时区测试、容器分流测试及启动帮助命令。

公开 PR 不会在 SG 上执行。SG 发布工作流只接受仓库所有者从 main 或版本标签触发的事件。不要给外部贡献者写入权限。

底层镜像已固定版本；升级它需要同时审查源码校验值和补丁。
