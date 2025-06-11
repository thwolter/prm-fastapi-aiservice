"""Services using the riskgpt library."""

from __future__ import annotations

from typing import Type

from pydantic import BaseModel

from riskgpt import chains
from riskgpt.models import schemas as rg_schemas


def _load_workflows():
    try:
        from riskgpt.workflows import (
            async_risk_workflow as _async_risk_workflow,
            external_context_enrichment as _external_context_enrichment,
            prepare_presentation_output as _prepare_presentation_output,
            check_context_quality as _check_context_quality,
        )
        return (
            _async_risk_workflow,
            _external_context_enrichment,
            _prepare_presentation_output,
            _check_context_quality,
        )
    except Exception:  # pragma: no cover - optional dependency
        return (None, None, None, None)


(
    async_risk_workflow,
    _external_context_enrichment,
    _prepare_presentation_output,
    _check_context_quality,
) = _load_workflows()


async def async_external_context_enrichment_fn(
    request: rg_schemas.ExternalContextRequest,
) -> rg_schemas.ExternalContextResponse:
    """Async wrapper around :func:`external_context_enrichment`."""
    if _external_context_enrichment is None:
        raise RuntimeError("riskgpt is not installed")
    return _external_context_enrichment(request)


async def async_prepare_presentation_output_fn(
    request: rg_schemas.PresentationRequest,
) -> rg_schemas.PresentationResponse:
    """Async wrapper around :func:`prepare_presentation_output`."""
    if _prepare_presentation_output is None:
        raise RuntimeError("riskgpt is not installed")
    return _prepare_presentation_output(request)


async def async_check_context_quality_fn(
    request: rg_schemas.ContextQualityRequest,
) -> rg_schemas.ContextQualityResponse:
    """Async wrapper around :func:`check_context_quality`."""
    if _check_context_quality is None:
        raise RuntimeError("riskgpt is not installed")
    return _check_context_quality(request)

from src.services.base_service import BaseService


# Risk Services


class RiskDefinitionCheckService(BaseService):
    """Service for checking risk definitions."""

    chain_fn = chains.async_check_definition_chain
    route_path = "/risk/check/definition/"
    QueryModel = rg_schemas.DefinitionCheckRequest
    ResultModel = rg_schemas.DefinitionCheckResponse


class RiskIdentificationService(BaseService):
    """Service for identifying risks."""

    chain_fn = chains.async_get_risks_chain
    route_path = "/risk/identify/"
    QueryModel = rg_schemas.RiskRequest
    ResultModel = rg_schemas.RiskResponse


class RiskDriverService(BaseService):
    """Service for identifying risk drivers."""

    chain_fn = chains.async_get_drivers_chain
    route_path = "/risk/drivers/"
    QueryModel = rg_schemas.DriverRequest
    ResultModel = rg_schemas.DriverResponse


class RiskAssessmentService(BaseService):
    """Service for assessing risk impact."""

    chain_fn = chains.async_get_assessment_chain
    route_path = "/risk/assessment/"
    QueryModel = rg_schemas.AssessmentRequest
    ResultModel = rg_schemas.AssessmentResponse


class RiskMitigationService(BaseService):
    """Service for identifying risk mitigations."""

    chain_fn = chains.async_get_mitigations_chain
    route_path = "/risk/mitigation/"
    QueryModel = rg_schemas.MitigationRequest
    ResultModel = rg_schemas.MitigationResponse


class RiskPrioritizationService(BaseService):
    """Service for prioritizing risks."""

    chain_fn = chains.async_prioritize_risks_chain
    route_path = "/risk/prioritize/"
    QueryModel = rg_schemas.PrioritizationRequest
    ResultModel = rg_schemas.PrioritizationResponse


class RiskCostBenefitService(BaseService):
    """Service for cost-benefit analysis of mitigations."""

    chain_fn = chains.async_cost_benefit_chain
    route_path = "/risk/cost-benefit/"
    QueryModel = rg_schemas.CostBenefitRequest
    ResultModel = rg_schemas.CostBenefitResponse


class RiskMonitoringService(BaseService):
    """Service for deriving monitoring indicators."""

    chain_fn = chains.async_get_monitoring_chain
    route_path = "/risk/monitoring/"
    QueryModel = rg_schemas.MonitoringRequest
    ResultModel = rg_schemas.MonitoringResponse


class RiskOpportunityService(BaseService):
    """Service for identifying opportunities from risks."""

    chain_fn = chains.async_get_opportunities_chain
    route_path = "/risk/opportunities/"
    QueryModel = rg_schemas.OpportunityRequest
    ResultModel = rg_schemas.OpportunityResponse


class RiskCommunicationService(BaseService):
    """Service for summarizing risks for stakeholders."""

    chain_fn = chains.async_communicate_risks_chain
    route_path = "/risk/communicate/"
    QueryModel = rg_schemas.CommunicationRequest
    ResultModel = rg_schemas.CommunicationResponse


class RiskBiasCheckService(BaseService):
    """Service for checking biases in risk descriptions."""

    chain_fn = chains.async_bias_check_chain
    route_path = "/risk/check/bias/"
    QueryModel = rg_schemas.BiasCheckRequest
    ResultModel = rg_schemas.BiasCheckResponse


class RiskCorrelationTagsService(BaseService):
    """Service for defining correlation tags for risks."""

    chain_fn = chains.async_get_correlation_tags_chain
    route_path = "/risk/correlation-tags/"
    QueryModel = rg_schemas.CorrelationTagRequest
    ResultModel = rg_schemas.CorrelationTagResponse


# Category Services


class CreateCategoriesService(BaseService):
    """Base service for category operations."""

    chain_fn = chains.async_get_categories_chain
    route_path = "/categories/"
    QueryModel: Type[BaseModel] = rg_schemas.CategoryRequest
    ResultModel: Type[BaseModel] = rg_schemas.CategoryResponse


class ContextQualityService(BaseService):
    """Service for evaluating context knowledge quality."""

    chain_fn = async_check_context_quality_fn
    route_path = "/context/check/"
    QueryModel = rg_schemas.ContextQualityRequest
    ResultModel = rg_schemas.ContextQualityResponse


class ExternalContextService(BaseService):
    """Service for enriching context with external information."""

    chain_fn = async_external_context_enrichment_fn
    route_path = "/context/external/"
    QueryModel = rg_schemas.ExternalContextRequest
    ResultModel = rg_schemas.ExternalContextResponse


class PresentationWorkflowService(BaseService):
    """Service for preparing presentation-ready summaries."""

    chain_fn = async_prepare_presentation_output_fn
    route_path = "/presentation/"
    QueryModel = rg_schemas.PresentationRequest
    ResultModel = rg_schemas.PresentationResponse


class RiskWorkflowService(BaseService):
    """Service orchestrating the full risk workflow."""

    chain_fn = async_risk_workflow
    route_path = "/risk/workflow/"
    QueryModel = rg_schemas.RiskRequest
    ResultModel = rg_schemas.RiskResponse
