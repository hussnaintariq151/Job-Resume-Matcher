import streamlit as st

def page_upload_resume():
    st.title("Step 1: Upload Resume")
    resume_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])
    if resume_file:
        resume_text = parse_file(resume_file)
        st.session_state['resume_text'] = resume_text
        st.session_state['page'] = 'select_role'
        st.experimental_rerun()

def page_select_role():
    st.title("Step 2: Select Role")
    resume_text = st.session_state.get('resume_text')
    if not resume_text:
        st.error("Resume not found. Please upload again.")
        st.session_state['page'] = 'upload_resume'
        st.experimental_rerun()

    inferred_roles = infer_roles(resume_text)
    selected_role = st.selectbox("Select a role", inferred_roles)
    if st.button("Next"):
        st.session_state['selected_role'] = selected_role
        st.session_state['page'] = 'select_job'
        st.experimental_rerun()

def page_select_job():
    st.title("Step 3: Select Job")
    selected_role = st.session_state.get('selected_role')
    if not selected_role:
        st.error("Role not selected.")
        st.session_state['page'] = 'select_role'
        st.experimental_rerun()

    jobs = search_jobs(selected_role)
    job_titles = [job['title'] for job in jobs]
    selected_job_title = st.selectbox("Select a job", job_titles)
    if st.button("Next"):
        selected_job = next((job for job in jobs if job['title'] == selected_job_title), None)
        st.session_state['selected_job'] = selected_job
        st.session_state['page'] = 'show_result'
        st.experimental_rerun()

def page_show_result():
    st.title("Step 4: Match Result")
    resume_text = st.session_state.get('resume_text')
    selected_job = st.session_state.get('selected_job')
    if not resume_text or not selected_job:
        st.error("Missing data, please start over.")
        st.session_state['page'] = 'upload_resume'
        st.experimental_rerun()

    st.markdown(f"**Job:** {selected_job['title']}")
    if selected_job.get('url'):
        st.markdown(f"[Job Posting]({selected_job['url']})")

    match_result = match_resume_to_job(resume_text, selected_job.get('description', ''))

    st.write(f"Score: {match_result['score']}")
    st.write("Matched Skills:", ", ".join(match_result["matched_skills"]))
    st.write("Missing Skills:", ", ".join(match_result["missing_skills"]))
    st.write("Suggestions:", match_result["suggestions"])

    if st.button("Start Over"):
        for key in ['resume_text', 'selected_role', 'selected_job', 'page']:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()


def parse_file(uploaded_file):
    import io
    import fitz  # PyMuPDF
    if uploaded_file.type == "application/pdf":
        with io.BytesIO(uploaded_file.read()) as f:
            doc = fitz.open(stream=f.read(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
    else:
        text = uploaded_file.read().decode("utf-8")
    return text

def infer_roles(resume_text):
    return ["Data Scientist", "Machine Learning Engineer", "Data Analyst"]

def search_jobs(role):
    return [
        {"title": f"{role} at Company A", "url": "https://companyA.jobs/123", "description": "Python, ML, data analysis."},
        {"title": f"{role} at Company B", "url": "https://companyB.jobs/456", "description": "ML Engineer with deep learning experience."},
    ]

def match_resume_to_job(resume_text, job_desc_text):
    return {
        "score": 85,
        "matched_skills": ["Python", "ML", "statistics"],
        "missing_skills": ["Deep Learning"],
        "suggestions": "Add Deep Learning experience."
    }

if 'page' not in st.session_state:
    st.session_state['page'] = 'upload_resume'

page = st.session_state['page']

if page == 'upload_resume':
    page_upload_resume()
elif page == 'select_role':
    page_select_role()
elif page == 'select_job':
    page_select_job()
elif page == 'show_result':
    page_show_result()
