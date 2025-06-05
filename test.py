# for testing parser.py

# from parsers.parser_selector import extract_text

# def test_regular_resume():
#     file_path = "data/resume_regular.pdf"
#     text = extract_text(file_path, mode="regular")
#     print("\n--- Regular Resume Text ---\n")
#     print(text[:1000])  # preview first 1000 characters

# def test_scanned_resume():
#     file_path = "data/resume_scanned.pdf"
#     text = extract_text(file_path, mode="scanned")
#     print("\n--- Scanned Resume Text ---\n")
#     print(text[:1000])  # preview first 1000 characters

# if __name__ == "__main__":
#     print("Testing regular resume parsing...")
#     test_regular_resume()

#     print("\nTesting scanned resume parsing...")
#     test_scanned_resume()

# =========================================================
#                  For testing inference
# =========================================================

# from llm.inferencer import infer_job_roles, ResumeInput
# from parsers.parser_selector import extract_text

# def test_role_inference():
#     file_path = "data/resume_regular.pdf"
#     resume_text = extract_text(file_path, mode="regular")

#     input_data = ResumeInput(resume_text=resume_text, top_k=5)
#     result = infer_job_roles(input_data)

#     print("\n--- Inferred Job Roles ---\n")
#     for i, role in enumerate(result.roles, 1):
#         print(f"{i}. {role}")

# if __name__ == "__main__":
#     test_role_inference()


# ================================================
#               Job_search
# ================================================
from duckduckgo_search import DDGS

results = DDGS().text("python programming", max_results=5)
print(results)

