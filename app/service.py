from app.config import settings
from langchain import hub
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class RiskDefinitionCheck(BaseModel):
    is_valid: bool = Field(..., description="Whether the text is valid or not.")
    classification: str = Field(..., description="The classification of the text.")
    original: str = Field(..., description="The original text.")
    suggestion: str = Field(..., description="Suggestions for a revised risk definition.")
    explanation: str = Field(..., description="Explanation of the classification.")


class BaseService:
    model_name: str = "gpt-4"
    prompt_name: str

    def __init__(self, *args, **kwargs) -> None:
        self.model = ChatOpenAI(model=self.model_name, openai_api_key=settings.OPENAI_API_KEY)
        self.parser = PydanticOutputParser(pydantic_object=RiskDefinitionCheck)
        self.prompt = self.create_prompt()

    def create_prompt(self) -> PromptTemplate:
        template = hub.pull(self.get_prompt_name()).template
        return PromptTemplate.from_template(
            template,
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )

    def get_prompt_name(self) -> str:
        if not self.prompt_name:
            raise NotImplementedError("Prompt name not set")
        return self.prompt_name


class RiskDefinitionService(BaseService):
    prompt_name = "risk-definition-check"

    def assess_definition(self, text: str) -> RiskDefinitionCheck:
        chain = self.prompt | self.model | self.parser
        return chain.invoke({'text': text})
