from abc import ABC

from langchain import hub
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.core.config import settings


class BaseAIService(ABC):
    model_name: str = 'gpt-4o-mini'
    prompt_name: str
    QueryModel = BaseModel
    temperature: float = 0.7
    ResultModel = BaseModel

    def __init__(self) -> None:
        self.model = ChatOpenAI(model=self.model_name, api_key=settings.OPENAI_API_KEY, temperature=self.temperature)
        self.parser = PydanticOutputParser(pydantic_object=self.ResultModel)

    def create_prompt(self, query: QueryModel) -> ChatPromptTemplate:
        template = hub.pull(self.get_prompt_name(query)).template
        format_instructions = self.parser.get_format_instructions()
        format_instructions = format_instructions.replace('{', '{{').replace('}', '}}')
        template += "\nPlease output the result as a JSON object that conforms to the schema above and do not include any additional text."

        return ChatPromptTemplate.from_template(
            template=template,
            partial_variables={'format_instructions': format_instructions},
        )

    def get_prompt_name(self, query: QueryModel) -> str:
        return self.prompt_name

    def execute_query(self, query: QueryModel) -> ResultModel:
        prompt = self.create_prompt(query)
        chain = prompt | self.model | self.parser
        return chain.invoke(query.model_dump())
