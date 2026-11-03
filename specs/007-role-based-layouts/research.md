# Research: Role-Based Layouts

## Decision 1: Composition-based role layouts in one app shell
- Decision: Use one app shell with role-composed layout modules.
- Rationale: Preserves single codebase while allowing differentiated UX.
- Alternatives considered: separate apps per role (rejected by constitution and overhead goals).

## Decision 2: Deterministic role priority routing
- Decision: Apply explicit role priority matrix for multi-role users.
- Rationale: Prevents unpredictable entry experiences.
- Alternatives considered: last-used-role default only (rejected for policy inconsistency).

## Decision 3: Shared workflow core + role wrappers
- Decision: Keep business workflow logic shared and layer role-specific UI wrappers.
- Rationale: Reduces duplicate implementation and drift.
- Alternatives considered: fully separate role workflow implementations (rejected for maintenance cost).
