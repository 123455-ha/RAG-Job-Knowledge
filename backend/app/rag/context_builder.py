def build_context(results: list[dict]) -> str:
    return "\n\n".join(
        f"[{i + 1}] {r['file_name']} (page {r.get('page') or 'n/a'}): {r['content']}"
        for i, r in enumerate(results)
    )
