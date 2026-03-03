# 行业调研报告 Agent（LangGraph）

这是一个基于 **LangGraph** 的多节点 Agent 示例，面向你的业务场景：自动生成行业调研报告。

## 架构

图中包含 4 个核心节点：

1. `planner_node`：生成报告提纲和关键研究问题。
2. `researcher_node`：调用内部知识库接口（自然语言查询）收集证据。
3. `writer_node`：基于提纲+证据撰写完整报告草稿。
4. `reviewer_node`：审核报告质量，必要时回退到 writer 迭代，最多 2 轮。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m industry_research_agent.cli "中国AI医疗行业"
```

## 对接内部知识库

目前在 `tools.py` 中提供了 `EnvConfiguredKBClient`，你可以替换 `query()` 的实现接入真实接口：

- 输入：自然语言问题（`question: str`）
- 输出：按相关性排序的文档列表（`list[KBResult]`）

数据结构：

```python
class KBResult(TypedDict):
    title: str
    snippet: str
    score: float
```

## 后续扩展建议

- 将 `RuleBasedLLM` 替换为企业实际可用的大模型（OpenAI/私有模型网关）。
- 在 `reviewer_node` 增加更细粒度的评分标准（事实性/完整性/可执行性）。
- 增加引用追踪：让报告每段落都附来源文档编号。
