from datetime import datetime

from pydantic import BaseModel, Field

today = datetime.now().strftime('%Y-%m-%d')


class BaseProjectRequest(BaseModel):
    name: str = Field(..., description='The name of the project.')
    context: str = Field(..., description='The project context to be checked.')


class CheckProjectContextResponse(BaseModel):
    is_valid: bool = Field(..., description='Whether the project context is valid or not.')
    suggestion: str = Field(..., description='Suggestions for a revised project context.')
    explanation: str = Field(..., description='Explanation of the classification.')
    missing: list[str] = Field(
        ..., description='The list of missing elements in the project context.'
    )
    context_example: str = Field(..., description='An example of a valid project context.')
    language: str = Field(
        ...,
        description='The language of the project context as two-letter ISO 639-1 language code.',
    )
    capabilities: list[str] = Field(
        ..., description='The list of capabilities required for the project.'
    )
    challenges: list[str] = Field(..., description='The list of challenges faced by the project.')
    budget: str = Field(..., description='The budget of the project as number.')
    currency: str = Field(..., description='The currency of the project budget.')
    timeline: str = Field(..., description='The timeline of the project.')
    deadline: str = Field(
        ..., description=f"The deadline of the project based on today's date being {today}."
    )


class ProjectSummaryResponse(BaseModel):
    summary: str = Field(..., description='A summary of the project.')
    image_url: str = Field(..., description='URL for the project picture.')
    tags: list[str] = Field(..., description='Tags associated with the project.')
