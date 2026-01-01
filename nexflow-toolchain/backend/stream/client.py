# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Kafka Client Module

High-level Kafka client for consuming, producing, and inspecting topics.
Supports SSL/SASL authentication and multiple cluster profiles.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple

from .config import KafkaConfig, KafkaProfile
from .decoder import DecodedMessage, MessageDecoder
from .filter import matches_filter
from .pii import create_masker


@dataclass
class TopicMetadata:
    """Kafka topic metadata."""
    name: str
    partitions: int
    replication_factor: int
    partition_offsets: Dict[int, Tuple[int, int]]  # partition -> (low, high)


@dataclass
class ConsumeOptions:
    """Options for consuming messages."""
    limit: int = 10
    offset: str = "latest"  # "earliest", "latest", or numeric offset
    partition: Optional[int] = None
    filter_expr: Optional[str] = None
    timeout_seconds: int = 30
    follow: bool = False


class KafkaClient:
    """High-level Kafka client for stream investigation."""

    def __init__(
        self,
        profile: KafkaProfile,
        kafka_config: KafkaConfig,
        decoder: Optional[MessageDecoder] = None,
    ):
        self.profile = profile
        self.kafka_config = kafka_config
        self.decoder = decoder or MessageDecoder()
        self._masker = create_masker(profile.pii_mask, kafka_config.pii)
        self._consumer = None
        self._producer = None
        self._admin = None

    def _get_consumer(self, group_id: Optional[str] = None):
        """Get or create a Kafka consumer."""
        if self._consumer:
            return self._consumer

        try:
            from confluent_kafka import Consumer
        except ImportError:
            raise RuntimeError("confluent-kafka is required. Install with: pip install confluent-kafka")

        config = self.profile.to_kafka_config()
        config['group.id'] = group_id or f'nexflow-peek-{datetime.now().strftime("%Y%m%d%H%M%S")}'
        config['auto.offset.reset'] = 'earliest'
        config['enable.auto.commit'] = False

        self._consumer = Consumer(config)
        return self._consumer

    def _get_producer(self):
        """Get or create a Kafka producer."""
        if self._producer:
            return self._producer

        try:
            from confluent_kafka import Producer
        except ImportError:
            raise RuntimeError("confluent-kafka is required. Install with: pip install confluent-kafka")

        config = self.profile.to_kafka_config()
        self._producer = Producer(config)
        return self._producer

    def _get_admin(self):
        """Get or create an admin client."""
        if self._admin:
            return self._admin

        try:
            from confluent_kafka.admin import AdminClient
        except ImportError:
            raise RuntimeError("confluent-kafka is required. Install with: pip install confluent-kafka")

        config = self.profile.to_kafka_config()
        self._admin = AdminClient(config)
        return self._admin

    def get_topic_metadata(self, topic: str) -> TopicMetadata:
        """Get metadata for a topic."""
        admin = self._get_admin()
        consumer = self._get_consumer()

        # Get cluster metadata
        metadata = admin.list_topics(topic=topic, timeout=10)

        if topic not in metadata.topics:
            raise ValueError(f"Topic not found: {topic}")

        topic_meta = metadata.topics[topic]
        partitions = len(topic_meta.partitions)

        # Get partition offsets
        from confluent_kafka import TopicPartition
        partition_offsets = {}

        for p in range(partitions):
            tp = TopicPartition(topic, p)
            low, high = consumer.get_watermark_offsets(tp, timeout=10)
            partition_offsets[p] = (low, high)

        return TopicMetadata(
            name=topic,
            partitions=partitions,
            replication_factor=len(topic_meta.partitions[0].replicas) if topic_meta.partitions else 0,
            partition_offsets=partition_offsets,
        )

    def consume(
        self,
        topic: str,
        options: ConsumeOptions,
    ) -> Generator[DecodedMessage, None, None]:
        """
        Consume messages from a topic.

        Yields decoded messages that match the filter criteria.
        """
        from confluent_kafka import TopicPartition, OFFSET_BEGINNING, OFFSET_END

        consumer = self._get_consumer()

        # Get topic metadata for partition info
        metadata = self.get_topic_metadata(topic)

        # Determine partitions to consume from
        if options.partition is not None:
            partitions = [options.partition]
        else:
            partitions = list(range(metadata.partitions))

        # Create topic-partition list with offsets
        tps = []
        for p in partitions:
            tp = TopicPartition(topic, p)

            if options.offset == "earliest":
                tp.offset = OFFSET_BEGINNING
            elif options.offset == "latest":
                tp.offset = OFFSET_END
            else:
                tp.offset = int(options.offset)

            tps.append(tp)

        # Assign partitions
        consumer.assign(tps)

        # Consume messages
        count = 0
        timeout_ms = options.timeout_seconds * 1000

        try:
            while options.follow or count < options.limit:
                msg = consumer.poll(timeout=timeout_ms / 1000)

                if msg is None:
                    if not options.follow:
                        break
                    continue

                if msg.error():
                    from confluent_kafka import KafkaError
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        if not options.follow:
                            break
                        continue
                    raise RuntimeError(f"Kafka error: {msg.error()}")

                # Decode message
                try:
                    decoded = self.decoder.decode_message(
                        data=msg.value(),
                        offset=msg.offset(),
                        partition=msg.partition(),
                        timestamp=msg.timestamp()[1] if msg.timestamp()[0] > 0 else None,
                        timestamp_type=str(msg.timestamp()[0]) if msg.timestamp()[0] > 0 else None,
                        key=msg.key(),
                        headers=msg.headers(),
                    )
                except Exception as e:
                    # Skip messages that fail to decode
                    continue

                # Apply filter
                if options.filter_expr:
                    if not matches_filter(decoded.value, options.filter_expr):
                        continue

                # Apply PII masking
                if self.profile.pii_mask:
                    decoded.value = self._masker.mask(decoded.value)

                yield decoded
                count += 1

                if not options.follow and count >= options.limit:
                    break

        finally:
            consumer.close()
            self._consumer = None

    def list_topics(self) -> List[str]:
        """List all topics in the cluster."""
        admin = self._get_admin()
        metadata = admin.list_topics(timeout=10)
        return sorted([
            name for name in metadata.topics.keys()
            if not name.startswith('_')  # Exclude internal topics
        ])

    def produce(
        self,
        topic: str,
        messages: List[Dict[str, Any]],
        key_field: Optional[str] = None,
        batch_size: int = 100,
        on_delivery: Optional[Callable] = None,
    ) -> int:
        """
        Produce messages to a topic.

        Returns the number of messages sent.
        """
        producer = self._get_producer()
        sent = 0

        def default_callback(err, msg):
            nonlocal sent
            if err:
                raise RuntimeError(f"Failed to deliver message: {err}")
            sent += 1

        callback = on_delivery or default_callback

        for msg in messages:
            key = None
            if key_field and key_field in msg:
                key = str(msg[key_field]).encode('utf-8')

            value = json.dumps(msg).encode('utf-8')

            producer.produce(
                topic=topic,
                value=value,
                key=key,
                callback=callback,
            )

            # Flush in batches
            if sent % batch_size == 0:
                producer.flush()

        # Final flush
        producer.flush()

        return sent

    def close(self):
        """Close all connections."""
        if self._consumer:
            self._consumer.close()
            self._consumer = None
        if self._producer:
            self._producer.flush()
            self._producer = None


def create_client(
    kafka_config: KafkaConfig,
    profile_name: Optional[str] = None,
    decoder: Optional[MessageDecoder] = None,
) -> KafkaClient:
    """Create a Kafka client for the specified profile."""
    profile = kafka_config.get_profile(profile_name)
    return KafkaClient(profile, kafka_config, decoder)
