"""Services using the riskgpt library."""
from __future__ import annotations

from typing import Type

from pydantic import BaseModel

from riskgpt import chains
from riskgpt.models import schemas as rg_schemas

from src.services.riskgpt_base_service import RiskGPTService


# Risk Services

class RiskDefinitionCheckService(RiskGPTService):
    """Service for checking risk definitions."""
    
    chain_fn = chains.async_check_definition_chain if chains else None
    route_path = '/risk/check/definition/'
    QueryModel = rg_schemas.DefinitionCheckRequest
    ResultModel = rg_schemas.DefinitionCheckResponse


class RiskIdentificationService(RiskGPTService):
    """Service for identifying risks."""
    
    chain_fn = chains.async_get_risks_chain if chains else None
    route_path = '/risk/identify/'
    QueryModel = rg_schemas.RiskRequest
    ResultModel = rg_schemas.RiskResponse


class RiskDriverService(RiskGPTService):
    """Service for identifying risk drivers."""
    
    chain_fn = chains.async_get_drivers_chain if chains else None
    route_path = '/risk/drivers/'
    QueryModel = rg_schemas.DriverRequest
    ResultModel = rg_schemas.DriverResponse


class RiskLikelihoodService(RiskGPTService):
    """Service for assessing risk likelihood."""
    
    chain_fn = chains.async_get_assessment_chain if chains else None
    route_path = '/risk/likelihood/'
    QueryModel = rg_schemas.AssessmentRequest
    ResultModel = rg_schemas.AssessmentResponse


class RiskAssessmentService(RiskGPTService):
    """Service for assessing risk impact."""
    
    chain_fn = chains.async_get_assessment_chain if chains else None
    route_path = '/risk/impact/'
    QueryModel = rg_schemas.AssessmentRequest
    ResultModel = rg_schemas.AssessmentResponse


class RiskMitigationService(RiskGPTService):
    """Service for identifying risk mitigations."""
    
    chain_fn = chains.async_get_mitigations_chain if chains else None
    route_path = '/risk/mitigation/'
    QueryModel = rg_schemas.MitigationRequest
    ResultModel = rg_schemas.MitigationResponse


# Category Services

class CreateCategoriesService(RiskGPTService):
    """Base service for category operations."""
    
    chain_fn = chains.async_get_categories_chain if chains else None
    route_path = '/categories/'
    QueryModel: Type[BaseModel] = rg_schemas.CategoryRequest
    ResultModel: Type[BaseModel] = rg_schemas.CategoryResponse
