import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain.output_parsers import OutputParser


def read_text_file(file_name: str) -> str:
    file_path = os.path.join(os.path.dirname(__file__), 'prompts', file_name)
    with open(file_path, 'r') as file:
        text = file.read()
    return text


class RiskAssessmentService:
    txt_definitions = 'definitions.txt'
    risk_prompt = 'risk_prompt.txt'

    def __init__(self, model_name="gpt-4"):
        self.model = ChatOpenAI(model=model_name)
        self.prompt_template = self.create_prompt()
        self.output_parser = OutputParser()

    def create_prompt(self):
        template = read_text_file(self.risk_prompt)
        return PromptTemplate(
            template=template,
            input_variables=["text", "definitions"]
        )

    def assess_text(self, text: str, definitions: str) -> dict:
        prompt = self.prompt_template.render(text=text, definitions=definitions)
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=text),
        ]
        response = self.model.invoke(messages)
        return self.parse_response(response)

    def parse_response(self, response: str) -> dict:
        parsed_output = self.output_parser.parse(response)
        return {
            "is_risk": parsed_output.get("is_risk", False),
            "category": parsed_output.get("category", "unknown"),
            "original": parsed_output.get("original", ""),
            "modified": parsed_output.get("modified", "")
        }

# Example usage:
# service = RiskAssessmentService()
# result = service.assess_text("The project might face delays due to unforeseen circumstances.")
# print(result)