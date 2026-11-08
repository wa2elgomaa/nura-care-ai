# 🚨 Route 1: Incident Detection & Alert - Implementation Spec

**Status:** 70% → 100%  
**Timeline:** 2 weeks  
**Priority:** P0 - CRITICAL

---

## 📋 Overview

**Goal:** Complete incident detection with person identification and video evidence

**Current State:**
- ✅ AI detectors working (violence, distress, body language, supervision)
- ✅ Alert service operational (email working)
- ✅ Person tracking and face recognition working
- ⚠️ Missing: Person names in alerts, video evidence, safety hazards

**Target State:**
- ✅ All incident types detected (violence, distress, unsupervised, abuse, safety)
- ✅ Person names and images in alerts
- ✅ Video evidence clips attached
- ✅ WiFi sensing integrated for bathroom monitoring
- ✅ Safety hazard detection (knife, stairs)

---

## 🎯 Missing Components

### 1. Enhanced Alert Payload with Person Identity
**Status:** Not implemented  
**Effort:** 3 days  
**Assigned to:** Backend Engineer

#### Current Alert Payload
```typescript
// Current (services/nura-alerts/src/models/alert.model.ts)
interface Alert {
  alert_id: string;
  type: 'violence' | 'distress' | 'supervision' | 'body_language';
  confidence: number;
  timestamp: string;
  camera_id: string;
  zone?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
}
```

#### Target Alert Payload
```typescript
// Target (NEW)
interface Alert {
  alert_id: string;
  type: 'violence' | 'distress' | 'supervision' | 'body_language' | 'stranger' | 'safety_hazard';
  confidence: number;
  timestamp: string;
  camera_id: string;
  zone?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  
  // NEW: Person identification
  persons_involved: PersonInAlert[];
  
  // NEW: Evidence
  evidence: AlertEvidence;
  
  // NEW: Context
  context: AlertContext;
}

interface PersonInAlert {
  person_id: string;
  name: string;                    // From enrollment DB
  role: 'child' | 'staff' | 'visitor' | 'unknown';
  confidence: number;              // Face recognition confidence
  image_url: string;               // Face crop from frame
  bbox: [number, number, number, number]; // [x, y, w, h]
  is_primary_subject: boolean;     // Main person in incident
}

interface AlertEvidence {
  snapshot_url: string;            // Single frame
  clip_url?: string;               // 10-30s video clip
  clip_duration_seconds?: number;
  frame_annotations?: {
    bboxes: Array<{
      person_id: string;
      bbox: [number, number, number, number];
      label: string;
    }>;
    zones: Array<{
      zone_id: string;
      polygon: number[][];
      label: string;
    }>;
  };
}

interface AlertContext {
  detection_method: 'fast_path' | 'vlm_validation' | 'hybrid';
  detector_scores: {
    violence?: number;
    distress?: number;
    supervision?: number;
    body_language?: number;
  };
  vlm_analysis?: string;           // VLM explanation if validated
  environment: {
    time_of_day: 'morning' | 'afternoon' | 'evening' | 'night';
    occupancy_count: number;
    adults_present: number;
    children_present: number;
  };
}
```

#### Implementation Tasks

**Task 1.1: Update Alert Model Schema** (4 hours)
```bash
# File: services/nura-alerts/src/models/alert.model.ts

1. Add new interfaces (PersonInAlert, AlertEvidence, AlertContext)
2. Update Alert interface
3. Create database migration for new fields
4. Update TypeORM entity

# File: edge/postgres/migrations/006_enhanced_alerts.sql
ALTER TABLE alerts 
  ADD COLUMN persons_involved JSONB,
  ADD COLUMN evidence JSONB,
  ADD COLUMN context JSONB;

CREATE INDEX idx_alerts_persons ON alerts USING GIN (persons_involved);
```

**Task 1.2: Modify VLM Service Response** (8 hours)
```python
# File: services/nura-vlm/src/hybrid_router.py

class HybridAnalysisResponse(BaseModel):
    """Enhanced response with person identification"""
    
    # Existing fields
    detections: Dict[str, float]
    decision: str
    confidence: float
    
    # NEW: Person tracking
    persons_detected: List[PersonDetection]
    
    # NEW: Evidence data
    annotated_frame: Optional[str]  # Base64 encoded
    
    # NEW: Context
    analysis_context: AnalysisContext

class PersonDetection(BaseModel):
    track_id: int
    person_id: Optional[str]        # From face recognition
    name: Optional[str]             # From enrollment DB
    role: Optional[str]             # child, staff, unknown
    confidence: float
    bbox: List[int]                 # [x, y, w, h]
    face_image: Optional[str]       # Base64 face crop
    is_primary_subject: bool        # Main person in incident

class AnalysisContext(BaseModel):
    detection_method: str
    detector_scores: Dict[str, float]
    vlm_analysis: Optional[str]
    environment: EnvironmentContext

class EnvironmentContext(BaseModel):
    occupancy_count: int
    adults_present: int
    children_present: int
```

**Implementation:**
```python
# File: services/nura-vlm/src/hybrid_router.py

async def analyze_frame_hybrid(
    self,
    frame: np.ndarray,
    camera_id: str,
    timestamp: datetime
) -> HybridAnalysisResponse:
    """Enhanced analysis with person identification"""
    
    # Step 1: Person tracking (existing)
    tracks = self.person_tracker.track(frame)
    
    # Step 2: Face recognition for each track
    persons_detected = []
    for track in tracks:
        # Extract face ROI
        face_roi = extract_face_roi(frame, track.bbox)
        
        if face_roi is not None:
            # Identify person
            person_id, confidence = self.face_identifier.identify(face_roi)
            
            if person_id:
                # Fetch person details from DB
                person_data = await self._get_person_details(person_id)
                
                persons_detected.append(PersonDetection(
                    track_id=track.id,
                    person_id=person_id,
                    name=person_data.get('name'),
                    role=person_data.get('role'),
                    confidence=confidence,
                    bbox=track.bbox,
                    face_image=encode_base64(face_roi),
                    is_primary_subject=False  # Will determine later
                ))
            else:
                # Unknown person
                persons_detected.append(PersonDetection(
                    track_id=track.id,
                    person_id=None,
                    name="Unknown",
                    role="unknown",
                    confidence=0.0,
                    bbox=track.bbox,
                    face_image=encode_base64(face_roi),
                    is_primary_subject=False
                ))
    
    # Step 3: Run detectors (existing)
    violence_result = self.violence_detector.detect(frame)
    distress_result = self.distress_detector.detect(frame)
    supervision_result = self.supervision_detector.detect(frame)
    body_language_result = self.body_language_detector.detect(frame)
    
    # Step 4: Determine primary subject (person closest to incident)
    if len(persons_detected) > 0:
        # Find person in center of frame or with highest distress score
        primary_idx = self._determine_primary_subject(
            persons_detected,
            distress_result,
            violence_result
        )
        if primary_idx >= 0:
            persons_detected[primary_idx].is_primary_subject = True
    
    # Step 5: VLM validation if needed (existing logic)
    # ...
    
    # Step 6: Build response
    return HybridAnalysisResponse(
        detections={
            'violence': violence_result.confidence,
            'distress': distress_result.confidence,
            'supervision': supervision_result.confidence,
            'body_language': body_language_result.confidence
        },
        decision=decision,
        confidence=max_confidence,
        persons_detected=persons_detected,
        annotated_frame=self._annotate_frame(frame, persons_detected),
        analysis_context=AnalysisContext(
            detection_method='hybrid',
            detector_scores={...},
            vlm_analysis=vlm_text if vlm_used else None,
            environment=EnvironmentContext(
                occupancy_count=len(tracks),
                adults_present=count_adults(persons_detected),
                children_present=count_children(persons_detected)
            )
        )
    )

async def _get_person_details(self, person_id: str) -> Dict:
    """Fetch person details from database"""
    async with self.db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT name, role FROM persons WHERE person_id = $1",
            person_id
        )
        if row:
            return dict(row)
        return {}

def _determine_primary_subject(
    self,
    persons: List[PersonDetection],
    distress_result,
    violence_result
) -> int:
    """Determine which person is the primary subject of the incident"""
    
    # If distress detected, find person with open mouth (crying)
    if distress_result.confidence > 0.7:
        # Use distress detector's face analysis
        if hasattr(distress_result, 'distressed_person_bbox'):
            # Find matching person
            for idx, person in enumerate(persons):
                if bbox_iou(person.bbox, distress_result.distressed_person_bbox) > 0.5:
                    return idx
    
    # If violence, find person closest to center of action
    if violence_result.confidence > 0.7:
        # Use motion vectors to find active person
        # (simplified: just use center-most person)
        frame_center = np.array([frame.shape[1] / 2, frame.shape[0] / 2])
        distances = [
            np.linalg.norm(bbox_center(p.bbox) - frame_center)
            for p in persons
        ]
        return np.argmin(distances)
    
    # Default: first person
    return 0 if len(persons) > 0 else -1

def _annotate_frame(
    self,
    frame: np.ndarray,
    persons: List[PersonDetection]
) -> str:
    """Draw bounding boxes and labels on frame"""
    annotated = frame.copy()
    
    for person in persons:
        x, y, w, h = person.bbox
        color = (0, 255, 0) if person.role in ['child', 'staff'] else (0, 0, 255)
        
        # Draw bbox
        cv2.rectangle(annotated, (x, y), (x+w, y+h), color, 2)
        
        # Draw label
        label = f"{person.name} ({person.confidence:.2f})"
        if person.is_primary_subject:
            label = "⚠️ " + label
        
        cv2.putText(annotated, label, (x, y-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return encode_base64(annotated)
```

**Task 1.3: Update Alert Service** (8 hours)
```typescript
// File: services/nura-alerts/src/services/alert.service.ts

async createAlert(alertData: CreateAlertDto): Promise<Alert> {
  // Extract person IDs from VLM response
  const personsInvolved: PersonInAlert[] = [];
  
  if (alertData.persons_detected && alertData.persons_detected.length > 0) {
    for (const person of alertData.persons_detected) {
      personsInvolved.push({
        person_id: person.person_id || 'unknown',
        name: person.name || 'Unknown Person',
        role: person.role || 'unknown',
        confidence: person.confidence,
        image_url: await this.savePersonImage(person.face_image, alertData.alert_id),
        bbox: person.bbox,
        is_primary_subject: person.is_primary_subject
      });
    }
  }
  
  // Build evidence
  const evidence: AlertEvidence = {
    snapshot_url: await this.saveSnapshot(alertData.annotated_frame, alertData.alert_id),
    clip_url: null, // Will be added in Task 2
    clip_duration_seconds: null
  };
  
  // Build context
  const context: AlertContext = {
    detection_method: alertData.analysis_context.detection_method,
    detector_scores: alertData.analysis_context.detector_scores,
    vlm_analysis: alertData.analysis_context.vlm_analysis,
    environment: alertData.analysis_context.environment
  };
  
  // Create alert
  const alert = await this.alertRepository.save({
    ...alertData,
    persons_involved: personsInvolved,
    evidence,
    context
  });
  
  // Send notifications with person names
  await this.sendNotifications(alert);
  
  return alert;
}

async savePersonImage(base64Image: string, alertId: string): Promise<string> {
  const filename = `${alertId}_person_${Date.now()}.jpg`;
  const filepath = path.join(this.config.storage.alerts, filename);
  
  // Decode and save
  const buffer = Buffer.from(base64Image, 'base64');
  await fs.writeFile(filepath, buffer);
  
  return `/api/alerts/${alertId}/persons/${filename}`;
}

async saveSnapshot(base64Image: string, alertId: string): Promise<string> {
  const filename = `${alertId}_snapshot.jpg`;
  const filepath = path.join(this.config.storage.alerts, filename);
  
  const buffer = Buffer.from(base64Image, 'base64');
  await fs.writeFile(filepath, buffer);
  
  return `/api/alerts/${alertId}/snapshot.jpg`;
}
```

**Task 1.4: Update Email Notifications** (4 hours)
```typescript
// File: services/nura-alerts/src/services/notification.service.ts

async sendEmailAlert(alert: Alert): Promise<void> {
  // Get primary person
  const primaryPerson = alert.persons_involved.find(p => p.is_primary_subject);
  const otherPersons = alert.persons_involved.filter(p => !p.is_primary_subject);
  
  const subject = primaryPerson
    ? `🚨 ${alert.type.toUpperCase()} Alert - ${primaryPerson.name}`
    : `🚨 ${alert.type.toUpperCase()} Alert`;
  
  const html = `
    <h2>Alert: ${alert.type}</h2>
    <p><strong>Time:</strong> ${alert.timestamp}</p>
    <p><strong>Location:</strong> ${alert.camera_id} - ${alert.zone || 'N/A'}</p>
    <p><strong>Severity:</strong> ${alert.severity}</p>
    <p><strong>Confidence:</strong> ${(alert.confidence * 100).toFixed(1)}%</p>
    
    <h3>Persons Involved:</h3>
    ${primaryPerson ? `
      <div style="border: 2px solid red; padding: 10px; margin: 10px 0;">
        <h4>⚠️ Primary Subject</h4>
        <img src="cid:primary_person" width="150" />
        <p><strong>${primaryPerson.name}</strong> (${primaryPerson.role})</p>
        <p>Confidence: ${(primaryPerson.confidence * 100).toFixed(1)}%</p>
      </div>
    ` : ''}
    
    ${otherPersons.length > 0 ? `
      <h4>Other Persons Present:</h4>
      <ul>
        ${otherPersons.map(p => `
          <li>${p.name} (${p.role}) - ${(p.confidence * 100).toFixed(1)}%</li>
        `).join('')}
      </ul>
    ` : ''}
    
    <h3>Evidence:</h3>
    <img src="cid:snapshot" width="600" />
    
    <h3>Analysis:</h3>
    <p>${alert.context.vlm_analysis || alert.description}</p>
    
    <p><strong>Detection Method:</strong> ${alert.context.detection_method}</p>
    <p><strong>Environment:</strong> ${alert.context.environment.occupancy_count} persons 
       (${alert.context.environment.adults_present} adults, ${alert.context.environment.children_present} children)</p>
    
    <hr>
    <p><small>Alert ID: ${alert.alert_id}</small></p>
  `;
  
  // Attach images
  const attachments = [
    {
      filename: 'snapshot.jpg',
      path: alert.evidence.snapshot_url,
      cid: 'snapshot'
    }
  ];
  
  if (primaryPerson) {
    attachments.push({
      filename: 'primary_person.jpg',
      path: primaryPerson.image_url,
      cid: 'primary_person'
    });
  }
  
  await this.mailer.sendMail({
    to: this.config.alert.email_recipients,
    subject,
    html,
    attachments
  });
}
```

---

### 2. Video Evidence Clips
**Status:** Not implemented  
**Effort:** 3 days  
**Assigned to:** Backend Engineer

#### Implementation Tasks

**Task 2.1: Frigate Clip Integration** (8 hours)
```typescript
// File: services/nura-alerts/src/services/evidence.service.ts

export class EvidenceService {
  constructor(
    private readonly frigateClient: FrigateClient,
    private readonly config: ConfigService
  ) {}
  
  async getClipForEvent(
    cameraId: string,
    timestamp: Date,
    beforeSeconds: number = 10,
    afterSeconds: number = 20
  ): Promise<string | null> {
    try {
      // Calculate clip window
      const startTime = new Date(timestamp.getTime() - beforeSeconds * 1000);
      const endTime = new Date(timestamp.getTime() + afterSeconds * 1000);
      
      // Query Frigate for clip
      const clip = await this.frigateClient.exportClip({
        camera: cameraId,
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
        playback: 'realtime' // or 'timelapse'
      });
      
      if (!clip) {
        this.logger.warn(`No clip available for ${cameraId} at ${timestamp}`);
        return null;
      }
      
      // Save clip to local storage
      const filename = `clip_${cameraId}_${timestamp.getTime()}.mp4`;
      const filepath = path.join(this.config.storage.clips, filename);
      
      await fs.writeFile(filepath, clip.data);
      
      return filepath;
    } catch (error) {
      this.logger.error(`Failed to get clip: ${error.message}`);
      return null;
    }
  }
  
  async attachClipToAlert(alertId: string): Promise<void> {
    const alert = await this.alertRepository.findOne({ where: { alert_id: alertId } });
    if (!alert) return;
    
    // Get clip from Frigate
    const clipPath = await this.getClipForEvent(
      alert.camera_id,
      new Date(alert.timestamp),
      10, // 10 seconds before
      20  // 20 seconds after
    );
    
    if (clipPath) {
      // Update alert evidence
      alert.evidence.clip_url = `/api/alerts/${alertId}/clip.mp4`;
      alert.evidence.clip_duration_seconds = 30;
      
      await this.alertRepository.save(alert);
      
      this.logger.log(`Attached clip to alert ${alertId}`);
    }
  }
}
```

**Task 2.2: Frigate API Client** (4 hours)
```typescript
// File: services/nura-alerts/src/clients/frigate.client.ts

export class FrigateClient {
  constructor(private readonly httpService: HttpService) {}
  
  async exportClip(params: {
    camera: string;
    start_time: string;
    end_time: string;
    playback?: 'realtime' | 'timelapse';
  }): Promise<{ data: Buffer } | null> {
    try {
      const response = await this.httpService.axiosRef.get(
        `${process.env.FRIGATE_API}/api/export/${params.camera}/start/${params.start_time}/end/${params.end_time}`,
        {
          params: {
            playback: params.playback || 'realtime'
          },
          responseType: 'arraybuffer'
        }
      );
      
      return { data: Buffer.from(response.data) };
    } catch (error) {
      console.error(`Frigate export failed: ${error.message}`);
      return null;
    }
  }
  
  async getSnapshot(camera: string, timestamp?: string): Promise<Buffer | null> {
    try {
      const url = timestamp
        ? `${process.env.FRIGATE_API}/api/${camera}/snapshot/${timestamp}`
        : `${process.env.FRIGATE_API}/api/${camera}/latest.jpg`;
      
      const response = await this.httpService.axiosRef.get(url, {
        responseType: 'arraybuffer'
      });
      
      return Buffer.from(response.data);
    } catch (error) {
      console.error(`Frigate snapshot failed: ${error.message}`);
      return null;
    }
  }
}
```

**Task 2.3: Clip Serving API** (4 hours)
```typescript
// File: services/nura-alerts/src/controllers/alert.controller.ts

@Controller('api/alerts')
export class AlertController {
  constructor(private readonly alertService: AlertService) {}
  
  @Get(':id/clip.mp4')
  @Header('Content-Type', 'video/mp4')
  async getAlertClip(@Param('id') alertId: string, @Res() res: Response): Promise<void> {
    const alert = await this.alertService.findOne(alertId);
    
    if (!alert || !alert.evidence.clip_url) {
      throw new NotFoundException('Clip not found');
    }
    
    // Get local file path
    const filepath = alert.evidence.clip_url.replace('/api/alerts/', '/data/alerts/');
    
    if (!await fs.pathExists(filepath)) {
      throw new NotFoundException('Clip file not found');
    }
    
    // Stream the file
    const stream = createReadStream(filepath);
    stream.pipe(res);
  }
  
  @Get(':id/snapshot.jpg')
  @Header('Content-Type', 'image/jpeg')
  async getAlertSnapshot(@Param('id') alertId: string, @Res() res: Response): Promise<void> {
    const alert = await this.alertService.findOne(alertId);
    
    if (!alert || !alert.evidence.snapshot_url) {
      throw new NotFoundException('Snapshot not found');
    }
    
    const filepath = alert.evidence.snapshot_url.replace('/api/alerts/', '/data/alerts/');
    
    if (!await fs.pathExists(filepath)) {
      throw new NotFoundException('Snapshot file not found');
    }
    
    const stream = createReadStream(filepath);
    stream.pipe(res);
  }
}
```

**Task 2.4: Background Clip Attachment** (4 hours)
```typescript
// File: services/nura-alerts/src/services/alert.service.ts

async createAlert(alertData: CreateAlertDto): Promise<Alert> {
  // ... existing alert creation ...
  
  // Schedule clip attachment in background
  this.scheduleClipAttachment(alert.alert_id);
  
  return alert;
}

private async scheduleClipAttachment(alertId: string): Promise<void> {
  // Wait 30 seconds for Frigate to finish recording clip
  setTimeout(async () => {
    try {
      await this.evidenceService.attachClipToAlert(alertId);
    } catch (error) {
      this.logger.error(`Failed to attach clip to alert ${alertId}: ${error.message}`);
    }
  }, 30000);
}
```

---

### 3. Safety Hazard Detector (Knife/Stairs)
**Status:** Dataset ready, not trained  
**Effort:** 1 week  
**Assigned to:** ML Engineer

#### Implementation Tasks

**Task 3.1: Training Script** (8 hours)
```python
# File: training/train_safety_detector.py

import tensorflow as tf
from tensorflow import keras
import numpy as np
from pathlib import Path
import argparse

def prepare_safety_dataset(dataset_path: Path):
    """Prepare knife/staircase detection dataset"""
    
    # Classes: knife, staircase, safe
    classes = {
        'knife': 0,
        'staircase': 1,
        'safe': 2
    }
    
    images = []
    labels = []
    
    # Load ToddlerActions dataset
    knife_dir = dataset_path / 'train' / 'Toddler with knife'
    staircase_dir = dataset_path / 'train' / 'Toddler on staircase'
    
    # Knife samples
    for img_path in knife_dir.glob('*.jpg'):
        images.append(str(img_path))
        labels.append(classes['knife'])
    
    # Staircase samples
    for img_path in staircase_dir.glob('*.jpg'):
        images.append(str(img_path))
        labels.append(classes['staircase'])
    
    # Safe samples (from other classes)
    safe_classes = ['Toddler playing', 'Toddler eating', 'Toddler drinking', 
                    'Toddler smiling', 'Toddler sleeping']
    for class_name in safe_classes:
        class_dir = dataset_path / 'train' / class_name
        # Sample 20% to balance dataset
        sample_size = len(list(class_dir.glob('*.jpg'))) // 5
        for img_path in list(class_dir.glob('*.jpg'))[:sample_size]:
            images.append(str(img_path))
            labels.append(classes['safe'])
    
    print(f"Dataset prepared:")
    print(f"  Knife: {labels.count(0)} samples")
    print(f"  Staircase: {labels.count(1)} samples")
    print(f"  Safe: {labels.count(2)} samples")
    
    return np.array(images), np.array(labels)

def create_safety_model(input_shape=(224, 224, 3), num_classes=3):
    """Create safety hazard detection model"""
    
    # Use MobileNetV3Small for edge deployment
    base_model = keras.applications.MobileNetV3Small(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model
    base_model.trainable = False
    
    # Add classification head
    model = keras.Sequential([
        base_model,
        keras.layers.GlobalAveragePooling2D(),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def train_safety_detector(
    dataset_path: Path,
    output_path: Path,
    epochs: int = 30,
    batch_size: int = 32
):
    """Train safety hazard detector"""
    
    # Prepare dataset
    images, labels = prepare_safety_dataset(dataset_path)
    
    # Split train/val
    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(
        images, labels, test_size=0.2, stratify=labels, random_state=42
    )
    
    # Data generators
    datagen = keras.preprocessing.image.ImageDataGenerator(
        preprocessing_function=keras.applications.mobilenet_v3.preprocess_input,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2
    )
    
    def load_and_preprocess(img_paths, labels):
        for img_path, label in zip(img_paths, labels):
            img = keras.preprocessing.image.load_img(img_path, target_size=(224, 224))
            img_array = keras.preprocessing.image.img_to_array(img)
            yield img_array, keras.utils.to_categorical(label, 3)
    
    train_gen = tf.data.Dataset.from_generator(
        lambda: load_and_preprocess(X_train, y_train),
        output_signature=(
            tf.TensorSpec(shape=(224, 224, 3), dtype=tf.float32),
            tf.TensorSpec(shape=(3,), dtype=tf.float32)
        )
    ).batch(batch_size).prefetch(tf.data.AUTOTUNE)
    
    val_gen = tf.data.Dataset.from_generator(
        lambda: load_and_preprocess(X_val, y_val),
        output_signature=(
            tf.TensorSpec(shape=(224, 224, 3), dtype=tf.float32),
            tf.TensorSpec(shape=(3,), dtype=tf.float32)
        )
    ).batch(batch_size).prefetch(tf.data.AUTOTUNE)
    
    # Create model
    model = create_safety_model()
    
    # Compile
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
    # Callbacks
    callbacks = [
        keras.callbacks.ModelCheckpoint(
            str(output_path / 'safety_detector_best.keras'),
            monitor='val_accuracy',
            save_best_only=True
        ),
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3
        )
    ]
    
    # Train
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=epochs,
        callbacks=callbacks
    )
    
    # Fine-tune (unfreeze top layers)
    model.layers[0].trainable = True
    for layer in model.layers[0].layers[:-10]:
        layer.trainable = False
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-4),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
    history_fine = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=20,
        callbacks=callbacks
    )
    
    # Save final model
    model.save(output_path / 'safety_detector_final.keras')
    
    # Evaluate
    results = model.evaluate(val_gen)
    print(f"\nFinal Results:")
    print(f"  Accuracy: {results[1]:.2%}")
    print(f"  Precision: {results[2]:.2%}")
    print(f"  Recall: {results[3]:.2%}")
    
    return model

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='datasets/ToddlerActions')
    parser.add_argument('--output', type=str, default='models/')
    parser.add_argument('--epochs', type=int, default=30)
    args = parser.parse_args()
    
    train_safety_detector(
        Path(args.dataset),
        Path(args.output),
        epochs=args.epochs
    )
```

**Task 3.2: Safety Detector Service** (8 hours)
```python
# File: services/nura-vlm/src/detectors/safety_detector.py

import cv2
import numpy as np
from tensorflow import keras
from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class SafetyDetection:
    has_hazard: bool
    hazard_type: str  # 'knife', 'staircase', 'none'
    confidence: float
    bbox: Tuple[int, int, int, int]  # If hazard detected
    description: str

class SafetyHazardDetector:
    """Detect safety hazards (knife, staircase)"""
    
    def __init__(self, model_path: str):
        self.model = keras.models.load_model(model_path)
        self.classes = ['knife', 'staircase', 'safe']
        self.input_size = (224, 224)
    
    def detect(self, frame: np.ndarray) -> SafetyDetection:
        """Detect safety hazards in frame"""
        
        # Preprocess
        resized = cv2.resize(frame, self.input_size)
        preprocessed = keras.applications.mobilenet_v3.preprocess_input(resized)
        batch = np.expand_dims(preprocessed, axis=0)
        
        # Predict
        predictions = self.model.predict(batch, verbose=0)[0]
        
        # Get class and confidence
        class_idx = np.argmax(predictions)
        confidence = float(predictions[class_idx])
        hazard_type = self.classes[class_idx]
        
        # If safe, return early
        if hazard_type == 'safe':
            return SafetyDetection(
                has_hazard=False,
                hazard_type='none',
                confidence=confidence,
                bbox=(0, 0, 0, 0),
                description="No safety hazards detected"
            )
        
        # Localize hazard (simple saliency map)
        bbox = self._localize_hazard(frame, hazard_type)
        
        return SafetyDetection(
            has_hazard=True,
            hazard_type=hazard_type,
            confidence=confidence,
            bbox=bbox,
            description=f"{hazard_type.capitalize()} detected with {confidence:.1%} confidence"
        )
    
    def _localize_hazard(
        self,
        frame: np.ndarray,
        hazard_type: str
    ) -> Tuple[int, int, int, int]:
        """Localize hazard in frame (simplified)"""
        
        # For production, use GradCAM or similar
        # For now, return center region
        h, w = frame.shape[:2]
        x, y = w // 4, h // 4
        w, h = w // 2, h // 2
        
        return (x, y, w, h)

# Usage
def detect_safety_hazard(frame: np.ndarray, use_ml: bool = True) -> Dict:
    """Detect safety hazards (public API)"""
    
    if not use_ml:
        return {
            'has_hazard': False,
            'hazard_type': 'none',
            'confidence': 0.0,
            'description': 'ML detection disabled'
        }
    
    detector = SafetyHazardDetector('models/safety_detector_final.keras')
    result = detector.detect(frame)
    
    return {
        'has_hazard': result.has_hazard,
        'hazard_type': result.hazard_type,
        'confidence': result.confidence,
        'bbox': result.bbox,
        'description': result.description
    }
```

**Task 3.3: Integration into Hybrid Router** (4 hours)
```python
# File: services/nura-vlm/src/hybrid_router.py

# Add to HybridRouter class

async def analyze_frame_hybrid(self, frame, camera_id, timestamp):
    # ... existing detectors ...
    
    # NEW: Safety hazard detection
    safety_result = self.safety_detector.detect(frame)
    
    # Update detections
    detections['safety_hazard'] = safety_result.confidence if safety_result.has_hazard else 0.0
    
    # If hazard detected, immediate alert
    if safety_result.has_hazard and safety_result.confidence > 0.7:
        decision = 'ALERT'
        reason = f"Safety hazard detected: {safety_result.hazard_type}"
    
    # ... rest of logic ...
```

---

### 4. WiFi Sensing Integration (Bathroom Monitoring)
**Status:** Not implemented  
**Effort:** 1 week  
**Assigned to:** Backend Engineer + IoT Engineer

#### Implementation Tasks

**Task 4.1: RuView Integration Service** (2 days)
See [ROUTE_1_IMPLEMENTATION.md] for full WiFi sensing spec...

---

## 📊 Testing Plan

### Unit Tests
```bash
# Test person identification
npm test services/nura-vlm/tests/person-identification.test.ts

# Test alert payload
npm test services/nura-alerts/tests/alert-payload.test.ts

# Test video evidence
npm test services/nura-alerts/tests/evidence.test.ts

# Test safety detector
python -m pytest training/tests/test_safety_detector.py
```

### Integration Tests
```bash
# Test full flow
./tests/integration/test_route1_complete.sh

# Expected:
# 1. Trigger incident (crying child)
# 2. Verify alert created with person name
# 3. Verify video clip attached
# 4. Verify email sent with person image
```

### Acceptance Criteria
- [ ] Person names appear in 90%+ of alerts (when face visible)
- [ ] Video evidence attached to 100% of alerts
- [ ] Safety hazard detector 80%+ accuracy
- [ ] Email notifications include person images
- [ ] Alert latency <10 seconds end-to-end

---

## 📋 Deployment Checklist

- [ ] Database migration applied
- [ ] VLM service updated and tested
- [ ] Alert service updated and tested
- [ ] Frigate integration tested
- [ ] Safety model trained and deployed
- [ ] Email templates updated
- [ ] Storage directories created
- [ ] Environment variables configured
- [ ] Integration tests passing
- [ ] Documentation updated

---

**Estimated Completion:** 2 weeks (10 working days)  
**Status:** Ready to implement
