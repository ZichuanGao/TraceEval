# TraceEval

用于 Agent 轨迹分析与可复现实验的个人评测平台。

项目按工程骨架、轨迹接入、确定性评测、真实 Agent 执行的顺序独立提交。
当前工程骨架提供依赖管理、Django 启动配置、服务令牌鉴权和编码质量检查；
业务 API 随后续模块接入。

## 开发环境

- Python 3.12
- uv
- PostgreSQL 14 或以上版本

在已有 PostgreSQL 数据库的环境中：

```bash
uv sync --locked
cp .env.example .env
```

在私有 .env 中设置随机的 DJANGO_SECRET_KEY、TRACEEVAL_API_TOKEN，
以及正确的 PostgreSQL 连接信息。测试涉及数据库时，测试角色需要创建测试数据库的权限。
DeepSeek 配置在本模块中不使用，保持为空即可。

```bash
uv run traceeval check
uv run python scripts/check.py
uv run traceeval runserver 127.0.0.1:8000 --noreload
```

本阶段尚无业务路由；启动后访问根路径返回 404 属于预期行为。

## 编码约定

开始修改前阅读 [AGENTS.md](AGENTS.md) 和
[编码规范](docs/CODING_STANDARDS.md)。完整检查统一使用 scripts/check.py，
纯静态检查可追加 --static-only。

测试使用离线客户端，并禁止真实的 urllib HTTP 请求。普通检查不需要模型密钥，
不会运行付费 Agent 批次。真实配置、运行数据和编辑器设置由 .gitignore 排除。
