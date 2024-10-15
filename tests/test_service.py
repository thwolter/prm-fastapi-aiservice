from app.models import (Risk, RiskDefinitionCheckQuery,
                        RiskDefinitionCheckResult, RiskIdentificationQuery,
                        RiskIdentificationResult)
from app.services.services import (RiskDefinitionService,
                                   RiskIdentificationService)


def test_service_initialization():
    service = RiskDefinitionService()
    assert service.model is not None, "Model should be initialized"
    assert service.parser is not None


def test_risk_definition_check():
    service = RiskDefinitionService()
    query = RiskDefinitionCheckQuery(text='The project might face delays due to unforeseen circumstances.')
    result = service.execute_query(query)
    assert isinstance(result, RiskDefinitionCheckResult)
    assert result.is_valid is True
    assert result.classification == "Risk"
    assert result.original == 'The project might face delays due to unforeseen circumstances.'


def test_identify_risks():
    service = RiskIdentificationService()
    query = RiskIdentificationQuery(
        category='Project',
        subcategory='Delays',
        context='A UGS operator is planning to build a new H2 cavern for the first time.'
    )
    result = service.execute_query(query)
    assert isinstance(result, RiskIdentificationResult)
    assert result.risks is not None
    assert len(result.risks) > 0
    assert all(isinstance(risk, Risk) for risk in result.risks)
    assert all(risk.title is not None for risk in result.risks)
    assert all(risk.description is not None for risk in result.risks)