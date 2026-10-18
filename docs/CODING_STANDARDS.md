# TraceEval AI 辅助编码规范

## 1. 规范来源与适用范围

本项目采用以下公开规范的核心约定，并按评测平台的需求补充项目规则：

- [PEP 8](https://peps.python.org/pep-0008/)：命名、布局、导入和可读性。
- [PEP 257](https://peps.python.org/pep-0257/)：文档字符串的位置与三双引号格式。
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)：
  复杂接口的参数、返回值、异常和副作用说明。
- [Ruff 文档](https://docs.astral.sh/ruff/rules/)：可自动执行的格式与检查规则。

这是一套项目约定，不声称上述来源要求所有私有函数、嵌套函数和测试都写文档。
**全量文档字符串覆盖是 TraceEval 的额外要求。** 项目行宽为 100，而非照搬
PEP 8 的默认行宽。规范正文使用中文；源码标识符与文档字符串使用英文，
便于后续公开协作。可解释业务数据、题目和界面文案中的中文不受此限制。

## 2. 每次编码的工作顺序

1. 阅读根目录 AGENTS.md 和本文件，核对相关代码、配置、测试与当前改动。
2. 确认数据流、行为边界和兼容性影响，优先做范围明确的改动。
3. 同步修改实现和相关说明；文档字符串必须描述最终行为。
4. 修改业务行为时补充必要测试；纯格式、注释调整以现有回归为主。
5. 执行 scripts/check.py；核对 diff，确认没有凭据、无关文件或意外协议变更。
6. 说明实际完成内容与验证结果；未运行的检查不能写成通过。

AI 生成代码与人工代码遵守同一规则。不要依赖模型“记住规范”：
AGENTS.md 提供入口，Ruff 和 AST 检查提供反馈，CI 再执行同一检查入口。

## 3. 文档字符串

### 3.1 强制覆盖

- 所有模块、类、函数和异步函数的第一条语句必须是非空字符串。
- 包括私有/魔术方法、构造方法、内部函数、测试辅助类、fixture、测试函数、
  Django Meta 和迁移类。空包的 __init__.py 也应说明包用途。
- 一律使用三双引号；不能以普通字符串、三单引号或 # 注释代替。
- 首句清楚说明职责并以英文句号结束；不能只写类名、函数名、TODO 或占位内容。
- 简单 getter、框架覆盖方法、异常类和测试允许一行说明。
- 描述原因、边界与语义，避免逐行翻译代码或为显而易见的赋值加噪声注释。

### 3.2 复杂接口

在摘要后留一个空行，按实际需要编写以下栏目：

- Args：说明业务含义、单位、前置条件；不重复 self/cls。
- Returns：说明返回结构、幂等标志和空值语义。
- Raises：说明调用方需要处理的异常和触发条件。
- Yields：用于生成器与上下文管理器的产出或作用域。

数据库写入、锁的生命周期、外部请求、失败重试策略和费用影响属于重要副作用，
应放进说明。不存在的参数、异常或返回值不要为了模板完整而编造。

```python
def evaluate_experiment(experiment_id):
    """Evaluate one frozen experiment and atomically persist its results.

    Args:
        experiment_id: Identifier of the experiment to evaluate.

    Returns:
        A pair containing the experiment and whether evaluation ran now.
        A completed experiment returns its existing results without rerunning.

    Raises:
        EvaluationInputError: The experiment, ruleset, or bound data is invalid.
    """
```

Ruff 使用 Google docstring convention；D417 不作为机械门禁，因为简单框架
方法和测试不必重复签名中的每个参数。复杂接口是否解释完整仍需代码审查。
AST 检查额外覆盖 Ruff 不一定检查的私有和嵌套定义。

### 3.3 框架与协议兼容性

Pydantic 会把类说明加入 JSON Schema。已对外使用或已写入实验配置指纹的工具
参数结构，不应因补注释而变化。工具参数 schema 经专门函数去除根级类说明，
保留原有字段定义；相应兼容性由测试和已有批次配置核验。

自动生成迁移之后，也需要补齐模块和 Migration 类文档，再运行检查；
不能为了补注释改变既有迁移的 operations。

## 4. Python 风格与结构

- Python 3.12；4 空格缩进；每行最多 100 字符；文件以换行结束。
- 类名使用 PascalCase，函数和变量使用 snake_case，常量使用 UPPER_SNAKE_CASE。
- 导入放在模块文档之后，按标准库、第三方、本项目分组；仅隔离可选依赖、初始化或循环依赖边界时允许延迟导入，并写明原因。
- 优先具体命名、简单分支和明确返回结构。复杂过程保持业务职责清晰，
  不为满足任意行数限制拆出没有独立含义的函数。
- 为新增独立工具函数及难以理解的返回结构使用准确类型；边界数据优先用
  Pydantic/serializer 明确表达。已有框架签名不要求为凑覆盖率添加 Any。
- 异常类说明错误含义；捕获可处理的具体异常。宽泛异常仅用于必要的边界兜底，
  必须更新失败状态并重新抛出安全错误，不静默吞掉异常。
- 不新增没有必要的依赖；变更依赖时同步锁文件。

## 5. 平台分层与数据契约

- API：鉴权、解析、调用 service、状态码和分页；不承载长任务或直接发起付费请求。
- Service：组织业务、事务、幂等、并发和持久化。
- Core/engine：纯数据校验、标准化和评分；不依赖外部模型服务。
- Agent client：官方网络端点、超时、响应大小、错误脱敏；不自动重试未知结果的请求。
- Tool：允许列表与严格参数校验；不执行模型提供的 shell、eval 或任意 Python。

单条轨迹及其事件必须原子落库。实验固定输入、Agent 配置、规则版本和轨迹哈希；
不能覆盖已完成结果后声称仍是同一次实验。对比必须使用兼容的数据集和评分规则。
结构合法、引用存在、语义得到支持是不同概念；规则只能报告自己实际验证的内容。

## 6. 费用、安全与测试

- 模型请求前先持久化预算预留，再发送请求；用量未知的失败也保留账本。
- 保留调用次数、输出、请求大小和估算费用上限；估算金额与实际账单明确区分。
- 并发调用同一批次必须受锁保护；中断或失败的批次不自动重放。
- 不记录或导出密钥、Tracking ID、密码、Authorization 头及原始敏感异常。
- 配置样例只放空值或明显占位符。私有 .env 必须被 Git 忽略。
- pytest 默认禁止当前 provider 使用的 urllib HTTP 请求；用 FakeClient 验证协议。
  新增其他 HTTP 客户端时同步补充网络隔离，不能绕过测试保护。
- 并发测试在 finally 中关闭线程内连接。数据库测试使用 PostgreSQL，
  不以 SQLite 通过代替对 PostgreSQL 事务、约束和锁的验证。
- 测试写明条件和预期，覆盖实际风险；不为每个注释或简单字段创建重复测试。

## 7. 自动检查

```bash
# 查看格式问题；不自动改业务逻辑
uv run ruff format --check .
uv run ruff check .

# 检查所有定义，包括私有方法和嵌套函数
uv run python scripts/check_docstrings.py

# 统一入口：格式、lint、文档、Django、迁移与离线回归
uv run python scripts/check.py
```

允许先用 ruff format 和 ruff check --fix 整理格式/导入，但必须检查修改。
需要豁免时只针对明确规则与范围，写出理由；不得全局禁用文档检查来掩盖缺口。
当前全量文档覆盖规则没有生成文件、测试或私有定义的豁免。

GitHub workflow 在 push 和 pull_request 上运行同一入口，使用临时 PostgreSQL，
无需 DeepSeek 密钥。CI 配置写入不代表远端已执行，结果以实际运行记录为准。
