import { Entity, Column, PrimaryColumn } from 'typeorm';

@Entity('wifi_rooms')
export class WiFiRoom {
  @PrimaryColumn({ length: 100 })
  roomId: string;

  @Column({ length: 50 })
  roomType: string;

  @Column({ length: 255 })
  roomName: string;

  @Column({ type: 'text', array: true, nullable: true })
  esp32NodeIds: string[];

  @Column({ default: false })
  cameraCoverage: boolean;

  @Column({ default: 2 })
  multiOccupancyThreshold: number;

  @Column({ default: 120 })
  multiOccupancyDurationSeconds: number;

  @Column({ type: 'time', default: '06:00' })
  operatingHoursStart: string;

  @Column({ type: 'time', default: '18:00' })
  operatingHoursEnd: string;

  @Column({ default: true })
  enabled: boolean;
}
