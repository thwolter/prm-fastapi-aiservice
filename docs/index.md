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
