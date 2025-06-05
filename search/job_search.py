
import logging
from typing import List
from pydantic import BaseModel, Field
from duckduckgo_search import DDGS

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(ch)

class JobSearchError(Exception):
    pass

class JobSearchInput(BaseModel):
    query: str = Field(..., example="Data Scientist remote")
    max_results: int = Field(default=10, ge=1, le=50)

class JobResult(BaseModel):
    title: str
    link: str
    snippet: str

def search_jobs(input_data: JobSearchInput) -> List[JobResult]:
    logger.info(f"Searching jobs for: '{input_data.query}', max_results: {input_data.max_results}")
    try:
        ddgs = DDGS()
        raw_results: List[dict] = ddgs.text(input_data.query, max_results=input_data.max_results)

        if not raw_results:
            logger.warning("No results found.")
            return []

        jobs = []
        for r in raw_results:
            job = JobResult(
                title=r.get("title", "No Title").strip(),
                link=r.get("href", "No Link").strip(),
                snippet=r.get("body", "No Snippet").strip(),
            )
            jobs.append(job)

        logger.info(f"Found {len(jobs)} jobs.")
        return jobs

    except Exception as e:
        logger.exception("Job search failed.")
        raise JobSearchError(f"Job search failed: {e}") from e

if __name__ == "__main__":
    try:
        input_data = JobSearchInput(query="Data Scientist remote", max_results=5)
        jobs = search_jobs(input_data)
        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job.title}\nLink: {job.link}\nSnippet: {job.snippet}\n")
    except Exception as e:
        logger.error(f"Error during job search test: {e}")
