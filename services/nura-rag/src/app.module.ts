import { Module } from '@nestjs/common';
import { ConfigModule } from './config/config.module.js';
import { RulesModule } from './rules/rules.module.js';
import { EmbeddingsModule } from './embeddings/embeddings.module.js';

@Module({
  imports: [
    ConfigModule,
    EmbeddingsModule,
    RulesModule,
  ],
})
export class AppModule {}
