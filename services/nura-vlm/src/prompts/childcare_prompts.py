"""
Improved VLM Prompts for Childcare Safety
Context-aware prompts with specific examples to improve accuracy

Spec: specs/026-hybrid-fast-path/spec.md
"""

# Base childcare safety prompt (improved from generic version)
CHILDCARE_SAFETY_PROMPT = """You are an expert childcare safety monitor analyzing this image for violations.

CRITICAL INSTRUCTIONS:
1. Be SPECIFIC - describe exactly what you see, not what might be happening
2. Do NOT assume play if you see physical contact
3. Do NOT hallucinate - if you don't see something, say so
4. Focus on OBSERVABLE facts, not interpretations

Analyze this childcare scene for:

1. SUPERVISION
   - Count adults visible (Be exact - if none visible, say "NO ADULTS VISIBLE")
   - Count children visible
   - Calculate ratio
   - Are adults actively supervising or distracted?

2. PHYSICAL SAFETY
   - Any physical contact between children?
   - If yes, describe the TYPE and FORCE (gentle/moderate/forceful)
   - Any objects being used? HOW are they being used?
   - Any defensive postures or reactions?

3. CHILD WELLBEING
   - Any child showing distress? (crying, covering face, pulling away)
   - Facial expressions: fear, pain, sadness?
   - Body language: tense, withdrawn, defensive?

4. ENVIRONMENT
   - Any visible hazards?
   - Age-appropriate equipment?

CLASSIFY:
- VIOLATION: Yes/No
- TYPE: violence | distress | supervision | environment | none
- SEVERITY: LOW | MEDIUM | HIGH
- CONFIDENCE: 0.0-1.0
- IMMEDIATE_ACTION: Yes/No

Provide specific evidence for your classification."""


# Violence-specific prompt with context from fast-path detector
VIOLENCE_DETECTION_PROMPT = """You are a childcare safety expert. The fast-path violence detector flagged this image with {confidence:.0%} confidence for potential {action_type}.

FAST-PATH DETECTED:
- Action: {action_type}
- Confidence: {confidence:.0%}
- Location: {bbox_description}

YOUR JOB: Validate or reject this detection with careful analysis.

==== EXAMPLES OF VIOLENCE (CONFIRM these) ====

1. HITTING:
   - One child's hand/arm extended toward another child's body
   - Contact or about-to-contact position
   - Object (pencil, ruler, toy) held like a weapon
   - Target child flinching, pulling away, or defensive

2. PUSHING/SHOVING:
   - Hands on another child's body
   - Child off-balance or falling
   - Forceful contact (not gentle touch)

3. THROWING AT:
   - Object in mid-air toward another child
   - Throwing motion visible
   - Target child dodging or reacting

4. HAIR PULLING:
   - Hand in another child's hair
   - Child's head tilted/pulled
   - Victim showing distress

==== EXAMPLES OF NORMAL PLAY (REJECT false positives) ====

1. COOPERATIVE PLAY:
   - Passing objects TO each other (not AT)
   - Gentle touch on shoulder/arm
   - Both children engaged and relaxed

2. WORKING TOGETHER:
   - Sitting close, sharing materials
   - Pointing at shared work
   - No defensive postures

3. PLAYFUL INTERACTION:
   - Both children smiling
   - Reciprocal actions
   - No signs of distress

==== YOUR ANALYSIS ====

Look at the area around {bbox_description}.

1. What EXACTLY do you see? (Describe arm positions, body language, facial expressions)

2. Is there actual physical contact or aggression?
   - If yes: What type? (hitting/pushing/throwing/other)
   - If yes: What force? (light/moderate/forceful)
   - If no: Why did the detector flag it?

3. How is the TARGET child reacting?
   - Flinching/pulling away = real aggression
   - Relaxed/engaged = likely false positive

4. Context clues:
   - Are adults intervening?
   - Are other children reacting?
   - Is this isolated or ongoing?

VERDICT:
- VIOLENCE_CONFIRMED: Yes/No
- TYPE: hitting | pushing | throwing | hair_pulling | none
- SEVERITY: LOW | MEDIUM | HIGH | NONE
- CONFIDENCE: 0.0-1.0
- EVIDENCE: [Specific observable facts]
- FAST_PATH_CORRECT: Yes/No

Be precise. The fast-path detector may be wrong - validate independently."""


# Distress-specific prompt with context
DISTRESS_DETECTION_PROMPT = """You are a childcare safety expert. The fast-path distress detector flagged this image with {confidence:.0%} confidence for potential {emotion}.

FAST-PATH DETECTED:
- Emotion: {emotion}
- Confidence: {confidence:.0%}
- Face location: {face_bbox_description}

YOUR JOB: Validate or reject this detection.

==== SIGNS OF REAL DISTRESS (CONFIRM these) ====

1. CRYING:
   - Tears visible
   - Red/flushed face
   - Mouth open wide
   - Scrunched facial features

2. FEAR:
   - Wide eyes
   - Pulled back/withdrawn posture
   - Defensive hand positions
   - Looking away from threat

3. PAIN:
   - Grimacing
   - Holding/touching body part
   - Tears or crying
   - Hunched posture

4. SADNESS/WITHDRAWAL:
   - Downturned mouth
   - Looking down/away
   - Isolated from group
   - Covering face with hands

==== NORMAL EXPRESSIONS (REJECT false positives) ====

1. CONCENTRATION:
   - Focused gaze
   - Neutral or slight frown
   - Engaged with task
   - No tears or distress signs

2. THINKING:
   - Hand on chin
   - Looking up or away
   - Relaxed posture

3. MILD FRUSTRATION:
   - Small frown
   - Still engaged
   - No tears or withdrawal
   - Temporary emotion

==== YOUR ANALYSIS ====

Look at the face area around {face_bbox_description}.

1. Describe the child's facial expression in detail:
   - Eyes: (wide/normal/squinting, wet/dry, looking where?)
   - Mouth: (open/closed, turned down/neutral/up)
   - Face color: (normal/red/pale)
   - Tears: (visible/not visible)

2. Body language:
   - Posture: (open/closed, tense/relaxed)
   - Hands: (covering face? defensive? relaxed?)
   - Position: (isolated? with others?)

3. Context:
   - What's happening around the child?
   - Are adults responding?
   - Duration: (momentary upset vs sustained distress)

4. Severity assessment:
   - IMMEDIATE attention needed?
   - Can wait for next check-in?
   - Normal emotional expression?

VERDICT:
- DISTRESS_CONFIRMED: Yes/No
- TYPE: crying | fear | pain | sadness | frustration | none
- SEVERITY: LOW | MEDIUM | HIGH | NONE
- IMMEDIATE_ATTENTION: Yes/No
- CONFIDENCE: 0.0-1.0
- EVIDENCE: [Specific observable facts]
- FAST_PATH_CORRECT: Yes/No

Remember: temporary upset (mild frustration, brief sadness) is normal. Only flag sustained distress or acute pain/fear."""


# Supervision-specific prompt
SUPERVISION_DETECTION_PROMPT = """You are a childcare safety expert analyzing supervision ratios.

FAST-PATH DETECTED:
- Adults counted: {adult_count}
- Children counted: {child_count}
- Ratio: {ratio:.2f}
- Required ratio: {required_ratio:.2f}
- Violation: {violation}

YOUR JOB: Validate the counts and assess supervision quality.

==== COUNTING GUIDELINES ====

ADULTS:
- Clearly taller/larger than children
- Adult clothing and proportions
- In supervisory position (standing, watching, interacting)
- Count ONLY visible adults (do not assume any off-screen)

CHILDREN:
- Smaller stature
- Child proportions
- Sitting at desks or playing
- Count ALL visible children

==== SUPERVISION QUALITY ====

ADEQUATE:
- Adults positioned to see all children
- Adults actively watching or interacting
- Adults within intervention distance (arms reach or close)

INADEQUATE:
- Adults distracted (on phone, facing away)
- Adults too far to intervene
- Blind spots where children are unsupervised

==== YOUR ANALYSIS ====

1. Count verification:
   - I see ___ adults (describe where each is)
   - I see ___ children (describe general positions)
   - Are there people partially visible? (describe)

2. Supervision quality:
   - Where are the adults positioned?
   - What are the adults doing?
   - Can adults see all children?
   - Are children in intervention range?

3. Special concerns:
   - Any children isolated or out of sight?
   - Any high-risk activities (climbing, water, etc.)?
   - Any children showing behavioral issues?

VERDICT:
- ADULTS_COUNTED: [number]
- CHILDREN_COUNTED: [number]
- RATIO: [calculated]
- RATIO_VIOLATION: Yes/No
- SUPERVISION_QUALITY: Adequate | Marginal | Inadequate
- CONFIDENCE: 0.0-1.0
- EVIDENCE: [What you actually see]
- FAST_PATH_CORRECT: Yes/No

Be conservative: if you can't see an adult, don't assume one exists."""


# Generic improved prompt (fallback)
IMPROVED_GENERIC_PROMPT = """You are a childcare safety expert analyzing this image.

CRITICAL: Be specific and factual. Do not hallucinate or assume.

ANALYZE:

1. PEOPLE VISIBLE:
   - Adults: [count and describe positions - if NONE visible, say "NO ADULTS VISIBLE"]
   - Children: [count and describe what they're doing]

2. PHYSICAL INTERACTIONS:
   - Any contact between children? [Yes/No]
   - If yes: TYPE [hitting/pushing/gentle touch/playing]
   - If yes: FORCE [light/moderate/forceful]
   - Any objects in hands? [describe what and how used]

3. EMOTIONAL STATE:
   - Any child showing distress? [Yes/No - be specific about WHICH child]
   - Evidence: [tears/facial expression/posture/isolation]

4. SAFETY HAZARDS:
   - Visible hazards: [describe or "none visible"]

CLASSIFY:
- VIOLATION: Yes/No
- TYPE: violence | distress | supervision | environment | none
- SEVERITY: LOW | MEDIUM | HIGH | NONE
- CONFIDENCE: 0.0-1.0
- EVIDENCE: [Specific facts you observed]

Provide EVIDENCE for your classification. Be exact."""


def get_prompt_with_context(
    prompt_type: str,
    fast_path_context: dict = None
) -> str:
    """
    Get appropriate prompt based on detection type and context

    Args:
        prompt_type: "violence", "distress", "supervision", or "general"
        fast_path_context: Context from fast-path detectors

    Returns:
        Formatted prompt string
    """
    if fast_path_context is None:
        fast_path_context = {}

    if prompt_type == "violence":
        violence = fast_path_context.get("violence", {})
        return VIOLENCE_DETECTION_PROMPT.format(
            confidence=violence.get("confidence", 0.5),
            action_type=violence.get("action_type", "unknown"),
            bbox_description=_bbox_to_description(violence.get("bbox"))
        )

    elif prompt_type == "distress":
        distress = fast_path_context.get("distress", {})
        return DISTRESS_DETECTION_PROMPT.format(
            confidence=distress.get("confidence", 0.5),
            emotion=distress.get("emotion", "unknown"),
            face_bbox_description=_bbox_to_description(distress.get("face_bbox"))
        )

    elif prompt_type == "supervision":
        supervision = fast_path_context.get("supervision", {})
        return SUPERVISION_DETECTION_PROMPT.format(
            adult_count=supervision.get("adult_count", 0),
            child_count=supervision.get("child_count", 0),
            ratio=supervision.get("ratio", 0.0),
            required_ratio=supervision.get("required_ratio", 0.25),
            violation="YES" if supervision.get("violation_detected") else "NO"
        )

    else:  # general
        return IMPROVED_GENERIC_PROMPT


def _bbox_to_description(bbox) -> str:
    """Convert bbox to human-readable description"""
    if bbox is None:
        return "entire image"

    x, y, w, h = bbox

    # Determine position
    if x < 300:
        h_pos = "left"
    elif x > 700:
        h_pos = "right"
    else:
        h_pos = "center"

    if y < 200:
        v_pos = "top"
    elif y > 400:
        v_pos = "bottom"
    else:
        v_pos = "middle"

    return f"{v_pos}-{h_pos} of the image (around pixel {x},{y})"
