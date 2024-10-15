from app.service import RiskDefinitionService, RiskDefinitionCheck


def test_service_initialization():
    service = RiskDefinitionService()
    assert service.model is not None
    assert service.prompt is not None
    assert service.parser is not None


def test_assess_test_live():
    service = RiskDefinitionService()
    text = 'The project might face delays due to unforeseen circumstances.'
    result: RiskDefinitionCheck = service.assess_definition(text)
    assert result.is_valid is True
    assert result.classification == "Risk"
    assert result.original == text
