# 贡献

先提交 Issue 描述音箱型号、时区和预期行为，不要提供凭证或真实设备编号。
运行本地测试：

```sh
python3 -m unittest discover -s tests -p 'test_local_time.py' -v
docker buildx build --platform linux/amd64 --load -t xiaogpt-local-time:test .
docker run --rm --platform linux/amd64 --network none -e TZ=Pacific/Auckland \
  -v "$PWD:/tests:ro" --entrypoint /app/.venv/bin/python \
  xiaogpt-local-time:test /tests/tests/test_image.py
```

扩展问句请采用精确匹配，避免截获“明天几点开会”等普通 AI 问题。
升级上游镜像时必须更新固定 digest、确认 source SHA256、审查补丁并重新运行全部测试。
