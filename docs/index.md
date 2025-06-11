# AI Service

This documentation is generated with [MkDocs](https://www.mkdocs.org/).

## Category detection

The `/api/categories/` endpoint uses the
[RiskGPT](https://pypi.org/project/riskgpt/) library (requires Python 3.12)
to return relevant categories for a project description. Ensure that the
package and its configuration file are installed.

## Context quality

Send a `ContextQualityRequest` to `/api/context/check/` to assess the quality of
a project context. The endpoint returns a `ContextQualityResponse` with a score
and rationale.

## External context enrichment

Use `/api/context/external/` with an `ExternalContextRequest` payload to gather
news, professional, regulatory and peer information. The service returns an
`ExternalContextResponse` summarising the findings.

## Presentation workflow

The `/api/presentation/` endpoint takes a `PresentationRequest` and returns a
`PresentationResponse` containing presentation-ready summaries tailored to the
requested audience.

## Risk workflow

Send a `RiskRequest` to `/api/risk/workflow/` to run the complete risk
identification and assessment workflow. The endpoint responds with a
`RiskResponse` including references and document links.
