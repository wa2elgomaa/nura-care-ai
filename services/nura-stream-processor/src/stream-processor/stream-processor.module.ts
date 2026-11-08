import { Module } from '@nestjs/common';
import { StreamProcessorService } from './stream-processor.service';
import { MqttBridgeService } from './mqtt-bridge.service';
import { FrigateClientService } from './frigate-client.service';
import { DetectionStorageService } from './detection-storage.service';
import { ActivityClassifierService } from './activity-classifier.service';
import { UnknownHandlerService } from './unknown-handler.service';
import { ConfigService } from '../config/config.service';

@Module({
  providers: [
    ConfigService,
    StreamProcessorService,
    MqttBridgeService,
    FrigateClientService,
    DetectionStorageService,
    ActivityClassifierService,
    UnknownHandlerService,
  ],
  exports: [StreamProcessorService],
})
export class StreamProcessorModule {}
