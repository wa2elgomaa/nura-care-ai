# Week 5: Student Behavioral Analytics

**Primary Focus**: Track student activities to enhance education and understand development  
**Secondary**: Track unknowns (potential unenrolled students)

---

## Core Objectives

### 1. Educational Enhancement
**Track student behaviors to improve teaching:**
- Which activities do students enjoy most?
- What are their natural interests? (reading, playing, building, art)
- When are they most engaged?
- What's their social interaction pattern?

### 2. Development Insights
**Understand each student's growth:**
- Skills development (fine motor, gross motor, social)
- Emotional patterns (happy, upset, isolated)
- Learning preferences (visual, kinesthetic, auditory)
- Attention span and focus patterns

### 3. Safety & Well-being
**Ensure every student is thriving:**
- Is the student isolated or well-integrated?
- Are they getting enough physical activity?
- Are they eating properly?
- Any signs of distress or unusual behavior?

---

## What We Track Per Student

### Activity Classification (11 types)
1. **Learning Activities**
   - `reading` - Looking at books, being read to
   - `building` - Blocks, construction, puzzles
   - `art` - Drawing, painting, crafts

2. **Physical Activities**
   - `playing` - Active play, toys, games
   - `running` - Gross motor activity
   - `sitting` - Quiet time, circle time

3. **Social Activities**
   - `interacting` - With other students or teachers
   - `eating` - Meal/snack time
   - `alone` - Independent play or isolation

4. **Emotional States**
   - `crying` - Distress, upset
   - `sleeping` - Nap time

5. **Other**
   - `standing` - Waiting, transition
   - `other` - Unclassified activity

### Time & Location Tracking
- Time spent in each zone (classroom, playground, cafeteria)
- Movement patterns throughout the day
- Transition frequency (how often moving between areas)

### Social Interaction Analysis
- Who do they play with most?
- Group size preference (alone, pairs, small group, large group)
- Time alone vs. time with others
- Teacher interaction frequency

---

## Daily Student Report

### Generated Every Evening
For each student, create a comprehensive daily report:

```json
{
  "student_id": "emma_s",
  "student_name": "Emma Smith",
  "report_date": "2026-11-08",
  "age_years": 4,
  "classroom": "Pre-K A",
  
  "attendance": {
    "arrival": "08:15",
    "departure": "15:30",
    "time_on_campus_hours": 7.25,
    "absent_periods": []
  },
  
  "activities": {
    "reading": {
      "minutes": 45,
      "percentage": 10.3,
      "engagement_level": "high"
    },
    "playing": {
      "minutes": 120,
      "percentage": 27.6,
      "engagement_level": "very_high"
    },
    "building": {
      "minutes": 60,
      "percentage": 13.8,
      "engagement_level": "high"
    },
    "eating": {
      "minutes": 40,
      "percentage": 9.2,
      "engagement_level": "medium"
    },
    "sitting": {
      "minutes": 90,
      "percentage": 20.7,
      "engagement_level": "medium"
    },
    "interacting": {
      "minutes": 150,
      "percentage": 34.5,
      "engagement_level": "high"
    },
    "alone": {
      "minutes": 30,
      "percentage": 6.9,
      "engagement_level": "low"
    }
  },
  
  "zones": {
    "classroom": {
      "minutes": 240,
      "percentage": 55.2,
      "primary_activities": ["reading", "building", "sitting"]
    },
    "playground": {
      "minutes": 120,
      "percentage": 27.6,
      "primary_activities": ["playing", "running", "interacting"]
    },
    "cafeteria": {
      "minutes": 40,
      "percentage": 9.2,
      "primary_activities": ["eating", "sitting"]
    },
    "quiet_room": {
      "minutes": 35,
      "percentage": 8.0,
      "primary_activities": ["sleeping"]
    }
  },
  
  "social": {
    "interaction_partners": [
      {"student_id": "noah_b", "student_name": "Noah Brown", "minutes": 85},
      {"student_id": "olivia_j", "student_name": "Olivia Jones", "minutes": 45}
    ],
    "group_size_preference": {
      "alone": 30,
      "pairs": 60,
      "small_group_3_5": 90,
      "large_group_6plus": 120
    },
    "teacher_interactions": 12,
    "avg_interaction_duration_minutes": 3.5
  },
  
  "emotional_wellness": {
    "positive_indicators": [
      "High engagement in play",
      "Strong peer connections",
      "Participates in group activities"
    ],
    "concerns": [
      "30 minutes alone (within normal range)"
    ],
    "crying_incidents": 0,
    "overall_mood": "positive"
  },
  
  "developmental_insights": {
    "strengths": [
      "Strong social skills (34.5% time interacting)",
      "Enjoys building activities (shows problem-solving)",
      "Good physical activity level"
    ],
    "areas_for_growth": [
      "Could increase reading time (10% vs classroom avg 15%)"
    ],
    "recommended_activities": [
      "More story time",
      "Interactive reading games"
    ]
  },
  
  "anomalies": [],
  
  "parent_summary": "Emma had a great day! She was very engaged in play and showed strong social connections with Noah and Olivia. She particularly enjoyed building with blocks this morning. Consider encouraging reading at home to complement classroom activities."
}
```

---

## Use Cases

### For Teachers
**Morning Review:**
- Check yesterday's report for each student
- Identify who needs extra attention today
- Plan activities based on student interests

**Real-time Monitoring:**
- "Where is Emma right now?" → Playground
- "Who is isolated and needs engagement?" → Noah alone for 15 min
- "Has Billy eaten lunch yet?" → Yes, 20 minutes ago

### For Parents
**Daily Summary Email:**
- What did my child do today?
- What activities did they enjoy?
- Who did they play with?
- How was their mood?

**Monthly Progress Report:**
- How has my child developed this month?
- What are their favorite activities?
- Are they making friends?
- Any recommended focus areas?

### For Administrators
**Classroom Insights:**
- Which activities engage students most?
- Optimal class size for activities
- Zone usage patterns
- Teacher-student interaction ratios

**Curriculum Planning:**
- What interests are trending?
- Which activities need more time?
- Student development patterns

---

## API Endpoints

### Student Analytics API

**1. Get Daily Report**
```bash
GET /api/analytics/student/{student_id}/daily?date=2026-11-08

# Response: Full daily report (JSON above)
```

**2. Get Current Activity**
```bash
GET /api/analytics/student/{student_id}/current

# Response:
{
  "student_id": "emma_s",
  "current_location": "playground",
  "current_activity": "playing",
  "activity_started": "2026-11-08T10:15:00",
  "duration_minutes": 12,
  "with_students": ["noah_b", "olivia_j"]
}
```

**3. Get Activity Timeline**
```bash
GET /api/analytics/student/{student_id}/timeline?date=2026-11-08

# Response: Chronological list of activities throughout day
[
  {
    "time": "08:15",
    "activity": "arrived",
    "location": "entrance"
  },
  {
    "time": "08:20-08:45",
    "activity": "sitting",
    "location": "classroom",
    "duration_minutes": 25
  },
  {
    "time": "08:45-09:30",
    "activity": "reading",
    "location": "classroom",
    "duration_minutes": 45
  }
]
```

**4. Get Social Network**
```bash
GET /api/analytics/student/{student_id}/social?period=week

# Response: Who student interacts with most
{
  "student_id": "emma_s",
  "period": "2026-11-01 to 2026-11-08",
  "primary_friends": [
    {"student_id": "noah_b", "interaction_minutes": 420},
    {"student_id": "olivia_j", "interaction_minutes": 180}
  ],
  "group_preference": "small_group_3_5",
  "avg_interaction_duration": 3.5
}
```

**5. Developmental Progress**
```bash
GET /api/analytics/student/{student_id}/progress?from=2026-10-01

# Response: Development trends over time
{
  "reading_trend": "increasing",  // 10% → 15% over month
  "social_trend": "stable",
  "physical_activity_trend": "increasing",
  "areas_of_growth": ["reading", "fine_motor_skills"]
}
```

**6. Class Overview (Teacher Dashboard)**
```bash
GET /api/analytics/classroom/{classroom_id}/overview?date=2026-11-08

# Response: All students in class
{
  "classroom": "Pre-K A",
  "date": "2026-11-08",
  "students_present": 15,
  "students_absent": 2,
  "current_activities": {
    "playing": 8,
    "reading": 4,
    "eating": 2,
    "sleeping": 1
  },
  "needs_attention": [
    {"student_id": "billy_t", "reason": "alone_15min"}
  ]
}
```

---

## Unknown Person Handling

### Potential Unenrolled Students

When unknown detected:
1. **Auto-create** `unknown_001` entry
2. **Track** same unknown across cameras
3. **Alert** staff: "Unknown person detected - potential unenrolled student"
4. **Manual identification**: Staff can link to:
   - Existing student (forgot to enroll face)
   - New enrollment (new student)
   - Visitor (not a student)

**Why Track Unknowns:**
- New students not yet enrolled
- Students whose face recognition failed
- Allows retroactive data linking after enrollment

---

## Implementation Priority

### Week 5 Tasks (Revised)

**Day 1-2: Student Activity Tracking**
- ✅ Database tables (already done)
- Create activity classifier (simple rule-based for now)
- Store detections with activities

**Day 3-4: Daily Report Generation**
- Analytics service to generate student reports
- Aggregate activities, zones, social interactions
- Parent-friendly summaries

**Day 5-6: Student Analytics API**
- Endpoints for daily reports
- Current activity tracking
- Timeline and social network APIs

**Day 7-8: Unknown Person Workflow**
- Auto-create unknowns
- Manual linking interface
- Staff notification system

---

## Success Metrics

**Student Analytics:**
- [ ] Daily reports generated for all students
- [ ] Activity classification working
- [ ] Social interaction tracking functional
- [ ] Parent summaries readable and useful

**Unknown Handling:**
- [ ] Unknowns auto-created
- [ ] Manual linking workflow functional
- [ ] Staff can identify and onboard

---

**Focus**: **Students first**, unknowns for identification only  
**Goal**: Enhance education and understand student development  
**Output**: Actionable insights for teachers and parents
