import { NestFactory } from '@nestjs/core';
import { Logger } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const logger = new Logger('Bootstrap');
  const app = await NestFactory.create(AppModule);

  logger.log('📡 NURA WiFi Sensing Service starting...');
  logger.log(`MQTT URL: ${process.env.MQTT_URL || 'mqtt://mosquitto:1883'}`);
  logger.log(`NATS URL: ${process.env.NATS_URL || 'nats://nats:4222'}`);
  logger.log(`RuView Topic: ${process.env.RUVIEW_TOPIC || 'ruview/occupancy/#'}`);

  // Start the application (service runs in background, no HTTP server needed)
  await app.init();

  logger.log('✓ WiFi Sensing Service initialized');
}

bootstrap();
