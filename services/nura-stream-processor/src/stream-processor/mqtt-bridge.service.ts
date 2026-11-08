import { Injectable, Logger, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import * as mqtt from 'mqtt';
import { connect, NatsConnection, JSONCodec } from 'nats';

/**
 * MQTT to NATS Bridge Service
 *
 * Subscribes to Frigate MQTT events and forwards them to NATS
 * for consumption by the AI pipeline.
 *
 * Frigate MQTT Topics:
 * - frigate/events → All events (new, update, end)
 * - frigate/{camera}/events → Camera-specific events
 * - frigate/{camera}/person → Person detection
 * - frigate/{camera}/person/snapshot → Person snapshot available
 */
@Injectable()
export class MqttBridgeService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(MqttBridgeService.name);
  private mqttClient: mqtt.MqttClient;
  private natsConnection: NatsConnection;
  private readonly jc = JSONCodec();

  private readonly MQTT_URL = process.env.MQTT_URL || 'mqtt://localhost:1883';
  private readonly NATS_URL = process.env.NATS_URL || 'nats://localhost:4222';

  // Frame processing rate (1 FPS = process 1 frame per second)
  private readonly FRAME_RATE = parseInt(process.env.FRAME_PROCESSING_RATE || '1', 10);
  private lastProcessedTime: Map<string, number> = new Map();

  async onModuleInit() {
    await this.connectNats();
    await this.connectMqtt();
  }

  async onModuleDestroy() {
    if (this.mqttClient) {
      this.mqttClient.end();
    }
    if (this.natsConnection) {
      await this.natsConnection.close();
    }
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

  private async connectMqtt() {
    this.mqttClient = mqtt.connect(this.MQTT_URL);

    this.mqttClient.on('connect', () => {
      this.logger.log(`✅ Connected to MQTT at ${this.MQTT_URL}`);
      this.subscribeToFrigateTopics();
    });

    this.mqttClient.on('error', (error) => {
      this.logger.error(`❌ MQTT connection error: ${error.message}`);
    });

    this.mqttClient.on('message', (topic, payload) => {
      this.handleMqttMessage(topic, payload);
    });
  }

  private subscribeToFrigateTopics() {
    // Subscribe to all Frigate event topics
    const topics = [
      'frigate/events',         // All events
      'frigate/+/events',       // Per-camera events
      'frigate/+/person',       // Person detections
      'frigate/+/person/snapshot', // Person snapshots
      'frigate/+/motion',       // Motion events
      'frigate/available',      // Frigate availability
    ];

    topics.forEach((topic) => {
      this.mqttClient.subscribe(topic, (err) => {
        if (err) {
          this.logger.error(`Failed to subscribe to ${topic}: ${err.message}`);
        } else {
          this.logger.log(`📡 Subscribed to ${topic}`);
        }
      });
    });
  }

  private handleMqttMessage(topic: string, payload: Buffer) {
    try {
      const payloadStr = payload.toString();

      // Some Frigate topics publish plain text values (not JSON)
      const plainTextTopics = ['frigate/available', '/motion'];
      const isPlainText = plainTextTopics.some(pt => topic.includes(pt));

      if (isPlainText) {
        // Handle plain text status messages
        if (topic === 'frigate/available') {
          this.publishToNats('frigate.status', {
            topic,
            timestamp: new Date().toISOString(),
            status: payloadStr, // "online", "offline", "stopped"
          });
        } else if (topic.includes('/motion')) {
          // Motion events are "ON" or "OFF" - we can ignore these for now
          // as we're processing person detections
          return;
        }
        this.logger.debug(`📨 Forwarded status message: ${topic} = ${payloadStr}`);
        return;
      }

      // Parse JSON messages
      const message = JSON.parse(payloadStr);

      // Rate limiting: Process frames at configured FPS
      if (this.shouldSkipFrame(topic)) {
        return;
      }

      // Route different event types to appropriate NATS subjects
      if (topic.includes('/person')) {
        this.publishToNats('frigate.detection.person', {
          topic,
          timestamp: new Date().toISOString(),
          ...message,
        });
      } else if (topic.includes('/events')) {
        this.publishToNats('frigate.events', {
          topic,
          timestamp: new Date().toISOString(),
          ...message,
        });
      }

      this.logger.debug(`📨 Forwarded MQTT message: ${topic}`);
    } catch (error) {
      this.logger.error(`❌ Error handling MQTT message from ${topic}: ${error.message}`);
    }
  }

  private shouldSkipFrame(topic: string): boolean {
    const now = Date.now();
    const lastTime = this.lastProcessedTime.get(topic) || 0;
    const minInterval = 1000 / this.FRAME_RATE; // milliseconds between frames

    if (now - lastTime < minInterval) {
      return true; // Skip this frame
    }

    this.lastProcessedTime.set(topic, now);
    return false;
  }

  private async publishToNats(subject: string, data: any) {
    try {
      await this.natsConnection.publish(subject, this.jc.encode(data));
      this.logger.debug(`📤 Published to NATS: ${subject}`);
    } catch (error) {
      this.logger.error(`❌ Failed to publish to NATS ${subject}: ${error.message}`);
    }
  }
}
