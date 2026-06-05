# Company Validation Playbook

Status: Beta framework  
Owner: OpenVals  
Scope: Microsoft, Google, Meta, Amazon, NVIDIA, OpenAI, Anthropic, xAI, Mistral, and Perplexity

## Purpose

The Company Validation Framework verifies whether each tracked company has enough trusted evidence to support APIP beta metrics. Validation is separate from metric confidence: confidence scores estimate metric reliability, while validation scores assess the total evidence package around a company.

## Initial Company Queue

- Microsoft
- Google
- Meta
- Amazon
- NVIDIA
- OpenAI
- Anthropic
- xAI
- Mistral
- Perplexity

## Validation Workflow

1. Create or load a company validation record.
2. Attach evidence sources to the validation.
3. Review each evidence item.
4. Review each underlying source.
5. Add reviewer notes.
6. Recalculate OpenVals Validation Score and Evidence Coverage Score.
7. Approve or reject the company validation.
8. Publish the validation dashboard state.

## Evidence Requirements

Preferred evidence order:

1. SEC filings, annual reports, earnings calls
2. Investor presentations and public company statements
3. Stanford AI Index, OECD AI Observatory, IMF, World Bank
4. Reuters, Bloomberg, Financial Times

Each evidence item stores:

- Source
- Evidence type
- Coverage weight
- Review status
- Reviewer notes
- Reviewed by
- Reviewed date

## Source Review Workflow

Each source review tracks:

- Source ID
- Company validation ID
- Review status: `pending`, `approved`, `verified`, or `rejected`
- Reviewer notes
- Reviewer identity
- Review timestamp

Rejected sources remain visible for auditability but are excluded from approval confidence unless the validation is recalculated after review.

## OpenVals Validation Score

The score is calculated as:

```text
OpenVals Validation Score =
Evidence Coverage Score * 40%
+ Source Confidence Score * 40%
+ Approved Evidence Ratio * 20%
```

Labels:

- `90-100`: Validated
- `75-89`: Strong Evidence
- `60-74`: Review Ready
- `40-59`: Evidence Gap
- `0-39`: Insufficient Evidence

## Evidence Coverage Score

Coverage uses the same source tier model as Real Data Beta:

- Tier 1: 45 points
- Tier 2: 25 points
- Tier 3: 20 points
- Tier 4: 10 points

Additional sources in a tier add limited incremental coverage. Coverage is recalculated from approved or verified evidence when available.

## Approval Criteria

Approve a company validation when:

- At least one Tier 1 or Tier 2 source is approved or verified.
- Evidence Coverage Score is at least 50.
- OpenVals Validation Score is at least 60.
- Reviewer notes explain any direct AI economics disclosure gaps.

Reject or keep in review when:

- Source attribution is incomplete.
- Evidence is stale or unverifiable.
- Private-company metrics rely only on uncorroborated public estimates.
- Reviewer notes identify unresolved methodology concerns.

## API Endpoints

Public dashboard:

- `GET /api/v1/company-validations`
- `GET /api/v1/company-validations/{validation_id}`

Admin workflow:

- `GET /api/v1/admin/company-validations`
- `POST /api/v1/admin/company-validations/{company_id}/evidence`
- `PATCH /api/v1/admin/company-validations/evidence/{evidence_id}/review`
- `PATCH /api/v1/admin/company-validations/source-reviews/{review_id}`
- `PATCH /api/v1/admin/company-validations/{validation_id}/approve`
- `PATCH /api/v1/admin/company-validations/{validation_id}/reject`

## Dashboard

The admin company validation dashboard shows:

- Company
- OpenVals Validation Score
- Evidence Coverage Score
- Confidence Score
- Evidence count
- Status
- Approval and rejection controls
