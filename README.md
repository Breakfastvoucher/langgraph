# Xiaoduo Agent Phase 1 PoC (LangGraph + FastAPI)

这个示例把你给出的 Graph Blueprint 转为可执行的 LangGraph 节点结构，并通过 FastAPI 暴露接口。

## 1) Blueprint -> 节点映射

1. `User Input` -> `user_input`
2. `Intent Classification Node` -> `intent_classification`
3. `Decision Node` -> `decision`
4. `Tool Node` -> `tool`
5. `Response Node` -> `response`

图执行顺序：

`START -> user_input -> intent_classification -> decision -> tool -> response -> END`

## 2) Tool 模板

已内置 3 个基于 `@tool` 的可扩展工具：

- `knowledge_query`
- `report_generator`
- `task_logger`

所有工具都使用 `langchain_core.tools.tool` 装饰器定义，并通过 `ToolGateway` 调用，LLM/Graph 不直接访问系统或数据库。

## 3) Memory 与 Checkpointer

- 每次 API 请求传入独立 `session_id`
- 默认图：无 checkpointer
- 可选图：`MemorySaver` checkpointer（内存态）
- 在请求里设置 `use_checkpointer=true` 即可走带 checkpoint 的图

## 4) 启动

```bash
pip install fastapi uvicorn langgraph
uvicorn app.main:app --reload --port 8000
```

## 5) 调用示例

```bash
curl -X POST http://127.0.0.1:8000/agent/run \
  -H 'content-type: application/json' \
  -d '{
    "session_id": "s-001",
    "user_input": "请生成一份市场分析报告",
    "use_checkpointer": true
  }'
```

## 6) 安全控制说明

- Tool 调用统一走 `ToolGateway.invoke`
- `allowed_tools` 控制白名单
- 未授权工具会被拒绝
- Graph 节点只生成意图和参数，不直接执行外部系统操作
