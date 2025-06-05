

import sys
import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel
import google.generativeai as genai
import ast
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from log_config import get_logger
from exception import APIQuotaExceededError, ModelNotFoundError, InvalidInputError

# Logger setup
logger = get_logger(__name__, log_file="app.log")

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.critical("GEMINI_API_KEY not found in environment.")
    raise ValueError("GEMINI_API_KEY not found")

# Configure Gemini
genai.configure(api_key=api_key)

try:
    # Initialize model and chat
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-001")
    chat = model.start_chat(history=[])
    logger.info("Gemini model initialized successfully.")
except Exception as e:
    logger.exception("Failed to initialize Gemini model.")
    raise ModelNotFoundError("Gemini model initialization failed.") from e

# Pydantic models
class ResumeInput(BaseModel):
    resume_text: str
    top_k: int = 5

class RoleOutput(BaseModel):
    roles: List[str]

def infer_job_roles(input_data: ResumeInput) -> RoleOutput:
    logger.debug(f"Inferring roles for resume with top_k={input_data.top_k}")

    prompt = f"""
    You are an AI career assistant. Based on the resume below, suggest the top {input_data.top_k} job roles.

    Resume:
    \"\"\"{input_data.resume_text}\"\"\"

    Return your response as a valid Python list of strings like:
    ["Data Scientist", "Machine Learning Engineer"]
    Do not wrap it in markdown code blocks or add explanations.
    """

    try:
        response = chat.send_message(prompt)
        reply = response.text.strip()
        logger.debug(f"Raw model reply: {reply}")
    except Exception as e:
        if "quota" in str(e).lower():
            logger.error("Quota exceeded error.")
            raise APIQuotaExceededError() from e
        if "not found" in str(e).lower():
            logger.error("Model not found error.")
            raise ModelNotFoundError() from e
        logger.exception("Unexpected error while calling Gemini API.")
        raise

    # Extract the first Python list from the response using regex
    try:
        match = re.search(r'\[.*?\]', reply, re.DOTALL)
        if match:
            role_list_str = match.group(0)
            roles = ast.literal_eval(role_list_str)
            if isinstance(roles, list):
                cleaned_roles = [r.strip() for r in roles if isinstance(r, str)]
                logger.info(f"Inferred roles: {cleaned_roles}")
                return RoleOutput(roles=cleaned_roles)
        logger.warning("No valid list found in response. Returning raw reply.")
        return RoleOutput(roles=[reply])
    except Exception as e:
        logger.warning(f"Failed to parse list from model reply. Returning raw string: {reply}")
        return RoleOutput(roles=[reply])
