# 复杂任务 Agent 路由架构设计（FastAPI + Milvus + LangGraph）

## 1. 目标与约束

### 1.1 业务目标
在不推翻现有 16 个知识问答意图子类的前提下，新增 **ComplexTaskAgentRoute**（复杂任务路由），用于营销人员的内容生产类任务，重点覆盖：

1. 给客户写邮件（冷启动、跟进、催单、挽回）。
2. 写汇报材料（周报、月报、复盘、专项汇报）。
3. 写调研报告（行业、竞品、客户需求、活动效果）。

### 1.2 技术约束

1. 保留现有工厂模式与意图识别主流程。
2. 继续复用现有知识库检索能力（Milvus）与流式输出能力。
3. 复杂任务使用 LangGraph 编排，支持多步骤规划、检索、草稿生成、校验与迭代。
4. 输出必须支持流式（token streaming + 阶段事件 streaming）。

---

## 2. 总体演进方案

## 2.1 现有主干不动，新增一个“复杂任务意图”

在意图识别阶段新增一级意图：`complex_content_generation`。

- 若命中该意图：路由到 `ComplexTaskAgentRoute`。
- 若未命中：保持原有 16 类子路由逻辑不变。

这样实现“增量演进”：
- 低风险：不影响已稳定的知识问答路径。
- 可回滚：复杂路由可独立开关。
- 易灰度：可按用户组/部门逐步放量。

## 2.2 新增路由在工厂模式中的位置

建议在原 `RouteFactory` 中增加注册：

- `IntentType.COMPLEX_CONTENT_GENERATION -> ComplexTaskAgentRoute`

`ComplexTaskAgentRoute` 对外仍只暴露统一接口，例如：
- `yield_result(request_ctx) -> AsyncGenerator[StreamEvent, None]`

从而保持与现有子类一致的调用契约，避免上层接口改造。

---

## 3. ComplexTaskAgentRoute 详细架构

## 3.1 路由职责

`ComplexTaskAgentRoute` 只做三件事：

1. **任务准入判断**：是否属于复杂任务；缺参数时触发澄清。
2. **LangGraph 执行**：调用图编排完成任务。
3. **流式事件转发**：把图内节点产生的阶段事件与模型 token 统一向前端输出。

## 3.2 推荐目录结构（示例）

```text
app/
  routes/
    complex_task_agent_route.py
  agent/
    graphs/
      marketing_content_graph.py
    nodes/
      classify_task.py
      collect_requirements.py
      plan_steps.py
      retrieve_knowledge.py
      draft_content.py
      critique_and_rewrite.py
      compliance_check.py
      finalize_output.py
    prompts/
      planner_prompt.py
      writer_prompt.py
      critic_prompt.py
      compliance_prompt.py
    tools/
      kb_search_tool.py
      template_loader_tool.py
      style_guide_tool.py
      metrics_tool.py
    schemas/
      graph_state.py
      stream_event.py
```

---

## 4. LangGraph 状态机设计

## 4.1 GraphState（核心状态）

建议最小状态字段：

- `user_id`
- `session_id`
- `raw_query`
- `task_type`（email/report/research/unknown）
- `task_goal`
- `audience`
- `tone`
- `constraints`（长度、格式、禁用词、合规要求）
- `required_inputs`
- `missing_inputs`
- `plan`（步骤列表）
- `retrieved_chunks`
- `citations`
- `draft`
- `critique`
- `final_answer`
- `stream_buffer`
- `iteration_count`
- `max_iterations`

## 4.2 节点与边（推荐）

1. `classify_task`
   - 识别任务类别与复杂度。
   - 若并非复杂任务：`END_WITH_FALLBACK`（回退至原知识问答路由）。

2. `collect_requirements`
   - 提取必要槽位（邮件对象、汇报周期、调研范围等）。
   - 若缺信息：进入 `need_clarification` 分支，流式输出澄清问题。

3. `plan_steps`
   - 生成执行计划（检索什么、先写什么、是否需要数据摘要）。

4. `retrieve_knowledge`
   - 调用 Milvus 检索 + 内部模板/历史素材检索。
   - 产出结构化证据包（事实、数据、案例、引用来源）。

5. `draft_content`
   - 基于计划与证据生成初稿。
   - 按任务类型套模板（邮件/汇报/调研报告）。

6. `critique_and_rewrite`
   - 从“完整性、说服力、结构、营销语气、可执行性”进行自检并重写。
   - 若评分未达阈值且 `iteration_count < max_iterations`，回到 `draft_content`。

7. `compliance_check`
   - 规则校验：禁用词、夸大宣传、敏感承诺、数据真实性标记。
   - 不通过则回 `draft_content` 或输出风险提示版本。

8. `finalize_output`
   - 输出最终内容与可选附录（摘要、行动项、可替换变量）。

---

## 5. 工具层设计（先最小化，避免过度引入）

## 5.1 必要工具（建议第一期）

1. **kb_search_tool**（必要）
   - 封装现有 Milvus 检索接口。
   - 入参：query、top_k、filters（产品线、时间、地区）。
   - 出参：chunk + score + metadata。

2. **template_loader_tool**（高价值）
   - 按任务类型加载内部模板。
   - 如：客户跟进邮件模板、月报模板、调研报告模板。

3. **style_guide_tool**（建议）
   - 统一品牌语气、术语表、禁用表达。

## 5.2 暂不强制引入 MCP

当前场景核心是“内部知识 + 写作生产”，第一期并不依赖跨系统实时操作（如发邮件、建工单、查外部CRM）。
因此建议：
- 第一阶段不强制接 MCP。
- 在第二阶段如需连接 CRM、BI、邮件系统，再通过 MCP 扩展工具注册。

---

## 6. 流式输出设计（重点）

为兼容前端体验，建议输出两类流：

1. **阶段事件流（event stream）**
   - `event_type`: `stage_update`
   - `stage`: `planning/retrieval/drafting/review/finalizing`
   - `message`: 当前进度描述

2. **文本 token 流（token stream）**
   - `event_type`: `token`
   - `content`: LLM 增量文本

3. **完成事件**
   - `event_type`: `final`
   - `payload`: `{ final_answer, citations, quality_score }`

路由层做统一封装：
- 将 LangGraph 节点事件映射为前端可消费协议（SSE 或 WebSocket）。
- 保留与现有 `yield_result` 一致的生成器接口。

---

## 7. 意图识别增强建议

## 7.1 识别策略
在现有意图分类器中增加“复杂任务触发特征”：

- 动词特征：写、生成、整理、润色、重写、起草、输出方案。
- 产物特征：邮件、汇报、报告、提案、话术、活动方案。
- 约束特征：面向某客户/某领导、字数要求、风格要求、截止时间。

## 7.2 双阈值路由

- `complex_score >= high_threshold`：直接进 Agent 路由。
- `low_threshold <= complex_score < high_threshold`：先澄清（“你希望我直接生成邮件还是先做知识总结？”）。
- `< low_threshold`：走原有 16 意图路由。

---

## 8. 三类典型任务的执行模板

## 8.1 客户邮件

- 输入槽位：客户画像、邮件目的、产品卖点、CTA、语气。
- 输出结构：主题建议 + 正文 + 可选PS + 下一步行动。
- Agent 重点：个性化、简洁、行动导向。

## 8.2 汇报材料

- 输入槽位：汇报对象、周期、核心指标、问题与措施。
- 输出结构：摘要 -> 数据亮点 -> 问题分析 -> 下阶段计划。
- Agent 重点：结构清晰、指标可信、结论先行。

## 8.3 调研报告

- 输入槽位：调研目标、范围、时间窗口、样本来源。
- 输出结构：背景 -> 方法 -> 发现 -> 建议 -> 风险与局限。
- Agent 重点：证据链、引用标注、可执行建议。

---

## 9. 质量与安全控制

## 9.1 质量评分（可在 critique 节点实现）

建议 5 个维度，每项 1~5 分：

1. 目标匹配度
2. 结构完整性
3. 事实依据充分性
4. 营销表达有效性
5. 可执行性

低于阈值（如总分 < 18）自动迭代重写。

## 9.2 幻觉控制

- 强制“无证据不下结论”策略。
- 对关键结论附引用来源（知识库片段 ID）。
- 对不确定内容打标（如“需业务确认”）。

## 9.3 合规控制

- 敏感词与违规承诺检测。
- 对价格、效果、时效等高风险描述加警示。

---

## 10. 观测与运营

建议埋点：

- 复杂任务命中率
- 澄清触发率
- 一次成稿率
- 平均迭代次数
- 平均响应首 token 时间
- 用户采纳率（复制/导出/二次编辑）

用于后续优化 prompt、模板与检索策略。

---

## 11. 分阶段落地计划

### Phase 1（2~3 周）

- 新增 `complex_content_generation` 意图。
- 接入 `ComplexTaskAgentRoute` + LangGraph 最小闭环（plan/retrieve/draft/final）。
- 支持邮件、汇报、调研三类模板。
- 完成流式输出协议对齐。

### Phase 2（2~4 周）

- 引入 critique + compliance 双校验。
- 上线质量评分与自动重写。
- 加入可观测埋点与灰度配置。

### Phase 3（按需）

- 按业务价值接入 MCP（CRM/BI/邮件发送）。
- 扩展到活动策划、话术库生成等更复杂营销场景。

---

## 12. 关键结论

1. 你的思路是正确的：**不推翻现有 16 路由，增量加入 Agent 路由**是最稳妥路线。
2. LangGraph 适合作为复杂任务编排层，负责“规划-检索-生成-校验-迭代”。
3. 第一阶段不必强引 MCP，先把内容生产闭环和质量控制做实，再按需扩展系统连接能力。
4. 通过统一 `yield_result` 流式接口，可实现与现有架构低耦合集成。


## 13. Graph 结构图

可查看独立图示文档：`docs/complex_task_agent_graph.md`。
