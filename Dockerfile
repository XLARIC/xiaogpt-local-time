FROM yihong0618/xiaogpt@sha256:e0e464294eacdf79cbedfd70aaa021e41cb015d9297f962825af8b3b78dec0b4

ARG VERSION=0.1.0
ARG VCS_REF=unknown
LABEL org.opencontainers.image.title="XiaoGPT Local Time" \
      org.opencontainers.image.description="Fix cross-timezone answers with deterministic local time/date for Xiaomi AI speakers" \
      org.opencontainers.image.source="https://github.com/XLARIC/xiaogpt-local-time" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}"

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    XDG_CONFIG_HOME=/config

COPY local_time.py /app/xiaogpt/local_time.py
COPY patch_local_time.py /tmp/patch_local_time.py
COPY LICENSE NOTICE THIRD_PARTY_LICENSES.md /usr/share/doc/xiaogpt-local-time/
RUN /app/.venv/bin/python /tmp/patch_local_time.py \
    && /app/.venv/bin/python -c "from xiaogpt.xiaogpt import MiGPT; from xiaogpt.local_time import configured_timezone; configured_timezone()" \
    && rm /tmp/patch_local_time.py

ENTRYPOINT ["/app/.venv/bin/python", "/app/xiaogpt.py"]
CMD ["--config=/config/config.yaml"]
