# Data Model: Billing Finance Automation

## FamilyBillingAccount
- Fields: id, familyId, siteId, status, autopayEnabled

## Invoice
- Fields: id, accountId, periodStart, periodEnd, subtotal, discountTotal, totalDue, status
- State transitions: draft -> issued -> partially_paid -> paid|overdue|credited

## InvoiceLine
- Fields: id, invoiceId, kind, description, quantity, unitAmount, amount

## SubsidyAllocation
- Fields: id, accountId, programCode, validFrom, validTo, amountRuleJson

## VoucherApplication
- Fields: id, invoiceId, voucherCode, appliedAmount, remainingBalance

## PaymentTransaction
- Fields: id, invoiceId, scheduledAt, attemptedAt, amount, status, failureCode
- State transitions: scheduled -> attempted -> succeeded|failed|retrying

## TaxReceipt
- Fields: id, invoiceId, paymentId, receiptNumber, issuedAt

## FinanceAuditEvent
- Fields: id, actorId, entityType, entityId, action, payloadJson, at
