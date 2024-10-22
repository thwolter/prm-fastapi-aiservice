from unittest.mock import patch

from app.models import (Risk, RiskDefinitionCheckQuery,
                        RiskDefinitionCheckResult, RiskIdentificationQuery,
                        RiskIdentificationResult, CategoriesIdentificationQuery, CategoriesIdentificationResult,
                        Category, CategoriesIdentificationRequest)
from app.services.services import (RiskDefinitionService,
                                   RiskIdentificationService, CategoryIdentificationService)


def test_service_initialization():
    service = RiskDefinitionService()
    assert service.model is not None, "Model should be initialized"
    assert service.parser is not None


@patch('app.services.base_service.BaseAIService.execute_query')
def test_risk_definition_check(mock_execute_query):
    service = RiskDefinitionService()
    query = RiskDefinitionCheckQuery(text='The project might face delays due to unforeseen circumstances.')
    expected_result = RiskDefinitionCheckResult(
        is_valid=True,
        classification="Risk",
        original=query.text,
        suggestion="Consider adding buffer time to the project schedule.",
        explanation="Delays can occur due to unforeseen circumstances, and having a buffer can mitigate this risk."
    )
    mock_execute_query.return_value = expected_result
    result = service.execute_query(query)
    assert isinstance(result, RiskDefinitionCheckResult)
    assert result.is_valid is True
    assert result.classification == "Risk"
    assert result.original == 'The project might face delays due to unforeseen circumstances.'
    assert result.suggestion == "Consider adding buffer time to the project schedule."
    assert result.explanation == "Delays can occur due to unforeseen circumstances, and having a buffer can mitigate this risk."
    mock_execute_query.assert_called_once_with(query)


@patch('app.services.base_service.BaseAIService.execute_query')
def test_identify_risks(mock_execute_query):
    service = RiskIdentificationService()
    query = RiskIdentificationQuery(
        category='Project',
        subcategory='Delays',
        context='A UGS operator is planning to build a new H2 cavern for the first time.'
    )
    expected_risks = [Risk(title="Risk 1", description="Description 1"),
                      Risk(title="Risk 2", description="Description 2")]
    expected_result = RiskIdentificationResult(risks=expected_risks)
    mock_execute_query.return_value = expected_result
    result = service.execute_query(query)
    assert isinstance(result, RiskIdentificationResult)
    assert result.risks is not None
    assert len(result.risks) > 0
    assert all(isinstance(risk, Risk) for risk in result.risks)
    assert all(risk.title is not None for risk in result.risks)
    assert all(risk.description is not None for risk in result.risks)
    mock_execute_query.assert_called_once_with(query)


@patch('app.services.base_service.BaseAIService.execute_query')
def test_category_identification(mock_execute_query):
    service = CategoryIdentificationService()
    query = CategoriesIdentificationRequest(text='The project involves building a new infrastructure.')
    expected_result = CategoriesIdentificationResult(
        categories=[Category(
            name="Infrastructure",
            description="The text indicates a project related to building new infrastructure.",
            examples=[]
        )]
    )
    mock_execute_query.return_value = expected_result
    result = service.execute_query(query)
    assert isinstance(result, CategoriesIdentificationResult)
    assert result.categories[0].name == "Infrastructure"
    assert result.categories[0].description == "The text indicates a project related to building new infrastructure."
    assert result.categories[0].examples == []
    mock_execute_query.assert_called_once_with(query)