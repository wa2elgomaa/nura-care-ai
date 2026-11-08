#!/usr/bin/env python3
"""
Test script: Publish detection event to NATS
Tests RAG + Rules integration end-to-end
"""
import asyncio
import json
from datetime import datetime
from nats.aio.client import Client as NATS

async def publish_test_event():
    # Connect to NATS
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    print("✓ Connected to NATS")

    # Test Event 1: Supervision violation (no adults detected)
    detection_event = {
        "camera_id": "classroom-01",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": "no_adults_detected",
        "adults_detected": 0,
        "children_detected": 3,
        "confidence": 0.85,
        "metadata": {}
    }

    print(f"\n📡 Publishing test event to nura.events.detection:")
    print(json.dumps(detection_event, indent=2))

    await nc.publish(
        "nura.events.detection",
        json.dumps(detection_event).encode()
    )

    print("\n✅ Event published!")
    print("\nExpected flow:")
    print("  1. nura-rules receives event")
    print("  2. Starts tracking (30s threshold)")
    print("  3. After 30s, queries RAG for matching rules")
    print("  4. Creates violation if rule matches")

    print("\n⏳ Waiting 3 seconds for event processing...")
    await asyncio.sleep(3)

    # Close connection
    await nc.close()
    print("\n✓ NATS connection closed")

    print("\n📋 Check nura-rules logs:")
    print("  docker compose logs nura-rules --tail 30")

if __name__ == "__main__":
    asyncio.run(publish_test_event())
