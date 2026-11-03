# Data Model: Teacher Pattern Insights

## ObservationAggregate
- Fields: id, childId, windowStart, windowEnd, metricKey, metricValue, contextJson

## PatternRuleDefinition
- Fields: id, ruleCode, thresholdJson, phraseTemplate, status, approvedByAdvisor, approvedAt

## PatternFlag
- Fields: id, childId, ruleCode, severity, phraseText, status, generatedAt, resolvedAt

## InsightConsentSnapshot
- Fields: id, childId, parentId, consentState, capturedAt, validUntil

## PatternFlagAuditEvent
- Fields: id, flagId, action, actorType, payloadJson, at
