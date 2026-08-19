from backend.app.database.database import execute


class QueryRewriter:
    """Adds minimal conversation context for short follow-up questions."""

    def rewrite(self, question: str, conversation_id: str | None) -> str:
        if not conversation_id:
            return question
        rows = execute(
            "SELECT content FROM messages WHERE conversation_id=? AND role='user' ORDER BY id DESC LIMIT 1",
            (conversation_id,),
        )
        is_follow_up = len(question) < 20 or any(
            marker in question
            for marker in ("它", "这个", "上述", "刚才", "that", "it")
        )
        return (
            f"{rows[0]['content']}\n后续问题：{question}"
            if rows and is_follow_up
            else question
        )
