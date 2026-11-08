import { NestFactory } from '@nestjs/core';
import { MicroserviceOptions, Transport } from '@nestjs/microservices';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';
import { Logger } from '@nestjs/common';

async function bootstrap() {
  const logger = new Logger('AlertService');

  // Create hybrid application (HTTP + NATS microservice)
  const app = await NestFactory.create(AppModule);

  // Enable validation
  app.useGlobalPipes(new ValidationPipe({
    transform: true,
    whitelist: true,
  }));

  // Connect to NATS for consuming violation events
  const natsUrl = process.env.NATS_URL || 'nats://localhost:4222';
  app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.NATS,
    options: {
      servers: [natsUrl],
      queue: 'alerts',
    },
  });

  await app.startAllMicroservices();

  const port = process.env.PORT || 3011;
  await app.listen(port, '0.0.0.0');  // Bind to all interfaces for Docker

  logger.log(`🚨 Alert Service started on port ${port}`);
  logger.log(`📡 Connected to NATS at ${natsUrl}`);
  logger.log(`📢 Multi-channel notifications active`);
}

bootstrap();
