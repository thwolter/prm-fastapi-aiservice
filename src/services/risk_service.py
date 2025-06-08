"""Services using the riskgpt library."""
from __future__ import annotations

from typing import Type

from pydantic import BaseModel

try:  # pragma: no cover - optional dependency
    from riskgpt import chains
    from riskgpt.models import schemas as rg_schemas
except Exception:  # pragma: no cover - riskgpt not installed
    chains = None

    class rg_schemas:  # type: ignore
        class DefinitionCheckRequest(BaseModel):
            text: str

        class DefinitionCheckResponse(BaseModel):
            is_valid: bool

        class RiskRequest(BaseModel):
            pass

        class RiskResponse(BaseModel):
            risks: list[str] = []

        class DriverRequest(BaseModel):
            pass

        class DriverResponse(BaseModel):
            drivers: list[str] = []

        class AssessmentRequest(BaseModel):
            pass

        class AssessmentResponse(BaseModel):
            assessment: str | None = None

        class MitigationRequest(BaseModel):
            pass

        class MitigationResponse(BaseModel):
            mitigations: list[str] = []


class RiskGPTService:
    """Base service calling RiskGPT chains."""

    chain_fn: callable
    route_path: str
    QueryModel: Type[BaseModel]
    ResultModel: Type[BaseModel]

    async def execute_query(self, query: BaseModel):
        if not self.chain_fn:
            raise RuntimeError('riskgpt is not installed')
        return await self.chain_fn(query)


class RiskDefinitionCheckService(RiskGPTService):
    chain_fn = chains.async_check_definition_chain if chains else None
    route_path = '/risk/check/definition/'
    QueryModel = rg_schemas.DefinitionCheckRequest
    ResultModel = rg_schemas.DefinitionCheckResponse


class RiskIdentificationService(RiskGPTService):
    chain_fn = chains.async_get_risks_chain if chains else None
    route_path = '/risk/identify/'
    QueryModel = rg_schemas.RiskRequest
    ResultModel = rg_schemas.RiskResponse


class RiskDriverService(RiskGPTService):
    chain_fn = chains.async_get_drivers_chain if chains else None
    route_path = '/risk/drivers/'
    QueryModel = rg_schemas.DriverRequest
    ResultModel = rg_schemas.DriverResponse


class RiskLikelihoodService(RiskGPTService):
    chain_fn = chains.async_get_assessment_chain if chains else None
    route_path = '/risk/likelihood/'
    QueryModel = rg_schemas.AssessmentRequest
    ResultModel = rg_schemas.AssessmentResponse


class RiskAssessmentService(RiskGPTService):
    chain_fn = chains.async_get_assessment_chain if chains else None
    route_path = '/risk/impact/'
    QueryModel = rg_schemas.AssessmentRequest
    ResultModel = rg_schemas.AssessmentResponse


class RiskMitigationService(RiskGPTService):
    chain_fn = chains.async_get_mitigations_chain if chains else None
    route_path = '/risk/mitigation/'
    QueryModel = rg_schemas.MitigationRequest
    ResultModel = rg_schemas.MitigationResponse
