import { Module } from '@nestjs/common';
import { RulesService } from './rules.service.js';
import { RulesController } from './rules.controller.js';
import { DatabaseService } from './database.service.js';
import { EmbeddingsModule } from '../embeddings/embeddings.module.js';

@Module({
  imports: [EmbeddingsModule],
  controllers: [RulesController],
  providers: [RulesService, DatabaseService],
  exports: [RulesService],
})
export class RulesModule {}
