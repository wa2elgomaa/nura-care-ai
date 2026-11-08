import { Module } from '@nestjs/common';
import { StreamProcessorService } from './stream-processor.service';
import { MqttBridgeService } from './mqtt-bridge.service';
import { FrigateClientService } from './frigate-client.service';

@Module({
  providers: [StreamProcessorService, MqttBridgeService, FrigateClientService],
  exports: [StreamProcessorService],
})
export class StreamProcessorModule {}
