from abc import ABC

from langchain import hub
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.core.config import settings


class BaseAIService(ABC):
    model_name: str = 'gpt-4'
    prompt_name: str
    QueryModel = BaseModel
    ResultModel = BaseModel

    def __init__(self) -> None:
        self.model = ChatOpenAI(model=self.model_name, api_key=settings.OPENAI_API_KEY)
        self.parser = PydanticOutputParser(pydantic_object=self.ResultModel)

    def create_prompt(self, query: QueryModel) -> PromptTemplate:
        template = hub.pull(self.get_prompt_name(query)).template
        return PromptTemplate.from_template(
            template,
            partial_variables={'format_instructions': self.parser.get_format_instructions()},
        )

    def get_prompt_name(self, query: QueryModel) -> str:
        return self.prompt_name

    def execute_query(self, query: QueryModel) -> ResultModel:
        prompt = self.create_prompt(query)
        chain = prompt | self.model | self.parser
        return chain.invoke(query.model_dump())
