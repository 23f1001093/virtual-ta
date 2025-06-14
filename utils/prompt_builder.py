def format_answer(question, matches):
    if not matches:
        return {"answer": "No relevant content found.", "links": []}
    return {
        "answer": f"I found {len(matches)} relevant results.",
        "links": [{"url": m["url"], "text": m["title"]} for m in matches]
    }
