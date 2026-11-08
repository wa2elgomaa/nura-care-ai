import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, MoreThan } from 'typeorm';
import { connect, NatsConnection, JSONCodec } from 'nats';
import * as crypto from 'crypto';
import { Alert, AlertSeverity, AlertStatus } from '../entities/alert.entity';
import { NotificationsService } from '../notifications/notifications.service';
import { ClipProcessingQueue } from '../entities/clip-processing-queue.entity';

@Injectable()
export class AlertsService implements OnModuleInit {
  private readonly logger = new Logger(AlertsService.name);
  private natsConnection: NatsConnection;
  private readonly jc = JSONCodec();

  private readonly AGGREGATION_WINDOW = parseInt(process.env.ALERT_AGGREGATION_WINDOW || '30', 10) * 1000; // ms
  private readonly NATS_URL = process.env.NATS_URL || 'nats://localhost:4222';

  constructor(
    @InjectRepository(Alert)
    private alertRepository: Repository<Alert>,
    @InjectRepository(ClipProcessingQueue)
    private clipQueueRepository: Repository<ClipProcessingQueue>,
    private notificationsService: NotificationsService,
  ) {}

  async onModuleInit() {
    await this.connectNats();
    await this.subscribeToViolations();
  }

  private async connectNats() {
    try {
      this.natsConnection = await connect({ servers: this.NATS_URL });
      this.logger.log(`✅ Connected to NATS at ${this.NATS_URL}`);
    } catch (error) {
      this.logger.error(`❌ Failed to connect to NATS: ${error.message}`);
      throw error;
    }
  }

  private async subscribeToViolations() {
    const sub = this.natsConnection.subscribe('violations.detected');
    this.logger.log('📡 Subscribed to violations.detected');

    for await (const msg of sub) {
      try {
        const violation = this.jc.decode(msg.data);
        await this.processViolation(violation);
      } catch (error) {
        this.logger.error(`Error processing violation: ${error.message}`);
      }
    }
  }

  private async processViolation(violation: any) {
    try {
      // Generate hash for deduplication
      const hash = this.generateHash(violation);

      // Check for recent duplicate
      const recentWindow = new Date(Date.now() - this.AGGREGATION_WINDOW);
      const existingAlert = await this.alertRepository.findOne({
        where: {
          hash,
          firstDetected: MoreThan(recentWindow),
        },
      });

      if (existingAlert) {
        // Aggregate with existing alert
        await this.aggregateAlert(existingAlert, violation);
      } else {
        // Create new alert
        await this.createNewAlert(violation, hash);
      }
    } catch (error) {
      this.logger.error(`Failed to process violation: ${error.message}`);
    }
  }

  private generateHash(violation: any): string {
    const key = `${violation.camera}_${violation.violation_type}_${violation.person_id || 'unknown'}`;
    return crypto.createHash('sha256').update(key).digest('hex');
  }

  private async aggregateAlert(alert: Alert, violation: any) {
    alert.detectionCount += 1;
    alert.lastDetected = new Date();
    alert.confidenceMax = Math.max(alert.confidenceMax || 0, violation.confidence);
    alert.confidenceAvg = ((alert.confidenceAvg * (alert.detectionCount - 1)) + violation.confidence) / alert.detectionCount;

    // Re-classify severity based on new data
    alert.severity = this.classifySeverity(violation.violation_type, alert);

    await this.alertRepository.save(alert);
    this.logger.log(`📊 Aggregated alert ${alert.id} (count: ${alert.detectionCount})`);

    // Send notification if severity increased
    if (alert.status === AlertStatus.PENDING && alert.detectionCount > 3) {
      await this.sendAlert(alert);
    }
  }

  private async createNewAlert(violation: any, hash: string) {
    const severity = this.classifySeverity(violation.violation_type, violation);

    const alert = this.alertRepository.create({
      camera: violation.camera,
      violationType: violation.violation_type,
      severity,
      confidence: violation.confidence,
      confidenceAvg: violation.confidence,
      confidenceMax: violation.confidence,
      personId: violation.person_id,
      details: violation.details || '',
      metadata: violation,
      hash,
      status: AlertStatus.PENDING,
      // Week 1: Person identification and context
      personsInvolved: violation.persons_involved || null,
      context: violation.context || null,
      evidence: violation.evidence || null,
    });

    await this.alertRepository.save(alert);
    this.logger.log(`🚨 New alert created: ${alert.id} (${violation.violation_type})`);

    // Week 2: Add to clip processing queue
    await this.queueClipProcessing(alert, violation);

    // Send notification immediately for high/critical severity
    if (severity === AlertSeverity.HIGH || severity === AlertSeverity.CRITICAL) {
      await this.sendAlert(alert);
    }
  }

  private async queueClipProcessing(alert: Alert, violation: any) {
    try {
      const clipJob = this.clipQueueRepository.create({
        alertId: alert.id,
        cameraId: violation.camera,
        incidentTimestamp: alert.firstDetected,
        beforeSeconds: parseInt(process.env.CLIP_BEFORE_SECONDS || '10', 10),
        afterSeconds: parseInt(process.env.CLIP_AFTER_SECONDS || '20', 10),
      });

      await this.clipQueueRepository.save(clipJob);
      this.logger.log(`📹 Queued clip processing for alert ${alert.id}`);
    } catch (error) {
      this.logger.error(`Failed to queue clip processing: ${error.message}`);
    }
  }

  private classifySeverity(violationType: string, data: any): AlertSeverity {
    const confidence = data.confidence || data.confidenceMax || 0;
    const count = data.detectionCount || 1;

    // Violence classification
    if (violationType === 'violence') {
      if (confidence > 0.9) return AlertSeverity.CRITICAL;
      if (confidence > 0.75) return AlertSeverity.HIGH;
      return AlertSeverity.MEDIUM;
    }

    // Distress classification
    if (violationType === 'distress') {
      if (count > 30) return AlertSeverity.HIGH;
      if (count > 10) return AlertSeverity.MEDIUM;
      return AlertSeverity.LOW;
    }

    // Supervision classification
    if (violationType === 'supervision') {
      const duration = data.duration || 0;
      if (duration > 300) return AlertSeverity.CRITICAL; // 5 minutes
      if (duration > 120) return AlertSeverity.HIGH; // 2 minutes
      return AlertSeverity.MEDIUM;
    }

    return AlertSeverity.MEDIUM;
  }

  private async sendAlert(alert: Alert) {
    try {
      await this.notificationsService.sendNotification(alert);
      alert.status = AlertStatus.SENT;
      await this.alertRepository.save(alert);
      this.logger.log(`📤 Alert sent: ${alert.id}`);
    } catch (error) {
      this.logger.error(`Failed to send alert ${alert.id}: ${error.message}`);
    }
  }

  async acknowledgeAlert(id: string, userId: string) {
    const alert = await this.alertRepository.findOne({ where: { id } });
    if (!alert) {
      throw new Error('Alert not found');
    }

    alert.status = AlertStatus.ACKNOWLEDGED;
    alert.acknowledgedAt = new Date();
    alert.acknowledgedBy = userId;
    await this.alertRepository.save(alert);

    this.logger.log(`✅ Alert acknowledged: ${id} by ${userId}`);
    return alert;
  }

  async resolveAlert(id: string) {
    const alert = await this.alertRepository.findOne({ where: { id } });
    if (!alert) {
      throw new Error('Alert not found');
    }

    alert.status = AlertStatus.RESOLVED;
    alert.resolvedAt = new Date();
    await this.alertRepository.save(alert);

    this.logger.log(`✅ Alert resolved: ${id}`);
    return alert;
  }
}
