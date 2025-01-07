import hashlib
import json
from abc import ABC

from langchain import hub
from langchain_community.callbacks import get_openai_callback
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.core.config import settings
from app.utils.cache import redis_cache


class BaseAIService(ABC):
    model_name: str = settings.OPENAI_MODEL_NAME
    temperature: float = settings.OPENAI_TEMPERATURE

    prompt_name: str
    QueryModel = BaseModel
    ResultModel = BaseModel

    def __init__(self) -> None:
        self.model = ChatOpenAI(
            model=self.model_name, api_key=settings.OPENAI_API_KEY, temperature=self.temperature
        )
        self.parser = PydanticOutputParser(pydantic_object=self.ResultModel)

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
        return f'{self.__class__.__name__}:{hashlib.md5(key_str.encode()).hexdigest()}'

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

    @redis_cache()
    async def execute_query(self, query: QueryModel) -> ResultModel:
        prompt = self.create_prompt(query)
        chain = prompt | self.model | self.parser
        with get_openai_callback() as cb:
            result = chain.invoke(query.model_dump())
            result.tokens_info = {
                'consumed_tokens': cb.total_tokens,
                'total_cost': cb.total_cost,
                'prompt_name': self.prompt_name,
                'model_name': self.model_name,
            }
        return result


class AIService(BaseAIService):
    prompt_name: str
    QueryModel: type
    ResultModel: type

    def get_prompt_name(self, query: BaseModel = None) -> str:
        """Returns the prompt name, can be overridden by subclasses for custom behavior."""
        return self.prompt_name



class BaseLLMService(ABC):

    def __init__(self) -> None:
        self.model_name = settings.OPENAI_MODEL_NAME
        self.temperature = settings.OPENAI_TEMPERATURE

        self.llm = ChatOpenAI(
            model=self.model_name,
            api_key=settings.OPENAI_API_KEY,
            temperature=self.temperature
        )

    def model_hash(self):
        raise NotImplementedError


    def generate_cache_key(self, prompt_name, *args, **kwargs) -> str:
        """Generate a consistent cache key based on query content and service parameters."""
        key_components = {
            'llm_name': self.model_name,
            'llm_temperature': self.temperature,
            'model_hash': self.model_hash(),
        }

        # Create a consistent string representation
        key_str = json.dumps(key_components, sort_keys=True)
        key_json = key_str.encode('utf-8')
        return f'{prompt_name}:{hashlib.md5(key_json).hexdigest()}'

    def create_prompt(self, prompt_name, parser) -> ChatPromptTemplate:
        template = hub.pull(prompt_name).template
        format_instructions = parser.get_format_instructions()
        format_instructions = format_instructions.replace('{', '{{').replace('}', '}}')
        template += '\nPlease output the result as a JSON object that conforms to the schema above and do not include any additional text.'

        return ChatPromptTemplate.from_template(
            template=template,
            partial_variables={'format_instructions': format_instructions},
        )

    @redis_cache()
    async def execute_query(self, prompt_name, model, parser):
        prompt = self.create_prompt(prompt_name, parser)
        chain = prompt | self.llm | parser
        with get_openai_callback() as cb:
            result = chain.invoke(model.model_dump())
            result.tokens_info = {
                'consumed_tokens': cb.total_tokens,
                'total_cost': cb.total_cost,
                'prompt_name': prompt_name,
                'model_name': self.model_name,
            }
        return result
