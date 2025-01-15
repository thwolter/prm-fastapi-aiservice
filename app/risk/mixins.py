from pydantic import computed_field

class RiskParserMixin:

    @computed_field
    @property
    def parsed_risk(self) -> str:
        if hasattr(self, 'risk'):
            return f'{self.risk.title}: {self.risk.description}'

    @computed_field
    @property
    def parsed_risks(self) -> str:
        if hasattr(self, 'risks'):
            return '\n'.join([f'{risk.title}: {risk.description}' for risk in self.risks])


class ScoreParserMixin:

    @computed_field
    @property
    def parsed_scores(self) -> str:
        if hasattr(self, 'scores'):
            return ', '.join([f'{score.score}: {score.description}' for score in self.scores])