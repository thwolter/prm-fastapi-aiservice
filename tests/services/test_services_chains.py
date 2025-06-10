import pytest
from unittest.mock import AsyncMock

from src.services import services
from riskgpt.models import schemas as rg_schemas

EXAMPLES = {
    rg_schemas.DefinitionCheckRequest: rg_schemas.DefinitionCheckRequest.model_json_schema()[
        "example"
    ],
    rg_schemas.RiskRequest: rg_schemas.RiskRequest.model_json_schema()["example"],
    rg_schemas.DriverRequest: rg_schemas.DriverRequest.model_json_schema()["example"],
    rg_schemas.AssessmentRequest: rg_schemas.AssessmentRequest.model_json_schema()["example"],
    rg_schemas.CategoryRequest: rg_schemas.CategoryRequest.model_json_schema()["example"],
    rg_schemas.MitigationRequest: {
        "business_context": {
            "project_id": "demo",
            "project_description": "demo",
            "language": "en",
        },
        "risk_description": "demo",
        "drivers": [],
    },
}

RESPONSE_EXAMPLES = {
    rg_schemas.DefinitionCheckResponse: rg_schemas.DefinitionCheckResponse.model_json_schema()[
        "example"
    ],
    rg_schemas.RiskResponse: rg_schemas.RiskResponse.model_json_schema()["example"],
    rg_schemas.DriverResponse: rg_schemas.DriverResponse.model_json_schema()["example"],
    rg_schemas.AssessmentResponse: rg_schemas.AssessmentResponse.model_json_schema()["example"],
    rg_schemas.CategoryResponse: rg_schemas.CategoryResponse.model_json_schema()["example"],
    rg_schemas.MitigationResponse: {
        "mitigations": [],
        "references": [],
        "response_info": None,
    },
}

SERVICE_PARAMS = [
    (services.RiskDefinitionCheckService, "riskgpt.chains.async_check_definition_chain"),
    (services.RiskIdentificationService, "riskgpt.chains.async_get_risks_chain"),
    (services.RiskDriverService, "riskgpt.chains.async_get_drivers_chain"),
    (services.RiskAssessmentService, "riskgpt.chains.async_get_assessment_chain"),
    (services.RiskMitigationService, "riskgpt.chains.async_get_mitigations_chain"),
    (services.CreateCategoriesService, "riskgpt.chains.async_get_categories_chain"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("service_cls,chain_path", SERVICE_PARAMS)
async def test_service_executes_chain(monkeypatch, service_cls, chain_path):
    example = RESPONSE_EXAMPLES[service_cls.ResultModel]
    mock_chain = AsyncMock(return_value=service_cls.ResultModel.model_validate(example))
    svc = service_cls()
    monkeypatch.setattr(svc, "chain_fn", mock_chain)
    query = service_cls.QueryModel.model_validate(EXAMPLES[service_cls.QueryModel])
    result = await svc.execute_query(query)
    mock_chain.assert_awaited_once_with(query)
    assert isinstance(result, service_cls.ResultModel)


@pytest.mark.asyncio
@pytest.mark.parametrize("service_cls,chain_path", SERVICE_PARAMS)
async def test_service_fallback(monkeypatch, service_cls, chain_path):
    mock_chain = AsyncMock(side_effect=Exception("boom"))
    svc = service_cls()
    monkeypatch.setattr(svc, "chain_fn", mock_chain)
    query = service_cls.QueryModel.model_validate(EXAMPLES[service_cls.QueryModel])
    result = await svc.execute_query(query)
    mock_chain.assert_awaited_once_with(query)
    assert isinstance(result, service_cls.ResultModel)
    assert (
        result.response_info.error == f"Service {service_cls.__name__} is temporarily unavailable"
    )
