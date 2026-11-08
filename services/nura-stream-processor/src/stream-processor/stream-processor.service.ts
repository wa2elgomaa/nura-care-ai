import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { connect, NatsConnection, JSONCodec } from 'nats';
import { FrigateClientService } from './frigate-client.service';
import { DetectionStorageService } from './detection-storage.service';
import { ActivityClassifierService } from './activity-classifier.service';
import { UnknownHandlerService } from './unknown-handler.service';
import { ConfigService } from '../config/config.service';
import axios from 'axios';

/**
 * Stream Processor Service
 *
 * Main orchestrator that:
 * 1. Listens to NATS events from the MQTT bridge
 * 2. Fetches frames from Frigate
 * 3. Sends frames to AI pipeline (HybridRouter via VLM service)
 * 4. Identifies persons via face recognition
 * 5. Classifies activities
 * 6. Stores detections to database for analytics
 * 7. Publishes results back to NATS
 *
 * Week 5: Fully automatic student behavioral analytics
 */
@Injectable()
export class StreamProcessorService implements OnModuleInit {
  private readonly logger = new Logger(StreamProcessorService.name);
  private natsConnection: NatsConnection;
  private readonly jc = JSONCodec();

  constructor(
    private readonly config: ConfigService,
    private readonly frigateClient: FrigateClientService,
    private readonly detectionStorage: DetectionStorageService,
    private readonly activityClassifier: ActivityClassifierService,
    private readonly unknownHandler: UnknownHandlerService,
  ) {}

  async onModuleInit() {
    await this.connectNats();
    await this.subscribeToEvents();
  }

  private async connectNats() {
    try {
      this.natsConnection = await connect({ servers: this.config.NATS_URL });
      this.logger.log(`✅ Connected to NATS at ${this.config.NATS_URL}`);
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

      // Week 5 Integration: Process detections for analytics
      if (aiResult && aiResult.persons_detected) {
        await this.processPersonDetections(camera, frame, aiResult);
      }

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
        `${this.config.VLM_SERVICE_URL}/analyze/hybrid`,
        {
          image_base64,
          camera_id: camera,
        },
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: this.config.AI_REQUEST_TIMEOUT,
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

  /**
   * Week 5: Process person detections for analytics
   *
   * For each detected person:
   * 1. Identify via face recognition (or create unknown)
   * 2. Classify activity
   * 3. Save to database
   */
  private async processPersonDetections(camera: string, frame: Buffer, aiResult: any) {
    try {
      const zone_name = this.detectionStorage.getZoneName(camera);
      const persons = aiResult.persons_detected || [];

      for (const person of persons) {
        // Step 1: Identify person (or create unknown)
        let person_id: string;

        if (this.config.FACE_RECOGNITION_ENABLED && person.bbox) {
          person_id = await this.identifyPerson(frame, person.bbox, person.face_embedding);
        } else {
          person_id = 'unidentified';
        }

        // Step 2: Classify activity
        let activity = 'other';
        let activity_confidence = 0.5;

        if (this.config.ACTIVITY_CLASSIFIER_ENABLED && person.bbox) {
          const classification = this.activityClassifier.classifyActivity(
            person_id,
            camera,
            person.bbox,
            {
              zone: zone_name,
              time_of_day: new Date().getHours(),
            }
          );
          activity = classification.activity;
          activity_confidence = classification.confidence;
        }

        // Step 3: Save detection to database
        await this.detectionStorage.saveDetection({
          person_id,
          camera_id: camera,
          zone_name,
          activity,
          activity_confidence,
          confidence: person.confidence || 0.9,
          bbox: person.bbox,
          frame_url: aiResult.frame_url,
        });

        this.logger.debug(`📊 Saved: ${person_id} @ ${zone_name} (${activity})`);
      }

    } catch (error) {
      this.logger.error(`Failed to process person detections: ${error.message}`);
    }
  }

  /**
   * Identify person via face recognition
   * Returns person_id or unknown_XXX
   */
  private async identifyPerson(frame: Buffer, bbox: any, face_embedding?: number[]): Promise<string> {
    try {
      // Call face recognition API
      const response = await axios.post(
        `${this.config.VLM_SERVICE_URL}/api/persons/search/by-image`,
        {
          photo: frame.toString('base64'),
          // Could also pass bbox to crop before sending
        },
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 10000,
        }
      );

      if (response.data && response.data.person_id) {
        return response.data.person_id;
      }

      // Not recognized - create or find unknown
      if (this.config.UNKNOWN_PERSON_TRACKING_ENABLED && face_embedding) {
        return await this.unknownHandler.findOrCreateUnknown(face_embedding);
      }

      return 'unidentified';

    } catch (error) {
      this.logger.debug(`Face recognition failed: ${error.message}`);

      // Fallback to unknown if we have embedding
      if (this.config.UNKNOWN_PERSON_TRACKING_ENABLED && face_embedding) {
        return await this.unknownHandler.findOrCreateUnknown(face_embedding);
      }

      return 'unidentified';
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
