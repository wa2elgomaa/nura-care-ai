import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { WiFiSensingService } from './wifi-sensing.service';
import { WiFiSensingEvent } from './entities/wifi-sensing-event.entity';
import { WiFiRoom } from './entities/wifi-room.entity';
import { ConfigService } from './config/config.service';

// Initialize config to get database URL
const configService = new ConfigService();

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'postgres',
      host: configService.POSTGRES_HOST,
      port: configService.POSTGRES_PORT,
      database: configService.POSTGRES_DB,
      username: configService.POSTGRES_USER,
      password: configService.POSTGRES_PASSWORD,
      autoLoadEntities: true,
      synchronize: false, // Use migrations
    }),
    TypeOrmModule.forFeature([WiFiSensingEvent, WiFiRoom]),
  ],
  providers: [ConfigService, WiFiSensingService],
})
export class AppModule {}
