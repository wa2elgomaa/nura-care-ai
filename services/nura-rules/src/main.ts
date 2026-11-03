/**
 * NURA Rules Engine
 * Violation detection orchestrator: connects detection → VLM → RAG → alerts
 * Spec: specs/024-rules-engine-violation/spec.md
 */
import { NestFactory } from '@nestjs/core';
import { MicroserviceOptions, Transport } from '@nestjs/microservices';
import { AppModule } from './app.module.js';

async function bootstrap() {
  // Create HTTP server
  const app = await NestFactory.create(AppModule, {
    logger: ['log', 'error', 'warn', 'debug'],
  });

  // Connect NATS microservice
  const natsUrl = process.env.NATS_URL || 'nats://nats:4222';
  app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.NATS,
    options: {
      servers: [natsUrl],
    },
  });

  await app.startAllMicroservices();

  const port = process.env.PORT || 3003;
  await app.listen(port);

  console.log(`🚀 NURA Rules Engine listening on port ${port}`);
  console.log(`📡 NATS connected: ${natsUrl}`);
  console.log(`📋 Spec: specs/024-rules-engine-violation/spec.md`);
}

bootstrap();
