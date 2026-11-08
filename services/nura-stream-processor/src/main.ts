import { NestFactory } from '@nestjs/core';
import { MicroserviceOptions, Transport } from '@nestjs/microservices';
import { AppModule } from './app.module';
import { Logger } from '@nestjs/common';

async function bootstrap() {
  const logger = new Logger('StreamProcessor');

  // Create hybrid application (HTTP + NATS microservice)
  const app = await NestFactory.create(AppModule);

  // Connect to NATS for publishing events
  const natsUrl = process.env.NATS_URL || 'nats://localhost:4222';
  app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.NATS,
    options: {
      servers: [natsUrl],
      queue: 'stream-processor',
    },
  });

  await app.startAllMicroservices();

  const port = process.env.PORT || 3010;
  await app.listen(port);

  logger.log(`🎬 Stream Processor Service started on port ${port}`);
  logger.log(`📡 Connected to NATS at ${natsUrl}`);
  logger.log(`🔌 MQTT bridge active`);
}

bootstrap();
