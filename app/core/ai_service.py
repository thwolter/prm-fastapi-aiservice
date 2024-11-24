import hashlib
import json
from abc import ABC
from diskcache import Cache

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
        self.model = ChatOpenAI(
            model=self.model_name, api_key=settings.OPENAI_API_KEY, temperature=self.temperature
        )
        self.parser = PydanticOutputParser(pydantic_object=self.ResultModel)
        self.cache = Cache(directory='.cache')

    def create_prompt(self, query: QueryModel) -> ChatPromptTemplate:
        template = hub.pull(self.get_prompt_name(query)).template
        format_instructions = self.parser.get_format_instructions()
        format_instructions = format_instructions.replace('{', '{{').replace('}', '}}')
        template += '\nPlease output the result as a JSON object that conforms to the schema above and do not include any additional text.'

        return ChatPromptTemplate.from_template(
            template=template,
            partial_variables={'format_instructions': format_instructions},
        )

    def get_prompt_name(self, query: QueryModel) -> str:
        return self.prompt_name

    @staticmethod
    def _cache_key(query: QueryModel) -> str:
        """Generate a unique cache key based on the query."""
        query_data = query.model_dump()
        return hashlib.md5(json.dumps(query_data, sort_keys=True).encode('utf-8')).hexdigest()

    def execute_query(self, query: QueryModel) -> ResultModel:
        cache_key = self._cache_key(query)

        if cache_key in self.cache:
            print(f"[Cache] Returning cached result for query: {cache_key}")
            return self.cache[cache_key]

        prompt = self.create_prompt(query)
        chain = prompt | self.model | self.parser
        result = chain.invoke(query.model_dump())

        self.cache[cache_key] = result
        print(f"[Cache] Storing result in cache for query: {cache_key}")
        return result


class BaseAIServiceWithPrompt(BaseAIService):
    prompt_name: str
    QueryModel: type
    ResultModel: type

    def get_prompt_name(self, query: BaseModel = None) -> str:
        """ Returns the prompt name, can be overridden by subclasses for custom behavior. """
        return self.prompt_name
