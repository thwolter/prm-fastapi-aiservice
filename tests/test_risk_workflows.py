from unittest.mock import patch
from fastapi.testclient import TestClient

from riskgpt.models import schemas as rg_schemas
from src.main import app

client = TestClient(app)


@patch("src.services.services.ContextQualityService.execute_query")
def test_context_quality_endpoint(mock_execute):
    mock_execute.return_value = rg_schemas.ContextQualityResponse(
        shortcomings=["too short"],
        rationale="r",
        suggested_improvements="i",
        response_info=None,
    )
    payload = {"business_context": {"project_id": "p"}}
    response = client.post("/api/context/check/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["shortcomings"] == ["too short"]


@patch("src.services.services.ExternalContextService.execute_query")
def test_external_context_endpoint(mock_execute):
    mock_execute.return_value = rg_schemas.ExternalContextResponse(
        sector_summary="sum",
        external_risks=["r1"],
        source_table=[{"title": "t", "url": "u"}],
        workshop_recommendations=["rec"],
        full_report=None,
        response_info=None,
    )
    payload = {"business_context": {"project_id": "p"}}
    response = client.post("/api/context/external/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sector_summary"] == "sum"


@patch("src.services.services.PresentationWorkflowService.execute_query")
def test_presentation_workflow_endpoint(mock_execute):
    mock_execute.return_value = rg_schemas.PresentationResponse(
        executive_summary="exec", main_risks=["r"], response_info=None
    )
    payload = {
        "business_context": {"project_id": "p"},
        "audience": "executive",
    }
    response = client.post("/api/presentation/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["executive_summary"] == "exec"


@patch("src.services.services.RiskWorkflowService.execute_query")
def test_risk_workflow_endpoint(mock_execute):
    mock_execute.return_value = rg_schemas.RiskResponse(
        risks=[rg_schemas.Risk(title="t", description="d", category="c")],
        references=None,
        response_info=None,
    )
    payload = {"business_context": {"project_id": "p"}, "category": "c"}
    response = client.post("/api/risk/workflow/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["risks"]) == 1

