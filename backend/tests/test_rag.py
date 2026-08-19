from backend.app.services.llm_service import LLMService


def test_unknown_answer():
    assert "没有找到足够" in LLMService().answer("unknown", "", [])
