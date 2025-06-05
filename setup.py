from setuptools import setup, find_packages

setup(
    name="job_resume_matcher",
    version="0.1.0",
    description="AI-powered job role inference based on resume text using Gemini API.",
    author="Hussnain Tariq",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "google-generativeai>=0.3.2"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
    python_requires=">=3.10",
)
