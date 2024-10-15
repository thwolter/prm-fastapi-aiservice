from app.services.services import RiskDefinitionService


def get_risk_definition_service() -> RiskDefinitionService:
    return RiskDefinitionService()
