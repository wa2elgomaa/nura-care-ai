# Quickstart: Evacuation Live Rollcall Validation

## Prerequisites
- BLE gate coverage configured
- QR fallback kits prepared at exits
- Teacher tablets enrolled

## Scenario 1: One-tap evacuation trigger
1. Trigger evacuation as director.
2. Verify all tablets enter rollcall mode.

## Scenario 2: BLE reconciliation
1. Simulate badge exits.
2. Verify accounted list updates and discrepancies appear.

## Scenario 3: QR fallback path
1. Disable BLE ingestion.
2. Scan QR fallback for children.
3. Verify accountability can still be closed safely.

## Scenario 4: Insurer hook contract
1. Generate evacuation summary.
2. Verify insurer-hook payload validates and excludes prohibited media data.
