# Data Model: Quarterly Interest Profile

## ActivityEvidenceEvent
- Fields: id, childId, category, observedAt, source, metadataJson

## QuarterlyProfileDraft
- Fields: id, childId, quarterKey, narrativeJson, evidenceCount, status, generatedAt

## ProfileConsentSnapshot
- Fields: id, childId, parentId, consentState, scope, capturedAt, validUntil

## PhraseRuleViolation
- Fields: id, draftId, ruleCode, phrase, detectedAt, resolvedBy

## ProfileAuditEvent
- Fields: id, draftId, action, actorType, payloadJson, at
