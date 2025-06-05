
import json
import logging
from google.generativeai import GenerativeModel
from pydantic import ValidationError

from llm.inferencer import infer_job_roles, ResumeInput
from llm.schemas import MatchRequest, MatchResult, UnifiedResponse
from search.job_search import search_jobs, JobSearchInput



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

model = GenerativeModel(model_name="models/gemini-1.5-flash-001")

def analyze_match(resume_text: str, job_description: str) -> MatchResult | dict:
    prompt = f"""
You are a job match assistant. Given a resume and job description, return a valid JSON with:
{{
  "score": <int 0-100>,
  "matched_skills": [list of matched skills],
  "missing_skills": [list of missing skills],
  "suggestions": "Improvement suggestions for the resume"
}}

Job Description:
\"\"\"{job_description}\"\"\"

Resume:
\"\"\"{resume_text}\"\"\"
"""
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        logger.debug(f"Gemini response: {raw}")

        json_str = raw[raw.find("{"): raw.rfind("}") + 1]
        data = json.loads(json_str)
        return MatchResult(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Gemini JSON parsing failed: {e}")
        return {"error": "Failed to parse Gemini response", "raw_response": raw}
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return {"error": str(e)}

def unified_job_resume_analyze(request: MatchRequest) -> UnifiedResponse:
    roles_output = infer_job_roles(ResumeInput(resume_text=request.resume_text, top_k=5))
    logger.info(f"Inferred roles: {roles_output.roles}")

    job_descriptions = []
    jobs_found = []

    if request.job_description_text:
        job_descriptions = [request.job_description_text]
        logger.info("Using provided job description.")
    else:
        selected_role = request.selected_role or (roles_output.roles[0] if roles_output.roles else "Data Scientist")
        search_input = JobSearchInput(query=f"{selected_role} remote", max_results=request.max_job_search_results)
        jobs_found = search_jobs(search_input)
        job_descriptions = [job.snippet for job in jobs_found if job.snippet]

    if not job_descriptions:
        logger.warning("No job descriptions available.")
        return UnifiedResponse(roles=roles_output.roles, jobs_found=jobs_found, match_result={"error": "No job description to match"})

    match_result = analyze_match(request.resume_text, job_descriptions[0])
    return UnifiedResponse(roles=roles_output.roles, jobs_found=jobs_found, match_result=match_result)
