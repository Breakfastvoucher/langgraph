from industry_research_agent.graph import build_report_graph


class ApproveLLM:
    def invoke(self, prompt: str) -> str:
        if "请审核以下报告" in prompt:
            return "APPROVE: 报告通过"
        return "这是一份可用报告草稿"


class FakeKB:
    def query(self, question: str):
        return [{"title": question, "snippet": "evidence", "score": 0.9}]


def test_graph_generates_final_report():
    app = build_report_graph(llm=ApproveLLM(), kb_client=FakeKB())
    result = app.invoke({"topic": "新能源", "revision_count": 0})

    assert result["final_report"]
    assert len(result["kb_results"]) > 0
