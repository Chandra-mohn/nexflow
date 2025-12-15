#!/usr/bin/env python3
"""
Sample Order Producer

Sends sample order messages to Kafka for the Nexflow E2E test.
"""

import json
import time
import random
import sys
from datetime import datetime

try:
    from kafka import KafkaProducer
except ImportError:
    print("kafka-python not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "kafka-python"])
    from kafka import KafkaProducer


def create_order(order_id: int) -> dict:
    """Generate a sample order."""
    customers = ["CUST001", "CUST002", "CUST003", "CUST004", "CUST005"]
    statuses = ["pending", "confirmed", "processing"]

    return {
        "orderId": f"ORD-{order_id:05d}",
        "customerId": random.choice(customers),
        "amount": round(random.uniform(10.0, 500.0), 2),
        "status": random.choice(statuses),
        "timestamp": int(datetime.now().timestamp() * 1000)
    }


def main():
    kafka_servers = sys.argv[1] if len(sys.argv) > 1 else "localhost:9093"
    topic = "orders.input"
    num_orders = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    delay = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0

    print(f"Connecting to Kafka at {kafka_servers}...")
    print(f"Topic: {topic}")
    print(f"Orders to send: {num_orders}")
    print(f"Delay between orders: {delay}s")
    print("-" * 50)

    producer = KafkaProducer(
        bootstrap_servers=kafka_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None
    )

    for i in range(1, num_orders + 1):
        order = create_order(i)

        # Use customerId as the key for partitioning
        future = producer.send(topic, key=order["customerId"], value=order)
        result = future.get(timeout=10)

        print(f"[{i}/{num_orders}] Sent: {order['orderId']} | "
              f"Customer: {order['customerId']} | "
              f"Amount: ${order['amount']:.2f} | "
              f"Partition: {result.partition}")

        if i < num_orders:
            time.sleep(delay)

    producer.flush()
    producer.close()

    print("-" * 50)
    print(f"Successfully sent {num_orders} orders to {topic}")
    print("Check Kafka UI at http://localhost:8085 to see the messages")


if __name__ == "__main__":
    main()
