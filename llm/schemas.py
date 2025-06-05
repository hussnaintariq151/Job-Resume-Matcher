

from typing import List, Optional, Union
from pydantic import BaseModel, Field
from search.job_search import JobResult  # adjust import as needed

class MatchRequest(BaseModel):
    resume_text: str
    job_description_text: Optional[str] = None
    selected_role: Optional[str] = None 
    max_job_search_results: int = Field(default=5, ge=1, le=20)

class MatchResult(BaseModel):
    score: int = Field(..., ge=0, le=100)
    matched_skills: List[str]
    missing_skills: List[str]
    suggestions: str

class UnifiedResponse(BaseModel):
    roles: List[str]
    jobs_found: List[JobResult]
    match_result: Union[MatchResult, dict]

class AnalyzeRequest(BaseModel):
    resume_text: str
    job_description_text: Optional[str] = None
    max_job_search_results: Optional[int] = 5
    selected_role: Optional[str] = None
