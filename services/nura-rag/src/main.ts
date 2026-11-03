/**
 * NURA RAG Service
 * Rule knowledge base with semantic similarity search using pgvector
 * Spec: specs/023-rag-rule-knowledge/spec.md
 */
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module.js';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    logger: ['log', 'error', 'warn', 'debug'],
  });

  const port = process.env.PORT || 3002;
  await app.listen(port);

  console.log(`🚀 NURA RAG Service listening on port ${port}`);
  console.log(`📚 Spec: specs/023-rag-rule-knowledge/spec.md`);
}

bootstrap();
