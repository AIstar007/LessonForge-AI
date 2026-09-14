from langgraph.graph import StateGraph, END
from schemas import AgentState, Evaluation, RejectionEntry
from prompts import GENERATOR_SYSTEM, EVALUATOR_SYSTEM, generation_prompt, evaluation_prompt
from llm import AzureOpenAIClient
from memory import MemoryStore

llm = AzureOpenAIClient()
memory = MemoryStore()


def generate(state: AgentState):
    patterns = memory.learned_patterns()
    lesson = llm.generate_text(
        GENERATOR_SYSTEM,
        generation_prompt(state.topic, state.feedback, patterns)
    )

    if state.inject_error and state.attempt == 0:
        lesson += "\n\n### Incorrect Demo Statement\nRAG permanently retrains the model every time it reads a document.\nVector database."

    return {
        **state.model_dump(),
        "lesson": lesson,
        "learned_patterns": patterns,
    }


def evaluate(state: AgentState):

    result = llm.evaluate_structured(

        # System prompt
        EVALUATOR_SYSTEM,

        # User prompt
        evaluation_prompt(
            state.topic,
            state.lesson
        ),

        # Structured schema
        Evaluation,
    )

    checks_dict = result.checks.model_dump()

    result.overall_pass = all(
        item["passed"]
        for item in checks_dict.values()
    )

    failed = [
        name
        for name, item in checks_dict.items()
        if not item["passed"]
    ]

    rejection_log = list(state.rejection_log)

    feedback = []
    reasons = []
    fixes = []

    for name in failed:

        item = checks_dict[name]

        reason = item["reason"]
        fix = item["fix"]

        reasons.append(reason)
        fixes.append(fix)

        feedback.append(
            f"{name}: FAILED.\n"
            f"Reason: {reason}\n"
            f"Required Fix: {fix}"
        )

    if failed:

        entry = RejectionEntry(
            attempt=state.attempt + 1,
            failed_checks=failed,
            reasons=reasons,
            changes_requested=fixes,
        )

        rejection_log.append(entry)

        memory.save_failure(
            state.run_id,
            state.topic,
            state.attempt + 1,
            failed,
            reasons,
            fixes,
        )

    return {
        **state.model_dump(),
        "evaluation": result,
        "feedback": "\n\n".join(feedback),
        "rejection_log": rejection_log,
    }

def route(state: AgentState):
    if state.evaluation.overall_pass:
        return "finish"
    if state.attempt >= state.max_retries:
        return "finish"
    return "retry"


def increment_attempt(state: AgentState):
    return {
        **state.model_dump(),
        "attempt": state.attempt + 1,
        "inject_error": False,
    }


def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("generate", generate)
    workflow.add_node("evaluate", evaluate)
    workflow.add_node("increment_attempt", increment_attempt)

    workflow.set_entry_point("generate")
    workflow.add_edge("generate", "evaluate")
    workflow.add_conditional_edges(
        "evaluate", route,
        {"retry": "increment_attempt", "finish": END}
    )
    workflow.add_edge("increment_attempt", "generate")
    return workflow.compile()
