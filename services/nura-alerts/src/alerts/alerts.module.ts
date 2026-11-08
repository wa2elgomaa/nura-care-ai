import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AlertsService } from './alerts.service';
import { Alert } from '../entities/alert.entity';
import { NotificationsModule } from '../notifications/notifications.module';

@Module({
  imports: [TypeOrmModule.forFeature([Alert]), NotificationsModule],
  providers: [AlertsService],
  exports: [AlertsService],
})
export class AlertsModule {}
