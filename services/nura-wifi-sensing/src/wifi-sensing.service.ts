import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { connect, MqttClient } from 'mqtt';
import { connect as natsConnect, NatsConnection, JSONCodec } from 'nats';
import { WiFiSensingEvent } from './entities/wifi-sensing-event.entity';
import { WiFiRoom } from './entities/wifi-room.entity';
import { ConfigService } from './config/config.service';

interface RuViewMessage {
  room_id: string;
  occupancy_count: number;
  device_count: number;
  timestamp: string;
  esp32_nodes?: string[];
}

@Injectable()
export class WiFiSensingService implements OnModuleInit {
  private readonly logger = new Logger(WiFiSensingService.name);
  private mqttClient: MqttClient;
  private natsClient: NatsConnection;
  private readonly jc = JSONCodec();

  constructor(
    private readonly config: ConfigService,
    @InjectRepository(WiFiSensingEvent)
    private eventRepository: Repository<WiFiSensingEvent>,
    @InjectRepository(WiFiRoom)
    private roomRepository: Repository<WiFiRoom>,
  ) {}

  async onModuleInit() {
    await this.connectNats();
    await this.connectMqtt();
  }

  private async connectNats() {
    try {
      this.natsClient = await natsConnect({ servers: this.config.NATS_URL });
      this.logger.log(`✓ Connected to NATS: ${this.config.NATS_URL}`);
    } catch (error) {
      this.logger.error(`Failed to connect to NATS: ${error.message}`);
    }
  }

  private async connectMqtt() {
    try {
      const mqttConfig = this.config.getMqttConfig();
      this.mqttClient = connect(mqttConfig.url, {
        username: mqttConfig.username || undefined,
        password: mqttConfig.password || undefined,
      });

      this.mqttClient.on('connect', () => {
        this.logger.log(`✓ Connected to MQTT: ${mqttConfig.url}`);
        mqttConfig.topics.forEach(topic => {
          this.mqttClient.subscribe(topic, (err) => {
            if (err) {
            this.logger.error(`Failed to subscribe: ${err.message}`);
          } else {
            this.logger.log(`✓ Subscribed to: ${this.ruviewTopic}`);
          }
        });
      });

      this.mqttClient.on('message', async (topic, message) => {
        await this.handleRuViewMessage(topic, message);
      });

      this.mqttClient.on('error', (error) => {
        this.logger.error(`MQTT error: ${error.message}`);
      });
    } catch (error) {
      this.logger.error(`Failed to connect to MQTT: ${error.message}`);
    }
  }

  private async handleRuViewMessage(topic: string, message: Buffer) {
    try {
      const data: RuViewMessage = JSON.parse(message.toString());

      // Get room configuration
      const room = await this.roomRepository.findOne({
        where: { roomId: data.room_id, enabled: true },
      });

      if (!room) {
        this.logger.warn(`Unknown or disabled room: ${data.room_id}`);
        return;
      }

      // Store event
      const event = this.eventRepository.create({
        roomId: data.room_id,
        roomType: room.roomType,
        occupancyCount: data.occupancy_count,
        deviceCount: data.device_count,
        timestamp: new Date(data.timestamp),
        esp32Nodes: data.esp32_nodes || [],
      });

      await this.eventRepository.save(event);

      this.logger.log(
        `WiFi event: ${room.roomName} - ${data.occupancy_count} occupants`
      );

      // Check for anomalies
      await this.checkAnomalies(room, event);
    } catch (error) {
      this.logger.error(`Failed to process WiFi message: ${error.message}`);
    }
  }

  private async checkAnomalies(room: WiFiRoom, event: WiFiSensingEvent) {
    // Check multi-occupancy
    if (
      event.occupancyCount >= room.multiOccupancyThreshold &&
      room.roomType === 'bathroom'
    ) {
      await this.checkMultiOccupancyDuration(room, event);
    }

    // Check after-hours
    await this.checkAfterHours(room, event);
  }

  private async checkMultiOccupancyDuration(
    room: WiFiRoom,
    currentEvent: WiFiSensingEvent
  ) {
    // Get recent events for this room
    const thresholdTime = new Date(
      currentEvent.timestamp.getTime() - room.multiOccupancyDurationSeconds * 1000
    );

    const recentEvents = await this.eventRepository.find({
      where: {
        roomId: room.roomId,
      },
      order: { timestamp: 'DESC' },
      take: 50,
    });

    // Check if occupancy >= threshold for the duration
    const highOccupancyEvents = recentEvents.filter(
      (e) =>
        e.timestamp >= thresholdTime &&
        e.occupancyCount >= room.multiOccupancyThreshold
    );

    if (highOccupancyEvents.length >= 10) {
      // ~2 minutes at 5s intervals
      await this.publishAlert({
        type: 'wifi_anomaly',
        data_source: 'wifi',
        camera: 'wifi_' + room.roomId,
        violation_type: 'multi_occupancy',
        severity: 'high',
        confidence: 0.9,
        details: `${room.roomName}: ${currentEvent.occupancyCount} people for ${room.multiOccupancyDurationSeconds}s`,
        wifi_event: {
          room_id: room.roomId,
          room_type: room.roomType,
          anomaly_type: 'multi_occupancy',
          occupancy_count: currentEvent.occupancyCount,
          duration_seconds: room.multiOccupancyDurationSeconds,
          started_at: thresholdTime.toISOString(),
        },
      });
    }
  }

  private async checkAfterHours(room: WiFiRoom, event: WiFiSensingEvent) {
    const currentTime = event.timestamp;
    const hours = currentTime.getHours();
    const minutes = currentTime.getMinutes();
    const currentMinutes = hours * 60 + minutes;

    const [startHour, startMin] = room.operatingHoursStart.split(':').map(Number);
    const [endHour, endMin] = room.operatingHoursEnd.split(':').map(Number);
    const startMinutes = startHour * 60 + startMin;
    const endMinutes = endHour * 60 + endMin;

    if (currentMinutes < startMinutes || currentMinutes > endMinutes) {
      if (event.occupancyCount > 0) {
        await this.publishAlert({
          type: 'wifi_anomaly',
          data_source: 'wifi',
          camera: 'wifi_' + room.roomId,
          violation_type: 'after_hours',
          severity: 'critical',
          confidence: 0.95,
          details: `${room.roomName}: ${event.occupancyCount} people detected after hours`,
          wifi_event: {
            room_id: room.roomId,
            room_type: room.roomType,
            anomaly_type: 'after_hours',
            occupancy_count: event.occupancyCount,
            duration_seconds: 0,
            started_at: currentTime.toISOString(),
          },
        });
      }
    }
  }

  private async publishAlert(alert: any) {
    try {
      if (this.natsClient) {
        this.natsClient.publish('violations.detected', this.jc.encode(alert));
        this.logger.warn(`🚨 WiFi Alert: ${alert.wifi_event.anomaly_type} - ${alert.details}`);
      }
    } catch (error) {
      this.logger.error(`Failed to publish alert: ${error.message}`);
    }
  }
}
