import os
import sys
import re
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = BASE_DIR / "scripts" / "evaluation_questions.md"
RESULTS_FILE = BASE_DIR / "scripts" / "evaluation_results.md"

sys.path.insert(0, str(BASE_DIR))
from backend.app.core.agent import init_agent


def load_questions_from_markdown() -> list:
    if not QUESTIONS_FILE.exists():
        print(f"[ERROR] {QUESTIONS_FILE} not found!")
        sys.exit(1)

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    questions = []
    category = "General"
    
    for line in text.splitlines():
        line_str = line.strip()
        if line_str.startswith("## "):
            category = line_str.replace("## ", "").strip()
        elif re.match(r"^\d+\.\s+", line_str):
            q_text = re.sub(r"^\d+\.\s+", "", line_str).strip()
            if q_text:
                questions.append({
                    "id": len(questions) + 1,
                    "category": category,
                    "question": q_text,
                })

    print(f"Loaded {len(questions)} evaluation questions from {QUESTIONS_FILE.name}")
    return questions


def run_evaluation():
    print("=" * 70)
    print("🚀 ArunCore Agent Multi-Turn Evaluation Suite (7-Iteration ReAct Loop)")
    print("=" * 70)

    questions = load_questions_from_markdown()
    if not questions:
        print("[ERROR] No valid questions found.")
        return

    main_llm, prompt, memory, tools = init_agent(temperature=0.3)
    tool_map = {t.name: t for t in tools}

    results_md_blocks = [
        "# 🧪 ArunCore AI Assistant — Evaluation Results & Traces",
        f"\n**Evaluated Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Questions Evaluated:** {len(questions)}\n",
        "---",
    ]

    for item in questions:
        qid = item["id"]
        cat = item["category"]
        q = item["question"]

        print(f"\n[Q{qid:02d} | {cat}] '{q}'")
        t0 = time.time()

        scratchpad = []
        tools_called = []
        max_turns = 7
        turn_count = 0
        final_answer = ""

        while turn_count < max_turns:
            turn_count += 1
            messages = prompt.format_messages(
                running_summary="",
                chat_history=[],
                input=q,
                agent_scratchpad=scratchpad
            )

            try:
                ai_msg = main_llm.invoke(messages)
            except Exception as le:
                final_answer = f"LLM Error: {le}"
                break

            if ai_msg.tool_calls:
                scratchpad.append(ai_msg)
                for tc in ai_msg.tool_calls:
                    tname = tc["name"]
                    targs = tc.get("args", {})
                    tools_called.append(f"{tname}({json.dumps(targs)})")
                    print(f"   ├─ Turn {turn_count}: Tool Call -> {tname}({targs})")

                    tool_func = tool_map.get(tname)
                    if tool_func:
                        try:
                            t_res = tool_func.invoke(targs)
                        except Exception as te:
                            t_res = f"Tool error: {te}"
                    else:
                        t_res = f"Unknown tool: {tname}"

                    scratchpad.append({
                        "role": "tool",
                        "name": tname,
                        "tool_call_id": tc.get("id", f"tc_{turn_count}"),
                        "content": str(t_res)[:3000]
                    })
            else:
                final_answer = (ai_msg.content or "").strip()
                break

        elapsed = round(time.time() - t0, 2)
        print(f"   └─ Final Answer ({elapsed}s, {len(tools_called)} tools used): {final_answer[:120]}...")

        tools_str = "\n".join([f"- `{t}`" for t in tools_called]) if tools_called else "*No tools called (Direct Answer)*"

        block = f"""
### Q{qid:02d} [{cat}]: {q}

**Execution Time:** `{elapsed}s` | **ReAct Turns:** `{turn_count}`

#### 🛠️ Tools Called:
{tools_str}

#### 🤖 AI Response:
{final_answer}

---
"""
        results_md_blocks.append(block)

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(results_md_blocks))

    print("\n" + "=" * 70)
    print(f"✅ Evaluation complete! Saved full traces and responses to {RESULTS_FILE.name}")
    print("=" * 70)


if __name__ == "__main__":
    import json
    run_evaluation()
