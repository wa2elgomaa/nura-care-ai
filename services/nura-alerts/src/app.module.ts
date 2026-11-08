import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ScheduleModule } from '@nestjs/schedule';
import { AlertsModule } from './alerts/alerts.module';
import { NotificationsModule } from './notifications/notifications.module';
import { HealthController } from './health.controller';
import { ConfigService } from './config/config.service';

// Initialize config to get database settings
const configService = new ConfigService();

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'postgres',
      ...configService.getDatabaseConfig(),
      autoLoadEntities: true,
      synchronize: false, // Use migrations
    }),
    ScheduleModule.forRoot(),
    AlertsModule,
    NotificationsModule,
  ],
  controllers: [HealthController],
  providers: [ConfigService],
})
export class AppModule {}
