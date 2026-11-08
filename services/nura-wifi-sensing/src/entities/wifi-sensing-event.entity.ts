import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn } from 'typeorm';

@Entity('wifi_sensing_events')
export class WiFiSensingEvent {
  @PrimaryGeneratedColumn('uuid')
  eventId: string;

  @Column({ length: 100 })
  roomId: string;

  @Column({ length: 50 })
  roomType: string;

  @Column()
  occupancyCount: number;

  @Column()
  deviceCount: number;

  @Column({ type: 'timestamp' })
  timestamp: Date;

  @Column({ nullable: true })
  durationSeconds: number;

  @Column({ type: 'text', array: true, nullable: true })
  esp32Nodes: string[];
}
