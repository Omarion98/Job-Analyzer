from pydantic import BaseModel
import logging

from telemetry import (
    setup_telemetry,
    get_tracer,
)

# Configure telemetry before importing FastAPI so automatic
# FastAPI instrumentation can be registered correctly.
setup_telemetry()

from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from cv_extractor import extract_cv_text
from llm_provider import (
    generate_with_llm,
    LLMProviderError,
)
from models import MatchAnalysis


logger = logging.getLogger("uvicorn.error")
tracer = get_tracer("api")

app = FastAPI(
    title="AI Job Description Analyzer"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://career-copilot-frontend.kindsand-10a068b0.germanywestcentral.azurecontainerapps.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JobRequest(BaseModel):
    job_description: str


@app.get("/")
def home():
    return {
        "message": "AI Job Analyzer API is running"
    }


@app.post("/api/analyze")
async def analyze_job(request: JobRequest):

    if not request.job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description is empty"
        )

    with tracer.start_as_current_span(
        "analyze.prompt.build"
    ) as span:
        span.set_attribute(
            "job_description.characters",
            len(request.job_description),
        )

        prompt = f"""
You are an AI career assistant.

Analyze the following job description.

Return the answer using these sections:

1. Required Technical Skills
2. Main Responsibilities
3. Important AI/Cloud Technologies
4. Likely Interview Topics
5. What I Should Learn First

Keep the answer practical and concise.

JOB DESCRIPTION:

{request.job_description}
"""

    try:
        generated_text = await generate_with_llm(
            prompt
        )

        return {
            "analysis": generated_text
        }

    except LLMProviderError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )


@app.post(
    "/api/match",
    response_model=MatchAnalysis
)
async def match_cv_to_job(
    cv: UploadFile = File(...),
    job_description: str = Form(...)
):

    if not cv.filename:
        raise HTTPException(
            status_code=400,
            detail="No CV uploaded"
        )

    if not cv.filename.lower().endswith(
        ".pdf"
    ):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description is empty"
        )

    with tracer.start_as_current_span(
        "cv.upload.read"
    ) as span:
        file_bytes = await cv.read()

        span.set_attribute(
            "cv.input_bytes",
            len(file_bytes),
        )

    cv_text = extract_cv_text(
        file_bytes
    )

    logger.info(
        "CV extraction completed successfully. "
        "Characters extracted: %d",
        len(cv_text),
    )

    if not cv_text.strip():
        raise HTTPException(
            status_code=400,
            detail=(
                "Could not extract text "
                "from this PDF"
            )
        )

    with tracer.start_as_current_span(
        "match.schema.build"
    ):
        schema = (
            MatchAnalysis.model_json_schema()
        )

    with tracer.start_as_current_span(
        "match.prompt.build"
    ) as span:
        span.set_attribute(
            "cv.extracted_characters",
            len(cv_text),
        )
        span.set_attribute(
            "job_description.characters",
            len(job_description),
        )

        prompt = f"""
    You are a senior AI Engineering recruiter.

    Compare the candidate CV against the job description.

    You MUST analyze each important requirement from the
    job description individually.

    For every important requirement, classify it as ONE of:

    1. STRONG MATCH
    The exact skill or clearly equivalent experience
    appears in the CV.

    2. PARTIAL MATCH
    The candidate has related experience but does not
    fully demonstrate the requested technology,
    experience level, or responsibility.

    3. MISSING SKILL
    The requirement appears in the job description but
    there is no clear evidence of it in the CV.


    IMPORTANT RULES:

    - Never assume skills that are not explicitly shown.
    - Never infer Azure experience from general cloud experience.
    - Never infer Kubernetes from Docker.
    - Never infer RAG from general LLM experience.
    - Never invent professional experience.
    - Do not give a high score based only on keyword overlap.
    - The same skill or concept must appear in only ONE category.
    - Treat equivalent terms as the same skill. Examples:
        RAG = Retrieval-Augmented Generation
        LLM = Large Language Model
        CI/CD = Continuous Integration / Continuous Deployment
    - If a skill is classified as a strong match, do not also include an equivalent version in partial_matches or missing_skills.
    - Avoid duplicate or semantically equivalent entries across all lists.
    The lists strong_matches, partial_matches, and
    missing_skills must reflect your comparison of the
    job requirements.

    INTERVIEW TOPICS:
    Return exactly 5 technical topics relevant to the job.

    LEARNING PRIORITIES:
    Return exactly 3 skills the candidate should improve.

    FINAL ASSESSMENT:
    Write 2-4 complete sentences explaining:
    - overall suitability
    - strongest area
    - biggest weakness
    - what would improve the candidate's chances

    Do NOT return a title such as:
    "Technical Deep Dive"
    "Interview Preparation"
    "Candidate Analysis"

    Return an actual assessment paragraph.


    SCORING INSTRUCTIONS:

    You MUST calculate the score from the job requirements.

    First identify all important requirements in the job description.

    For every requirement classify it as:

    STRONG MATCH = 1 point
    PARTIAL MATCH = 0.5 points
    MISSING = 0 points

    Then calculate:

    match_score =
    (points earned / total possible points) * 100

    Round the result to the nearest whole number.

    The score MUST be based on these classifications.
    Do not choose an approximate score based on overall impression.

    Examples:

    8 strong, 1 partial, 1 missing:
    (8 + 0.5) / 10 = 85%

    3 strong, 2 partial, 5 missing:
    (3 + 1) / 10 = 40%


    Return ONLY JSON matching this schema:

    {schema}


    ================ CV ================

    {cv_text}


    ========== JOB DESCRIPTION ==========

    {job_description}
    """

        span.set_attribute(
            "llm.prompt_characters",
            len(prompt),
        )

    try:
        generated_text = await generate_with_llm(
            prompt,
            schema=schema,
        )

        with tracer.start_as_current_span(
            "response.validation"
        ) as span:
            analysis = (
                MatchAnalysis.model_validate_json(
                    generated_text
                )
            )

            span.set_attribute(
                "match.score",
                analysis.match_score,
            )

        return analysis

    except ValidationError:
        raise HTTPException(
            status_code=500,
            detail=(
                "The AI returned an invalid "
                "analysis format."
            ),
        )

    except LLMProviderError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )
