import hashlib
import json
import logging
from abc import ABC

from langchain import hub
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.core.config import settings
from core.redis import initialize_redis


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
        self.redis = initialize_redis()


    def generate_cache_key(self, query: QueryModel, *args, **kwargs) -> str:
        """Generate a consistent cache key based on query content and service parameters."""
        key_components = {
            'model_name': self.model_name,
            'prompt_name': self.get_prompt_name(query),
            'temperature': self.temperature,
            'query': query.model_dump(),
        }

        # Create a consistent string representation
        key_str = json.dumps(key_components, sort_keys=True)
        return f"{self.__class__.__name__}:{hashlib.sha256(key_str.encode()).hexdigest()}"

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

    async def execute_query(self, query: QueryModel) -> ResultModel:
        try:
            cache_key = self.generate_cache_key(query)
            cached_result = self.redis.get(cache_key)
            if cached_result:
                logging.info(f"Cache hit for key: {cache_key}")
                return self.ResultModel.parse_raw(cached_result)

            prompt = self.create_prompt(query)
            chain = prompt | self.model | self.parser
            result = chain.invoke(query.model_dump())
            self.redis.set(cache_key, result.json(), ex=settings.CACHE_TIMEOUT)
            logging.info(f"Cache miss, key stored: {cache_key}")
            return result

        except Exception as e:
            logging.error(f"Error executing query: {str(e)}")
            raise e

class BaseAIServiceWithPrompt(BaseAIService):
    prompt_name: str
    QueryModel: type
    ResultModel: type

    def get_prompt_name(self, query: BaseModel = None) -> str:
        """ Returns the prompt name, can be overridden by subclasses for custom behavior. """
        return self.prompt_name
