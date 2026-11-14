"""fallback_form.py - guided question form used when the router is not sure. No LLM."""


def build_fallback_form(domains, question=""):
    options = []
    followups = {}
    for d in domains:
        options.append({
            "id": d["id"],
            "label": d.get("description", d["id"]),
            "examples": list(d.get("example_questions", []))[:3],
        })
        followups[d["id"]] = [
            {
                "name": a.get("name"),
                "prompt": a.get("prompt", ""),
                "why_it_matters": a.get("why_it_matters", ""),
            }
            for a in d.get("axes", [])
            if a.get("source") == "ask_user"
        ]
    options.append({"id": "none", "label": "Something else (not supported yet)", "examples": []})
    return {
        "type": "guided_form",
        "message": "I could not match your question to a topic I can analyse. Please pick one.",
        "original_question": question,
        "step1_pick_topic": {"field": "domain", "options": options},
        "step2_followups": followups,
    }


def form_to_text(form):
    lines = [form["message"], ""]
    for i, opt in enumerate(form["step1_pick_topic"]["options"], 1):
        lines.append(f"{i}. {opt['label']}")
        for ex in opt["examples"]:
            lines.append(f"     e.g. {ex}")
    return "\n".join(lines)