from pydantic import BaseModel, Field

class CorpusReference(BaseModel):
    github_number: int
    url: str
    why_relevant: str
    

class ResearchBrief(BaseModel):
    problem_restatement:str
    root_cause_hypothesis: str
    corpus_references: list[CorpusReference] = Field(default_factory=list)
    external_finding: list[str] = Field(default_factory=list)
    suggested_response_direction: str
    open_questions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    needs_escalation: bool
    
    