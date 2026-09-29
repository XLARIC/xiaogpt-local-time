# 安全与凭证

小米账号、密码、cookie、.mi.token、Gemini/API 密钥仅保存在 NAS 本地的配置和 data 目录。
不要贴到 Issue、提交到 Git 或写进 Dockerfile。构建上下文只允许六个必需文件。
verbose 建议保持 false，上游详细日志可能打印配置。
发现安全问题请使用 GitHub 仓库的私密漏洞报告功能，不要公开凭证。
