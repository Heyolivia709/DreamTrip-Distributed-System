"""Kafka producer service - send events to Kafka"""
import json
import logging
from typing import Dict, Optional
try:
    from kafka import KafkaProducer
    from kafka.errors import KafkaError
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    KafkaProducer = None
    KafkaError = Exception

from config import settings


logger = logging.getLogger(__name__)


class KafkaProducerService:
    """Kafka producer service"""
    
    def __init__(self):
        self.producer: Optional[KafkaProducer] = None
        self._initialize_producer()
    
    def _initialize_producer(self):
        """Initialize Kafka producer"""
        if not KAFKA_AVAILABLE:
            logger.warning("⚠️  kafka-python library unavailable, Kafka Producer will be disabled")
            self.producer = None
            return
            
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[settings.kafka_broker],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas to confirm
                retries=3,   # Retry count
                max_in_flight_requests_per_connection=1,  # Ensure message order
                compression_type='gzip'  # Compression
            )
            logger.info(f"✅ Kafka Producer connected: {settings.kafka_broker}")
        except Exception as e:
            logger.warning(f"⚠️  Kafka Producer initialization failed: {e}")
            logger.warning("System will run without Kafka")
            self.producer = None
    
    def send_event(
        self,
        topic: str,
        event_type: str,
        data: Dict,
        key: Optional[str] = None
    ) -> bool:
        """Send event to Kafka
        
        Args:
            topic: Kafka topic
            event_type: Event type
            data: Event data
            key: Message key (for partitioning)
            
        Returns:
            True if sent successfully, False if failed
        """
        if not self.producer:
            logger.warning(f"Kafka Producer not initialized, skipping event: {event_type}")
            return False
        
        try:
            event = {
                "event_type": event_type,
                "data": data,
                "timestamp": None  # Automatically added by Kafka
            }
            
            future = self.producer.send(
                topic=topic,
                value=event,
                key=key
            )
            
            # Async send, non-blocking
            future.add_callback(self._on_send_success)
            future.add_errback(self._on_send_error)
            
            logger.info(f"📤 Kafka event sent: {event_type} → {topic}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send Kafka event: {e}")
            return False
    
    def _on_send_success(self, record_metadata):
        """Send success callback"""
        logger.debug(
            f"✅ Kafka message confirmed: topic={record_metadata.topic}, "
            f"partition={record_metadata.partition}, "
            f"offset={record_metadata.offset}"
        )
    
    def _on_send_error(self, exc):
        """Send failure callback"""
        logger.error(f"❌ Kafka message send failed: {exc}")
    
    def send_trip_created_event(self, trip_id: int, trip_data: Dict) -> bool:
        """Send trip plan created event
        
        Args:
            trip_id: Trip plan ID
            trip_data: Trip plan data
            
        Returns:
            Return True if sent successfully
        """
        return self.send_event(
            topic="trip_events",
            event_type="trip_created",
            data={
                "trip_id": trip_id,
                "origin": trip_data.get("origin"),
                "destination": trip_data.get("destination"),
                "duration": trip_data.get("duration"),
                "preferences": trip_data.get("preferences")
            },
            key=str(trip_id)
        )
    
    def send_trip_completed_event(self, trip_id: int) -> bool:
        """Send trip plan completed event
        
        Args:
            trip_id: Trip plan ID
            
        Returns:
            Return True if sent successfully
        """
        return self.send_event(
            topic="trip_events",
            event_type="trip_completed",
            data={"trip_id": trip_id},
            key=str(trip_id)
        )
    
    def send_trip_failed_event(self, trip_id: int, error: str) -> bool:
        """Send trip plan failed event
        
        Args:
            trip_id: Trip plan ID
            error: Error message
            
        Returns:
            Return True if sent successfully
        """
        return self.send_event(
            topic="trip_events",
            event_type="trip_failed",
            data={
                "trip_id": trip_id,
                "error": error
            },
            key=str(trip_id)
        )
    
    def close(self):
        """Close producer"""
        if self.producer:
            self.producer.flush()  # Ensure all messages are sent
            self.producer.close()
            logger.info("Kafka Producer closed")


# Singleton
kafka_producer = KafkaProducerService()
