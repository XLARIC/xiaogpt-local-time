# 更新记录

## 0.1.0

- 使用音箱所在地的 IANA 时区回答本地时间、日期、星期及日期时间组合问句。
- 在关键词与 LLM 分流之前处理，解决跨时区实时信息回答不准的问题。
- 自动处理夏令时；支持 TZ 或宿主机 /etc/localtime。
- 锁定 XiaoGPT 基础镜像 digest 和源码 SHA256，拒绝静默套用到未知版本。
- 提供三音箱配置、MIT 许可证、离线测试和 GitHub Actions。
- 发布目标 linux/amd64，适用于 Intel / AMD NAS。
