#!/usr/bin/env python3
"""
Order Consumer

Consumes processed/enriched orders from Kafka to verify the pipeline.
"""

import json
import sys

try:
    from kafka import KafkaConsumer
except ImportError:
    print("kafka-python not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "kafka-python"])
    from kafka import KafkaConsumer


def main():
    kafka_servers = sys.argv[1] if len(sys.argv) > 1 else "localhost:9093"
    topic = sys.argv[2] if len(sys.argv) > 2 else "orders.processed"

    print(f"Connecting to Kafka at {kafka_servers}...")
    print(f"Consuming from topic: {topic}")
    print("Press Ctrl+C to stop")
    print("-" * 60)

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=kafka_servers,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='e2e-test-consumer',
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

    count = 0
    try:
        for message in consumer:
            count += 1
            order = message.value

            # Check if it's an enriched order (has taxAmount)
            if 'taxAmount' in order:
                print(f"[{count}] ENRICHED Order: {order.get('orderId')}")
                print(f"     Customer: {order.get('customerId')}")
                print(f"     Amount: ${order.get('amount', 0):.2f}")
                print(f"     Tax: ${order.get('taxAmount', 0):.2f}")
                print(f"     Total: ${order.get('totalAmount', 0):.2f}")
                print(f"     Enriched at: {order.get('enrichedAt')}")
            else:
                print(f"[{count}] RAW Order: {json.dumps(order, indent=2)}")

            print("-" * 60)

    except KeyboardInterrupt:
        print(f"\nConsumed {count} messages")

    finally:
        consumer.close()


if __name__ == "__main__":
    main()
