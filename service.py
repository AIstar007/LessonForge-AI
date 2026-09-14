import json
import uuid
from pathlib import Path
from schemas import AgentState
from graph import build_graph
from memory import MemoryStore
from config import MAX_RETRIES


def run_agent(topic: str, inject_error: bool = False):
    run_id = str(uuid.uuid4())[:8]
    app = build_graph()

    initial = AgentState(
        topic=topic,
        max_retries=MAX_RETRIES,
        inject_error=inject_error,
        run_id=run_id,
    )

    result = app.invoke(initial.model_dump())
    final = AgentState.model_validate(result)

    status = "PASS" if final.evaluation and final.evaluation.overall_pass else "MAX_RETRIES_REACHED"

    payload = {
        "run_id": run_id,
        "topic": final.topic,
        "status": status,
        "attempts_used": final.attempt + 1,
        "lesson": final.lesson,
        "evaluation": final.evaluation.model_dump() if final.evaluation else None,
        "rejection_log": [x.model_dump() for x in final.rejection_log],
        "learned_patterns_used": final.learned_patterns,
    }

    Path("output").mkdir(exist_ok=True)
    path = Path("output") / f"{run_id}_result.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("output/latest_result.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    MemoryStore().save_run(run_id, topic, status, final.attempt + 1)
    return payload
