from abc import ABC
from langchain import hub
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config import settings


class BaseAIService(ABC):
    model_name: str = "gpt-4"
    prompt_name: str
    QueryModel = BaseModel
    ResultModel = BaseModel

    def __init__(self) -> None:
        self.model = ChatOpenAI(model=self.model_name, api_key=settings.OPENAI_API_KEY)
        self.parser = PydanticOutputParser(pydantic_object=self.ResultModel)
        self.prompt = self.create_prompt()

    def create_prompt(self) -> PromptTemplate:
        template = hub.pull(self.get_prompt_name()).template
        return PromptTemplate.from_template(
            template,
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )

    def get_prompt_name(self) -> str:
        if not self.prompt_name:
            raise ValueError("Prompt name must be set")
        return self.prompt_name

    def execute_query(self, query: QueryModel) -> ResultModel:
        chain = self.prompt | self.model | self.parser
        return chain.invoke(query.model_dump())
