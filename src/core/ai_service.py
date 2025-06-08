"""Generic service wrapper around RiskGPT chains."""

import hashlib
import json
import logging
from abc import ABC

from langchain import hub
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from riskgpt.chains.base import BaseChain
from src.core.config import riskgpt_settings
from src.utils.cache import redis_cache

logger = logging.getLogger(__name__)

class BaseAIService(ABC):
    model_name: str = riskgpt_settings.MODEL_NAME or ""
    temperature: float = riskgpt_settings.TEMPERATURE or 0.0

    prompt_name: str
    QueryModel = BaseModel
    ResultModel = BaseModel

    def __init__(self) -> None:
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

    def create_chain(self, query: QueryModel) -> BaseChain:
        template = hub.pull(self.get_prompt_name(query)).template
        format_instructions = self.parser.get_format_instructions()
        format_instructions = format_instructions.replace('{', '{{').replace('}', '}}')
        if hasattr(query, 'language_instructions'):
            language_instructions = query.language_instructions
            template += '\n\n' + language_instructions
        template += '\nPlease output the result as a JSON object that conforms to the schema above and do not include any additional text.'

        prompt = ChatPromptTemplate.from_template(
            template=template,
            partial_variables={'format_instructions': format_instructions},
        )

        return BaseChain(
            prompt_template=prompt.template,
            parser=self.parser,
            settings=riskgpt_settings,
            prompt_name=self.get_prompt_name(query),
        )

    def get_prompt_name(self, query: QueryModel) -> str:
        return self.prompt_name

    @redis_cache()
    async def execute_query(self, query: QueryModel) -> ResultModel:
        chain = self.create_chain(query)
        result = await chain.invoke_async(query.model_dump())
        if hasattr(result, "response_info") and result.response_info:
            ri = result.response_info
            result.tokens_info = {
                "prompt_tokens": ri.consumed_tokens,
                "completion_tokens": 0,
                "total_tokens": ri.consumed_tokens,
                "total_cost": ri.total_cost,
                "prompt_name": ri.prompt_name,
                "model_name": ri.model_name,
            }
        return result


class AIService(BaseAIService):
    prompt_name: str
    QueryModel: type
    ResultModel: type

    def get_prompt_name(self, query: BaseModel = None) -> str:
        """Returns the prompt name, can be overridden by subclasses for custom behavior."""
        return self.prompt_name


