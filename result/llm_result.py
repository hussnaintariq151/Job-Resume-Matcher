# # gemini_matcher.py

# import json
# import logging
# from typing import List, Optional, Union
# from pydantic import BaseModel, Field, ValidationError
# import google.generativeai as genai

# # Import your modules
# from llm.inferencer import infer_job_roles, ResumeInput, RoleOutput
# from search.job_search import search_jobs, JobSearchInput, JobResult
# from parsers.parser_selector import extract_text

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# if not logger.hasHandlers():
#     ch = logging.StreamHandler()
#     ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
#     logger.addHandler(ch)

# # Initialize Gemini model (API key should be configured in env)
# model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-001")


# class MatchRequest(BaseModel):
#     resume_text: str
#     job_description_text: Optional[str] = None
#     max_job_search_results: int = Field(default=5, ge=1, le=20)


# class MatchResult(BaseModel):
#     score: int = Field(..., ge=0, le=100)
#     matched_skills: List[str]
#     missing_skills: List[str]
#     suggestions: str


# class UnifiedResponse(BaseModel):
#     roles: List[str]
#     jobs_found: List[JobResult]
#     match_result: Union[MatchResult, dict]


# def analyze_match(resume_text: str, job_description: str) -> Union[MatchResult, dict]:
#     """
#     Call Gemini LLM to analyze match between resume and job description.
#     """
#     prompt = f"""
# You are a job match assistant. Given a resume and job description, return a valid JSON with:

# {{
#   "score": <int 0-100>,
#   "matched_skills": [list of matched skills],
#   "missing_skills": [list of missing skills],
#   "suggestions": "Improvement suggestions for the resume"
# }}

# Job Description:
# \"\"\"{job_description}\"\"\"

# Resume:
# \"\"\"{resume_text}\"\"\"
# """
#     try:
#         response = model.generate_content(prompt)
#         raw_text = response.text.strip()
#         logger.debug(f"Gemini raw response: {raw_text}")

#         # Extract JSON substring (simple heuristic)
#         start = raw_text.find("{")
#         end = raw_text.rfind("}") + 1
#         json_str = raw_text[start:end]

#         data = json.loads(json_str)
#         match_result = MatchResult(**data)
#         return match_result
#     except (json.JSONDecodeError, ValidationError) as e:
#         logger.error(f"Parsing Gemini response failed: {e}")
#         return {"error": "Failed to parse Gemini response", "raw_response": raw_text}
#     except Exception as e:
#         logger.error(f"Unexpected error in Gemini call: {e}")
#         return {"error": str(e)}


# def unified_job_resume_analyze(request: MatchRequest) -> UnifiedResponse:
#     # Step 1: Infer roles from resume
#     roles_output: RoleOutput = infer_job_roles(ResumeInput(resume_text=request.resume_text, top_k=5))
#     logger.info(f"Inferred roles: {roles_output.roles}")

#     # Step 2: Prepare job descriptions
#     job_descriptions = []
#     jobs_found: List[JobResult] = []

#     if request.job_description_text:
#         job_descriptions = [request.job_description_text]
#         logger.info("Using user-uploaded job description.")
#     else:
#         # Search jobs based on top inferred role + "remote" (simple heuristic)
#         query = f"{roles_output.roles[0]} remote" if roles_output.roles else "Data Scientist remote"
#         search_input = JobSearchInput(query=query, max_results=request.max_job_search_results)
#         jobs_found = search_jobs(search_input)
#         job_descriptions = [job.snippet for job in jobs_found if job.snippet]
#         logger.info(f"Fetched {len(job_descriptions)} job descriptions from search.")

#     # Step 3: Pick first job description for matching (could loop over all for batch)
#     if not job_descriptions:
#         logger.warning("No job descriptions available for matching.")
#         return UnifiedResponse(roles=roles_output.roles, jobs_found=jobs_found, match_result={"error": "No job description to match"})

#     job_desc = job_descriptions[0]

#     # Step 4: Call Gemini to analyze match
#     match_result = analyze_match(request.resume_text, job_desc)

#     return UnifiedResponse(
#         roles=roles_output.roles,
#         jobs_found=jobs_found,
#         match_result=match_result
#     )


# if __name__ == "__main__":
#     import os
#     from dotenv import load_dotenv
#     load_dotenv()

#     sample_resume = "Experienced data scientist skilled in Python, ML, statistics, and data visualization."
#     sample_jd = None  # Or provide a sample job description string here

#     req = MatchRequest(resume_text=sample_resume, job_description_text=sample_jd)
#     response = unified_job_resume_analyze(req)

#     print("Inferred roles:", response.roles)
#     if response.jobs_found:
#         print(f"Jobs found: {len(response.jobs_found)}")
#         for i, job in enumerate(response.jobs_found, 1):
#             print(f"{i}. {job.title} - {job.link}")
#     print("Match result:", response.match_result)

# app/main/cli_demo.py
#========================================================================

# import sys
# import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from matcher.llm_matcher import unified_job_resume_analyze

# from dotenv import load_dotenv
# from matcher.llm_matcher import unified_job_resume_analyze

# from llm.schemas import MatchRequest

# load_dotenv()

# sample_resume = "Experienced data scientist skilled in Python, ML, statistics, and data visualization."
# sample_jd = None

# req = MatchRequest(resume_text=sample_resume, job_description_text=sample_jd)
# res = unified_job_resume_analyze(req)

# print("Inferred Roles:", res.roles)
# if res.jobs_found:
#     print(f"Jobs Found: {len(res.jobs_found)}")
#     for i, job in enumerate(res.jobs_found, 1):
#         print(f"{i}. {job.title} - {job.link}")
# print("Match Result:", res.match_result)

# # Save results to JSON
# import json
# from datetime import datetime
# import os

# # Combine all data
# results_dict = {
#     "inferred_roles": inferred_roles,
#     "jobs_found": jobs,
#     "match_result": match_result
# }

# # Create output directory if it doesn't exist
# output_dir = "output"
# os.makedirs(output_dir, exist_ok=True)

# # Create a timestamped filename
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# filename = os.path.join(output_dir, f"job_match_result_{timestamp}.json")

# # Write to JSON file
# with open(filename, "w", encoding="utf-8") as f:
#     json.dump(results_dict, f, indent=2, ensure_ascii=False)

# print(f"\n✅ Match results saved to: {filename}")

# ===========================================================

import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Setup import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Imports
from matcher.llm_matcher import unified_job_resume_analyze
from llm.schemas import MatchRequest

# Load environment variables
load_dotenv()

# --- Sample Input
sample_resume = "Experienced data scientist skilled in Python, ML, statistics, and data visualization."
sample_jd = None  # Will be selected automatically in the pipeline

# --- Run Matching Pipeline
req = MatchRequest(resume_text=sample_resume, job_description_text=sample_jd)
res = unified_job_resume_analyze(req)

# --- Display Results
print("Inferred Roles:", res.roles)

if res.jobs_found:
    print(f"Jobs Found: {len(res.jobs_found)}")
    for i, job in enumerate(res.jobs_found, 1):
        print(f"{i}. {job.title} - {job.link}")
else:
    print("No jobs found.")

print("Match Result:", res.match_result)

# --- Save to JSON
results_dict = {
    "inferred_roles": res.roles,
    "jobs_found": [
        {"title": job.title, "link": job.link}
        for job in res.jobs_found
    ] if res.jobs_found else [],
    "match_result": {
        "score": res.match_result.score,
        "matched_skills": res.match_result.matched_skills,
        "missing_skills": res.match_result.missing_skills,
        "suggestions": res.match_result.suggestions
    } if res.match_result else {}
}

# Create output directory if needed
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Timestamped filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = os.path.join(output_dir, f"job_match_result_{timestamp}.json")

# Write JSON file
with open(filename, "w", encoding="utf-8") as f:
    json.dump(results_dict, f, indent=2, ensure_ascii=False)

print(f"\n✅ Match results saved to: {filename}")
