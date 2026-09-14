from typing import List
from pydantic import BaseModel, Field


class CheckResult(BaseModel):
    passed: bool
    reason: str
    fix: str


class EvaluationChecks(BaseModel):
    accuracy: CheckResult
    beginner_language: CheckResult
    example: CheckResult
    no_unexplained_jargon: CheckResult
    key_concepts: CheckResult
    teaching_flow: CheckResult


class Evaluation(BaseModel):
    overall_pass: bool
    checks: EvaluationChecks
    summary: str


class RejectionEntry(BaseModel):
    attempt: int
    failed_checks: List[str]
    reasons: List[str]
    changes_requested: List[str]


class AgentState(BaseModel):
    topic: str
    lesson: str = ""
    attempt: int = 0
    max_retries: int = 2
    evaluation: Evaluation | None = None
    feedback: str = ""
    learned_patterns: List[str] = Field(default_factory=list)
    rejection_log: List[RejectionEntry] = Field(default_factory=list)
    inject_error: bool = False
    run_id: str = ""