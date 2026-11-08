#!/bin/bash
# Load Sample Policy Documents into nura-rag
# Usage: ./scripts/load-sample-rules.sh [RAG_URL]

RAG_URL="${1:-http://localhost:3002}"

echo "Loading sample policy documents into RAG service at $RAG_URL"
echo ""

# Rule 1: Continuous Adult Supervision (State Regulation)
echo "[1/5] Loading STATE-REG-45.1.2: Continuous Adult Supervision..."
curl -X POST "$RAG_URL/rules" \
  -H "Content-Type: application/json" \
  -d '{
  "rule_id": "STATE-REG-45.1.2",
  "title": "Continuous Adult Supervision Required",
  "description": "Children ages 0-5 must be within sight and sound of qualified staff at all times",
  "clause": "Children ages zero through five years must be within sight and sound of qualified child care staff at all times during the hours of operation. Staff must maintain visual contact and be able to hear children at all times.",
  "source": "State Childcare Licensing Code § 45.1.2",
  "severity": "critical",
  "category": "supervision",
  "enabled": true
}' \
  -s -o /dev/null -w "Status: %{http_code}\n"

# Rule 2: Maximum Room Capacity (Fire Code)
echo "[2/5] Loading FIRE-CODE-12.4: Maximum Room Capacity..."
curl -X POST "$RAG_URL/rules" \
  -H "Content-Type: application/json" \
  -d '{
  "rule_id": "FIRE-CODE-12.4",
  "title": "Maximum Room Capacity",
  "description": "Classroom capacity must not exceed 1 child per 35 square feet of usable floor space",
  "clause": "The maximum number of children permitted in any room must not exceed one child per thirty-five square feet of usable floor space. This requirement ensures adequate space for safe evacuation and normal activities.",
  "source": "State Fire Safety Code § 12.4",
  "severity": "high",
  "category": "capacity",
  "enabled": true
}' \
  -s -o /dev/null -w "Status: %{http_code}\n"

# Rule 3: Restricted Area Access (Health Code)
echo "[3/5] Loading HEALTH-CODE-8.2: Restricted Area Access..."
curl -X POST "$RAG_URL/rules" \
  -H "Content-Type: application/json" \
  -d '{
  "rule_id": "HEALTH-CODE-8.2",
  "title": "Restricted Area Access",
  "description": "Children must not access kitchen, storage, mechanical rooms, or other hazardous areas",
  "clause": "Children shall not be permitted in kitchen areas, food preparation spaces, storage rooms, mechanical rooms, custodial closets, or other areas that present safety or health hazards. These areas must be secured when not supervised by staff.",
  "source": "State Health & Safety Code § 8.2",
  "severity": "high",
  "category": "restricted_area",
  "enabled": true
}' \
  -s -o /dev/null -w "Status: %{http_code}\n"

# Rule 4: After-Hours Facility Access (Ministry Regulation)
echo "[4/5] Loading MINISTRY-EDU-15.3: After-Hours Access..."
curl -X POST "$RAG_URL/rules" \
  -H "Content-Type: application/json" \
  -d '{
  "rule_id": "MINISTRY-EDU-15.3",
  "title": "After-Hours Facility Access",
  "description": "Facility must be secured and unoccupied outside of licensed operating hours",
  "clause": "Licensed childcare facilities must not be occupied by children outside of the hours specified in the operating license. All children must be signed out by authorized guardians before closing time. Facilities must be secured after operating hours.",
  "source": "Ministry of Education Childcare Regulations § 15.3",
  "severity": "medium",
  "category": "after_hours",
  "enabled": true
}' \
  -s -o /dev/null -w "Status: %{http_code}\n"

# Rule 5: Playground Supervision Ratio (School Policy)
echo "[5/5] Loading SCHOOL-POLICY-2024-01: Playground Supervision..."
curl -X POST "$RAG_URL/rules" \
  -H "Content-Type: application/json" \
  -d '{
  "rule_id": "SCHOOL-POLICY-2024-01",
  "title": "Playground Supervision Ratio",
  "description": "Minimum 1 staff member required per 8 children on outdoor playground",
  "clause": "When children are engaged in outdoor play activities, a minimum ratio of one qualified staff member per eight children must be maintained. Staff must position themselves to maintain visual contact with all children in their assigned supervision zone.",
  "source": "School Safety Policy 2024 § 1",
  "severity": "high",
  "category": "supervision",
  "enabled": true
}' \
  -s -o /dev/null -w "Status: %{http_code}\n"

echo ""
echo "✅ Sample policy documents loaded successfully!"
echo ""
echo "Verify by running:"
echo "  curl $RAG_URL/rules | jq"
