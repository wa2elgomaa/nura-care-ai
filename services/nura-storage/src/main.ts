import { NestFactory } from '@nestjs/core';
import { Logger } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const logger = new Logger('Bootstrap');
  const app = await NestFactory.create(AppModule);

  const port = process.env.PORT || 3012;

  // Enable CORS for cross-service communication
  app.enableCors();

  await app.listen(port);
  logger.log(`🗄️  NURA Storage Service running on port ${port}`);
  logger.log(`Storage backend: ${process.env.STORAGE_BACKEND || 'local'}`);
  logger.log(`Base directory: ${process.env.STORAGE_BASE_DIR || '/tmp/nura-storage'}`);
}

bootstrap();
