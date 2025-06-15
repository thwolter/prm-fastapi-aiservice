from unittest.mock import patch

import pytest
from riskgpt.models import schemas as rg_schemas
from riskgpt.models.schemas import default_response_info


@patch("src.services.services.RiskDefinitionCheckService.execute_query")
def test_risk_definition_check_valid_input(mock_execute_query, test_client):
    request_data = {
        "business_context": {
            "project_id": "test-project",
            "project_description": "Test project description",
        },
        "risk_description": "The project might face delays due to unforeseen circumstances.",
    }
    mock_execute_query.return_value = rg_schemas.DefinitionCheckResponse(
        revised_description="The project might face delays due to unforeseen circumstances.",
        biases=["None detected"],
        rationale="This is a valid risk statement that identifies a potential negative event.",
        response_info=default_response_info(),
    )
    response = test_client.post("/api/risk/check/definition/", json=request_data)
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert isinstance(
        rg_schemas.DefinitionCheckResponse(**response_data), rg_schemas.DefinitionCheckResponse
    )
    assert (
        response_data["revised_description"]
        == "The project might face delays due to unforeseen circumstances."
    )
    assert response_data["biases"] == ["None detected"]
    assert (
        response_data["rationale"]
        == "This is a valid risk statement that identifies a potential negative event."
    )


@patch("src.services.services.RiskDefinitionCheckService.execute_query")
def test_risk_definition_check_with_mock(mock_execute_query, test_client):
    """Test risk definition check with mocked service response."""
    # Mock the service response
    mock_execute_query.return_value = rg_schemas.DefinitionCheckResponse(
        revised_description="The project might face delays due to unforeseen circumstances.",
        biases=["None detected"],
        rationale="This is a valid risk statement that identifies a potential negative event.",
        response_info=default_response_info(),
    )

    request_data = {
        "business_context": {
            "project_id": "test-project",
            "project_description": "Test project description",
        },
        "risk_description": "The project might face delays due to unforeseen circumstances.",
    }
    response = test_client.post("/api/risk/check/definition/", json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(
        rg_schemas.DefinitionCheckResponse(**response_data), rg_schemas.DefinitionCheckResponse
    )
    assert (
        response_data["revised_description"]
        == "The project might face delays due to unforeseen circumstances."
    )
    assert response_data["biases"] == ["None detected"]
    assert (
        response_data["rationale"]
        == "This is a valid risk statement that identifies a potential negative event."
    )


@patch("src.services.services.RiskDefinitionCheckService.execute_query")
def test_risk_definition_check_missing_text(mock_execute_query, test_client):
    request_data: dict[str, str] = {}
    response = test_client.post("/api/risk/check/definition/", json=request_data)
    assert response.status_code == 422


@patch("src.services.services.RiskDefinitionCheckService.execute_query")
def test_risk_definition_check_empty_text(mock_execute_query, test_client):
    request_data: dict[str, str] = {"text": ""}
    response = test_client.post("/api/risk/check/definition/", json=request_data)
    assert response.status_code == 422


@patch("src.services.services.RiskDefinitionCheckService.execute_query")
def test_risk_definition_check_invalid_text_type(mock_execute_query, test_client):
    request_data = {"text": 12345}
    response = test_client.post("/api/risk/check/definition/", json=request_data)
    assert response.status_code == 422


@pytest.fixture(scope="function")
def risk_identification_request_data():
    return rg_schemas.RiskRequest(
        business_context=rg_schemas.BusinessContext(
            project_id="dinner-project",
            project_description="Going out for dinner with friends at a local restaurant.",
            domain_knowledge="Challenges in securing a reservation at the desired restaurant. Examples include fully booked restaurants and limited seating capacity.",
        ),
        category="Operational",
    ).model_dump()


@patch("src.services.services.RiskIdentificationService.execute_query")
def test_risk_identification_valid_input(
    mock_execute_query, test_client, risk_identification_request_data
):
    mock_execute_query.return_value = rg_schemas.RiskResponse(
        risks=[
            rg_schemas.Risk(
                title="Identified Risk 1",
                description="Description of Identified Risk 1",
                category="Operational",
            ),
            rg_schemas.Risk(
                title="Identified Risk 2",
                description="Description of Identified Risk 2",
                category="Operational",
            ),
        ],
        references=None,
        response_info=default_response_info(),
    )
    response = test_client.post("/api/risk/identify/", json=risk_identification_request_data)
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert isinstance(rg_schemas.RiskResponse(**response_data), rg_schemas.RiskResponse)
    assert len(response_data["risks"]) == 2
    assert response_data["risks"][0]["title"] == "Identified Risk 1"


@patch("src.services.services.RiskIdentificationService.execute_query")
def test_risk_identification_missing_category(mock_execute_query, test_client):
    request_data = {
        "business_context": {
            "project_id": "test-project",
            "project_description": "Test project description",
        },
        "existing_risks": [{"title": "Risk 1", "description": "Description of Risk 1"}],
    }
    response = test_client.post("/api/risk/identify/", json=request_data)
    assert response.status_code == 422


@patch("src.services.services.RiskIdentificationService.execute_query")
def test_risk_identification_empty_existing(
    mock_execute_query, test_client, risk_identification_request_data
):
    mock_execute_query.return_value = rg_schemas.RiskResponse(
        risks=[
            rg_schemas.Risk(
                title="Identified Risk 1",
                description="Description of Identified Risk 1",
                category="Operational",
            ),
            rg_schemas.Risk(
                title="Identified Risk 2",
                description="Description of Identified Risk 2",
                category="Operational",
            ),
        ],
        references=None,
        response_info=default_response_info(),
    )
    request_data = risk_identification_request_data
    request_data["existing_risks"] = []
    response = test_client.post("/api/risk/identify/", json=request_data)
    assert response.status_code == 200
    mock_execute_query.assert_called_once()
    response_data = response.json()
    assert isinstance(rg_schemas.RiskResponse(**response_data), rg_schemas.RiskResponse)


@patch("src.services.services.RiskIdentificationService.execute_query")
def test_risk_identification_invalid_existing_type(mock_execute_query, test_client):
    request_data = {
        "business_context": {
            "project_id": "test-project",
            "project_description": "Test project description",
        },
        "category": "Operational",
        "existing_risks": "invalid_type",
    }
    response = test_client.post("/api/risk/identify/", json=request_data)
    assert response.status_code == 422
