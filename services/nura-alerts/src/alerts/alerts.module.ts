import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { HttpModule } from '@nestjs/axios';
import { AlertsService } from './alerts.service';
import { Alert } from '../entities/alert.entity';
import { ClipProcessingQueue } from '../entities/clip-processing-queue.entity';
import { ClipRetention } from '../entities/clip-retention.entity';
import { NotificationsModule } from '../notifications/notifications.module';
import { FrigateClient } from '../clients/frigate.client';
import { StorageClient } from '../clients/storage.client';
import { ClipProcessingWorker } from '../workers/clip-processing.worker';

@Module({
  imports: [
    TypeOrmModule.forFeature([Alert, ClipProcessingQueue, ClipRetention]),
    NotificationsModule,
    HttpModule,
  ],
  providers: [AlertsService, FrigateClient, StorageClient, ClipProcessingWorker],
  exports: [AlertsService],
})
export class AlertsModule {}
