from backend.app.services.llm_service import LLMService
from backend.app.services.llm_service import extract_message_content


def test_unknown_answer():
    assert "没有找到足够" in LLMService().answer("unknown", "", [])


def test_extract_compatible_content():
    assert (
        extract_message_content({"choices": [{"message": {"content": "回答"}}]})
        == "回答"
    )
    assert (
        extract_message_content(
            {"choices": [{"message": {"content": [{"text": "分段"}]}}]}
        )
        == "分段"
    )
    assert (
        extract_message_content(
            {"choices": [{"message": {"reasoning_content": "兜底"}}]}
        )
        == "兜底"
    )
