from pydantic import BaseModel, Field


class MatchAnalysis(BaseModel):

    match_score: int = Field(
        ge=0,
        le=100
    )

    strong_matches: list[str] = Field(
        min_length=1
    )

    missing_skills: list[str]

    partial_matches: list[str]

    interview_topics: list[str] = Field(
        min_length=5,
        max_length=5
    )

    learning_priorities: list[str] = Field(
        min_length=3,
        max_length=3
    )

    final_assessment: str = Field(
        min_length=80
    )