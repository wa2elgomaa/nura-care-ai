import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { FrigateClient } from '../clients/frigate.client';
import { StorageClient } from '../clients/storage.client';
import { ClipProcessingQueue, ClipStatus } from '../entities/clip-processing-queue.entity';
import { ClipRetention } from '../entities/clip-retention.entity';
import { Alert } from '../entities/alert.entity';

@Injectable()
export class ClipProcessingWorker implements OnModuleInit {
  private readonly logger = new Logger(ClipProcessingWorker.name);
  private isRunning = false;
  private readonly pollInterval: number;
  private readonly retentionDays: number;
  private readonly maxRetries: number;

  constructor(
    @InjectRepository(ClipProcessingQueue)
    private readonly queueRepository: Repository<ClipProcessingQueue>,
    @InjectRepository(ClipRetention)
    private readonly retentionRepository: Repository<ClipRetention>,
    @InjectRepository(Alert)
    private readonly alertRepository: Repository<Alert>,
    private readonly frigateClient: FrigateClient,
    private readonly storageClient: StorageClient,
  ) {
    this.pollInterval = parseInt(process.env.CLIP_POLL_INTERVAL || '10000', 10); // 10s default
    this.retentionDays = parseInt(process.env.CLIP_RETENTION_DAYS || '30', 10);
    this.maxRetries = parseInt(process.env.CLIP_MAX_RETRIES || '3', 10);
  }

  async onModuleInit() {
    // Start the worker
    this.start();
  }

  async start() {
    if (this.isRunning) {
      this.logger.warn('Worker already running');
      return;
    }

    this.isRunning = true;
    this.logger.log('🎬 Clip processing worker started');
    this.logger.log(`  Poll interval: ${this.pollInterval}ms`);
    this.logger.log(`  Retention: ${this.retentionDays} days`);
    this.logger.log(`  Max retries: ${this.maxRetries}`);

    this.processLoop();
  }

  async stop() {
    this.logger.log('Stopping clip processing worker');
    this.isRunning = false;
  }

  private async processLoop() {
    while (this.isRunning) {
      try {
        await this.processNextClip();
      } catch (error) {
        this.logger.error(`Error in processing loop: ${error.message}`);
      }

      // Wait before next poll
      await this.sleep(this.pollInterval);
    }
  }

  private async processNextClip() {
    // Get next pending job
    const job = await this.queueRepository.findOne({
      where: { status: ClipStatus.PENDING },
      order: { createdAt: 'ASC' },
    });

    if (!job) {
      return; // No jobs to process
    }

    // Mark as processing
    job.status = ClipStatus.PROCESSING;
    await this.queueRepository.save(job);

    this.logger.log(`Processing clip job ${job.queueId} for alert ${job.alertId}`);

    try {
      // Calculate clip window
      const startTime = new Date(
        job.incidentTimestamp.getTime() - job.beforeSeconds * 1000
      );
      const endTime = new Date(
        job.incidentTimestamp.getTime() + job.afterSeconds * 1000
      );

      // Check if clip available in Frigate
      const available = await this.frigateClient.verifyClipAvailable(
        job.cameraId,
        startTime
      );

      if (!available) {
        throw new Error('No recording available for this time period');
      }

      // Export clip from Frigate
      const stream = await this.frigateClient.exportClip({
        camera: job.cameraId,
        start_time: startTime,
        end_time: endTime,
      });

      if (!stream) {
        throw new Error('Failed to export clip from Frigate');
      }

      // Save to storage via StorageClient (HTTP call to nura-storage service)
      const filename = `${job.alertId}_clip.mp4`;
      const filepath = await this.storageClient.saveStream(stream, 'clips', filename);

      // Get file metadata
      const metadata = await this.storageClient.getMetadata('clips', filename);

      if (metadata.size === 0) {
        throw new Error('Downloaded clip is empty');
      }

      // Update alert with clip URL
      const alert = await this.alertRepository.findOne({ where: { id: job.alertId } });
      if (alert) {
        const evidence = alert.evidence || {};
        evidence.clip_url = `/api/alerts/${job.alertId}/clip`;
        evidence.clip_duration_seconds = job.beforeSeconds + job.afterSeconds;
        evidence.clip_start_time = startTime.toISOString();
        evidence.clip_end_time = endTime.toISOString();
        evidence.clip_size_bytes = fileSizeBytes;
        evidence.clip_status = 'available';

        alert.evidence = evidence;
        await this.alertRepository.save(alert);
      }

      // Add to retention tracking
      const expiresAt = new Date();
      expiresAt.setDate(expiresAt.getDate() + this.retentionDays);

      const retention = this.retentionRepository.create({
        alertId: job.alertId,
        filePath: filepath,
        fileSizeBytes,
        expiresAt,
      });
      await this.retentionRepository.save(retention);

      // Mark job as completed
      job.status = ClipStatus.COMPLETED;
      job.processedAt = new Date();
      await this.queueRepository.save(job);

      this.logger.log(`✓ Clip processed: ${filename} (${fileSizeBytes} bytes)`);
    } catch (error) {
      this.logger.error(`Failed to process clip: ${error.message}`);

      // Update retry count
      job.retryCount += 1;
      job.errorMessage = error.message;

      if (job.retryCount >= this.maxRetries) {
        // Max retries reached, mark as failed
        job.status = ClipStatus.FAILED;
        job.processedAt = new Date();

        // Update alert to show clip unavailable
        const alert = await this.alertRepository.findOne({ where: { id: job.alertId } });
        if (alert) {
          const evidence = alert.evidence || {};
          evidence.clip_url = null;
          evidence.clip_status = 'unavailable';
          evidence.clip_error = error.message;
          alert.evidence = evidence;
          await this.alertRepository.save(alert);
        }

        this.logger.error(`✗ Clip processing failed after ${this.maxRetries} retries: ${job.alertId}`);
      } else {
        // Retry
        job.status = ClipStatus.PENDING;
        this.logger.warn(`Retrying clip processing (attempt ${job.retryCount}/${this.maxRetries})`);
      }

      await this.queueRepository.save(job);
    }
  }

  private async saveStream(stream: Readable, filepath: string): Promise<void> {
    const writeStream = createWriteStream(filepath);
    await pipeline(stream, writeStream);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Daily cleanup job - delete expired clips
   */
  async cleanupExpiredClips(): Promise<number> {
    const now = new Date();

    const expiredClips = await this.retentionRepository.find({
      where: { expiresAt: { $lt: now } as any, deletedAt: null },
    });

    let deletedCount = 0;

    for (const clip of expiredClips) {
      try {
        // Delete file
        await unlink(clip.filePath);

        // Mark as deleted
        clip.deletedAt = now;
        await this.retentionRepository.save(clip);

        // Update alert
        const alert = await this.alertRepository.findOne({ where: { id: clip.alertId } });
        if (alert && alert.evidence) {
          alert.evidence.clip_status = 'deleted';
          await this.alertRepository.save(alert);
        }

        deletedCount++;
      } catch (error) {
        this.logger.error(`Failed to delete clip ${clip.clipId}: ${error.message}`);
      }
    }

    if (deletedCount > 0) {
      this.logger.log(`🗑️  Deleted ${deletedCount} expired clips`);
    }

    return deletedCount;
  }
}
