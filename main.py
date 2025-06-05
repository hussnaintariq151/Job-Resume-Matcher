from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from matcher.llm_matcher import unified_job_resume_analyze
from llm.schemas import MatchRequest, AnalyzeRequest, UnifiedResponse
from parsers.parser_selector import extract_text
from llm.inferencer import infer_job_roles, ResumeInput
from search.job_search import search_jobs, JobSearchInput, JobSearchError


load_dotenv()

app = FastAPI()

# Static files and template setup
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory user session (in production, use session store or DB)
user_data = {}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("intro.html", {"request": request})


@app.get("/upload-page", response_class=HTMLResponse)
async def upload_resume(request: Request):
    return templates.TemplateResponse("resume_upload.html", {"request": request})


@app.post("/upload", response_class=HTMLResponse)
async def handle_upload(
    request: Request,
    file: UploadFile = File(...),
    mode: str = Form("regular")
):
    try:
        # Read and save uploaded file
        contents = await file.read()
        os.makedirs("temp", exist_ok=True)
        file_path = f"temp/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(contents)

        # Step 1: Extract resume text
        resume_text = extract_text(file_path, mode)
        user_data["resume_text"] = resume_text

        # Step 2: Infer top 5 roles from resume using Gemini
        role_result = infer_job_roles(ResumeInput(resume_text=resume_text, top_k=5))
        user_data["inferred_roles"] = role_result.roles

        # Redirect to role selection page
        return RedirectResponse(url="/select-role", status_code=303)

    except Exception as e:
        return templates.TemplateResponse("resume_upload.html", {
            "request": request,
            "error": f"Failed to process resume: {str(e)}"
        })



@app.get("/select-role", response_class=HTMLResponse)
async def select_role(request: Request):
    roles = user_data.get("inferred_roles")

    if not roles:
        # Absolute fallback in rare case of missing session data
        roles = ["Data Scientist", "ML Engineer", "Teacher"]

    return templates.TemplateResponse("role_select.html", {
        "request": request,
        "roles": roles,
    })



@app.post("/select-role", response_class=HTMLResponse)
async def submit_role(
    request: Request,
    selected_role: str = Form(...),
    custom_role: str = Form(None),
):
    final_role = custom_role.strip() if custom_role else selected_role
    user_data["selected_role"] = final_role
    return RedirectResponse(url="/jobmatch", status_code=303)





# @app.get("/jobmatch", response_class=HTMLResponse)
# async def perform_job_matching(request: Request):
#     resume_text = user_data.get("resume_text")
#     selected_role = user_data.get("selected_role")

#     if not resume_text or not selected_role:
#         return templates.TemplateResponse("error.html", {
#             "request": request,
#             "error_message": "Missing resume or role. Please upload again."
#         })

#     # Search jobs with selected role
#     search_input = JobSearchInput(query=f"{selected_role} remote", max_results=5)
#     jobs_found = search_jobs(search_input)

#     if not jobs_found:
#         return templates.TemplateResponse("error.html", {
#             "request": request,
#             "error_message": f"No jobs found for {selected_role}."
#         })

#     # Analyze top job
#     top_job = jobs_found[0]
#     req = MatchRequest(
#         resume_text=resume_text,
#         job_description_text=top_job.snippet,
#         selected_role=selected_role,
#         max_job_search_results=5
#     )
#     result = unified_job_resume_analyze(req)

#     return templates.TemplateResponse("match_results.html", {
#         "request": request,
#         "selected_role": selected_role,
#         "match_result": result.match_result,
#         "jobs_found": result.jobs_found
#     })


@app.get("/jobmatch", response_class=HTMLResponse)
async def perform_job_matching(request: Request):
    resume_text = user_data.get("resume_text")
    selected_role = user_data.get("selected_role")

    if not resume_text or not selected_role:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": "Missing resume or role. Please upload again."
        })

    # Search jobs with selected role
    search_input = JobSearchInput(query=f"{selected_role} remote", max_results=5)
    jobs_found = search_jobs(search_input)

    if not jobs_found:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": f"No jobs found for {selected_role}."
        })

    # Analyze top job
    top_job = jobs_found[0]
    req = MatchRequest(
        resume_text=resume_text,
        job_description_text=top_job.snippet,
        selected_role=selected_role,
        max_job_search_results=5
    )
    result = unified_job_resume_analyze(req)

    return templates.TemplateResponse("match_results.html", {
        "request": request,
        "selected_role": selected_role,
        "match_result": result.match_result,
        "jobs_found": result.jobs_found
    })


@app.get("/jobsearch", response_class=HTMLResponse)
async def job_search_from_selected_role(request: Request):
    selected_role = user_data.get("selected_role")

    if not selected_role:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "No role selected. Please select a role first."
            }
        )

    try:
        query = f"{selected_role} remote"
        search_input = JobSearchInput(query=query, max_results=10)
        job_results = search_jobs(search_input)

        if not job_results:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "error_message": f"No job listings found for role: {selected_role}"
                }
            )

        return templates.TemplateResponse(
            "job_list.html",
            {
                "request": request,
                "selected_role": selected_role,
                "job_results": job_results
            }
        )

    except JobSearchError as e:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": f"Job search failed: {str(e)}"
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": f"Unexpected error during job search: {str(e)}"
            }
        )