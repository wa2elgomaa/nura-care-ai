# API Contracts: Teacher Pattern Insights

## POST /api/pattern-insights/rules/evaluate
- Body: childId, windowKey
- Preconditions: active consent + staff role context

## GET /api/pattern-insights/flags
- Query: childId, status, dateRange
- Access: staff/director only

## POST /api/pattern-insights/flags/{flagId}/resolve
- Body: actorId, note

## POST /api/pattern-insights/rules/{ruleId}/clinical-approve
- Body: advisorId, approvalDecision, notes
