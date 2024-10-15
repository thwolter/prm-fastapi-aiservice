from app.services.risk_definition_check import RiskDefinitionService


def get_risk_definition_service() -> RiskDefinitionService:
    return RiskDefinitionService()
