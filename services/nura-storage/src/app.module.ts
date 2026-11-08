import { Module } from '@nestjs/common';
import { StorageController } from './storage.controller';
import { StorageService } from './storage.service';
import { ConfigService } from './config/config.service';

@Module({
  controllers: [StorageController],
  providers: [ConfigService, StorageService],
})
export class AppModule {}
