# Guardian/Parent Management API

**Service**: nura-vlm  
**Router**: `/api/guardians`  
**Purpose**: Permanent enrollment of students' parents/guardians (whitelisted persons)  
**Created**: 2026-11-08 (Week 3+)

## Overview

The Guardian API allows schools to enroll students' parents and guardians as **whitelisted persons**. Unlike visitors (temporary), guardians are permanent enrollments linked to their children/students.

**Key Differences from Visitors:**

| Feature | Visitors | Guardians |
|---------|----------|-----------|
| Duration | Temporary (hours/day) | Permanent |
| Linked to Students | No | Yes (required) |
| Storage | `visitors` table | `enrolled_persons` table |
| Authorized Pickup | N/A | Yes (configurable) |
| Auto-expires | Yes | No (manually deactivate) |
| Face Recognition | Optional | Required |

## Use Cases

1. **Authorized Pickup**: Parents picking up their children
2. **Campus Access**: Guardian visiting during school hours
3. **No Stranger Alerts**: Recognized guardians won't trigger unknown person alerts
4. **Parent-Teacher Meetings**: Parents attend meetings on campus
5. **Family Events**: School events where parents are present

## API Endpoints

### 1. Enroll Guardian

**POST** `/api/guardians/enroll`

Enroll a parent/guardian with face recognition, linked to their children.

**Request:**
```bash
curl -X POST http://localhost:8001/api/guardians/enroll \
  -F 'full_name=Jane Smith' \
  -F 'relationship=mother' \
  -F 'linked_students=alice_j,bob_j' \
  -F 'phone=555-1234' \
  -F 'email=jane.smith@email.com' \
  -F 'authorized_pickup=true' \
  -F 'photo=@jane_smith.jpg'
```

**Parameters:**
- `full_name` (required): Full name of guardian
- `relationship` (required): mother, father, grandmother, grandfather, aunt, uncle, guardian, etc.
- `linked_students` (required): Comma-separated student person_ids (e.g., "alice_j,bob_j")
- `phone` (optional): Contact phone number
- `email` (optional): Contact email
- `authorized_pickup` (optional, default=true): Can pick up children?
- `photo` (required): Photo file for face recognition

**Response:**
```json
{
  "guardian_id": "guardian_jane_smith",
  "full_name": "Jane Smith",
  "relationship": "mother",
  "linked_students": ["alice_j", "bob_j"],
  "phone": "555-1234",
  "email": "jane.smith@email.com",
  "authorized_pickup": true,
  "photo_path": "/data/storage/guardians/guardian_jane_smith_1699456789.jpg",
  "created_at": "2026-11-08T12:00:00",
  "active": true
}
```

**Validation:**
- Face must be detected in photo (InsightFace)
- All linked students must exist in `enrolled_persons` table
- Face embedding is extracted and stored for recognition

### 2. List All Guardians

**GET** `/api/guardians/`

List all enrolled guardians.

**Query Parameters:**
- `active_only` (optional, default=true): Only show active guardians

**Request:**
```bash
curl http://localhost:8001/api/guardians/?active_only=true
```

**Response:**
```json
[
  {
    "guardian_id": "guardian_jane_smith",
    "full_name": "Jane Smith",
    "relationship": "mother",
    "linked_students": ["alice_j", "bob_j"],
    "phone": "555-1234",
    "email": "jane.smith@email.com",
    "authorized_pickup": true,
    "photo_path": "/data/storage/guardians/guardian_jane_smith.jpg",
    "created_at": "2026-11-08T12:00:00",
    "active": true
  },
  ...
]
```

### 3. Get Guardian Details

**GET** `/api/guardians/{guardian_id}`

Get details for a specific guardian.

**Request:**
```bash
curl http://localhost:8001/api/guardians/guardian_jane_smith
```

**Response:**
```json
{
  "guardian_id": "guardian_jane_smith",
  "full_name": "Jane Smith",
  "relationship": "mother",
  "linked_students": ["alice_j", "bob_j"],
  "phone": "555-1234",
  "email": "jane.smith@email.com",
  "authorized_pickup": true,
  "photo_path": "/data/storage/guardians/guardian_jane_smith.jpg",
  "created_at": "2026-11-08T12:00:00",
  "active": true
}
```

### 4. Get Guardians by Student

**GET** `/api/guardians/by-student/{student_id}`

Get all guardians linked to a specific student.

**Request:**
```bash
curl http://localhost:8001/api/guardians/by-student/alice_j
```

**Response:**
```json
[
  {
    "guardian_id": "guardian_jane_smith",
    "full_name": "Jane Smith",
    "relationship": "mother",
    "linked_students": ["alice_j", "bob_j"],
    ...
  },
  {
    "guardian_id": "guardian_john_smith",
    "full_name": "John Smith",
    "relationship": "father",
    "linked_students": ["alice_j", "bob_j"],
    ...
  }
]
```

**Use Case:** When a student is picked up, verify the person is authorized

### 5. Deactivate Guardian

**PUT** `/api/guardians/{guardian_id}/deactivate`

Deactivate a guardian (soft delete - won't be recognized, won't trigger stranger alerts).

**Request:**
```bash
curl -X PUT http://localhost:8001/api/guardians/guardian_jane_smith/deactivate
```

**Response:**
```json
{
  "success": true,
  "message": "Guardian Jane Smith deactivated"
}
```

**When to Use:**
- Parent is no longer authorized (e.g., custody changes)
- Student has graduated/left school
- Guardian requests removal

### 6. Reactivate Guardian

**PUT** `/api/guardians/{guardian_id}/reactivate`

Reactivate a previously deactivated guardian.

**Request:**
```bash
curl -X PUT http://localhost:8001/api/guardians/guardian_jane_smith/reactivate
```

**Response:**
```json
{
  "success": true,
  "message": "Guardian Jane Smith reactivated"
}
```

## Data Storage

Guardians are stored in the `enrolled_persons` table with:
- `person_id`: `guardian_{name}` format
- `face_embedding`: 512D vector for recognition
- `is_visitor`: `false` (permanent, not temporary)
- `notes`: Contains guardian metadata (relationship, linked students, phone, email, authorized_pickup)

## Face Recognition Flow

```
Guardian arrives at school
  ↓
Camera detects person
  ↓
Face Identifier checks enrolled_persons
  ↓
Match found: guardian_jane_smith (confidence 0.95)
  ↓
Check notes: Authorized Pickup = true
  ↓
No stranger alert ✓
Alert: "Jane Smith (mother of Alice) arrived for pickup"
```

## Integration with Stranger Detection

**Before Guardian API:**
```
Unknown parent → Stranger Alert → Manual verification
```

**With Guardian API:**
```
Parent enrolled as guardian → Face recognized → No alert → Authorized
```

## Example Workflows

### Workflow 1: Parent Pickup
```bash
# 1. Enroll parent
curl -X POST http://localhost:8001/api/guardians/enroll \
  -F 'full_name=Jane Smith' \
  -F 'relationship=mother' \
  -F 'linked_students=alice_j' \
  -F 'authorized_pickup=true' \
  -F 'photo=@jane.jpg'

# 2. When Jane arrives for pickup:
# Camera recognizes face → No stranger alert
# System knows: Jane is Alice's mother, authorized pickup

# 3. Verify authorized guardians for student
curl http://localhost:8001/api/guardians/by-student/alice_j
# Shows Jane Smith (mother) + John Smith (father)
```

### Workflow 2: Custody Change
```bash
# Parent no longer authorized
curl -X PUT http://localhost:8001/api/guardians/guardian_john_smith/deactivate

# Now if John arrives:
# Face still in database but active=false
# Won't trigger stranger alert (known person)
# But won't be authorized for pickup
```

### Workflow 3: Family Event
```bash
# Enroll multiple family members
curl -X POST http://localhost:8001/api/guardians/enroll \
  -F 'full_name=Mary Johnson' \
  -F 'relationship=grandmother' \
  -F 'linked_students=alice_j' \
  -F 'photo=@grandma.jpg'

# All family members recognized during school event
# No stranger alerts for enrolled guardians
```

## Configuration

No additional configuration needed. Uses existing:
- `POSTGRES_*` for database
- `STORAGE_SERVICE_URL` for photo storage
- InsightFace for face recognition

## Testing

```bash
# Enroll guardian
curl -X POST http://localhost:8001/api/guardians/enroll \
  -F 'full_name=Test Parent' \
  -F 'relationship=mother' \
  -F 'linked_students=adam_w' \
  -F 'phone=555-0000' \
  -F 'email=test@test.com' \
  -F 'authorized_pickup=true' \
  -F 'photo=@test_parent.jpg'

# List guardians
curl http://localhost:8001/api/guardians/ | jq

# Get guardians for student
curl http://localhost:8001/api/guardians/by-student/adam_w | jq

# Deactivate
curl -X PUT http://localhost:8001/api/guardians/guardian_test_parent/deactivate
```

## Security Considerations

1. **Photo Required**: Guardian must have face photo for recognition
2. **Student Validation**: Linked students must exist
3. **Soft Delete**: Deactivation is reversible (not permanent delete)
4. **Authorized Pickup**: Flag controls pickup permissions
5. **Active Status**: Inactive guardians won't be recognized

## Database Schema

Guardian data is stored in existing `enrolled_persons` table:

```sql
-- Guardian example
INSERT INTO enrolled_persons (
  person_id,              -- 'guardian_jane_smith'
  full_name,              -- 'Jane Smith'
  display_name,           -- 'Jane Smith'
  face_embedding,         -- Vector(512)
  enrollment_photo_url,   -- Storage path
  active,                 -- true/false
  is_visitor,             -- false (permanent)
  notes                   -- 'Relationship: mother, Students: alice_j, ...'
) VALUES (...);
```

## Future Enhancements

- [ ] Separate `guardians` table for richer metadata
- [ ] Emergency contact priority levels
- [ ] Pickup time logging
- [ ] SMS notifications when guardian recognized
- [ ] Pickup authorization workflow (request → approve)
- [ ] Multiple photos per guardian (different angles)
- [ ] Guardian-student relationship history

---

**Guardian API Status: ✅ IMPLEMENTED**  
**Router Registered: ✅ /api/guardians**  
**Ready for Use!**
