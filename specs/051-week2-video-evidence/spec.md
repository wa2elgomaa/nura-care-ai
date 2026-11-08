# Feature Specification: Week 2 - Video Evidence Clips

**Feature Branch**: `051-week2-video-evidence`

**Created**: 2026-11-08

**Status**: Ready for Implementation

**Sprint**: Core Safety Routes - Week 2 of 8

**Input**: Route 1 (Incident Detection) - Attach 10-30s video clips to all alerts as evidence

## Overview

Integrate with Frigate NVR to automatically attach video clips to all incident alerts. When an alert is created, the system should retrieve a video clip (10s before + 20s after the incident) and attach it to the alert for evidence.

**Current State:** Alerts contain snapshots only  
**Target State:** Alerts contain 30-second video clips showing incident context

**Dependencies:**
- Week 1: Enhanced alerts completed ✅
- Frigate NVR operational ✅
- Storage space for video clips (~10MB × 100 alerts/day = 1GB/day)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Incident Video Evidence (Priority: P1)

As a school administrator, when reviewing an incident alert, I need to watch a video clip of what happened (not just a snapshot) so I can understand the full context and take appropriate action.

**Why this priority**: A single snapshot can be misleading. Video shows what led to the incident, what happened during, and what happened after - critical for fair assessment.

**Independent Test**: Can be fully tested by triggering an alert, waiting 30s for clip attachment, then verifying the clip URL is accessible and shows 30s of video.

**Acceptance Scenarios**:

1. **Given** a distress alert is triggered at 10:30:15,
   **When** the clip attachment job runs (30s later),
   **Then** a video clip from 10:30:05 to 10:30:35 is attached
   **And** the clip URL is `/api/alerts/{alert_id}/clip.mp4`
   **And** the clip duration is 30 seconds

2. **Given** an alert email is sent,
   **When** I click the "View Video Evidence" link,
   **Then** the video clip plays in my browser
   **And** shows 10s before + 20s after the incident

3. **Given** Frigate has no recording for the time period,
   **When** the clip attachment job runs,
   **Then** the alert is updated with `clip_url: null`
   **And** a warning is logged: "No clip available for camera X at time Y"

---

### User Story 2 - Email Notifications with Video Links (Priority: P1)

As a school administrator, when I receive an alert email, I need a direct link to watch the video clip so I can assess the situation immediately without logging into the system.

**Why this priority**: Email is the primary notification channel. Quick access to video enables faster response.

**Independent Test**: Can be tested by triggering an alert, receiving the email, and clicking the video link.

**Acceptance Scenarios**:

1. **Given** an alert with attached video clip,
   **When** the email notification is sent,
   **Then** the email contains a button: "▶️ Watch Video Evidence (30s)"
   **And** clicking it opens the video in a browser

2. **Given** the video clip is not yet attached (still processing),
   **When** the email is sent,
   **Then** the email shows: "⏳ Video processing - will be available in ~30 seconds"
   **And** includes a link to refresh

3. **Given** no video is available,
   **When** the email is sent,
   **Then** the email shows: "📷 Snapshot only (no video recording available)"

---

### User Story 3 - Clip Storage Management (Priority: P2)

As a system administrator, I need old video clips to be automatically deleted after the retention period (30 days default) so storage doesn't fill up.

**Why this priority**: Video clips consume significant storage. Without cleanup, the system will run out of disk space.

**Independent Test**: Can be tested by creating old clips (backdated), running cleanup job, and verifying they're deleted.

**Acceptance Scenarios**:

1. **Given** video clips older than 30 days,
   **When** the cleanup job runs daily,
   **Then** old clips are deleted from storage
   **And** alert records are updated with `clip_deleted: true`

2. **Given** an alert with deleted clip,
   **When** I try to access the clip URL,
   **Then** I receive a 410 Gone status
   **And** message: "Video clip expired (retention period: 30 days)"

3. **Given** storage is 90% full,
   **When** the cleanup job runs,
   **Then** it deletes oldest clips first until storage < 80%
   **And** logs a warning about storage pressure

---

### Edge Cases

1. **Frigate API timeout** - Clip export takes >60s
   - **Expected**: Job retries 3 times, then marks clip as unavailable
   - **Test**: Simulate slow Frigate API, verify retry logic

2. **Clip file corrupted** - Downloaded clip is not valid MP4
   - **Expected**: Job detects corruption, deletes file, retries download
   - **Test**: Inject corrupted data, verify re-download

3. **Storage full** - No space to save clip
   - **Expected**: Emergency cleanup triggered, old clips deleted
   - **Test**: Fill storage to 99%, trigger alert, verify cleanup

4. **Clip spans camera restart** - Frigate restarted during incident
   - **Expected**: Partial clip saved if available, or null if unavailable
   - **Test**: Restart Frigate mid-incident, verify graceful handling

5. **Multiple concurrent clip requests** - 10 alerts at once
   - **Expected**: Queue system handles requests, no race conditions
   - **Test**: Trigger 10 alerts simultaneously, verify all get clips

---

## Data Model

### Updated Alert Schema

```typescript
interface Alert {
  // ... existing fields from Week 1 ...
  
  evidence: AlertEvidence;  // Updated
}

interface AlertEvidence {
  snapshot_url: string;
  
  // NEW: Video clip fields
  clip_url: string | null;
  clip_duration_seconds: number | null;
  clip_start_time: string | null;    // ISO timestamp
  clip_end_time: string | null;      // ISO timestamp
  clip_size_bytes: number | null;
  clip_status: 'pending' | 'available' | 'unavailable' | 'deleted';
  clip_error?: string;                // If clip_status = unavailable
}
```

### Database Migration

```sql
-- File: edge/postgres/migrations/007_video_clips.sql

-- Update alerts table
ALTER TABLE alerts 
  ALTER COLUMN evidence TYPE JSONB USING evidence::JSONB;

-- Add clip processing queue
CREATE TABLE clip_processing_queue (
  queue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id UUID REFERENCES alerts(alert_id) ON DELETE CASCADE,
  camera_id VARCHAR(255) NOT NULL,
  incident_timestamp TIMESTAMP NOT NULL,
  before_seconds INTEGER DEFAULT 10,
  after_seconds INTEGER DEFAULT 20,
  status VARCHAR(50) DEFAULT 'pending',  -- pending, processing, completed, failed
  retry_count INTEGER DEFAULT 0,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP,
  
  CONSTRAINT valid_status CHECK (status IN ('pending', 'processing', 'completed', 'failed'))
);

CREATE INDEX idx_queue_status ON clip_processing_queue(status, created_at);
CREATE INDEX idx_queue_alert ON clip_processing_queue(alert_id);

-- Clip retention tracking
CREATE TABLE clip_retention (
  clip_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id UUID REFERENCES alerts(alert_id) ON DELETE CASCADE,
  file_path VARCHAR(500) NOT NULL,
  file_size_bytes BIGINT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL,
  deleted_at TIMESTAMP
);

CREATE INDEX idx_clip_expires ON clip_retention(expires_at) WHERE deleted_at IS NULL;
```

---

## Technical Architecture

### Component Changes

**1. Alert Service - Clip Processing Worker**
- New background job: `ClipProcessingWorker`
- Polls `clip_processing_queue` every 10s
- Downloads clips from Frigate
- Updates alerts with clip URLs

**2. Frigate API Client**
- Export clip endpoint integration
- Streaming download (no memory issues)
- Retry logic for failures

**3. Storage Management**
- Daily cleanup job
- Storage monitoring
- Emergency cleanup (>90% full)

### System Flow

```
Alert Created
  ↓
Add to clip_processing_queue (status: pending)
  ↓
Background Worker picks up (status: processing)
  ↓
Call Frigate API: export clip (10s before + 20s after)
  ↓
Stream clip to local storage
  ↓
Verify clip integrity (playable MP4)
  ↓
Update alert.evidence.clip_url
  ↓
Update queue status: completed
  ↓
Add to clip_retention with expiry date
```

---

## Implementation Tasks

### Task 1: Frigate API Client (1 day)

**Files to create:**
- `services/nura-alerts/src/clients/frigate.client.ts`

**Code:**
```typescript
export class FrigateClient {
  constructor(
    private readonly httpService: HttpService,
    private readonly config: ConfigService
  ) {}
  
  async exportClip(params: {
    camera: string;
    start_time: Date;
    end_time: Date;
    playback?: 'realtime' | 'timelapse';
  }): Promise<ReadableStream | null> {
    try {
      const startTs = Math.floor(params.start_time.getTime() / 1000);
      const endTs = Math.floor(params.end_time.getTime() / 1000);
      
      const url = `${this.config.frigateApi}/api/export/${params.camera}/start/${startTs}/end/${endTs}`;
      
      const response = await this.httpService.axiosRef.get(url, {
        params: { playback: params.playback || 'realtime' },
        responseType: 'stream',
        timeout: 60000  // 60s timeout
      });
      
      return response.data;
    } catch (error) {
      this.logger.error(`Frigate export failed: ${error.message}`);
      return null;
    }
  }
  
  async verifyClipAvailable(
    camera: string,
    timestamp: Date
  ): Promise<boolean> {
    try {
      // Check if Frigate has recordings for this time
      const response = await this.httpService.axiosRef.get(
        `${this.config.frigateApi}/api/${camera}/recordings`,
        { params: { after: timestamp.getTime() / 1000 } }
      );
      
      return response.data && response.data.length > 0;
    } catch (error) {
      return false;
    }
  }
}
```

**Acceptance Criteria:**
- [ ] Can export clips from Frigate
- [ ] Handles Frigate API errors gracefully
- [ ] Verifies clip availability before export
- [ ] Streams data (no memory issues)
- [ ] Unit tests pass

### Task 2: Clip Processing Worker (2 days)

**Files to create:**
- `services/nura-alerts/src/workers/clip-processing.worker.ts`

**Code:**
```typescript
@Injectable()
export class ClipProcessingWorker {
  private isRunning = false;
  
  constructor(
    private readonly frigateClient: FrigateClient,
    private readonly alertService: AlertService,
    private readonly storageService: StorageService,
    private readonly queueRepository: Repository<ClipProcessingQueue>
  ) {}
  
  async start() {
    this.isRunning = true;
    this.logger.log('Clip processing worker started');
    
    while (this.isRunning) {
      await this.processNextClip();
      await this.sleep(10000);  // Poll every 10s
    }
  }
  
  async processNextClip() {
    // Get next pending job
    const job = await this.queueRepository.findOne({
      where: { status: 'pending' },
      order: { created_at: 'ASC' }
    });
    
    if (!job) return;
    
    // Mark as processing
    job.status = 'processing';
    await this.queueRepository.save(job);
    
    try {
      // Calculate clip window
      const startTime = new Date(
        job.incident_timestamp.getTime() - job.before_seconds * 1000
      );
      const endTime = new Date(
        job.incident_timestamp.getTime() + job.after_seconds * 1000
      );
      
      // Check if clip available
      const available = await this.frigateClient.verifyClipAvailable(
        job.camera_id,
        startTime
      );
      
      if (!available) {
        throw new Error('No recording available for this time period');
      }
      
      // Export clip from Frigate
      const stream = await this.frigateClient.exportClip({
        camera: job.camera_id,
        start_time: startTime,
        end_time: endTime
      });
      
      if (!stream) {
        throw new Error('Failed to export clip from Frigate');
      }
      
      // Save to storage
      const filename = `${job.alert_id}_clip.mp4`;
      const filepath = await this.storageService.saveStream(
        stream,
        'clips',
        filename
      );
      
      // Verify clip is playable
      const isValid = await this.verifyClip(filepath);
      if (!isValid) {
        throw new Error('Downloaded clip is corrupted');
      }
      
      // Get file size
      const stats = await fs.stat(filepath);
      
      // Update alert
      await this.alertService.updateEvidence(job.alert_id, {
        clip_url: `/api/alerts/${job.alert_id}/clip.mp4`,
        clip_duration_seconds: job.before_seconds + job.after_seconds,
        clip_start_time: startTime.toISOString(),
        clip_end_time: endTime.toISOString(),
        clip_size_bytes: stats.size,
        clip_status: 'available'
      });
      
      // Add to retention tracking
      const expiresAt = new Date();
      expiresAt.setDate(expiresAt.getDate() + 30);  // 30 days retention
      
      await this.storageService.trackClip({
        alert_id: job.alert_id,
        file_path: filepath,
        file_size_bytes: stats.size,
        expires_at: expiresAt
      });
      
      // Mark job completed
      job.status = 'completed';
      job.processed_at = new Date();
      await this.queueRepository.save(job);
      
      this.logger.log(`Clip attached to alert ${job.alert_id}`);
      
    } catch (error) {
      this.logger.error(`Clip processing failed: ${error.message}`);
      
      // Retry logic
      job.retry_count++;
      
      if (job.retry_count >= 3) {
        // Max retries reached
        job.status = 'failed';
        job.error_message = error.message;
        
        // Update alert - no clip available
        await this.alertService.updateEvidence(job.alert_id, {
          clip_status: 'unavailable',
          clip_error: error.message
        });
      } else {
        // Retry
        job.status = 'pending';
      }
      
      await this.queueRepository.save(job);
    }
  }
  
  async verifyClip(filepath: string): Promise<boolean> {
    try {
      // Use ffprobe to verify
      const { stdout } = await exec(
        `ffprobe -v error -show_format -show_streams "${filepath}"`
      );
      
      return stdout.includes('codec_type=video');
    } catch (error) {
      return false;
    }
  }
  
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  stop() {
    this.isRunning = false;
  }
}
```

**Acceptance Criteria:**
- [ ] Processes clips from queue
- [ ] Downloads from Frigate successfully
- [ ] Verifies clip integrity
- [ ] Handles retries (max 3)
- [ ] Updates alert with clip URL
- [ ] Unit tests pass

### Task 3: Clip Serving API (0.5 days)

**Files to modify:**
- `services/nura-alerts/src/controllers/alert.controller.ts`

**Code:**
```typescript
@Controller('api/alerts')
export class AlertController {
  
  @Get(':id/clip.mp4')
  @Header('Content-Type', 'video/mp4')
  @Header('Accept-Ranges', 'bytes')
  async streamClip(
    @Param('id') alertId: string,
    @Req() req: Request,
    @Res() res: Response
  ): Promise<void> {
    const alert = await this.alertService.findOne(alertId);
    
    if (!alert || !alert.evidence.clip_url) {
      throw new NotFoundException('Clip not found');
    }
    
    if (alert.evidence.clip_status === 'deleted') {
      throw new GoneException('Clip expired (retention period exceeded)');
    }
    
    if (alert.evidence.clip_status === 'pending') {
      throw new ServiceUnavailableException('Clip still processing - try again in 30s');
    }
    
    if (alert.evidence.clip_status === 'unavailable') {
      throw new NotFoundException(alert.evidence.clip_error || 'Clip unavailable');
    }
    
    // Get file path
    const filepath = path.join(
      this.config.storage.clips,
      `${alertId}_clip.mp4`
    );
    
    if (!await fs.pathExists(filepath)) {
      throw new NotFoundException('Clip file not found');
    }
    
    // Get file stats
    const stats = await fs.stat(filepath);
    
    // Handle range requests (for video seeking)
    const range = req.headers.range;
    
    if (range) {
      const parts = range.replace(/bytes=/, '').split('-');
      const start = parseInt(parts[0], 10);
      const end = parts[1] ? parseInt(parts[1], 10) : stats.size - 1;
      const chunksize = (end - start) + 1;
      
      res.writeHead(206, {
        'Content-Range': `bytes ${start}-${end}/${stats.size}`,
        'Content-Length': chunksize
      });
      
      const stream = createReadStream(filepath, { start, end });
      stream.pipe(res);
    } else {
      res.writeHead(200, {
        'Content-Length': stats.size
      });
      
      const stream = createReadStream(filepath);
      stream.pipe(res);
    }
  }
}
```

**Acceptance Criteria:**
- [ ] Clips stream correctly
- [ ] Handles range requests (seeking)
- [ ] Returns appropriate HTTP status codes
- [ ] Works in browser video players

### Task 4: Storage Cleanup Job (1 day)

**Files to create:**
- `services/nura-alerts/src/jobs/clip-cleanup.job.ts`

**Code:**
```typescript
@Injectable()
export class ClipCleanupJob {
  constructor(
    private readonly clipRetentionRepository: Repository<ClipRetention>,
    private readonly alertService: AlertService
  ) {}
  
  @Cron('0 2 * * *')  // Daily at 2 AM
  async cleanupExpiredClips() {
    this.logger.log('Starting clip cleanup job');
    
    // Find expired clips
    const expiredClips = await this.clipRetentionRepository.find({
      where: {
        expires_at: LessThan(new Date()),
        deleted_at: IsNull()
      }
    });
    
    this.logger.log(`Found ${expiredClips.length} expired clips`);
    
    let deletedCount = 0;
    let deletedBytes = 0;
    
    for (const clip of expiredClips) {
      try {
        // Delete file
        if (await fs.pathExists(clip.file_path)) {
          await fs.unlink(clip.file_path);
          deletedBytes += clip.file_size_bytes;
          deletedCount++;
        }
        
        // Mark as deleted
        clip.deleted_at = new Date();
        await this.clipRetentionRepository.save(clip);
        
        // Update alert
        await this.alertService.updateEvidence(clip.alert_id, {
          clip_status: 'deleted'
        });
        
      } catch (error) {
        this.logger.error(`Failed to delete clip ${clip.clip_id}: ${error.message}`);
      }
    }
    
    this.logger.log(
      `Cleanup complete: ${deletedCount} clips deleted, ` +
      `${(deletedBytes / 1024 / 1024).toFixed(2)} MB freed`
    );
  }
  
  @Cron('0 */6 * * *')  // Every 6 hours
  async checkStorageSpace() {
    const stats = await this.getStorageStats();
    
    const usagePercent = (stats.used / stats.total) * 100;
    
    if (usagePercent > 90) {
      this.logger.warn(`Storage ${usagePercent.toFixed(1)}% full - triggering emergency cleanup`);
      await this.emergencyCleanup();
    } else if (usagePercent > 80) {
      this.logger.warn(`Storage ${usagePercent.toFixed(1)}% full`);
    }
  }
  
  async emergencyCleanup() {
    // Delete oldest clips until < 80% full
    const target = 0.80;
    
    while (true) {
      const stats = await this.getStorageStats();
      const usage = stats.used / stats.total;
      
      if (usage < target) break;
      
      // Find oldest clip
      const oldestClip = await this.clipRetentionRepository.findOne({
        where: { deleted_at: IsNull() },
        order: { created_at: 'ASC' }
      });
      
      if (!oldestClip) break;
      
      // Delete it
      if (await fs.pathExists(oldestClip.file_path)) {
        await fs.unlink(oldestClip.file_path);
      }
      
      oldestClip.deleted_at = new Date();
      await this.clipRetentionRepository.save(oldestClip);
      
      await this.alertService.updateEvidence(oldestClip.alert_id, {
        clip_status: 'deleted'
      });
    }
    
    this.logger.log('Emergency cleanup complete');
  }
  
  async getStorageStats(): Promise<{ total: number; used: number; free: number }> {
    const { stdout } = await exec('df -B1 /data/alerts/clips | tail -1');
    const parts = stdout.trim().split(/\s+/);
    
    return {
      total: parseInt(parts[1]),
      used: parseInt(parts[2]),
      free: parseInt(parts[3])
    };
  }
}
```

**Acceptance Criteria:**
- [ ] Daily cleanup deletes expired clips
- [ ] Storage monitoring triggers emergency cleanup
- [ ] Alerts updated with deleted status
- [ ] Metrics logged

### Task 5: Update Email Notifications (0.5 days)

**Files to modify:**
- `services/nura-alerts/src/templates/alert-email.html`

**Update:**
```html
<h3>Evidence:</h3>

<!-- Snapshot -->
<img src="cid:snapshot" width="600" />

<!-- NEW: Video clip -->
{{#if evidence.clip_url}}
  <div style="margin: 20px 0;">
    <a href="{{baseUrl}}{{evidence.clip_url}}" 
       style="display: inline-block; padding: 15px 30px; background: #2563eb; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
      ▶️ Watch Video Evidence ({{evidence.clip_duration_seconds}}s)
    </a>
    <p style="font-size: 12px; color: #666;">
      Clip: {{evidence.clip_start_time}} to {{evidence.clip_end_time}}
    </p>
  </div>
{{else if evidence.clip_status === 'pending'}}
  <div style="margin: 20px 0; padding: 15px; background: #fef3c7; border-left: 4px solid #f59e0b;">
    <p>⏳ Video processing - will be available in ~30 seconds</p>
    <a href="{{baseUrl}}/api/alerts/{{alert_id}}">Refresh to see video</a>
  </div>
{{else}}
  <div style="margin: 20px 0; padding: 15px; background: #fee2e2; border-left: 4px solid #ef4444;">
    <p>📷 Snapshot only (no video recording available)</p>
    {{#if evidence.clip_error}}
      <p style="font-size: 12px;">Reason: {{evidence.clip_error}}</p>
    {{/if}}
  </div>
{{/if}}
```

**Acceptance Criteria:**
- [ ] Email shows video link when available
- [ ] Shows processing status when pending
- [ ] Shows error message when unavailable
- [ ] Link opens video in browser

---

## Testing Strategy

### Unit Tests

```typescript
// tests/frigate.client.spec.ts
describe('FrigateClient', () => {
  it('should export clip successfully', async () => {
    // Mock Frigate API
    // Call exportClip
    // Verify stream returned
  });
  
  it('should handle Frigate API timeout', async () => {
    // Mock timeout
    // Verify returns null
  });
});

// tests/clip-processing.worker.spec.ts
describe('ClipProcessingWorker', () => {
  it('should process clip from queue', async () => {
    // Create queue job
    // Run processNextClip
    // Verify clip downloaded and alert updated
  });
  
  it('should retry failed jobs', async () => {
    // Simulate Frigate failure
    // Verify retry count increases
    // Verify status changes after 3 retries
  });
});
```

### Integration Tests

```bash
# tests/integration/test_video_evidence.sh

# Test 1: Clip attachment
./demo.sh crying
sleep 35  # Wait for clip processing
curl http://localhost:3011/api/alerts/{id} | jq '.evidence.clip_url'
# Expected: URL present

# Test 2: Clip download
curl http://localhost:3011/api/alerts/{id}/clip.mp4 -o test.mp4
ffprobe test.mp4
# Expected: Valid 30s video

# Test 3: Clip cleanup
# Create old clip (backdate)
# Run cleanup job
# Verify clip deleted
```

---

## Deployment Plan

### Pre-deployment

- [ ] Test Frigate API connectivity
- [ ] Ensure storage space available (10GB minimum)
- [ ] Install ffmpeg/ffprobe (for clip verification)
- [ ] Configure retention period (default 30 days)

### Deployment Steps

1. **Database migration**
   ```bash
   psql -U nura -d nura_db -f edge/postgres/migrations/007_video_clips.sql
   ```

2. **Create storage directories**
   ```bash
   mkdir -p /data/alerts/clips
   chown nura:nura /data/alerts/clips
   chmod 755 /data/alerts/clips
   ```

3. **Deploy alert service**
   ```bash
   docker compose restart nura-alerts
   ```

4. **Start clip processing worker**
   - Worker starts automatically with alert service

5. **Test**
   ```bash
   ./demo.sh crying
   # Wait 35s
   curl http://localhost:3011/api/alerts/latest/clip.mp4 -I
   # Expect 200 OK
   ```

---

## Success Metrics

- [ ] 95%+ of alerts have video clips attached
- [ ] Clip processing time <30s average
- [ ] Zero storage out-of-space incidents
- [ ] Video clips playable in all major browsers
- [ ] Email video links have 80%+ click-through rate

---

**Sprint Duration:** 1 week (5 working days)  
**Team Size:** 1-2 backend engineers  
**Status:** ✅ Ready to implement  
**Dependencies:** Week 1 complete  
**Next:** Week 3 - Stranger Detection
