import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { WiFiSensingService } from './wifi-sensing.service';
import { WiFiSensingEvent } from './entities/wifi-sensing-event.entity';
import { WiFiRoom } from './entities/wifi-room.entity';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    TypeOrmModule.forRoot({
      type: 'postgres',
      url: process.env.DATABASE_URL,
      autoLoadEntities: true,
      synchronize: false, // Use migrations
    }),
    TypeOrmModule.forFeature([WiFiSensingEvent, WiFiRoom]),
  ],
  providers: [WiFiSensingService],
})
export class AppModule {}
