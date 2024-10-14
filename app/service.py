import os

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


class RiskDefinitionService:

    def __init__(self, model_name: str = "gpt-4o") -> None:
        self.model = ChatOpenAI(model=model_name)
        self.parser = PydanticOutputParser(pydantic_object=RiskDefinitionCheck)
        self.prompt = self.create_prompt()

    def create_prompt(self) -> PromptTemplate:
        template = hub.pull("risk-definition-check").template
        return PromptTemplate.from_template(
            template,
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )

    def assess_definition(self, text: str) -> RiskDefinitionCheck:
        chain = self.prompt | self.model | self.parser
        return chain.invoke({'text': text})
