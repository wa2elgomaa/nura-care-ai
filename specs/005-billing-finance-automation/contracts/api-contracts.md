# API Contracts: Billing Finance Automation

## POST /api/billing/invoices/generate
- Body: siteId, periodStart, periodEnd
- Response: generatedInvoiceCount, runId

## GET /api/billing/invoices
- Query: siteId, accountId, status, period
- Response: invoices[]

## POST /api/billing/invoices/{invoiceId}/adjustments
- Body: kind(CHARGE|CREDIT), amount, reason

## POST /api/billing/payments/schedule
- Body: invoiceId, scheduledAt

## POST /api/billing/payments/{paymentId}/attempt
- Response: status, failureCode?

## POST /api/billing/receipts/issue
- Body: paymentId
- Response: receiptNumber, issuedAt
