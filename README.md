# XiaoGPT Local Time

[简体中文](README.zh-CN.md)

Answer **time and date in the speaker's local timezone**, independently of the AI provider, Xiaomi service, NAS timezone, or build server location.

This MIT-licensed extension to [XiaoGPT](https://github.com/yihong0618/xiaogpt) intercepts supported Chinese clock questions before keyword and LLM routing. It reads the host clock with an IANA timezone, handles daylight saving automatically, and uses the speaker's existing Xiaomi TTS. Other questions follow the upstream bot configuration.

## Supported questions

- Time: `几点了`, `现在几点了`, `现在是几点`
- Date: `今天几号了`, `今天是几月几日`
- Weekday: `今天星期几`, `今天周几`
- Combined: `今天几号，现在几点`
- Common prefixes such as `请告诉我`, `帮我`, and punctuation are accepted.

A keyword is not required for local-clock questions. Explicit city names and other real-time topics remain with the configured AI bot; this version does not resolve place names, weather or Home Assistant commands.

## Docker quick start

Image: `alaricx/xiaogpt-local-time:0.1.0`

Platform: `linux/amd64` (Intel / AMD Linux NAS)

```sh
git clone https://github.com/XLARIC/xiaogpt-local-time.git
cd xiaogpt-local-time
cp .env.example .env
cp speaker1/config.example.yaml speaker1/config.yaml
```

1. Edit `.env`: set `TZ` to the **speaker's physical location**, such as `Pacific/Auckland`, `Asia/Shanghai`, `Europe/London`, or `America/New_York`. The Singapore build server does not determine runtime timezone.
2. Edit `speaker1/config.yaml`: set the Xiaomi DID and Gemini API key. Use a valid Xiaomi account/password or your own compatible login token. Confirm that the chosen Gemini model is available to your account.
3. If using a previously acquired token, copy your own `.mi.token` into `speaker1/data/.mi.token`. Do not share it.
4. Start one speaker first:

```sh
docker compose pull xiaogpt-1
docker compose up -d xiaogpt-1
docker compose logs --tail 100 xiaogpt-1
```

Prepare `speaker2` and `speaker3` the same way, using a different DID for each. Then run `docker compose up -d`. Each container has a separate login-data directory. To use different timezones, override the `TZ` environment per service.

NAS automatic time synchronization must be enabled. The image converts the host clock; it cannot repair an inaccurate host clock. Xiaomi may begin its native reply before the extension pauses playback and speaks the local answer.

## Without Compose

```sh
docker run -d --name xiaogpt-local-time --restart unless-stopped --init \
  --platform linux/amd64 --network host -e TZ=Pacific/Auckland \
  --mount type=bind,src="$PWD/speaker1/config.yaml",dst=/config/config.yaml,readonly \
  --mount type=bind,src="$PWD/speaker1/data",dst=/root \
  alaricx/xiaogpt-local-time:0.1.0
```

When `TZ` is omitted, the image uses `/etc/localtime`. On Linux, mount the host file with `--mount type=bind,src=/etc/localtime,dst=/etc/localtime,readonly` to follow the NAS timezone. Without a timezone setting or host file, UTC is used. Compose requires an explicit `TZ` to prevent accidental UTC answers.

## Build and tests

```sh
python3 -m unittest discover -s tests -p 'test_local_time.py' -v
docker compose -f compose.yaml -f compose.build.yaml build xiaogpt-1
docker run --rm --platform linux/amd64 --network none -e TZ=Pacific/Auckland \
  -v "$PWD:/tests:ro" --entrypoint /app/.venv/bin/python \
  alaricx/xiaogpt-local-time:0.1.0 /tests/tests/test_image.py
```

The base image is pinned by digest and its source is guarded by SHA256. An unknown source revision fails the build instead of receiving an unreviewed patch. Tests cover cross-timezone calendar boundaries, DST transitions, local routing and continuous conversation.

## Automated publishing on SG

The publishing workflow uses the repository's self-hosted SG runner with labels `self-hosted, Linux, X64, aliyun-sg-t5`. Pull-request tests use GitHub-hosted Ubuntu. Only trusted `main` / `v*` pushes and manual runs publish.

Configure repository variable `DOCKERHUB_USERNAME=alaricx`, repository secret `DOCKERHUB_TOKEN` (a Docker Hub write token), and enable `SG_PUBLISH_ENABLED=true` after the repository-specific SG runner is online. Builds validate the image before publishing version, commit and `latest` tags. Runtime credentials never enter the Docker build context.

See [SG setup](docs/SG_SETUP.zh-CN.md), [contributing](CONTRIBUTING.md), [security](SECURITY.md), and [upstream licenses](THIRD_PARTY_LICENSES.md).

This project is a community extension; it is not affiliated with Xiaomi or Google. Offline tests do not verify Xiaomi login, live speaker playback or external AI API access.
