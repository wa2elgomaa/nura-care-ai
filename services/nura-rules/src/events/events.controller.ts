import { Controller, Logger } from '@nestjs/common';
import { EventPattern, Payload, Ctx, NatsContext } from '@nestjs/microservices';
import { ViolationsService, DetectionEvent, VLMAnalysis } from '../violations/violations.service.js';

/**
 * Events Controller
 * Subscribes to NATS events from detection pipeline
 * Spec: FR-001 - Subscribe to NATS events
 */
@Controller()
export class EventsController {
  private readonly logger = new Logger(EventsController.name);

  constructor(private readonly violationsService: ViolationsService) {}

  /**
   * Handle detection events from nura-perception (YOLO)
   * Topic: nura.events.detection
   */
  @EventPattern('nura.events.detection')
  async handleDetectionEvent(
    @Payload() data: DetectionEvent,
    @Ctx() context: NatsContext,
  ) {
    this.logger.log(
      `Received detection event: ${data.event_type} from ${data.camera_id}`,
    );

    try {
      const violation = await this.violationsService.processDetectionEvent(data);

      if (violation) {
        // Publish violation alert (FR-005)
        await this.publishViolationAlert(violation);
      }
    } catch (error) {
      this.logger.error('Failed to handle detection event:', error);
    }
  }

  /**
   * Handle VLM analysis events
   * Topic: nura.events.vlm_analysis
   */
  @EventPattern('nura.events.vlm_analysis')
  async handleVLMAnalysis(
    @Payload() data: { detection: DetectionEvent; analysis: VLMAnalysis },
    @Ctx() context: NatsContext,
  ) {
    this.logger.log(
      `Received VLM analysis for ${data.detection.camera_id}`,
    );

    try {
      const violation = await this.violationsService.processDetectionEvent(
        data.detection,
        data.analysis,
      );

      if (violation) {
        await this.publishViolationAlert(violation);
      }
    } catch (error) {
      this.logger.error('Failed to handle VLM analysis:', error);
    }
  }

  /**
   * Publish violation alert to NATS (FR-005)
   * Topic: nura.alerts.violation
   */
  private async publishViolationAlert(violation: any) {
    this.logger.log(
      `🚨 VIOLATION ALERT: ${violation.rule_id} - ${violation.title} (${violation.severity})`,
    );

    // TODO: Publish to NATS for nura-notifier
    // await this.natsClient.emit('nura.alerts.violation', violation);
  }
}
