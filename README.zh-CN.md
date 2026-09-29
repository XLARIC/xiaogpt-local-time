# XiaoGPT Local Time

[English](README.md)

解决 **跨时区时，小爱音箱无法准确回答本地时间和日期** 的问题。

AI 服务、NAS、构建服务器可能处于不同地区。只在提示词里写“我住在哪里”，不能保证 AI 得到准确的当前时刻。本项目在调用 AI 前截获时间和日期问句，直接使用系统时钟，按音箱所在地的 IANA 时区计算，再通过小爱原有语音接口播报。

## 功能

- “几点了”“现在几点了”：回答本地时间。
- “今天几号了”“今天是几月几日”：回答本地日期。
- “今天星期几”“今天周几”：回答星期。
- “今天几号，现在几点”：回答日期和时间。
- 支持“请告诉我”“帮我”等常见前缀与标点；无需触发 AI 的关键词。
- 自动处理夏令时；其他问题按原 XiaoGPT 配置交给 Gemini 或其他 bot。

项目没有绑定奥克兰，时区由运行配置决定。SG 服务器只负责构建镜像，不影响家庭音箱的时区。带明确城市名称的问题仍交给原 AI；此版本不解析地名，也不提供天气或 Home Assistant 控制。

## 在 Intel / AMD NAS 上使用

镜像：`alaricx/xiaogpt-local-time:0.1.0`，平台：`linux/amd64`。

```sh
git clone https://github.com/XLARIC/xiaogpt-local-time.git
cd xiaogpt-local-time
cp .env.example .env
cp speaker1/config.example.yaml speaker1/config.yaml
```

编辑 `.env`，将 `TZ` 设为音箱所在地，例如：

```dotenv
TZ=Pacific/Auckland
XIAOGPT_IMAGE=alaricx/xiaogpt-local-time:0.1.0
```

其他地区可以用 `Asia/Shanghai`、`Europe/London`、`America/New_York`。不能只填写“北京时间”或固定偏移量，否则无法正确处理夏令时。

编辑 `speaker1/config.yaml`，填写设备 DID、自己的 Gemini Key 和小米认证信息。示例中的 DID 是占位符。Gemini 模型名称可以修改，需确认你的账号可以调用该模型。

若之前已在可信设备取得小米登录文件，把自己的 `.mi.token` 复制到 `speaker1/data/.mi.token`。不要将它提交到 GitHub。账号、密码、cookie、token 的有效性由上游小米登录流程决定。

先启动一台：

```sh
docker compose pull xiaogpt-1
docker compose up -d xiaogpt-1
docker compose logs --tail 100 xiaogpt-1
```

确认正常后，同样准备 `speaker2`、`speaker3` 的配置和认证文件，各自填写不同 DID，再执行：

```sh
docker compose up -d
```

每台音箱独立运行一个容器，登录数据分别保存。不同地区的音箱可以在对应服务中单独覆盖 `TZ`。

## 直接跟随 NAS 时区

不使用 Compose 时，可以不设置 `TZ`，将 Linux 宿主机的 `/etc/localtime` 只读挂载到容器的同一路径。显式的 `TZ` 优先于该文件。

未指定时区或挂载宿主机文件时，镜像可能采用 UTC。随项目提供的 Compose 强制要求配置 `TZ`，避免误用默认时区。

NAS 必须开启自动校时。此功能只转换时区，不会校正错误的系统时钟。小爱原厂回复可能已经开始播放，程序会尝试暂停，再播报本地答案。

## 自行构建

```sh
docker compose -f compose.yaml -f compose.build.yaml build xiaogpt-1
```

构建使用固定的上游镜像 digest，并校验待补丁源码的 SHA256；未知版本会直接失败，避免上游更新导致静默失效。

本地时间测试：

```sh
python3 -m unittest discover -s tests -p 'test_local_time.py' -v
```

镜像集成测试：

```sh
docker run --rm --platform linux/amd64 --network none -e TZ=Pacific/Auckland \
  -v "$PWD:/tests:ro" --entrypoint /app/.venv/bin/python \
  alaricx/xiaogpt-local-time:0.1.0 /tests/tests/test_image.py
```

## 开源和自动发布

MIT 许可证，保留 [XiaoGPT 上游](https://github.com/yihong0618/xiaogpt)的授权说明。GitHub 主分支和版本标签提交后，通过 SG 的专用 Runner 构建、测试并发布到 Docker Hub。外部 PR 只在 GitHub 托管环境运行时间逻辑测试。

部署接入见 [SG 自动构建说明](docs/SG_SETUP.zh-CN.md)。API Key 和小米 token 只留在 NAS 本地，镜像中不包含实际凭证。

离线测试验证了代码和容器启动方式，不能代替真实小米登录、音箱播报和 Gemini API 联调。
