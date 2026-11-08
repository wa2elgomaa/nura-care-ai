import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { connect, NatsConnection, JSONCodec } from 'nats';
import { FrigateClientService } from './frigate-client.service';
import axios from 'axios';

/**
 * Stream Processor Service
 *
 * Main orchestrator that:
 * 1. Listens to NATS events from the MQTT bridge
 * 2. Fetches frames from Frigate
 * 3. Sends frames to AI pipeline (HybridRouter via VLM service)
 * 4. Publishes results back to NATS
 */
@Injectable()
export class StreamProcessorService implements OnModuleInit {
  private readonly logger = new Logger(StreamProcessorService.name);
  private natsConnection: NatsConnection;
  private readonly jc = JSONCodec();

  private readonly NATS_URL = process.env.NATS_URL || 'nats://localhost:4222';
  private readonly VLM_SERVICE_URL = process.env.VLM_SERVICE_URL || 'http://localhost:8001';

  constructor(private readonly frigateClient: FrigateClientService) {}

  async onModuleInit() {
    await this.connectNats();
    await this.subscribeToEvents();
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

  private async subscribeToEvents() {
    // Subscribe to person detection events
    const sub = this.natsConnection.subscribe('frigate.detection.person');

    this.logger.log('📡 Subscribed to frigate.detection.person');

    for await (const msg of sub) {
      try {
        const event = this.jc.decode(msg.data);
        await this.processDetectionEvent(event);
      } catch (error) {
        this.logger.error(`Error processing event: ${error.message}`);
      }
    }
  }

  private async processDetectionEvent(event: any) {
    try {
      this.logger.debug(`Processing detection event from ${event.topic}`);

      // Extract camera name from topic (e.g., "frigate/classroom_1/person")
      const topicParts = event.topic.split('/');
      const camera = topicParts[1];

      if (!camera) {
        this.logger.warn('No camera found in topic');
        return;
      }

      // Fetch latest frame from Frigate
      const frame = await this.frigateClient.getLatestFrame(camera);

      // Send frame to AI pipeline
      const aiResult = await this.sendToAIPipeline(camera, frame, event);

      // Publish AI results to NATS
      if (aiResult) {
        await this.publishResult(aiResult);
      }

    } catch (error) {
      this.logger.error(`Failed to process detection event: ${error.message}`);
    }
  }

  private async sendToAIPipeline(camera: string, frame: Buffer, event: any): Promise<any> {
    try {
      // Convert frame to base64 for VLM service
      const image_base64 = frame.toString('base64');

      // Send to VLM service hybrid endpoint
      const response = await axios.post(
        `${this.VLM_SERVICE_URL}/analyze/hybrid`,
        {
          image_base64,
          camera_id: camera,
        },
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 120000, // 120s timeout (first request loads models, takes 30-90s)
        }
      );

      this.logger.debug(`✅ AI analysis complete for ${camera}`);
      return {
        camera,
        timestamp: new Date().toISOString(),
        ...response.data,
      };

    } catch (error) {
      if (error.response) {
        this.logger.error(`AI pipeline error: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
      } else {
        this.logger.error(`Failed to send frame to AI pipeline: ${error.message}`);
      }
      return null;
    }
  }

  private async publishResult(result: any) {
    try {
      // Publish to different subjects based on violations detected
      if (result.violation_detected) {
        await this.natsConnection.publish(
          'violations.detected',
          this.jc.encode(result)
        );
        this.logger.log(`🚨 Violation detected: ${result.violation_type}`);
      } else {
        await this.natsConnection.publish(
          'detections.processed',
          this.jc.encode(result)
        );
      }

      // Also publish to camera-specific channel
      await this.natsConnection.publish(
        `camera.${result.camera}.analysis`,
        this.jc.encode(result)
      );

    } catch (error) {
      this.logger.error(`Failed to publish result: ${error.message}`);
    }
  }
}
