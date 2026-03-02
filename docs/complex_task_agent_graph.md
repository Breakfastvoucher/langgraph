# ComplexTaskAgentRoute Graph 结构图

下面是新增复杂任务路由对应的 LangGraph 流程图（Mermaid）：

```mermaid
flowchart TD
    A([START]) --> B[classify_task]

    B -->|fallback_to_qa = true| Z1([END: fallback to QA route])
    B -->|fallback_to_qa = false| C[collect_requirements]

    C -->|missing_inputs 非空| Z2([END: clarification needed])
    C -->|missing_inputs 为空| D[plan_steps]

    D --> E[retrieve_knowledge]
    E --> F[draft_content]
    F --> G[critique_and_rewrite]

    G -->|quality_score < 18 且 iteration_count < max_iterations| F
    G -->|通过质量阈值或达到迭代上限| H[compliance_check]

    H --> I[finalize_output]
    I --> J([END: final answer])
```

## 节点说明（与代码一一对应）

1. `classify_task`：识别是否为复杂内容生产任务。
2. `collect_requirements`：检查必要槽位，缺失则触发澄清。
3. `plan_steps`：生成执行计划。
4. `retrieve_knowledge`：调用 Milvus 检索证据。
5. `draft_content`：按模板 + 语气 + 证据生成草稿。
6. `critique_and_rewrite`：质量评分，不达标回环重写。
7. `compliance_check`：执行合规检查。
8. `finalize_output`：拼装最终可流式返回内容。
